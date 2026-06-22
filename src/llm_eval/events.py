from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from llm_eval.schemas import EvaluationResult


class EventType(StrEnum):
    RUN_STARTED = "RunStarted"
    RUN_FINISHED = "RunFinished"
    TASK_STARTED = "TaskStarted"
    TASK_FINISHED = "TaskFinished"
    TASK_FAILED = "TaskFailed"
    MODEL_CALL_STARTED = "ModelCallStarted"
    MODEL_CALL_FINISHED = "ModelCallFinished"
    TOOL_CALL_STARTED = "ToolCallStarted"
    TOOL_CALL_FINISHED = "ToolCallFinished"


@dataclass(slots=True)
class EvalEvent:
    type: EventType | str
    run_id: str
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            try:
                self.type = EventType(self.type)
            except ValueError:
                pass


def run_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.RUN_STARTED, run_id, payload)


def run_finished(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.RUN_FINISHED, run_id, payload)


def task_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.TASK_STARTED, run_id, payload)


def task_finished(run_id: str, result: EvaluationResult) -> EvalEvent:
    return EvalEvent(EventType.TASK_FINISHED, run_id, {"result": result})


def task_failed(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.TASK_FAILED, run_id, payload)


def model_call_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.MODEL_CALL_STARTED, run_id, payload)


def model_call_finished(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.MODEL_CALL_FINISHED, run_id, payload)


def tool_call_started(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.TOOL_CALL_STARTED, run_id, payload)


def tool_call_finished(run_id: str, **payload: Any) -> EvalEvent:
    return EvalEvent(EventType.TOOL_CALL_FINISHED, run_id, payload)
