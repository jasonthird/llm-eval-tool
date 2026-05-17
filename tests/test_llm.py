from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent_eval.llm import LiteLLMClient, _float_value, _int_value, _mock_answer, _mock_tool_for_question
from agent_eval.schemas import ModelConfig, ProviderConfig
from agent_eval.tools import openai_tool_schemas


class DumpableToolCall:
    def model_dump(self):
        return {"id": "dumped", "type": "function", "function": {"name": "python_exec", "arguments": "{}"}}


@pytest.mark.asyncio
async def test_litellm_client_passes_config_and_tools(monkeypatch):
    captured = {}

    async def fake_acompletion(**kwargs):
        captured.update(kwargs)
        message = SimpleNamespace(
            content=None,
            tool_calls=[DumpableToolCall(), {"id": "dict"}],
            reasoning_content="private reasoning",
        )
        usage = {
            "prompt_tokens": 10,
            "completion_tokens": 3,
            "total_tokens": 13,
            "prompt_tokens_details": {"cached_tokens": 4},
            "completion_tokens_details": {"reasoning_tokens": 2},
        }
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message)],
            usage=usage,
            _hidden_params={"response_cost": 0.0123},
        )

    import litellm

    monkeypatch.setattr(litellm, "acompletion", fake_acompletion)
    monkeypatch.setenv("MODEL_KEY", "secret")
    client = LiteLLMClient()
    response = await client.complete(
        ModelConfig(
            name="model",
            model="openai/model",
            temperature=0.3,
            max_tokens=12,
            extra={"presence_penalty": 0.1},
        ),
        [{"role": "user", "content": "hi"}],
        timeout_seconds=9,
        tools=openai_tool_schemas(["python_exec"]),
        provider_config=ProviderConfig(
            name="local",
            api_base="http://localhost:8000/v1",
            api_key_env="MODEL_KEY",
            extra={"top_p": 0.9},
        ),
    )

    assert response.content == ""
    assert response.tool_calls == [
        {"id": "dumped", "type": "function", "function": {"name": "python_exec", "arguments": "{}"}},
        {"id": "dict"},
    ]
    assert response.reasoning_content == "private reasoning"
    assert captured["api_key"] == "secret"
    assert captured["api_base"] == "http://localhost:8000/v1"
    assert captured["tool_choice"] == "auto"
    assert captured["top_p"] == 0.9
    assert captured["presence_penalty"] == 0.1
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 3
    assert response.total_tokens == 13
    assert response.cached_tokens == 4
    assert response.reasoning_tokens == 2
    assert response.cost_usd == 0.0123


@pytest.mark.asyncio
async def test_litellm_client_omits_empty_optional_config(monkeypatch):
    captured = {}

    async def fake_acompletion(**kwargs):
        captured.update(kwargs)
        message = SimpleNamespace(content="done", tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], response_cost="0.5")

    import litellm

    monkeypatch.setattr(litellm, "acompletion", fake_acompletion)
    response = await LiteLLMClient().complete(
        ModelConfig(name="model", model="openai/model"),
        [{"role": "user", "content": "hi"}],
        timeout_seconds=9,
        provider_config=ProviderConfig(name="openai", api_key_env="MISSING_KEY"),
    )

    assert response.content == "done"
    assert "api_key" not in captured
    assert "tools" not in captured
    assert response.cost_usd == 0.5


def test_mock_tool_selection_paths():
    python_tools = openai_tool_schemas(["python_exec"])
    assert _mock_tool_for_question("8 raised to the power of 3", python_tools)[0] == "python_exec"
    assert _mock_tool_for_question("1 plus 2", python_tools)[1]["code"].startswith("result = 1.0 + 2.0")
    assert "result = 'unknown'" in _mock_tool_for_question("solve symbolically", python_tools)[1]["code"]
    assert _mock_tool_for_question("8 raised to the power of 3")[0] == "calculator_power"
    assert _mock_tool_for_question("8 * 3")[0] == "calculator_multiply"
    assert _mock_tool_for_question("8 plus 3")[0] == "calculator_add"


def test_mock_answer_paths():
    assert _mock_answer("9 multiply the number by 3") == "27"
    assert _mock_answer("remember cobalt") == "cobalt"
    assert _mock_answer("what is 6 * 7") == "42"
    assert _mock_answer("what is 15 + 27") == "42"
    assert _mock_answer("what is 987 - 654") == "333"
    assert _mock_answer("what is 3^5") == "243"
    assert _mock_answer("no numbers") == "unknown"


def test_usage_value_helpers_ignore_bad_values():
    assert _int_value("not-int") == 0
    assert _float_value("not-float") == 0.0


@pytest.mark.asyncio
async def test_litellm_client_reads_provider_cost_and_cache_hit_tokens(monkeypatch):
    async def fake_acompletion(**kwargs):
        message = SimpleNamespace(content="ok", tool_calls=None)
        usage = {
            "prompt_tokens": 10,
            "completion_tokens": 2,
            "total_tokens": 12,
            "prompt_cache_hit_tokens": 7,
        }
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage, cost="0.0042")

    import litellm

    monkeypatch.setattr(litellm, "acompletion", fake_acompletion)
    response = await LiteLLMClient().complete(
        ModelConfig(name="model", model="openai/model"),
        [{"role": "user", "content": "hi"}],
        timeout_seconds=9,
    )

    assert response.cached_tokens == 7
    assert response.cost_usd == 0.0042
