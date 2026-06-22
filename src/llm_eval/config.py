from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import TypeAdapter

from llm_eval.schemas import (
    AppConfig,
    BenchmarkConfig,
    ModelConfig,
    PromptConfig,
    ProviderConfig,
    RunnerConfig,
    Task,
)
from llm_eval.tools import DEFAULT_TOOL_REGISTRY, ToolRegistry

TASK_ADAPTER = TypeAdapter(Task)


class ConfigValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))


class ConfigPathResolver:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root)

    def resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.root / candidate

    def default_config_path(self, name: str) -> Path:
        return self.resolve(Path("configs") / name)


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(
    models_path: str | Path | None = None,
    prompts_path: str | Path | None = None,
    benchmarks_path: str | Path | None = None,
    tools_path: str | Path | None = None,
    runner_path: str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AppConfig:
    load_dotenv()
    resolver = ConfigPathResolver(root)
    models_path = resolver.default_config_path("models.yaml") if models_path is None else resolver.resolve(models_path)
    prompts_path = resolver.default_config_path("prompts.yaml") if prompts_path is None else resolver.resolve(prompts_path)
    benchmarks_path = resolver.default_config_path("benchmarks.yaml") if benchmarks_path is None else resolver.resolve(benchmarks_path)
    tools_path = resolver.default_config_path("tools.yaml") if tools_path is None else resolver.resolve(tools_path)
    runner_path = resolver.default_config_path("runner.yaml") if runner_path is None else resolver.resolve(runner_path)
    model_data = load_yaml(models_path)
    providers = [ProviderConfig.model_validate(item) for item in model_data.get("providers", [])]
    models = [ModelConfig.model_validate(item) for item in model_data.get("models", [])]
    prompts = [PromptConfig.model_validate(item) for item in load_yaml(prompts_path).get("prompts", [])]
    benchmarks = [
        BenchmarkConfig.model_validate(item) for item in load_yaml(benchmarks_path).get("benchmarks", [])
    ]
    for benchmark in benchmarks:
        benchmark.path = str(resolver.resolve(benchmark.path))
    tools_enabled = list(load_yaml(tools_path).get("tools", {}).get("enabled", []))
    runner = RunnerConfig.model_validate(load_yaml(runner_path).get("runner", {}))
    return AppConfig(
        models=models,
        providers=providers,
        prompts=prompts,
        benchmarks=benchmarks,
        tools_enabled=tools_enabled,
        runner=runner,
    )


def load_tasks(path: str | Path) -> list[Task]:
    tasks: list[Task] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                tasks.append(TASK_ADAPTER.validate_python(json.loads(line)))
            except Exception as exc:
                raise ValueError(f"Invalid task JSONL at {path}:{line_no}: {exc}") from exc
    return tasks


def validate_config(config: AppConfig, *, tool_registry: ToolRegistry = DEFAULT_TOOL_REGISTRY) -> None:
    errors: list[str] = []
    _validate_unique("provider", [provider.name for provider in config.providers], errors)
    _validate_unique("model", [model.name for model in config.models], errors)
    _validate_unique("prompt", [prompt.name for prompt in config.prompts], errors)
    _validate_unique("benchmark", [benchmark.name for benchmark in config.benchmarks], errors)
    _validate_unique("enabled tool", config.tools_enabled, errors)

    provider_names = {provider.name for provider in config.providers}
    for model in config.models:
        if model.provider not in provider_names:
            errors.append(f"Model '{model.name}' references unknown provider '{model.provider}'")

    prompt_names = {prompt.name for prompt in config.prompts}
    for benchmark in config.benchmarks:
        if benchmark.prompt not in prompt_names:
            errors.append(f"Benchmark '{benchmark.name}' references unknown prompt '{benchmark.prompt}'")
        path = Path(benchmark.path)
        if not path.exists():
            errors.append(f"Benchmark '{benchmark.name}' file does not exist: {path}")
            continue
        try:
            tasks = load_tasks(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        task_ids: set[str] = set()
        enabled_tools = set(config.tools_enabled)
        for task in tasks:
            if task.id in task_ids:
                errors.append(f"Benchmark '{benchmark.name}' contains duplicate task id '{task.id}'")
            task_ids.add(task.id)
            if task.task_type != benchmark.task_type:
                errors.append(
                    f"Benchmark '{benchmark.name}' has task '{task.id}' with task_type '{task.task_type}', "
                    f"expected '{benchmark.task_type}'"
                )
            if hasattr(task, "expected_tools"):
                for tool_name in task.expected_tools:
                    if tool_name not in enabled_tools:
                        errors.append(
                            f"Benchmark '{benchmark.name}' task '{task.id}' expects disabled tool '{tool_name}'"
                        )

    for tool_name in config.tools_enabled:
        if tool_name not in tool_registry:
            errors.append(f"Configured tool '{tool_name}' is not available")

    if errors:
        raise ConfigValidationError(errors)


def _validate_unique(label: str, names: list[str], errors: list[str]) -> None:
    seen: set[str] = set()
    duplicates = sorted({name for name in names if name in seen or seen.add(name)})
    for name in duplicates:
        errors.append(f"Duplicate {label} name '{name}'")
