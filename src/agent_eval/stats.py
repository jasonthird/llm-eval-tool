from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LiveStats:
    total: int = 0
    correct: int = 0
    errors: int = 0
    latency_sum: float = 0.0
    latest: str = ""

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def average_latency(self) -> float:
        return self.latency_sum / self.total if self.total else 0.0
