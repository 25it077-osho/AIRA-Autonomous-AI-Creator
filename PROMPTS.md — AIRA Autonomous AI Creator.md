# PROMPTS.md — AIRA Autonomous AI Creator

## Project

**AIRA — Autonomous AI Creator**

AIRA is an autonomous AI persona designed to discover topics, reason about them, make editorial decisions, generate content, and publish an ongoing feed with minimal manual intervention.

---

## 1. Initial Project Prompt

> Build an autonomous AI creator called AIRA.
>
> AIRA should behave as an autonomous AI persona that can discover topics, think about them, make decisions, create content, and publish it autonomously.
>
> The project should have a modern frontend dashboard and a FastAPI backend. The backend should manage agent initialization, autonomous execution, memory, scheduling, and the published feed.
>
> The frontend should allow the user to configure the persona name and domain, initialize the agent, and view the autonomous activity and published content.

---

## 2. Backend Architecture Prompt

> Create a FastAPI backend for AIRA Autonomous AI Creator.
>
> Required endpoints:
>
> - `POST /api/agent/init` — initialize an AIRA agent and start autonomous operation.
> - `GET /api/agent/feed` — return the published content feed for an initialized agent.
> - `GET /health` — backend health/monitoring endpoint.
>
> Keep the existing API contracts stable.
>
> Use separate modules for the agent, memory, models, scheduler, and FastAPI application entrypoint.
>
> The agent should have a unique agent ID and maintain its autonomous operation through the scheduler.
>
> Published posts should persist through the memory layer so the feed can survive backend restarts.

---

## 3. Agent Prompt

> Implement an `AiraAgent` that represents an autonomous AI creator.
>
> The agent should receive a persona name and domain, maintain its own identity through an agent ID, discover relevant topics, reason about what is worth publishing, generate editorial content, and publish the resulting posts.
>
> The agent should operate autonomously rather than requiring the user to manually create every post.
>
> Keep the implementation modular so the agent, memory, and scheduler can be developed and tested independently.

---

## 4. Memory Prompt

> Add a persistent memory layer for AIRA.
>
> Store published posts and relevant agent state on disk so that generated content can survive backend restarts.
>
> Provide a simple interface for retrieving posts and storing new content.
>
> Keep the feed compatible with the existing `/api/agent/feed` API.

---

## 5. Scheduler Prompt

> Implement an autonomous scheduler for AIRA.
>
> Once an agent is initialized, the scheduler should start autonomous execution in the background.
>
> The scheduler should periodically trigger the agent's discovery, reasoning, content generation, and publishing workflow.
>
> Ensure background execution is cleaned up correctly and avoid thread-safety or race-condition problems.
>
> Preserve the existing agent initialization and feed API contracts.

---

## 6. Frontend Prompt

> Build a React/Vite frontend for AIRA Autonomous AI Creator.
>
> Create an initialization screen where the user can enter:
>
> - Persona name
> - Domain
>
> Add an Initialize Agent button and show the initialization state and errors.
>
> After initialization, display an autonomous AI dashboard containing:
>
> - Agent/persona information
> - Published posts
> - Autonomous activity/events
> - Statistics
> - Topics
> - Feed status
> - Refresh/reset controls
>
> The interface should feel like a professional autonomous AI control center rather than a basic CRUD application.

---

## 7. Frontend–Backend Integration Prompt

> Connect the React frontend to the FastAPI backend.
>
> Use a centralized API service with an `API_BASE_URL` configuration.
>
> The production frontend must use the deployed backend URL instead of localhost.
>
> Store the initialized agent ID and persona information on the frontend so the dashboard can retrieve the correct feed.
>
> Handle network errors, HTTP errors, loading states, and backend failures gracefully.

---

## 8. CORS / Deployment Prompt

> Configure FastAPI CORS so the deployed GitHub Pages frontend can communicate with the deployed Render backend.
>
> Preserve local development origins while also allowing the production GitHub Pages origin:
>
> `https://25it077-osho.github.io`
>
> Keep credentials, methods, and headers configured correctly for the frontend API requests.

---

## 9. Production Environment Prompt

> Configure the frontend production API URL using Vite environment variables.
>
> The production environment should contain:
>
> `VITE_API_BASE_URL=https://aira-autonomous-ai-creator-1.onrender.com`
>
> The frontend must use this deployed backend URL when built for production.
>
> Do not hardcode localhost as the production API endpoint.

---

## 10. Debugging Prompt — Backend Connection

> Debug the AIRA frontend/backend connection.
>
> Verify:
>
> 1. The FastAPI backend is running.
> 2. `/health` is reachable.
> 3. `POST /api/agent/init` returns an agent ID.
> 4. CORS allows the deployed frontend.
> 5. The frontend uses the deployed Render URL.
> 6. The production Vite build contains the correct API URL.
>
> Do not change working API contracts unnecessarily.

---

## 11. Debugging Prompt — Autonomous Agent

> Debug and enhance the AIRA Autonomous AI Creator backend.
>
> Fix thread-safety race conditions, HTML artifact leakage, fallback generator phrasing issues, and background task cleanup.
>
> Add an automated test suite covering the important backend behavior.
>
> Preserve the existing API contracts:
>
> - `/api/agent/init`
> - `/api/agent/feed`
> - `/health`
>
> Preserve scheduler behavior and memory persistence.

---

## 12. Deployment Prompt

> Prepare the AIRA frontend for GitHub Pages deployment.
>
> Configure the Vite base path for:
>
> `/AIRA-Autonomous-AI-Creator/`
>
> Build the production frontend and publish the generated `dist` directory to GitHub Pages.
>
> The deployed frontend must communicate with the Render backend rather than localhost.

---

## 13. Production Verification Prompt

> Verify the complete deployed AIRA system end-to-end.
>
> Test:
>
> 1. GitHub Pages frontend loads.
> 2. Frontend can reach the Render backend.
> 3. Agent initialization succeeds.
> 4. An agent ID is returned.
> 5. Autonomous execution starts.
> 6. The feed endpoint returns published content.
> 7. The dashboard displays autonomous activity and generated posts.
>
> Identify and fix deployment-specific issues without breaking the working backend.

---

## 14. Final Product Goal

> AIRA should demonstrate a complete autonomous AI creation loop:
>
> **Discover → Think → Decide → Create → Publish → Remember → Repeat**
>
> The final product should make this autonomous behavior visible through the dashboard and provide a working deployed demonstration rather than only a static prototype.

---

## Development Notes

The project was developed iteratively using AI-assisted/vibe-coded development. Prompts were used to design the architecture, implement the frontend and backend, integrate the services, debug deployment issues, configure CORS, and verify the production system.

The final deployed architecture consists of:

- **Frontend:** React + Vite + GitHub Pages
- **Backend:** FastAPI + Uvicorn + Render
- **Agent:** AIRA autonomous creator
- **Memory:** Persistent backend storage
- **Scheduler:** Background autonomous execution
- **API:** `/api/agent/init`, `/api/agent/feed`, `/health`

## Production URLs

Frontend:

`https://25it077-osho.github.io/AIRA-Autonomous-AI-Creator/`

Backend:

`https://aira-autonomous-ai-creator-1.onrender.com`