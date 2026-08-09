"""
scheduler.py

Runs AIRA's autonomous loop in the background, independent of any further
API calls.

Design notes:
    - Uses a plain asyncio background task started on the running event
      loop (created via `asyncio.create_task` from within the FastAPI
      request handler / lifespan, so it shares the loop with the server).
    - The actual cycle logic (`agent.run_cycle`) is synchronous and may do
      blocking network I/O, so it's executed via `asyncio.to_thread` to
      avoid blocking the event loop / other requests (like /api/agent/feed).
    - The loop never raises out of itself: any exception during a cycle is
      logged and the loop waits for the next interval and continues, per
      the "must not crash" requirement.
    - Only one scheduler runs per agent instance (idempotent start).
"""
from __future__ import annotations

import asyncio
import logging
import os

from agent import AiraAgent

logger = logging.getLogger("aira.scheduler")

AUTONOMOUS_INTERVAL_SECONDS = int(os.getenv("AUTONOMOUS_INTERVAL_SECONDS", "60"))


class AiraScheduler:
    def __init__(self, agent: AiraAgent, interval_seconds: int = AUTONOMOUS_INTERVAL_SECONDS):
        self.agent = agent
        self.interval_seconds = interval_seconds
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            logger.info("[AIRA] Scheduler already running, ignoring duplicate start.")
            return

        self._task = asyncio.create_task(self._run_forever())
        logger.info("[AIRA] Autonomous scheduler started")

    def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def _run_forever(self) -> None:
        while True:
            try:
                await asyncio.to_thread(self.agent.run_cycle)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover - defensive: never die
                logger.error("[AIRA] Autonomous cycle raised an unexpected error: %s", exc)

            logger.info("[AIRA] Next cycle in %d seconds", self.interval_seconds)
            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                raise
