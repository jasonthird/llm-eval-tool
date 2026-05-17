import asyncio
from pathlib import Path

import pytest

from agent_eval.config import load_config, load_tasks
from agent_eval.schemas import AppConfig, BenchmarkConfig, ModelConfig, PromptConfig, RetryConfig, RunnerConfig
from agent_eval.runner import run_evaluation


@pytest.mark.asyncio
async def test_async_runner_writes_once_and_emits_finished(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import shutil

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "configs", tmp_path / "configs")
    shutil.copytree(root / "data", tmp_path / "data")

    output = tmp_path / "results" / "runner.jsonl"
    events = []
    async for event in run_evaluation(output_path=output, task_type="tool_calling", mock_mode=True, run_id="run_async"):
        events.append(event.type)
    lines = output.read_text(encoding="utf-8").strip().splitlines()
    assert events.count("RunStarted") == 1
    assert events.count("RunFinished") == 1
    assert events.count("TaskFinished") == len(lines)
    config = load_config()
    tool_tasks = sum(len(load_tasks(benchmark.path)) for benchmark in config.benchmarks if benchmark.task_type == "tool_calling")
    assert len(lines) == tool_tasks * len(config.models)


@pytest.mark.asyncio
async def test_runner_can_be_cancelled(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import shutil

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "configs", tmp_path / "configs")
    shutil.copytree(root / "data", tmp_path / "data")

    async def consume():
        async for _event in run_evaluation(output_path=tmp_path / "results" / "cancel.jsonl", mock_mode=True):
            await asyncio.sleep(0)

    task = asyncio.create_task(consume())
    await asyncio.sleep(0.001)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert task.cancelled() or task.done()


@pytest.mark.asyncio
async def test_runner_propagates_producer_errors(tmp_path):
    config = AppConfig(
        models=[ModelConfig(name="mock", model="mock/model")],
        prompts=[PromptConfig(name="default", system="system")],
        benchmarks=[BenchmarkConfig(name="missing", task_type="single_turn", path=str(tmp_path / "missing.jsonl"))],
        tools_enabled=[],
        runner=RunnerConfig(),
    )
    seen = []
    with pytest.raises(FileNotFoundError):
        async for event in run_evaluation(
            output_path=tmp_path / "results" / "missing.jsonl",
            mock_mode=True,
            config=config,
            run_id="run_missing",
        ):
            seen.append(event.type)
    assert seen == ["RunStarted"]


@pytest.mark.asyncio
async def test_runner_records_model_failures_after_retries(tmp_path):
    task_file = tmp_path / "tasks.jsonl"
    task_file.write_text(
        '{"id":"math","task_type":"single_turn","question":"What is 1 + 1?","answer":"2"}\n',
        encoding="utf-8",
    )
    config = AppConfig(
        models=[ModelConfig(name="broken", model="mock/broken")],
        prompts=[PromptConfig(name="default", system="system")],
        benchmarks=[BenchmarkConfig(name="sample", task_type="single_turn", path=str(task_file))],
        tools_enabled=[],
        runner=RunnerConfig(retries=RetryConfig(max_attempts=2, initial_backoff_seconds=0, max_backoff_seconds=0)),
    )
    output = tmp_path / "results" / "failed.jsonl"
    events = []

    class FailingClient:
        def __init__(self, mock_mode=False):
            self.mock_mode = mock_mode

        async def complete(self, *args, **kwargs):
            raise RuntimeError("provider down")

    import agent_eval.runner as runner_module

    original = runner_module.LiteLLMClient
    runner_module.LiteLLMClient = FailingClient
    try:
        async for event in run_evaluation(output_path=output, mock_mode=False, config=config, run_id="run_failed"):
            events.append(event)
    finally:
        runner_module.LiteLLMClient = original

    failed = [event for event in events if event.type == "TaskFailed"]
    finished = [event for event in events if event.type == "TaskFinished"]
    assert failed and "provider down" in failed[0].payload["error"]
    assert finished[0].payload["result"].error.startswith("Model call failed after 2 attempts")


@pytest.mark.asyncio
async def test_runner_include_exclude_filters_tasks(tmp_path):
    task_file = tmp_path / "tasks.jsonl"
    task_file.write_text(
        "\n".join(
            [
                '{"id":"keep_by_id","task_type":"single_turn","category":"alpha","question":"What is 1?","answer":"1"}',
                '{"id":"drop_by_exclude","task_type":"single_turn","category":"alpha","question":"What is 2?","answer":"2"}',
                '{"id":"not_included","task_type":"single_turn","category":"beta","question":"What is 3?","answer":"3"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config = AppConfig(
        models=[ModelConfig(name="mock", model="mock/model")],
        prompts=[PromptConfig(name="default", system="system")],
        benchmarks=[BenchmarkConfig(name="sample", task_type="single_turn", path=str(task_file))],
        tools_enabled=[],
        runner=RunnerConfig(),
    )
    output = tmp_path / "results" / "filtered.jsonl"
    results = []

    async for event in run_evaluation(
        output_path=output,
        mock_mode=True,
        config=config,
        run_id="run_filtered",
        include=["alpha"],
        exclude=["drop_by_exclude"],
    ):
        if event.type == "TaskFinished":
            results.append(event.payload["result"])

    assert [result.task_id for result in results] == ["keep_by_id"]


@pytest.mark.asyncio
async def test_runner_executes_multi_turn_mock(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import shutil

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "configs", tmp_path / "configs")
    shutil.copytree(root / "data", tmp_path / "data")

    output = tmp_path / "results" / "multi.jsonl"
    results = []
    async for event in run_evaluation(output_path=output, task_type="multi_turn", mock_mode=True, run_id="run_multi"):
        if event.type == "TaskFinished":
            results.append(event.payload["result"])
    config = load_config()
    multi_tasks = sum(len(load_tasks(benchmark.path)) for benchmark in config.benchmarks if benchmark.task_type == "multi_turn")
    assert len(results) == multi_tasks * len(config.models)
    assert all(result.conversation_trace for result in results)
