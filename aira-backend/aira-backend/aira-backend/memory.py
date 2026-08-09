"""
memory.py

Simple, persistent, file-backed memory for AIRA.

Responsibilities:
    * Track published posts (so /api/agent/feed can always serve them,
      even across backend restarts).
    * Track which topics / URLs / keywords have already been covered so the
      agent does not repeat itself.
    * Track rejected topics so the editorial layer doesn't re-evaluate the
      exact same weak candidate over and over.

Storage is plain JSON on disk (data/posts.json, data/memory.json). A simple
asyncio.Lock (plus a process-wide threading.Lock for the sync file I/O)
protects against concurrent writes, since the scheduler and API requests
can both touch these files.
"""
from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
POSTS_FILE = os.path.join(DATA_DIR, "posts.json")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")

_file_lock = threading.Lock()


def _ensure_data_files() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump({"posts": []}, f, indent=2)

    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "covered_urls": [],
                    "covered_titles": [],
                    "covered_keywords": [],
                    "rejected_urls": [],
                    "rejected_titles": [],
                },
                f,
                indent=2,
            )


def _read_json_unlocked(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_json_unlocked(path: str, data: Dict[str, Any]) -> None:
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, path)


def _read_json(path: str) -> Dict[str, Any]:
    with _file_lock:
        return _read_json_unlocked(path)


def _write_json(path: str, data: Dict[str, Any]) -> None:
    with _file_lock:
        _write_json_unlocked(path, data)


class Memory:
    """In-process convenience wrapper around the on-disk JSON memory."""

    def __init__(self) -> None:
        _ensure_data_files()

    # ------------------------------------------------------------------
    # Posts
    # ------------------------------------------------------------------
    def get_posts(self) -> List[Dict[str, Any]]:
        with _file_lock:
            data = _read_json_unlocked(POSTS_FILE)
            return data.get("posts", [])

    def add_post(self, post: Dict[str, Any]) -> None:
        with _file_lock:
            data = _read_json_unlocked(POSTS_FILE)
            posts = data.get("posts", [])
            posts.append(post)
            data["posts"] = posts
            _write_json_unlocked(POSTS_FILE, data)

    def next_post_id(self) -> str:
        with _file_lock:
            data = _read_json_unlocked(POSTS_FILE)
            posts = data.get("posts", [])
            return f"p{len(posts) + 1}"

    # ------------------------------------------------------------------
    # Memory (covered / rejected topics)
    # ------------------------------------------------------------------
    def _get_memory_unlocked(self) -> Dict[str, Any]:
        data = _read_json_unlocked(MEMORY_FILE)
        if not data:
            data = {
                "covered_urls": [],
                "covered_titles": [],
                "covered_keywords": [],
                "rejected_urls": [],
                "rejected_titles": [],
            }
        for key in (
            "covered_urls",
            "covered_titles",
            "covered_keywords",
            "rejected_urls",
            "rejected_titles",
        ):
            data.setdefault(key, [])
        return data

    def get_memory(self) -> Dict[str, Any]:
        with _file_lock:
            return self._get_memory_unlocked()

    def has_covered(self, url: str, title: str) -> bool:
        with _file_lock:
            mem = self._get_memory_unlocked()
            norm_title = _normalize(title)
            return url in mem["covered_urls"] or norm_title in mem["covered_titles"]

    def was_rejected(self, url: str, title: str) -> bool:
        with _file_lock:
            mem = self._get_memory_unlocked()
            norm_title = _normalize(title)
            return url in mem["rejected_urls"] or norm_title in mem["rejected_titles"]

    def mark_covered(self, url: str, title: str, keywords: Optional[List[str]] = None) -> None:
        with _file_lock:
            mem = self._get_memory_unlocked()
            if url not in mem["covered_urls"]:
                mem["covered_urls"].append(url)
            norm_title = _normalize(title)
            if norm_title not in mem["covered_titles"]:
                mem["covered_titles"].append(norm_title)
            if keywords:
                existing = set(mem["covered_keywords"])
                existing.update(k.lower() for k in keywords)
                mem["covered_keywords"] = sorted(existing)
            _write_json_unlocked(MEMORY_FILE, mem)

    def mark_rejected(self, url: str, title: str) -> None:
        with _file_lock:
            mem = self._get_memory_unlocked()
            if url not in mem["rejected_urls"]:
                mem["rejected_urls"].append(url)
            norm_title = _normalize(title)
            if norm_title not in mem["rejected_titles"]:
                mem["rejected_titles"].append(norm_title)
            _write_json_unlocked(MEMORY_FILE, mem)

    def covered_keywords(self) -> List[str]:
        with _file_lock:
            return self._get_memory_unlocked().get("covered_keywords", [])


def _normalize(title: str) -> str:
    return " ".join(title.lower().split())


# A single process-wide memory instance is enough for this simple backend.
memory = Memory()

