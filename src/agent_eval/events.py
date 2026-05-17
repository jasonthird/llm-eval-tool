from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent_eval.schemas import EvaluationResult


@dataclass(slots=True)
class EvalEvent:
    type: str
    run_id: str
    payload: dict[str, Any] = field(default_factory=dict)


def run_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("RunStarted", run_id, payload)


def run_finished(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("RunFinished", run_id, payload)


def task_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("TaskStarted", run_id, payload)


def task_finished(run_id: str, result: EvaluationResult) -> EvalEvent:
    return EvalEvent("TaskFinished", run_id, {"result": result})


def task_failed(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("TaskFailed", run_id, payload)


def model_call_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("ModelCallStarted", run_id, payload)


def model_call_finished(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("ModelCallFinished", run_id, payload)


def tool_call_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("ToolCallStarted", run_id, payload)


def tool_call_finished(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent("ToolCallFinished", run_id, payload)

