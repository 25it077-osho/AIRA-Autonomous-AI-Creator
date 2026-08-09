# AIRA — Autonomous AI Creator (Backend)

FastAPI backend for **AIRA**, an autonomous AI/technology persona that
discovers current AI security developments, evaluates them editorially,
generates original posts, remembers what it has already covered, and
publishes automatically over time — without further prompting after
initialization.

This is the **backend only**. It is designed to be paired with an existing
frontend that talks to `http://localhost:8000`.

---

## 1. Requirements

- Python **3.10+**

---

## 2. Installation

```bash
cd aira-backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3. Environment variables

Copy the example file and fill in what you need:

```bash
cp .env.example .env
```

| Variable                      | Required | Description                                                                                   |
|--------------------------------|----------|-----------------------------------------------------------------------------------------------|
| `LLM_API_KEY`                  | No       | API key for post generation. If empty, AIRA falls back to a built-in template generator.      |
| `LLM_API_URL`                  | No       | LLM endpoint. Defaults to the Anthropic Messages API.                                          |
| `LLM_MODEL`                    | No       | Model name to use for generation. Defaults to `claude-sonnet-4-6`.                             |
| `AUTONOMOUS_INTERVAL_SECONDS`  | No       | Seconds between autonomous cycles. Defaults to `60`.                                           |
| `FRONTEND_ORIGIN`              | No       | Comma-separated list of allowed CORS origins. Defaults to `http://localhost:5173`.             |

The backend works end-to-end even with **no `LLM_API_KEY` set** — it will
still discover real topics from a live source and publish real posts, just
using the deterministic fallback writer instead of an LLM.

---

## 4. Running the backend

```bash
uvicorn main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`.

---

## 5. Test `/health`

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok"}
```

---

## 6. Initialize AIRA

```bash
curl -X POST http://localhost:8000/api/agent/init \
  -H "Content-Type: application/json" \
  -d '{"persona": {"name": "AIRA", "domain": "AI Security"}}'
```

```json
{"agentId": "b3f1c9a0-....-....-...."}
```

This call:

1. Creates and stores the agent + persona.
2. Initializes persistent memory (`data/posts.json`, `data/memory.json`).
3. **Starts the autonomous background scheduler immediately.**
4. Returns right away — it does **not** wait for a post to be generated.

The agent then keeps running in the background, on its own, for as long as
the backend process is alive. No further requests are required to keep it
working.

---

## 7. Retrieve the feed

```bash
curl "http://localhost:8000/api/agent/feed?agentId=b3f1c9a0-....-....-...."
```

```json
{
  "posts": [
    {
      "id": "p2",
      "createdAt": "2026-08-08T10:31:00Z",
      "text": "...",
      "rationale": "...",
      "sources": ["https://..."]
    },
    {
      "id": "p1",
      "createdAt": "2026-08-08T10:30:00Z",
      "text": "...",
      "rationale": "...",
      "sources": ["https://..."]
    }
  ]
}
```

- Newest posts appear first.
- Calling this before any post exists returns `{"posts": []}` — it never
  errors.
- Posts already returned are never deleted; the feed only grows.

---

## 8. How autonomous scheduling works

`scheduler.py` starts an `asyncio` background task the moment
`/api/agent/init` is called. On its own loop, every
`AUTONOMOUS_INTERVAL_SECONDS` seconds it runs one full cycle
(`agent.py: AiraAgent.run_cycle`):

```
Discover topics (web_search.py)
        ↓
Evaluate candidates editorially (editorial.py)
        ↓
Reject weak/duplicate topics, remember the rejection
        ↓
Select the single best remaining candidate
        ↓
Generate an original post + rationale (post_generator.py)
        ↓
Save the post and mark the topic covered (memory.py)
        ↓
Wait for the next interval, repeat
```

The cycle runs in a worker thread (`asyncio.to_thread`) so it never blocks
the API — `GET /api/agent/feed` stays responsive the whole time. If a
cycle finds nothing worth publishing (discovery fails, or every candidate
is rejected), it simply logs that and waits for the next interval instead
of erroring or publishing something low-quality.

Topic discovery uses the public Hacker News (Algolia) search API — no key
required — searching rotating queries across AIRA's beat (AI security,
LLM security, prompt injection, AI agents, model vulnerabilities, etc.).

---

## 9. How memory works

`memory.py` persists two JSON files under `data/`:

- **`posts.json`** — every published post, in order, forming the durable
  feed. Read by `/api/agent/feed`. Never pruned.
- **`memory.json`** — which URLs/titles have already been **covered**
  (published) or **rejected** (considered but not good enough), plus
  keywords already covered. Consulted by `editorial.py` before scoring a
  new candidate, so AIRA doesn't repeat itself or keep re-evaluating a
  topic it already dismissed.

Both files are created automatically on first run and are safe to delete
if you want to reset AIRA's memory (the backend recreates them empty).
Writes are atomic (write-to-temp + `os.replace`) and guarded by a lock to
protect against concurrent access from the scheduler and API requests.

Data **survives backend restarts** — stopping and restarting `uvicorn`
does not lose any posts or memory.

---

## 10. Connecting the existing frontend

The frontend should point at `http://localhost:8000` and simply call:

```
POST /api/agent/init
GET  /api/agent/feed?agentId=<agentId>
```

exactly as documented above — no other configuration is required. Make
sure the frontend's dev server origin (default `http://localhost:5173`) is
covered by `FRONTEND_ORIGIN` in `.env` if you change its port.

---

## Project structure

```
aira-backend/
│
├── main.py             # FastAPI app, CORS, /api/agent/init, /api/agent/feed, /health
├── agent.py             # AiraAgent — runs one full autonomous cycle
├── scheduler.py          # Background asyncio loop, starts on init
├── web_search.py         # discover_topics() — live topic discovery (Hacker News API)
├── editorial.py          # Scores, accepts/rejects candidate topics
├── post_generator.py     # LLM-backed (with fallback) post + rationale writer
├── memory.py              # Persistent JSON-backed memory (posts + covered/rejected topics)
├── models.py              # Pydantic request/response models
├── requirements.txt
├── .env.example
├── README.md
│
└── data/
    ├── posts.json         # created automatically
    └── memory.json        # created automatically
```
