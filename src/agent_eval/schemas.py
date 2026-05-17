from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

TaskType = Literal["single_turn", "multi_turn", "tool_calling"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_run_id() -> str:
    return f"run_{utc_now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"


class ChatMessage(BaseModel):
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class BaseTask(BaseModel):
    id: str
    task_type: TaskType
    answer: str
    answer_regex: str | None = None
    category: str = "default"


class SingleTurnTask(BaseTask):
    task_type: Literal["single_turn"]
    question: str


class MultiTurnTask(BaseTask):
    task_type: Literal["multi_turn"]
    turns: list[ChatMessage]


class ToolCallingTask(BaseTask):
    task_type: Literal["tool_calling"]
    question: str
    expected_tools: list[str] = Field(default_factory=list)


Task = SingleTurnTask | MultiTurnTask | ToolCallingTask


class ModelConfig(BaseModel):
    name: str
    model: str
    provider: str = "openai"
    temperature: float = 0.0
    max_tokens: int = 1024
    concurrency_limit: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    name: str
    api_key_env: str | None = None
    api_base: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class PromptConfig(BaseModel):
    name: str
    system: str
    user_template: str = "{question}"


class BenchmarkConfig(BaseModel):
    name: str
    task_type: TaskType
    path: str
    prompt: str = "default"


class ConcurrencyConfig(BaseModel):
    global_limit: int = 8
    per_model_limit: int = 2


class RetryConfig(BaseModel):
    max_attempts: int = 3
    initial_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 10.0


class TimeoutConfig(BaseModel):
    request_timeout_seconds: float = 120
    task_timeout_seconds: float = 300


class ToolCallingConfig(BaseModel):
    max_tool_steps: int = 4


class RunnerConfig(BaseModel):
    concurrency: ConcurrencyConfig = Field(default_factory=ConcurrencyConfig)
    retries: RetryConfig = Field(default_factory=RetryConfig)
    timeouts: TimeoutConfig = Field(default_factory=TimeoutConfig)
    tool_calling: ToolCallingConfig = Field(default_factory=ToolCallingConfig)


class AppConfig(BaseModel):
    models: list[ModelConfig]
    providers: list[ProviderConfig] = Field(default_factory=list)
    prompts: list[PromptConfig]
    benchmarks: list[BenchmarkConfig]
    tools_enabled: list[str]
    runner: RunnerConfig

    def provider_by_name(self, name: str) -> ProviderConfig:
        for provider in self.providers:
            if provider.name == name:
                return provider
        return ProviderConfig(name=name)

    def prompt_by_name(self, name: str) -> PromptConfig:
        for prompt in self.prompts:
            if prompt.name == name:
                return prompt
        raise KeyError(f"Unknown prompt: {name}")


class ToolTrace(BaseModel):
    name: str
    args: dict[str, Any]
    output: Any = None
    error: str | None = None
    latency_seconds: float = 0.0


class EvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    task_id: str
    task_type: TaskType
    benchmark_name: str
    category: str
    model_name: str
    model: str
    prompt_name: str
    expected_answer: str
    raw_response: str
    extracted_answer: str
    correct: bool
    latency_seconds: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0
    error: str | None = None
    conversation_trace: list[dict[str, Any]] = Field(default_factory=list)
    called_tools: list[str] = Field(default_factory=list)
    expected_tools: list[str] = Field(default_factory=list)
    tool_trace: list[ToolTrace] = Field(default_factory=list)
    tool_selection_correct: bool | None = None
    invalid_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    mock_mode: bool = False
