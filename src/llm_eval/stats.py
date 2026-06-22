from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_eval.schemas import EvaluationResult


@dataclass
class LiveStats:
    """Running totals for an in-progress evaluation run.

    Single home for the live accumulation the CLI shows in its progress line
    and final summary; feed it each result with :meth:`update`.
    """

    total: int = 0
    correct: int = 0
    errors: int = 0
    latency_sum: float = 0.0
    total_tokens: int = 0
    cached_tokens: int = 0
    cost_usd: float = 0.0
    latest: str = ""

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def average_latency(self) -> float:
        return self.latency_sum / self.total if self.total else 0.0

    def update(self, result: "EvaluationResult") -> None:
        self.total += 1
        self.correct += int(result.correct)
        self.errors += int(result.error is not None)
        self.latency_sum += result.latency_seconds
        self.total_tokens += result.total_tokens
        self.cached_tokens += result.cached_tokens
        self.cost_usd += result.cost_usd
        self.latest = result.task_id
