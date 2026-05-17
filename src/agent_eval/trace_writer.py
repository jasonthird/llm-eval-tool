from __future__ import annotations

import asyncio
from pathlib import Path

from agent_eval.schemas import EvaluationResult


class AsyncTraceWriter:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.queue: asyncio.Queue[EvaluationResult | None] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None

    async def __aenter__(self) -> "AsyncTraceWriter":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._task = asyncio.create_task(self._write_loop())
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def write(self, result: EvaluationResult) -> None:
        await self.queue.put(result)

    async def close(self) -> None:
        await self.queue.put(None)
        if self._task:
            await self._task

    async def _write_loop(self) -> None:
        with self.path.open("w", encoding="utf-8") as fh:
            while True:
                item = await self.queue.get()
                if item is None:
                    break
                fh.write(item.model_dump_json() + "\n")
                fh.flush()
