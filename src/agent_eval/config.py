from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import TypeAdapter

from agent_eval.schemas import (
    AppConfig,
    BenchmarkConfig,
    ModelConfig,
    PromptConfig,
    ProviderConfig,
    RunnerConfig,
    Task,
)

TASK_ADAPTER = TypeAdapter(Task)


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(
    models_path: str | Path = "configs/models.yaml",
    prompts_path: str | Path = "configs/prompts.yaml",
    benchmarks_path: str | Path = "configs/benchmarks.yaml",
    tools_path: str | Path = "configs/tools.yaml",
    runner_path: str | Path = "configs/runner.yaml",
) -> AppConfig:
    load_dotenv()
    model_data = load_yaml(models_path)
    providers = [ProviderConfig.model_validate(item) for item in model_data.get("providers", [])]
    models = [ModelConfig.model_validate(item) for item in model_data.get("models", [])]
    prompts = [PromptConfig.model_validate(item) for item in load_yaml(prompts_path).get("prompts", [])]
    benchmarks = [
        BenchmarkConfig.model_validate(item) for item in load_yaml(benchmarks_path).get("benchmarks", [])
    ]
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
