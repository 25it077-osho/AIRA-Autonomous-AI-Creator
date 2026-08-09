"""
agent.py

The AIRA agent itself: holds persona/state and knows how to run a single
autonomous cycle:

    discover -> evaluate -> reject/select -> generate -> remember -> publish

The scheduler (scheduler.py) is responsible for calling `run_cycle()`
repeatedly; this module just implements what a cycle *does*.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import editorial
import post_generator
import web_search
from memory import memory

logger = logging.getLogger("aira.agent")


class AiraAgent:
    def __init__(self, name: str = "AIRA", domain: str = "AI Security"):
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.domain = domain
        self.initialized_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.is_running = False

    # ------------------------------------------------------------------
    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "agentId": self.agent_id,
            "name": self.name,
            "domain": self.domain,
            "initializedAt": self.initialized_at,
        }

    # ------------------------------------------------------------------
    def run_cycle(self) -> Optional[Dict[str, Any]]:
        """
        Run exactly one autonomous cycle. Returns the published post dict,
        or None if nothing was published this cycle (e.g. discovery failed,
        or no candidate met the editorial bar).

        This method is intentionally synchronous / blocking so it is easy
        to reason about and test; the scheduler runs it in a worker thread
        so it never blocks the FastAPI event loop.
        """
        logger.info("[AIRA] Discovering topics...")
        try:
            raw_topics = web_search.discover_topics()
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("[AIRA] Topic discovery raised unexpectedly: %s", exc)
            raw_topics = []

        if not raw_topics:
            logger.info("[AIRA] No candidate topics discovered this cycle.")
            return None

        logger.info("[AIRA] Found %d candidate topics", len(raw_topics))

        logger.info("[AIRA] Evaluating candidates...")
        evaluation = editorial.evaluate_candidates(raw_topics)
        accepted = evaluation["accepted"]
        rejected = evaluation["rejected"]

        if not accepted:
            logger.info(
                "[AIRA] No candidate met the editorial bar this cycle (%d rejected).",
                len(rejected),
            )
            return None

        selected, others = editorial.select_best_topic(accepted)
        if not selected:
            return None

        logger.info("[AIRA] Selected: %s", selected.get("title"))

        logger.info("[AIRA] Generating post...")
        try:
            post_text = post_generator.generate_post_text(selected)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("[AIRA] Post generation failed: %s", exc)
            return None

        rationale = post_generator.generate_rationale(selected, others, rejected)

        post_id = memory.next_post_id()
        post = {
            "id": post_id,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "text": post_text,
            "rationale": rationale,
            "sources": [selected.get("url")] if selected.get("url") else [],
        }

        memory.add_post(post)
        memory.mark_covered(
            selected.get("url", ""),
            selected.get("title", ""),
            keywords=selected.get("reasons", []),
        )

        logger.info("[AIRA] Post published: %s", post_id)
        logger.info("[AIRA] Memory updated")

        return post
