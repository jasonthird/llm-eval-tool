from __future__ import annotations

from typing import Any

from llm_eval.llm import LLMClient, ModelResponse
from llm_eval.schemas import ModelConfig, PromptConfig, ProviderConfig, SingleTurnTask


def build_messages(task: SingleTurnTask, prompt: PromptConfig) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": prompt.system},
        {"role": "user", "content": prompt.user_template.format(question=task.question)},
    ]


async def run_single_turn(
    task: SingleTurnTask,
    prompt: PromptConfig,
    model_config: ModelConfig,
    provider_config: ProviderConfig,
    client: LLMClient,
    timeout_seconds: float,
) -> tuple[ModelResponse, list[dict[str, Any]]]:
    messages = build_messages(task, prompt)
    response = await client.complete(
        model_config,
        messages,
        timeout_seconds=timeout_seconds,
        provider_config=provider_config,
    )
    return response, [*messages, {"role": "assistant", "content": response.content}]
