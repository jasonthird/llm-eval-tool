import pytest

from agent_eval.events import task_failed
from agent_eval.schemas import AppConfig, ModelConfig, PromptConfig, RunnerConfig


def test_task_failed_event_and_missing_prompt():
    event = task_failed("run", task_id="task", error="failed")
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
