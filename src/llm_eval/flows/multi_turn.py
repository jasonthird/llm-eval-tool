from __future__ import annotations

from typing import Any

from llm_eval.llm import LLMClient, ModelResponse
from llm_eval.schemas import ModelConfig, MultiTurnTask, PromptConfig, ProviderConfig


async def run_multi_turn(
    task: MultiTurnTask,
    prompt: PromptConfig,
    model_config: ModelConfig,
    provider_config: ProviderConfig,
    client: LLMClient,
    timeout_seconds: float,
) -> tuple[ModelResponse, list[dict[str, Any]]]:
    messages: list[dict[str, Any]] = [{"role": "system", "content": prompt.system}]
    response = ModelResponse(content="")
    for turn in task.turns:
        messages.append(turn.model_dump(exclude_none=True))
        turn_response = await client.complete(
            model_config,
            messages,
            timeout_seconds=timeout_seconds,
            provider_config=provider_config,
        )
        response.content = turn_response.content
        response.raw = turn_response.raw
        response.tool_calls = turn_response.tool_calls
        response.add_usage(turn_response)
        messages.append({"role": "assistant", "content": response.content})
    return response, messages
