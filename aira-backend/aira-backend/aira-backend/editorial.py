"""
editorial.py

AIRA's editorial judgment layer. Takes raw discovered topics and decides
which (if any) are worth writing about.

Every candidate is scored against a set of editorial criteria. Topics that
fall below the acceptance threshold are rejected (and remembered as
rejected, so they aren't re-considered every cycle). The single
highest-scoring surviving candidate is selected for post generation.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from memory import memory

logger = logging.getLogger("aira.editorial")

# Terms that signal genuine relevance to AIRA's beat (AI security).
RELEVANT_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml", "llm",
    "large language model", "agent", "agentic", "prompt injection",
    "jailbreak", "model", "neural", "security", "vulnerability", "exploit",
    "red team", "adversarial", "safety", "guardrail", "supply chain",
    "open source", "open-source", "inference", "training data", "gpt",
    "claude", "gemini", "transformer", "chatbot", "autonomous",
]

# Terms that suggest low editorial value (clickbait / hype / unrelated noise).
LOW_QUALITY_SIGNALS = [
    "you won't believe", "shocking", "top 10", "top ten", "clickbait",
    "sponsored", "advertisement", "giveaway", "discount code",
]

ACCEPTANCE_THRESHOLD = 0.45
MIN_SUMMARY_LENGTH = 20  # characters - very short summaries lack substance


def _relevance_score(text: str) -> Tuple[float, List[str]]:
    text_lower = text.lower()
    hits = [kw for kw in RELEVANT_KEYWORDS if kw in text_lower]
    # Cap contribution so a single keyword-stuffed title can't dominate.
    score = min(len(hits) / 4.0, 1.0)
    return score, hits


def _recency_score(published_at: Optional[str]) -> float:
    if not published_at:
        return 0.4  # unknown recency - neutral-ish, not a dealbreaker
    try:
        published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - published).total_seconds() / 86400
    except ValueError:
        return 0.4

    if age_days <= 2:
        return 1.0
    if age_days <= 7:
        return 0.75
    if age_days <= 30:
        return 0.4
    return 0.15


def _quality_score(topic: Dict[str, Any]) -> Tuple[float, List[str]]:
    reasons: List[str] = []
    title = topic.get("title", "")
    summary = topic.get("summary", "")
    combined = f"{title} {summary}".lower()

    score = 1.0

    if any(sig in combined for sig in LOW_QUALITY_SIGNALS):
        score -= 0.6
        reasons.append("contains low-quality / clickbait signal")

    if len(summary) < MIN_SUMMARY_LENGTH:
        score -= 0.2
        reasons.append("very little substance in summary")

    points = topic.get("points")
    if isinstance(points, (int, float)) and points >= 20:
        score += 0.15
        reasons.append("meaningful community engagement")

    return max(score, 0.0), reasons


def evaluate_topic(topic: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score a single topic and attach reasoning. Returns the topic dict
    augmented with `score`, `accepted`, and `reasons`.
    """
    title = topic.get("title", "").strip()
    url = topic.get("url", "").strip()
    summary = topic.get("summary", "") or ""

    reasons: List[str] = []

    # Already covered or already rejected -> immediate reject, no need to score.
    if memory.has_covered(url, title):
        topic["score"] = 0.0
        topic["accepted"] = False
        topic["reasons"] = ["already covered previously"]
        return topic

    if memory.was_rejected(url, title):
        topic["score"] = 0.0
        topic["accepted"] = False
        topic["reasons"] = ["previously rejected as low quality"]
        return topic

    relevance, relevant_hits = _relevance_score(f"{title} {summary}")
    if relevance == 0.0:
        reasons.append("not related to AI or AI security")

    recency = _recency_score(topic.get("published_at"))
    quality, quality_reasons = _quality_score(topic)
    reasons.extend(quality_reasons)

    if relevant_hits:
        reasons.append(f"relevant to AI security editorial focus ({', '.join(relevant_hits[:4])})")

    # Weighted composite score.
    score = (relevance * 0.55) + (recency * 0.25) + (quality * 0.20)

    accepted = score >= ACCEPTANCE_THRESHOLD and relevance > 0

    topic["score"] = round(score, 3)
    topic["accepted"] = accepted
    topic["reasons"] = reasons
    return topic


def evaluate_candidates(topics: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Evaluate every candidate topic. Deduplicates already-seen topics within
    this batch, evaluates each, and splits into accepted / rejected lists
    (accepted sorted best-first).
    """
    seen_in_batch = set()
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for topic in topics:
        url = topic.get("url", "").strip()
        if not url or url in seen_in_batch:
            continue
        seen_in_batch.add(url)

        evaluated = evaluate_topic(topic)
        if evaluated["accepted"]:
            accepted.append(evaluated)
        else:
            rejected.append(evaluated)
            memory.mark_rejected(evaluated.get("url", ""), evaluated.get("title", ""))
            logger.info(
                "[AIRA] Rejected topic: %s (score=%.2f, reasons=%s)",
                evaluated.get("title"),
                evaluated.get("score", 0.0),
                "; ".join(evaluated.get("reasons", [])) or "n/a",
            )

    accepted.sort(key=lambda t: t.get("score", 0.0), reverse=True)
    return {"accepted": accepted, "rejected": rejected}


def select_best_topic(
    accepted: List[Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Pick the single best topic from the accepted list.

    Returns (selected_topic_or_None, other_candidates_considered).
    """
    if not accepted:
        return None, []
    selected = accepted[0]
    others = accepted[1:]
    return selected, others
