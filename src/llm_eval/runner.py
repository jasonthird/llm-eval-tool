from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable

from llm_eval.config import load_config, load_tasks
from llm_eval.events import (
    EvalEvent,
    model_call_finished,
    model_call_started,
    run_finished,
    run_started,
    task_failed,
    task_finished,
    task_started,
)
from llm_eval.extraction import extract_answer
from llm_eval.flows.multi_turn import run_multi_turn
from llm_eval.flows.single_turn import run_single_turn
from llm_eval.flows.tool_calling import run_tool_calling
from llm_eval.llm import LLMClient, LiteLLMClient, ModelResponse
from llm_eval.schemas import (
    AppConfig,
    BenchmarkConfig,
    EvaluationResult,
    ModelConfig,
    MultiTurnTask,
    SingleTurnTask,
    Task,
    ToolTrace,
    ToolCallingTask,
    new_run_id,
)
from llm_eval.scoring import response_correct, tool_selection_correct
from llm_eval.trace_writer import AsyncTraceWriter


FlowResult = tuple[ModelResponse, list[dict[str, Any]], list[ToolTrace], list[dict[str, Any]]]
FlowHandler = Callable[..., Awaitable[FlowResult]]


class EvaluationRunner:
    def __init__(self, config: AppConfig, mock_mode: bool = False):
        self.config = config
        self.mock_mode = mock_mode
        self.client: LLMClient = LiteLLMClient(mock_mode=mock_mode)
        self.global_sem = asyncio.Semaphore(config.runner.concurrency.global_limit)
        self.model_sems: dict[str, asyncio.Semaphore] = {}
        self._flow_handlers: dict[str, FlowHandler] = {
            "single_turn": self._run_single_turn_flow,
            "multi_turn": self._run_multi_turn_flow,
            "tool_calling": self._run_tool_calling_flow,
        }

    def _model_sem(self, model_config: ModelConfig) -> asyncio.Semaphore:
        limit = model_config.concurrency_limit or self.config.runner.concurrency.per_model_limit
        return self.model_sems.setdefault(model_config.name, asyncio.Semaphore(limit))

    async def run(
        self,
        *,
        run_id: str,
        output_path: str | Path,
        task_type: str | None = None,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> AsyncIterator[EvalEvent]:
        event_queue: asyncio.Queue[EvalEvent | None] = asyncio.Queue()

        async def emit(event: EvalEvent) -> None:
            await event_queue.put(event)

        async def produce() -> None:
            start = time.perf_counter()
            try:
                await emit(run_started(run_id, mock_mode=self.mock_mode))
                async with AsyncTraceWriter(output_path) as writer:
                    jobs = []
                    for benchmark in self.config.benchmarks:
                        if task_type and task_type != "all" and benchmark.task_type != task_type:
                            continue
                        for task in load_tasks(benchmark.path):
                            if not task_matches_filter(task, include=include, exclude=exclude):
                                continue
                            for model_config in self.config.models:
                                jobs.append(
                                    asyncio.create_task(
                                        self._run_one(
                                            run_id,
                                            benchmark,
                                            task,
                                            model_config,
                                            writer,
                                            emit,
                                        )
                                    )
                                )
                    results = await asyncio.gather(*jobs, return_exceptions=True)
                    failures = sum(1 for item in results if isinstance(item, Exception))
                await emit(
                    run_finished(
                        run_id,
                        total=len(jobs),
                        failures=failures,
                        output_path=str(output_path),
                        elapsed_seconds=time.perf_counter() - start,
                    )
                )
            finally:
                await event_queue.put(None)

        producer = asyncio.create_task(produce())
        try:
            while True:
                event = await event_queue.get()
                if event is None:
                    break
                yield event
            await producer
        finally:
            if not producer.done():
                producer.cancel()
                await asyncio.gather(producer, return_exceptions=True)

    async def _run_one(
        self,
        run_id: str,
        benchmark: BenchmarkConfig,
        task: Task,
        model_config: ModelConfig,
        writer: AsyncTraceWriter,
        emit,
    ) -> None:
        prompt = self.config.prompt_by_name(benchmark.prompt)
        provider = self.config.provider_by_name(model_config.provider)
        await emit(task_started(run_id, task_id=task.id, model_name=model_config.name))
        start = None
        try:
            async with self.global_sem, self._model_sem(model_config):
                start = time.perf_counter()
                response, conversation, tool_trace, invalid_tool_calls = await asyncio.wait_for(
                    self._run_with_retries(run_id, task, prompt, model_config, provider, emit),
                    timeout=self.config.runner.timeouts.task_timeout_seconds,
                )
            raw_response = response.content
            extracted = extract_answer(raw_response)
            called_tools = [trace.name for trace in tool_trace]
            selection_correct = None
            if isinstance(task, ToolCallingTask):
                selection_correct = tool_selection_correct(task.expected_tools, called_tools)
            result = EvaluationResult(
                run_id=run_id,
                task_id=task.id,
                task_type=task.task_type,
                benchmark_name=benchmark.name,
                category=task.category,
                model_name=model_config.name,
                model=model_config.model,
                prompt_name=prompt.name,
                expected_answer=task.answer,
                raw_response=raw_response,
                extracted_answer=extracted,
                correct=response_correct(task.answer, extracted, raw_response, task.answer_regex),
                latency_seconds=time.perf_counter() - start,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                total_tokens=response.total_tokens,
                cached_tokens=response.cached_tokens,
                reasoning_tokens=response.reasoning_tokens,
                cost_usd=response.cost_usd,
                conversation_trace=conversation,
                called_tools=called_tools,
                expected_tools=task.expected_tools if isinstance(task, ToolCallingTask) else [],
                tool_trace=tool_trace,
                tool_selection_correct=selection_correct,
                invalid_tool_calls=invalid_tool_calls,
                mock_mode=self.mock_mode,
            )
            await writer.write(result)
            await emit(task_finished(run_id, result))
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            result = EvaluationResult(
                run_id=run_id,
                task_id=task.id,
                task_type=task.task_type,
                benchmark_name=benchmark.name,
                category=task.category,
                model_name=model_config.name,
                model=model_config.model,
                prompt_name=prompt.name,
                expected_answer=task.answer,
                raw_response="",
                extracted_answer="",
                correct=False,
                latency_seconds=time.perf_counter() - start if start is not None else 0.0,
                error=str(exc),
                mock_mode=self.mock_mode,
            )
            await writer.write(result)
            await emit(task_failed(run_id, task_id=task.id, model_name=model_config.name, error=str(exc)))
            await emit(task_finished(run_id, result))

    async def _run_with_retries(self, run_id, task, prompt, model_config, provider_config, emit):
        retries = self.config.runner.retries
        backoff = retries.initial_backoff_seconds
        last_exc: Exception | None = None
        for attempt in range(1, retries.max_attempts + 1):
            try:
                await emit(model_call_started(run_id, task_id=task.id, model_name=model_config.name, attempt=attempt))
                response, conversation, tool_trace, invalid = await self._run_task_flow(
                    run_id,
                    task,
                    prompt,
                    model_config,
                    provider_config,
                    emit,
                )
                await emit(model_call_finished(run_id, task_id=task.id, model_name=model_config.name, attempt=attempt))
                return response, conversation, tool_trace, invalid
            except Exception as exc:
                last_exc = exc
                if attempt >= retries.max_attempts:
                    break
                await asyncio.sleep(backoff)
                backoff = min(retries.max_backoff_seconds, backoff * 2)
        raise RuntimeError(f"Model call failed after {retries.max_attempts} attempts: {last_exc}") from last_exc

    async def _run_task_flow(self, run_id, task, prompt, model_config, provider_config, emit) -> FlowResult:
        handler = self._flow_handlers[task.task_type]
        return await handler(run_id, task, prompt, model_config, provider_config, emit)

    async def _run_single_turn_flow(self, _run_id, task, prompt, model_config, provider_config, _emit) -> FlowResult:
        if not isinstance(task, SingleTurnTask):
            raise TypeError(f"Expected SingleTurnTask for single_turn flow, got {type(task).__name__}")
        response, conversation = await run_single_turn(
            task,
            prompt,
            model_config,
            provider_config,
            self.client,
            self.config.runner.timeouts.request_timeout_seconds,
        )
        return response, conversation, [], []

    async def _run_multi_turn_flow(self, _run_id, task, prompt, model_config, provider_config, _emit) -> FlowResult:
        if not isinstance(task, MultiTurnTask):
            raise TypeError(f"Expected MultiTurnTask for multi_turn flow, got {type(task).__name__}")
        response, conversation = await run_multi_turn(
            task,
            prompt,
            model_config,
            provider_config,
            self.client,
            self.config.runner.timeouts.request_timeout_seconds,
        )
        return response, conversation, [], []

    async def _run_tool_calling_flow(self, run_id, task, prompt, model_config, provider_config, emit) -> FlowResult:
        if not isinstance(task, ToolCallingTask):
            raise TypeError(f"Expected ToolCallingTask for tool_calling flow, got {type(task).__name__}")
        return await run_tool_calling(
            task,
            prompt,
            model_config,
            provider_config,
            self.client,
            self.config.runner.timeouts.request_timeout_seconds,
            self.config.tools_enabled,
            self.config.runner.tool_calling.max_tool_steps,
            run_id,
            emit,
        )


async def run_evaluation(
    *,
    output_path: str | Path | None = None,
    task_type: str | None = None,
    include: set[str] | list[str] | None = None,
    exclude: set[str] | list[str] | None = None,
    mock_mode: bool = False,
    config: AppConfig | None = None,
    run_id: str | None = None,
) -> AsyncIterator[EvalEvent]:
    config = config or load_config()
    run_id = run_id or new_run_id()
    output_path = output_path or Path("results") / f"{run_id}.jsonl"
    runner = EvaluationRunner(config, mock_mode=mock_mode)
    async for event in runner.run(
        run_id=run_id,
        output_path=output_path,
        task_type=task_type,
        include=set(include) if include else None,
        exclude=set(exclude) if exclude else None,
    ):
        yield event


def task_matches_filter(task: Task, *, include: set[str] | None, exclude: set[str] | None) -> bool:
    labels = {task.id, task.category}
    if include and labels.isdisjoint(include):
        return False
    return not (exclude and not labels.isdisjoint(exclude))
