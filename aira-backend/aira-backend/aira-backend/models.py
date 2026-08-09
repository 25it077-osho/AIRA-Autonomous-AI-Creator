"""
Pydantic models shared across the AIRA backend.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Persona / init
# ---------------------------------------------------------------------------

class PersonaConfig(BaseModel):
    name: str = "AIRA"
    domain: str = "AI Security"


class AgentInitRequest(BaseModel):
    persona: Optional[PersonaConfig] = Field(default_factory=PersonaConfig)


class AgentInitResponse(BaseModel):
    agentId: str


# ---------------------------------------------------------------------------
# Topics (internal, not exposed directly via API but used across modules)
# ---------------------------------------------------------------------------

class Topic(BaseModel):
    title: str
    summary: str
    url: str
    published_at: Optional[str] = None
    source: Optional[str] = None
    # Filled in by the editorial module
    score: Optional[float] = None
    reasons: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

class Post(BaseModel):
    id: str
    createdAt: str
    text: str
    rationale: str
    sources: List[str] = Field(default_factory=list)


class FeedResponse(BaseModel):
    posts: List[Post]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
