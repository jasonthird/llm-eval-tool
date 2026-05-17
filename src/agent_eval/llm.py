from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

from agent_eval.schemas import ModelConfig, ProviderConfig


@dataclass
class ModelResponse:
    content: str
    raw: Any = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    reasoning_content: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0

    def add_usage(self, other: "ModelResponse") -> None:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        self.cached_tokens += other.cached_tokens
        self.reasoning_tokens += other.reasoning_tokens
        self.cost_usd += other.cost_usd


class LiteLLMClient:
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode

    async def complete(
        self,
        model_config: ModelConfig,
        messages: list[dict[str, Any]],
        timeout_seconds: float,
        tools: list[dict[str, Any]] | None = None,
        provider_config: ProviderConfig | None = None,
    ) -> ModelResponse:
        if self.mock_mode:
            return await self._mock_complete(messages, tools)
        from litellm import acompletion

        kwargs: dict[str, Any] = {
            "model": model_config.model,
            "messages": messages,
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
            "timeout": timeout_seconds,
            **(provider_config.extra if provider_config else {}),
            **model_config.extra,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if provider_config and provider_config.api_base:
            kwargs["api_base"] = provider_config.api_base
        if provider_config and provider_config.api_key_env:
            api_key = os.getenv(provider_config.api_key_env)
            if api_key:
                kwargs["api_key"] = api_key
        response = await acompletion(**kwargs)
        message = response.choices[0].message
        content = message.content or ""
        tool_calls = [tc.model_dump() if hasattr(tc, "model_dump") else dict(tc) for tc in (message.tool_calls or [])]
        reasoning_content = _get_value(message, "reasoning_content")
        usage = _response_usage(response)
        return ModelResponse(
            content=content,
            raw=response,
            tool_calls=tool_calls,
            reasoning_content=str(reasoning_content) if reasoning_content else None,
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
            cached_tokens=usage["cached_tokens"],
            reasoning_tokens=usage["reasoning_tokens"],
            cost_usd=_response_cost(response),
        )

    async def _mock_complete(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None
    ) -> ModelResponse:
        await asyncio.sleep(0.01)
        if tools and not any(msg.get("role") == "tool" for msg in messages):
            question = " ".join(str(msg.get("content", "")) for msg in messages if msg.get("role") == "user")
            tool_name, args = _mock_tool_for_question(question, tools)
            return ModelResponse(
                content="",
                tool_calls=[
                    {
                        "id": "mock_tool_call_1",
                        "type": "function",
                        "function": {"name": tool_name, "arguments": json.dumps(args)},
                    }
                ],
            )
        if any(msg.get("role") == "tool" for msg in messages):
            tool_outputs = [str(msg.get("content", "")) for msg in messages if msg.get("role") == "tool"]
            return ModelResponse(content=f"FINAL_ANSWER: {tool_outputs[-1]}")
        prompt_text = " ".join(str(msg.get("content", "")) for msg in messages)
        return ModelResponse(content=f"FINAL_ANSWER: {_mock_answer(prompt_text)}")


def _get_value(data: Any, key: str, default: Any = None) -> Any:
    if isinstance(data, dict):
        return data.get(key, default)
    return getattr(data, key, default)


def _int_value(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _float_value(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _response_usage(response: Any) -> dict[str, int]:
    usage = _get_value(response, "usage", {}) or {}
    prompt_details = _get_value(usage, "prompt_tokens_details", {}) or {}
    completion_details = _get_value(usage, "completion_tokens_details", {}) or {}
    cached_tokens = _int_value(_get_value(prompt_details, "cached_tokens"))
    if cached_tokens == 0:
        cached_tokens = _int_value(_get_value(usage, "prompt_cache_hit_tokens"))
    return {
        "prompt_tokens": _int_value(_get_value(usage, "prompt_tokens")),
        "completion_tokens": _int_value(_get_value(usage, "completion_tokens")),
        "total_tokens": _int_value(_get_value(usage, "total_tokens")),
        "cached_tokens": cached_tokens,
        "reasoning_tokens": _int_value(_get_value(completion_details, "reasoning_tokens")),
    }


def _response_cost(response: Any) -> float:
    direct = _get_value(response, "response_cost")
    if direct is not None:
        return _float_value(direct)
    provider_cost = _get_value(response, "cost")
    if provider_cost is not None:
        return _float_value(provider_cost)
    hidden = _get_value(response, "_hidden_params", {}) or {}
    return _float_value(_get_value(hidden, "response_cost"))


def _mock_tool_for_question(question: str, tools: list[dict[str, Any]] | None = None) -> tuple[str, dict[str, Any]]:
    nums = [float(n) for n in re.findall(r"[-+]?\d+(?:\.\d+)?", question)]
    lower = question.lower()
    tool_names = {
        str(tool.get("function", {}).get("name", ""))
        for tool in tools or []
        if isinstance(tool.get("function"), dict)
    }
    if "python_exec" in tool_names:
        if len(nums) >= 2 and ("power" in lower or "raised" in lower):
            expression = f"{nums[0]!r} ** {nums[1]!r}"
        elif len(nums) >= 2 and ("*" in lower or "multiply" in lower or "product" in lower):
            expression = f"{nums[0]!r} * {nums[1]!r}"
        elif len(nums) >= 2:
            expression = f"{nums[0]!r} + {nums[1]!r}"
        elif nums:
            expression = f"{nums[0]!r}"
        else:
            expression = "'unknown'"
        return "python_exec", {"code": f"result = {expression}\nprint(int(result) if result == int(result) else result)"}
    if "power" in lower or "raised" in lower:
        return "calculator_power", {"base": nums[0], "exponent": nums[1]}
    if "*" in lower or "multiply" in lower or "product" in lower:
        return "calculator_multiply", {"a": nums[0], "b": nums[1]}
    return "calculator_add", {"a": nums[0], "b": nums[1]}


def _mock_answer(text: str) -> str:
    lower = text.lower()
    nums = [int(n) for n in re.findall(r"[-+]?\d+", text)]
    if "17 * 23" in text or "17*23" in text:
        return "391"
    if "144 / 12" in text or "144/12" in text:
        return "12"
    if "2^8" in text or "2 ^ 8" in text:
        return "256"
    power = re.search(r"(-?\d+)\s*(?:\^|\*\*)\s*(-?\d+)", text)
    if power:
        return str(int(power.group(1)) ** int(power.group(2)))
    if "multiply the number by 3" in lower and nums:
        return str(nums[0] * 3)
    if "cobalt" in lower:
        return "cobalt"
    if len(nums) >= 2 and "*" in text:
        return str(nums[-2] * nums[-1])
    if len(nums) >= 2 and "+" in text:
        return str(nums[-2] + nums[-1])
    if len(nums) >= 2 and "-" in text:
        return str(nums[-2] - nums[-1])
    return nums[-1] if nums else "unknown"
