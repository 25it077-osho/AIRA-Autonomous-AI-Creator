"""
post_generator.py

Generates AIRA's posts (and their publishing rationale) using an LLM.

AIRA's voice:
    - Technical but understandable
    - Concise
    - Analytical, evidence-based
    - Not sensational, avoids generic AI hype
    - Focuses on *why the development matters* and its security implications
    - Sounds like an AI security researcher, not a marketing account

If no LLM_API_KEY is configured (or the LLM call fails for any reason),
we fall back to a deterministic template-based generator so the pipeline
never crashes and always produces a reasonable post.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("aira.post_generator")

LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.anthropic.com/v1/messages")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
REQUEST_TIMEOUT_SECONDS = 30.0

SYSTEM_PROMPT = """You are AIRA, an autonomous AI security researcher and technology analyst.

Voice and editorial rules:
- Technical but understandable to a broad tech-literate audience.
- Concise: 3 short paragraphs, no more than about 130 words total.
- Analytical and evidence-based, never sensational or hype-driven.
- Focus on WHY the development matters, especially its security implications.
- Do not simply restate the headline - add original analysis.
- Do not copy phrasing from the source material; write in your own words.
- No hashtags, no emoji, no marketing language, no exclamation points.
- Sound like a researcher publishing a brief analytical note, not a company account.

Output ONLY the post text itself, nothing else (no preamble, no title, no quotes around it)."""


def _build_user_prompt(topic: Dict[str, Any]) -> str:
    return (
        f"Topic title: {topic.get('title', '')}\n"
        f"Summary / context: {topic.get('summary', '')}\n"
        f"Source: {topic.get('url', '')}\n\n"
        "Write AIRA's post about this development, following your voice and editorial rules."
    )


def _call_llm(topic: Dict[str, Any]) -> Optional[str]:
    if not LLM_API_KEY:
        return None

    try:
        headers = {
            "content-type": "application/json",
            "x-api-key": LLM_API_KEY,
            "anthropic-version": "2023-06-01",
        }
        body = {
            "model": LLM_MODEL,
            "max_tokens": 400,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": _build_user_prompt(topic)}
            ],
        }
        with httpx.Client() as client:
            resp = client.post(
                LLM_API_URL, headers=headers, json=body, timeout=REQUEST_TIMEOUT_SECONDS
            )
        resp.raise_for_status()
        data = resp.json()
        parts = [
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        ]
        text = "\n".join(p for p in parts if p).strip()
        return text or None
    except Exception as exc:  # pragma: no cover - defensive: never crash the cycle
        logger.warning("[AIRA] LLM post generation failed, using fallback: %s", exc)
        return None


def _fallback_post(topic: Dict[str, Any]) -> str:
    """Deterministic, template-based post used when no LLM is configured
    or the LLM call fails. Not a copy of the source - original phrasing
    built from the topic's title/summary."""
    title = topic.get("title", "this development").rstrip(".")
    summary = (topic.get("summary") or "").strip()
    summary_clause = f" Early discussion centers on {summary[:160].rstrip('.')}." if summary else ""

    return (
        f"{title} is drawing attention, but the more useful question is what it changes "
        f"for security rather than the announcement itself.{summary_clause}\n\n"
        "The relevant shift is usually not the capability alone - it's the new attack "
        "surface created as systems like this gain more autonomy, more tool access, or "
        "wider deployment.\n\n"
        "For teams building or deploying AI systems, that argues for treating this as a "
        "prompt to revisit assumptions about trust boundaries, not just a headline to note."
    )


def generate_post_text(topic: Dict[str, Any]) -> str:
    """Generate the body text of a post about `topic`."""
    text = _call_llm(topic)
    if text:
        return text
    return _fallback_post(topic)


def generate_rationale(
    selected: Dict[str, Any], other_candidates: List[Dict[str, Any]], rejected: List[Dict[str, Any]]
) -> str:
    """
    Build the publishing rationale required for every post:
      1. Why this topic was selected.
      2. Why it is relevant now.
      3. Why it was selected over other discovered candidates.
      4. Why it fits AIRA's editorial focus.
    """
    title = selected.get("title", "this topic")
    reasons = selected.get("reasons", [])
    reason_str = "; ".join(reasons) if reasons else "it met AIRA's relevance and quality bar"

    other_titles = [c.get("title") for c in other_candidates[:3] if c.get("title")]
    rejected_titles = [c.get("title") for c in rejected[:3] if c.get("title")]

    parts = [
        f"Selected \"{title}\" because {reason_str}.",
        "It is timely and connects directly to AIRA's editorial focus on AI security "
        "and the practical implications of AI system deployment.",
    ]

    if other_titles:
        parts.append(
            "It was prioritized over other candidates considered in this cycle, including "
            + "; ".join(other_titles)
            + ", which scored lower on relevance, recency, or substance."
        )
    elif rejected_titles:
        parts.append(
            "Other candidates discovered in this cycle were rejected for being repetitive, "
            "low-substance, or only tangentially related to AI security, including "
            + "; ".join(rejected_titles)
            + "."
        )
    else:
        parts.append(
            "No other candidates from this cycle met the acceptance bar, making this the "
            "clear choice."
        )

    return " ".join(parts)
