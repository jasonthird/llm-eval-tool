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
    role: str = Field(min_length=1)
    content: str | None = None
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class BaseTask(BaseModel):
    id: str = Field(min_length=1)
    task_type: TaskType
    answer: str = Field(min_length=1)
    answer_regex: str | None = None
    category: str = Field(default="default", min_length=1)


class SingleTurnTask(BaseTask):
    task_type: Literal["single_turn"]
    question: str = Field(min_length=1)


class MultiTurnTask(BaseTask):
    task_type: Literal["multi_turn"]
    turns: list[ChatMessage] = Field(min_length=1)


class ToolCallingTask(BaseTask):
    task_type: Literal["tool_calling"]
    question: str = Field(min_length=1)
    expected_tools: list[str] = Field(default_factory=list)


Task = SingleTurnTask | MultiTurnTask | ToolCallingTask


class ModelConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str = Field(min_length=1)
    model: str = Field(min_length=1)
    provider: str = Field(default="openai", min_length=1)
    temperature: float = 0.0
    max_tokens: int = Field(default=1024, gt=0)
    concurrency_limit: int | None = Field(default=None, gt=0)
    extra: dict[str, Any] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    name: str = Field(min_length=1)
    api_key_env: str | None = None
    api_base: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class PromptConfig(BaseModel):
    name: str = Field(min_length=1)
    system: str = Field(min_length=1)
    user_template: str = Field(default="{question}", min_length=1)


class BenchmarkConfig(BaseModel):
    name: str = Field(min_length=1)
    task_type: TaskType
    path: str = Field(min_length=1)
    prompt: str = Field(default="default", min_length=1)


class ConcurrencyConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    global_limit: int = Field(default=8, gt=0)
    per_model_limit: int = Field(default=2, gt=0)


class RetryConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    max_attempts: int = Field(default=3, gt=0)
    initial_backoff_seconds: float = Field(default=1.0, ge=0)
    max_backoff_seconds: float = Field(default=10.0, ge=0)


class TimeoutConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    request_timeout_seconds: float = Field(default=120, gt=0)
    task_timeout_seconds: float = Field(default=300, gt=0)


class ToolCallingConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    max_tool_steps: int = Field(default=4, gt=0)


class RunnerConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

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
    name: str = Field(min_length=1)
    args: dict[str, Any]
    output: Any = None
    error: str | None = None
    latency_seconds: float = Field(default=0.0, ge=0)


class EvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=utc_now)
    task_id: str = Field(min_length=1)
    task_type: TaskType
    benchmark_name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model: str = Field(min_length=1)
    prompt_name: str = Field(min_length=1)
    expected_answer: str = Field(min_length=1)
    raw_response: str
    extracted_answer: str
    correct: bool
    latency_seconds: float = Field(ge=0)
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    cached_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0)
    error: str | None = None
    conversation_trace: list[dict[str, Any]] = Field(default_factory=list)
    called_tools: list[str] = Field(default_factory=list)
    expected_tools: list[str] = Field(default_factory=list)
    tool_trace: list[ToolTrace] = Field(default_factory=list)
    tool_selection_correct: bool | None = None
    invalid_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    mock_mode: bool = False
