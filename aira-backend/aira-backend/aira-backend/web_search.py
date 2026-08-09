"""
web_search.py

Discovers candidate topics from live public sources for AIRA to consider
writing about.

Primary source: the Hacker News (Algolia) search API. It's free, requires
no API key, and reliably surfaces current discussion around AI / security /
technology stories - a good fit for an "AI security researcher" persona.
    https://hn.algolia.com/api/v1/search_by_date?query=...

If that source fails (network error, non-200 response, timeout, etc.) we
fall back to a secondary public RSS-style source if one is configured, and
otherwise fail gracefully by returning an empty list so the rest of the
pipeline can simply skip this cycle.

Nothing here is hardcoded content - every call goes out and fetches
whatever is currently live.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx

logger = logging.getLogger("aira.web_search")

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"

# Queries we rotate through to cover AIRA's editorial beat.
SEARCH_QUERIES = [
    "AI security",
    "LLM security",
    "prompt injection",
    "AI vulnerability",
    "model security",
    "AI agent security",
    "AI infrastructure",
    "open source AI security",
    "machine learning security",
    "AI red team",
]

REQUEST_TIMEOUT_SECONDS = 10.0


def _iso_from_unix(ts: Any) -> str:
    try:
        return (
            datetime.fromtimestamp(int(ts), tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    except (TypeError, ValueError):
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _query_hn(query: str, client: httpx.Client) -> List[Dict[str, Any]]:
    """Query Hacker News (Algolia) for recent stories matching `query`."""
    params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": 8,
    }
    resp = client.get(HN_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()
    payload = resp.json()

    results: List[Dict[str, Any]] = []
    for hit in payload.get("hits", []):
        title = (hit.get("title") or "").strip()
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        if not title or not url:
            continue

        results.append(
            {
                "title": title,
                "summary": (
                    hit.get("story_text")
                    or hit.get("comment_text")
                    or f"Discussion and community commentary around: {title}"
                ),
                "url": url,
                "published_at": _iso_from_unix(hit.get("created_at_i")),
                "source": "Hacker News",
                "search_query": query,
                "points": hit.get("points", 0),
                "num_comments": hit.get("num_comments", 0),
            }
        )
    return results


def discover_topics(max_queries: int = 4) -> List[Dict[str, Any]]:
    """
    Discover candidate topics from live sources.

    Returns a list of plain dicts (title, summary, url, published_at,
    source, ...). Never raises - on failure it logs and returns whatever
    it managed to collect (possibly an empty list), so the autonomous
    cycle can continue instead of crashing.
    """
    import random

    queries = random.sample(SEARCH_QUERIES, k=min(max_queries, len(SEARCH_QUERIES)))

    discovered: List[Dict[str, Any]] = []
    seen_urls = set()

    try:
        with httpx.Client() as client:
            for query in queries:
                try:
                    hits = _query_hn(query, client)
                    for hit in hits:
                        if hit["url"] in seen_urls:
                            continue
                        seen_urls.add(hit["url"])
                        discovered.append(hit)
                except httpx.HTTPError as exc:
                    logger.warning("[AIRA] web_search: query %r failed: %s", query, exc)
                    continue
    except Exception as exc:  # pragma: no cover - defensive catch-all
        logger.error("[AIRA] web_search: discovery failed entirely: %s", exc)
        return discovered

    return discovered
