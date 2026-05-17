from __future__ import annotations

import asyncio
import inspect
import sys
import tempfile
import time
from typing import Any, Callable

from agent_eval.schemas import ToolTrace

PYTHON_TIMEOUT_SECONDS = 5.0


def calculator_add(a: float, b: float) -> float:
    return a + b


def calculator_multiply(a: float, b: float) -> float:
    return a * b


def calculator_power(base: float, exponent: float) -> float:
    return base**exponent


async def python_exec(code: str) -> str:
    """Run short Python snippets for model-assisted calculation."""
    with tempfile.TemporaryDirectory(prefix="agent-eval-python-") as cwd:
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-I",
            "-c",
            code,
            cwd=cwd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=PYTHON_TIMEOUT_SECONDS)
        except TimeoutError:
            proc.kill()
            await proc.communicate()
            raise RuntimeError(f"Python execution timed out after {PYTHON_TIMEOUT_SECONDS:.1f}s")

    stdout_text = stdout.decode("utf-8", errors="replace").strip()
    stderr_text = stderr.decode("utf-8", errors="replace").strip()
    if proc.returncode:
        detail = stderr_text or stdout_text or f"exit status {proc.returncode}"
        raise RuntimeError(f"Python execution failed: {detail}")
    return stdout_text


TOOL_REGISTRY: dict[str, Callable[..., Any]] = {
    "calculator_add": calculator_add,
    "calculator_multiply": calculator_multiply,
    "calculator_power": calculator_power,
    "python_exec": python_exec,
}

TOOL_DESCRIPTIONS: dict[str, str] = {
    "calculator_add": "Add two numbers.",
    "calculator_multiply": "Multiply two numbers.",
    "calculator_power": "Raise a number to a power.",
    "python_exec": "Run a short Python snippet for calculation or problem solving. Print the final answer to stdout.",
}


def tool_schema(name: str) -> dict[str, Any]:
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {name}")
    fn = TOOL_REGISTRY[name]
    properties: dict[str, Any] = {}
    required: list[str] = []
    for param_name, param in inspect.signature(fn).parameters.items():
        param_type = "string" if param.annotation in (str, "str") else "number"
        properties[param_name] = {"type": param_type}
        required.append(param_name)
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": TOOL_DESCRIPTIONS[name],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


def openai_tool_schemas(enabled: list[str]) -> list[dict[str, Any]]:
    return [tool_schema(name) for name in enabled if name in TOOL_REGISTRY]


async def execute_tool(name: str, args: dict[str, Any]) -> ToolTrace:
    start = time.perf_counter()
    if name not in TOOL_REGISTRY:
        return ToolTrace(name=name, args=args, error=f"Unknown tool: {name}")
    try:
        output = TOOL_REGISTRY[name](**args)
        if inspect.isawaitable(output):
            output = await output
        if isinstance(output, float) and output.is_integer():
            output = int(output)
        return ToolTrace(
            name=name,
            args=args,
            output=output,
            latency_seconds=time.perf_counter() - start,
        )
    except Exception as exc:
        return ToolTrace(
            name=name,
            args=args,
            error=str(exc),
            latency_seconds=time.perf_counter() - start,
        )
