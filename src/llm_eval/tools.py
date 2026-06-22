from __future__ import annotations

import asyncio
import inspect
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Callable

from llm_eval.schemas import ToolTrace

PYTHON_TIMEOUT_SECONDS = 5.0


def calculator_add(a: float, b: float) -> float:
    return a + b


def calculator_multiply(a: float, b: float) -> float:
    return a * b


def calculator_power(base: float, exponent: float) -> float:
    return base**exponent


async def python_exec(code: str) -> str:
    """Run short Python snippets for model-assisted calculation."""
    with tempfile.TemporaryDirectory(prefix="llm-eval-python-") as cwd:
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


DEFAULT_TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
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


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    function: Callable[..., Any]
    description: str


class ToolRegistry:
    def __init__(self, definitions: list[ToolDefinition] | None = None):
        definitions = definitions or [
            ToolDefinition(name=name, function=function, description=TOOL_DESCRIPTIONS[name])
            for name, function in DEFAULT_TOOL_FUNCTIONS.items()
        ]
        self._definitions = {definition.name: definition for definition in definitions}

    def __contains__(self, name: str) -> bool:
        return name in self._definitions

    def schema(self, name: str) -> dict[str, Any]:
        definition = self._definition(name)
        properties: dict[str, Any] = {}
        required: list[str] = []
        for param_name, param in inspect.signature(definition.function).parameters.items():
            param_type = "string" if param.annotation in (str, "str") else "number"
            properties[param_name] = {"type": param_type}
            required.append(param_name)
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": definition.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            },
        }

    def schemas(self, enabled: list[str]) -> list[dict[str, Any]]:
        return [self.schema(name) for name in enabled if name in self]

    async def execute(self, name: str, args: dict[str, Any]) -> ToolTrace:
        start = time.perf_counter()
        if name not in self:
            return ToolTrace(name=name, args=args, error=f"Unknown tool: {name}")
        try:
            definition = self._definition(name)
            bound_args = self._bind_args(definition, args)
            output = definition.function(**bound_args)
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

    def _definition(self, name: str) -> ToolDefinition:
        try:
            return self._definitions[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def _bind_args(self, definition: ToolDefinition, args: dict[str, Any]) -> dict[str, Any]:
        signature = inspect.signature(definition.function)
        bound = signature.bind(**args)
        return dict(bound.arguments)


DEFAULT_TOOL_REGISTRY = ToolRegistry()
TOOL_REGISTRY = DEFAULT_TOOL_FUNCTIONS


def tool_schema(name: str) -> dict[str, Any]:
    return DEFAULT_TOOL_REGISTRY.schema(name)


def openai_tool_schemas(enabled: list[str]) -> list[dict[str, Any]]:
    return DEFAULT_TOOL_REGISTRY.schemas(enabled)


async def execute_tool(name: str, args: dict[str, Any]) -> ToolTrace:
    return await DEFAULT_TOOL_REGISTRY.execute(name, args)
