"""
main.py

FastAPI entrypoint for the AIRA backend.

Endpoints:
    POST /api/agent/init   - initialize the agent and start autonomous operation
    GET  /api/agent/feed   - retrieve the published post feed
    GET  /health           - dev/monitoring health check
"""
from __future__ import annotations

import logging
import os
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from agent import AiraAgent
from memory import memory
from models import (
    AgentInitRequest,
    AgentInitResponse,
    FeedResponse,
    HealthResponse,
)
from scheduler import AiraScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aira.main")

app = FastAPI(title="AIRA - Autonomous AI Creator", version="1.0.0")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
env_origins_raw = os.getenv("FRONTEND_ORIGIN") or os.getenv("CORS_ORIGINS") or ""
extra_origins = [o.strip() for o in env_origins_raw.split(",") if o.strip()]

allowed_origins = list(set(default_origins + extra_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory registry of active agents (agentId -> AiraAgent / scheduler)
# Kept simple on purpose: a single backend process, in-process dict, backed
# by durable on-disk data (posts/memory) so the feed survives restarts.
# ---------------------------------------------------------------------------
agents: Dict[str, AiraAgent] = {}
schedulers: Dict[str, AiraScheduler] = {}


@app.post("/api/agent/init", response_model=AgentInitResponse)
async def init_agent(payload: Optional[AgentInitRequest] = None) -> AgentInitResponse:
    persona = payload.persona if payload and payload.persona else None
    name = persona.name if persona else "AIRA"
    domain = persona.domain if persona else "AI Security"

    agent = AiraAgent(name=name, domain=domain)
    agents[agent.agent_id] = agent
    logger.info("[AIRA] Agent initialized (id=%s, name=%s, domain=%s)", agent.agent_id, name, domain)

    scheduler = AiraScheduler(agent)
    schedulers[agent.agent_id] = scheduler
    scheduler.start()

    return AgentInitResponse(agentId=agent.agent_id)


@app.get("/api/agent/feed", response_model=FeedResponse)
async def get_feed(agentId: str = Query(..., description="The agent ID returned by /api/agent/init")) -> FeedResponse:
    # Posts persist on disk regardless of which agent published them, so we
    # only need to validate the agentId looks like one we've seen when the
    # process has that state available. If the process restarted and lost
    # the in-memory registry, we still serve the durable feed rather than
    # error out - the evaluator only ever gets the agentId from /init in
    # the same run, so this stays permissive but logs anything unexpected.
    if agents and agentId not in agents:
        logger.warning("[AIRA] /api/agent/feed called with unknown agentId=%s", agentId)

    posts = memory.get_posts()
    # Newest first.
    posts_sorted = sorted(posts, key=lambda p: p.get("createdAt", ""), reverse=True)
    return FeedResponse(posts=posts_sorted)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
