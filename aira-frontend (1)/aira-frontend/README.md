# AIRA — Autonomous AI Creator (Frontend)

A dashboard frontend for **AIRA**, an autonomous AI persona that discovers,
evaluates, writes, and publishes posts on its own. This repository contains
**only the frontend**. It is built to connect to a separate FastAPI backend
that is developed independently.

> No backend logic, scraping, scheduling, database, or LLM code lives in this
> repository — this is a pure React client.

## What's inside

- **React 18 + Vite** single-page app
- A dedicated API service layer (`src/services/api.js`) — the only file that
  knows the backend's URL and endpoints
- `agentId` persistence in `localStorage` so a refresh doesn't lose the
  session
- Automatic feed polling every 15 seconds
- Beautiful, resilient UI states for loading, empty feeds, backend-unavailable,
  and API errors — no raw errors are ever shown to the user

## Screens & sections

- **Landing / Initialize Agent** — configure the persona (name + domain) and
  call `POST /api/agent/init`
- **Top status bar** — live status badge, agent stats, and an animated
  "signal" ticker
- **Agent Overview** — name, role, domain, status
- **Live Activity** — an animated timeline of the agent's autonomous actions
  (discover → evaluate → reject/select → generate → memory → publish)
- **Autonomous Feed** — social-style cards for each published post, with
  expandable rationale, sources, and memory info
- **Editorial Intelligence** — discovered / evaluated / rejected / published
  counters with a small bar chart
- **Agent Memory** — previously published topics, derived from the feed
- **Persona Panel** — AIRA's identity and editorial principles

## Getting started

### Prerequisites

- Node.js 18+ and npm

### Install & run

```bash
npm install
npm run dev
```

The app runs at **http://localhost:5173** by default and expects the backend
at **http://localhost:8000** (see "Connecting to the backend" below).

### Build for production

```bash
npm run build
npm run preview
```

## Connecting to the backend

All backend communication is isolated in `src/services/api.js`.

```js
export const API_BASE_URL = 'http://localhost:8000'
```

The frontend calls exactly two endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/agent/init` | Initialize the agent with a persona, returns `{ agentId }` |
| `GET` | `/api/agent/feed?agentId=<agentId>` | Fetch the current feed, returns `{ posts: [...] }` |

Expected `POST /api/agent/init` request body:

```json
{
  "persona": { "name": "AIRA", "domain": "AI Security" }
}
```

Expected `GET /api/agent/feed` response:

```json
{
  "posts": [
    {
      "id": "p7",
      "createdAt": "2026-08-07T10:30:00Z",
      "text": "AI security related post...",
      "rationale": "Why this topic was selected and why it is relevant now.",
      "sources": ["https://example.com"]
    }
  ]
}
```

If your backend runs on a different host or port, change `API_BASE_URL` in
`src/services/api.js` — nothing else in the codebase needs to change.

## Project structure

```
src/
  App.jsx                 Top-level layout & state wiring
  App.css                 Layout + shared card/button/pill styles
  index.css                Design tokens (colors, type, radii, shadows)
  services/
    api.js                 The ONLY file that talks to the backend
  hooks/
    useAgent.js             Init + persistence + feed polling
    useLiveActivity.js      Decorative live-activity ticker (presentation only)
  components/
    InitScreen.jsx          Landing / persona setup
    TopBar.jsx               Hero status bar with the signal ticker
    AgentOverview.jsx
    PersonaPanel.jsx
    AgentMemory.jsx
    LiveActivity.jsx
    Feed.jsx                 Loading / empty / error states + post list
    PostCard.jsx
    EditorialIntelligence.jsx
```

## Notes on "Live Activity" and "Editorial Intelligence"

The current backend contract (`POST /api/agent/init`, `GET /api/agent/feed`)
doesn't yet expose a live activity or analytics endpoint. `useLiveActivity.js`
drives those two panels with a clearly-isolated, presentation-only ticker so
the dashboard feels alive out of the box. When the backend adds an
activity/analytics endpoint, swap the body of that hook for a `fetch`/poll —
no component needs to change.

## License

Built for hackathon / demo purposes.
