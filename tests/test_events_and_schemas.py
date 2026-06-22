import pytest
from pydantic import ValidationError

from llm_eval.events import EvalEvent, EventType, task_failed, task_started
from llm_eval.schemas import AppConfig, BenchmarkConfig, ModelConfig, PromptConfig, RunnerConfig, SingleTurnTask


def test_task_failed_event_and_missing_prompt():
    event = task_failed("run", task_id="task", error="failed")
    assert event.type is EventType.TASK_FAILED
    assert event.type == "TaskFailed"
    assert event.payload["error"] == "failed"

    config = AppConfig(
        models=[ModelConfig(name="model", model="mock/model")],
        prompts=[PromptConfig(name="default", system="system")],
        benchmarks=[],
        tools_enabled=[],
        runner=RunnerConfig(),
    )
    assert config.provider_by_name("openai").name == "openai"
    with pytest.raises(KeyError):
        config.prompt_by_name("missing")


def test_event_type_is_backward_compatible_with_strings():
    event = EvalEvent("TaskFinished", "run")
    assert event.type is EventType.TASK_FINISHED
    assert event.type == "TaskFinished"

    unknown = EvalEvent("PluginEvent", "run")
    assert unknown.type == "PluginEvent"

    started = task_started("run", task_id="task")
    assert started.type is EventType.TASK_STARTED


def test_schema_validation_rejects_empty_names_and_invalid_limits():
    with pytest.raises(ValidationError):
        ModelConfig(name="", model="mock/model")
    with pytest.raises(ValidationError):
        BenchmarkConfig(name="bench", task_type="single_turn", path="")
    with pytest.raises(ValidationError):
        SingleTurnTask(id="task", task_type="single_turn", question="", answer="42")
    with pytest.raises(ValidationError):
        RunnerConfig(concurrency={"global_limit": 0})
    with pytest.raises(ValidationError):
        RunnerConfig(retries={"max_attempts": 0})
    with pytest.raises(ValidationError):
        RunnerConfig(timeouts={"request_timeout_seconds": 0})
