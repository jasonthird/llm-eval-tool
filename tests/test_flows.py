from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from agent_eval.flows.multi_turn import run_multi_turn
from agent_eval.flows.tool_calling import run_tool_calling
from agent_eval.llm import ModelResponse
from agent_eval.schemas import ChatMessage, ModelConfig, MultiTurnTask, PromptConfig, ProviderConfig, ToolCallingTask


@dataclass
class FakeClient:
    responses: list[ModelResponse]

    async def complete(self, *_: Any, **__: Any) -> ModelResponse:
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_multi_turn_flow_builds_conversation():
    task = MultiTurnTask(
        id="mt",
        task_type="multi_turn",
        turns=[ChatMessage(role="user", content="remember 2"), ChatMessage(role="user", content="double it")],
        answer="4",
    )
    response, messages = await run_multi_turn(
        task,
        PromptConfig(name="default", system="system"),
        ModelConfig(name="mock", model="mock/model"),
        ProviderConfig(name="mock"),
        FakeClient(
            [
                ModelResponse("ok", prompt_tokens=2, completion_tokens=1, total_tokens=3, cached_tokens=1),
                ModelResponse("FINAL_ANSWER: 4", prompt_tokens=4, completion_tokens=2, total_tokens=6, cost_usd=0.02),
            ]
        ),
        timeout_seconds=1,
    )
    assert response.content == "FINAL_ANSWER: 4"
    assert response.prompt_tokens == 6
    assert response.total_tokens == 9
    assert response.cached_tokens == 1
    assert response.cost_usd == 0.02
    assert [message["role"] for message in messages] == ["system", "user", "assistant", "user", "assistant"]


@pytest.mark.asyncio
async def test_tool_calling_invalid_arguments_then_final_answer():
    task = ToolCallingTask(
        id="tool",
        task_type="tool_calling",
        question="calculate",
        answer="42",
        expected_tools=["python_exec"],
    )
    events = []

    async def emit(event):
        events.append(event)

    response, messages, tool_trace, invalid = await run_tool_calling(
        task,
        PromptConfig(name="default", system="system"),
        ModelConfig(name="mock", model="mock/model"),
        ProviderConfig(name="mock"),
        FakeClient(
            [
                ModelResponse(
                    "",
                    reasoning_content="reasoning to replay",
                    tool_calls=[
                        {
                            "id": "bad",
                            "type": "function",
                            "function": {"name": "python_exec", "arguments": "{"},
                        }
                    ],
                ),
                ModelResponse("FINAL_ANSWER: 42", total_tokens=5, reasoning_tokens=2),
            ]
        ),
        timeout_seconds=1,
        enabled_tools=["python_exec"],
        max_tool_steps=2,
        run_id="run",
        emit=emit,
    )
    assert response.content == "FINAL_ANSWER: 42"
    assert response.total_tokens == 5
    assert response.reasoning_tokens == 2
    assert invalid[0]["name"] == "python_exec"
    assert tool_trace == []
    assert messages[2]["reasoning_content"] == "reasoning to replay"
    assert messages[-2]["content"].startswith("Invalid tool arguments")


@pytest.mark.asyncio
async def test_tool_calling_returns_after_step_limit():
    task = ToolCallingTask(id="tool", task_type="tool_calling", question="calculate", answer="42")
    events = []

    async def emit(event):
        events.append(event)

    response, _messages, tool_trace, invalid = await run_tool_calling(
        task,
        PromptConfig(name="default", system="system"),
        ModelConfig(name="mock", model="mock/model"),
        ProviderConfig(name="mock"),
        FakeClient(
            [
                ModelResponse(
                    "",
                    tool_calls=[
                        {
                            "id": "call",
                            "type": "function",
                            "function": {"name": "python_exec", "arguments": "{\"code\": \"print(42)\"}"},
                        }
                    ],
                )
            ]
        ),
        timeout_seconds=1,
        enabled_tools=["python_exec"],
        max_tool_steps=0,
        run_id="run",
        emit=emit,
    )
    assert response.tool_calls
    assert tool_trace[0].output == "42"
    assert invalid == []
