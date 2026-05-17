from __future__ import annotations

import json
from typing import Any, Awaitable, Callable

from agent_eval.events import tool_call_finished, tool_call_started
from agent_eval.llm import LiteLLMClient, ModelResponse
from agent_eval.schemas import ModelConfig, PromptConfig, ProviderConfig, ToolCallingTask, ToolTrace
from agent_eval.tools import execute_tool, openai_tool_schemas

Emit = Callable[[Any], Awaitable[None]]


async def run_tool_calling(
    task: ToolCallingTask,
    prompt: PromptConfig,
    model_config: ModelConfig,
    provider_config: ProviderConfig,
    client: LiteLLMClient,
    timeout_seconds: float,
    enabled_tools: list[str],
    max_tool_steps: int,
    run_id: str,
    emit: Emit,
) -> tuple[ModelResponse, list[dict[str, Any]], list[ToolTrace], list[dict[str, Any]]]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": prompt.system},
        {"role": "user", "content": prompt.user_template.format(question=task.question)},
    ]
    tools = openai_tool_schemas(enabled_tools)
    tool_trace: list[ToolTrace] = []
    invalid_tool_calls: list[dict[str, Any]] = []
    response = ModelResponse(content="")

    for _step in range(max_tool_steps + 1):
        step_response = await client.complete(
            model_config,
            messages,
            timeout_seconds=timeout_seconds,
            tools=tools,
            provider_config=provider_config,
        )
        response.content = step_response.content
        response.raw = step_response.raw
        response.tool_calls = step_response.tool_calls
        response.reasoning_content = step_response.reasoning_content
        response.add_usage(step_response)
        assistant_message: dict[str, Any] = {"role": "assistant", "content": response.content}
        if response.tool_calls:
            assistant_message["tool_calls"] = response.tool_calls
        if response.reasoning_content:
            assistant_message["reasoning_content"] = response.reasoning_content
        messages.append(assistant_message)
        if not response.tool_calls:
            return response, messages, tool_trace, invalid_tool_calls

        for tool_call in response.tool_calls:
            fn = tool_call.get("function", {})
            name = fn.get("name", "")
            args_raw = fn.get("arguments") or "{}"
            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else dict(args_raw)
            except Exception as exc:
                invalid = {"name": name, "arguments": args_raw, "error": str(exc)}
                invalid_tool_calls.append(invalid)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", "invalid_tool_call"),
                        "name": name,
                        "content": f"Invalid tool arguments: {exc}",
                    }
                )
                continue

            await emit(tool_call_started(run_id, task_id=task.id, tool_name=name, args=args))
            trace = await execute_tool(name, args)
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

    return response, messages, tool_trace, invalid_tool_calls
