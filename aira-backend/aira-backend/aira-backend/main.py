"""
main.py

FastAPI entrypoint for the AIRA backend.

Endpoints:
POST /api/agent/init
GET  /api/agent/feed
GET  /health
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Query
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


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("aira.main")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AIRA - Autonomous AI Creator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# Temporary allow-all configuration to verify browser connectivity.
# credentials=False is required when using allow_origins=["*"].

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Active agents and schedulers
# ---------------------------------------------------------------------------

agents: Dict[str, AiraAgent] = {}
schedulers: Dict[str, AiraScheduler] = {}


# ---------------------------------------------------------------------------
# Initialize agent
# ---------------------------------------------------------------------------

@app.post(
    "/api/agent/init",
    response_model=AgentInitResponse,
)
async def init_agent(
    payload: Optional[AgentInitRequest] = None,
) -> AgentInitResponse:

    persona = payload.persona if payload and payload.persona else None

    name = persona.name if persona else "AIRA"
    domain = persona.domain if persona else "AI Security"

    agent = AiraAgent(
        name=name,
        domain=domain,
    )

    agents[agent.agent_id] = agent

    logger.info(
        "[AIRA] Agent initialized (id=%s, name=%s, domain=%s)",
        agent.agent_id,
        name,
        domain,
    )

    scheduler = AiraScheduler(agent)

    schedulers[agent.agent_id] = scheduler

    scheduler.start()

    return AgentInitResponse(
        agentId=agent.agent_id
    )


# ---------------------------------------------------------------------------
# Get autonomous feed
# ---------------------------------------------------------------------------

@app.get(
    "/api/agent/feed",
    response_model=FeedResponse,
)
async def get_feed(
    agentId: str = Query(
        ...,
        description="The agent ID returned by /api/agent/init",
    ),
) -> FeedResponse:

    if agents and agentId not in agents:
        logger.warning(
            "[AIRA] /api/agent/feed called with unknown agentId=%s",
            agentId,
        )

    posts = memory.get_posts()

    posts_sorted = sorted(
        posts,
        key=lambda p: p.get("createdAt", ""),
        reverse=True,
    )

    return FeedResponse(
        posts=posts_sorted
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
)
async def health() -> HealthResponse:

    return HealthResponse(
        status="ok"
    )