import pytest

from llm_eval import tools
from llm_eval.tools import ToolDefinition, ToolRegistry, execute_tool, openai_tool_schemas, tool_schema


@pytest.mark.asyncio
async def test_execute_tool_success():
    trace = await execute_tool("calculator_multiply", {"a": 123, "b": 456})
    assert trace.output == 56088
    assert trace.error is None


@pytest.mark.asyncio
async def test_execute_tool_unknown():
    trace = await execute_tool("missing", {})
    assert trace.error


@pytest.mark.asyncio
async def test_calculator_add_and_power():
    add = await execute_tool("calculator_add", {"a": 2.0, "b": 3.0})
    fractional = await execute_tool("calculator_add", {"a": 2.25, "b": 0.5})
    power = await execute_tool("calculator_power", {"base": 2, "exponent": 8})
    assert add.output == 5
    assert fractional.output == 2.75
    assert power.output == 256


@pytest.mark.asyncio
async def test_python_exec_success_and_failure():
    trace = await execute_tool("python_exec", {"code": "print(6 * 7)"})
    assert trace.output == "42"
    assert trace.error is None

    failure = await execute_tool("python_exec", {"code": "raise ValueError('bad math')"})
    assert failure.output is None
    assert "bad math" in failure.error


@pytest.mark.asyncio
async def test_python_exec_timeout(monkeypatch):
    monkeypatch.setattr(tools, "PYTHON_TIMEOUT_SECONDS", 0.001)
    trace = await execute_tool("python_exec", {"code": "import time; time.sleep(1)"})
    assert "timed out" in trace.error


def test_tool_schema_unknown_raises():
    with pytest.raises(KeyError):
        tool_schema("missing")


def test_openai_tool_schema_shape():
    schemas = openai_tool_schemas(["calculator_add", "missing", "python_exec"])
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "calculator_add"
    assert schemas[1]["function"]["parameters"]["properties"]["code"]["type"] == "string"


@pytest.mark.asyncio
async def test_tool_registry_executes_custom_definition():
    def echo(value: str) -> str:
        return value

    registry = ToolRegistry([ToolDefinition(name="echo", function=echo, description="Echo a string.")])

    assert registry.schemas(["echo", "missing"])[0]["function"]["name"] == "echo"
    trace = await registry.execute("echo", {"value": "ok"})

    assert trace.output == "ok"
    assert trace.error is None


@pytest.mark.asyncio
async def test_tool_registry_reports_argument_binding_errors():
    trace = await execute_tool("calculator_add", {"a": 1, "b": 2, "extra": 3})

    assert trace.output is None
    assert "unexpected keyword argument" in trace.error
