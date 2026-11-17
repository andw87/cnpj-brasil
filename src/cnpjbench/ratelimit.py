"""Per-source pacing: fixed minimum interval derived from rate_limit_rpm (docs/methodology.md, section 3)."""
from __future__ import annotations

import asyncio
import time


class Pacer:
    def __init__(self, rpm: float | None):
        self.interval = 60.0 / rpm if rpm else 0.0
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            if now < self._next:
                await asyncio.sleep(self._next - now)
            self._next = max(now, self._next) + self.interval

    def penalize(self, seconds: float) -> None:
        """Push the next slot forward (after a 429 / Retry-After)."""
        self._next = max(self._next, time.monotonic() + seconds)
