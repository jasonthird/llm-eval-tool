from __future__ import annotations

import json
from typing import Any, Awaitable, Callable

from llm_eval.events import tool_call_finished, tool_call_started
from llm_eval.llm import LLMClient, ModelResponse
from llm_eval.schemas import ModelConfig, PromptConfig, ProviderConfig, ToolCallingTask, ToolTrace
from llm_eval.tools import DEFAULT_TOOL_REGISTRY, ToolRegistry

Emit = Callable[[Any], Awaitable[None]]
ToolCallingResult = tuple[ModelResponse, list[dict[str, Any]], list[ToolTrace], list[dict[str, Any]]]


async def run_tool_calling(
    task: ToolCallingTask,
    prompt: PromptConfig,
    model_config: ModelConfig,
    provider_config: ProviderConfig,
    client: LLMClient,
    timeout_seconds: float,
    enabled_tools: list[str],
    max_tool_steps: int,
    run_id: str,
    emit: Emit,
    tool_registry: ToolRegistry = DEFAULT_TOOL_REGISTRY,
) -> tuple[ModelResponse, list[dict[str, Any]], list[ToolTrace], list[dict[str, Any]]]:
    messages = _initial_messages(task, prompt)
    tools = tool_registry.schemas(enabled_tools)
    tool_trace: list[ToolTrace] = []
    invalid_tool_calls: list[dict[str, Any]] = []
    response = ModelResponse(content="")

    for _step in range(max_tool_steps + 1):
        step_response = await _request_tool_step(
            client,
            model_config,
            provider_config,
            messages,
            tools,
            timeout_seconds,
        )
        _merge_step_response(response, step_response)
        messages.append(_assistant_message(response))
        tool_calls = _extract_tool_calls(response)
        if not tool_calls:
            return _final_result(response, messages, tool_trace, invalid_tool_calls)

        await _handle_tool_calls(tool_calls, task, messages, tool_trace, invalid_tool_calls, run_id, emit, tool_registry)

    return _final_result(response, messages, tool_trace, invalid_tool_calls)


def _initial_messages(task: ToolCallingTask, prompt: PromptConfig) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": prompt.system},
        {"role": "user", "content": prompt.user_template.format(question=task.question)},
    ]


async def _request_tool_step(
    client: LLMClient,
    model_config: ModelConfig,
    provider_config: ProviderConfig,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    timeout_seconds: float,
) -> ModelResponse:
    return await client.complete(
        model_config,
        messages,
        timeout_seconds=timeout_seconds,
        tools=tools,
        provider_config=provider_config,
    )


def _merge_step_response(response: ModelResponse, step_response: ModelResponse) -> None:
    response.content = step_response.content
    response.raw = step_response.raw
    response.tool_calls = step_response.tool_calls
    response.reasoning_content = step_response.reasoning_content
    response.add_usage(step_response)


def _assistant_message(response: ModelResponse) -> dict[str, Any]:
    message: dict[str, Any] = {"role": "assistant", "content": response.content}
    if response.tool_calls:
        message["tool_calls"] = response.tool_calls
    if response.reasoning_content:
        message["reasoning_content"] = response.reasoning_content
    return message


def _extract_tool_calls(response: ModelResponse) -> list[dict[str, Any]]:
    return response.tool_calls


async def _handle_tool_calls(
    tool_calls: list[dict[str, Any]],
    task: ToolCallingTask,
    messages: list[dict[str, Any]],
    tool_trace: list[ToolTrace],
    invalid_tool_calls: list[dict[str, Any]],
    run_id: str,
    emit: Emit,
    tool_registry: ToolRegistry,
) -> None:
    for tool_call in tool_calls:
        name, args_raw = _tool_call_function(tool_call)
        try:
            args = _parse_tool_args(args_raw)
        except Exception as exc:
            _append_invalid_tool_call(tool_call, name, args_raw, exc, messages, invalid_tool_calls)
            continue

        await _execute_and_append_tool_call(tool_call, name, args, task, messages, tool_trace, run_id, emit, tool_registry)


def _tool_call_function(tool_call: dict[str, Any]) -> tuple[str, Any]:
    fn = tool_call.get("function", {})
    return fn.get("name", ""), fn.get("arguments") or "{}"


def _parse_tool_args(args_raw: Any) -> dict[str, Any]:
    return json.loads(args_raw) if isinstance(args_raw, str) else dict(args_raw)


def _append_invalid_tool_call(
    tool_call: dict[str, Any],
    name: str,
    args_raw: Any,
    exc: Exception,
    messages: list[dict[str, Any]],
    invalid_tool_calls: list[dict[str, Any]],
) -> None:
    invalid_tool_calls.append({"name": name, "arguments": args_raw, "error": str(exc)})
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.get("id", "invalid_tool_call"),
            "name": name,
            "content": f"Invalid tool arguments: {exc}",
        }
    )


async def _execute_and_append_tool_call(
    tool_call: dict[str, Any],
    name: str,
    args: dict[str, Any],
    task: ToolCallingTask,
    messages: list[dict[str, Any]],
    tool_trace: list[ToolTrace],
    run_id: str,
    emit: Emit,
    tool_registry: ToolRegistry,
) -> None:
    await emit(tool_call_started(run_id, task_id=task.id, tool_name=name, args=args))
    trace = await tool_registry.execute(name, args)
    tool_trace.append(trace)
    await emit(tool_call_finished(run_id, task_id=task.id, tool_name=name, error=trace.error))
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.get("id", name),
            "name": name,
            "content": str(trace.output if trace.error is None else trace.error),
        }
    )


def _final_result(
    response: ModelResponse,
    messages: list[dict[str, Any]],
    tool_trace: list[ToolTrace],
    invalid_tool_calls: list[dict[str, Any]],
) -> ToolCallingResult:
    return response, messages, tool_trace, invalid_tool_calls
