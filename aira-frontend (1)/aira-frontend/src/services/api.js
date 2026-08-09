// ---------------------------------------------------------------------------
// AIRA API service layer
//
// Every component talks to the backend through the functions exported here.
// ---------------------------------------------------------------------------

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const AGENT_ID_STORAGE_KEY = 'aira.agentId'
const PERSONA_STORAGE_KEY = 'aira.persona'

/**
 * A typed error so the UI can tell "backend is unreachable" apart from
 * "backend responded with an error" apart from "response was malformed".
 */
export class ApiError extends Error {
  constructor(message, { kind = 'unknown', status = null, cause = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind // 'network' | 'http' | 'parse' | 'unknown'
    this.status = status
    this.cause = cause
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch (err) {
    throw new ApiError('Could not reach the AIRA backend.', {
      kind: 'network',
      cause: err,
    })
  }

  if (!response.ok) {
    let detail = ''
    try {
      const body = await response.json()
      detail = body?.message || body?.detail || ''
    } catch {
      // response wasn't JSON — ignore, we still have the status code
    }
    throw new ApiError(detail || `Backend responded with ${response.status}.`, {
      kind: 'http',
      status: response.status,
    })
  }

  try {
    return await response.json()
  } catch (err) {
    throw new ApiError('Backend returned a response we could not parse.', {
      kind: 'parse',
      cause: err,
    })
  }
}

/**
 * POST /api/agent/init
 * Initializes the autonomous agent with a persona.
 * Returns the exact backend-issued agentId.
 */
export async function initializeAgent(persona) {
  const data = await request('/api/agent/init', {
    method: 'POST',
    body: JSON.stringify({ persona }),
  })

  if (!data?.agentId) {
    throw new ApiError('Backend did not return an agentId.', { kind: 'parse' })
  }

  return data.agentId
}

/**
 * GET /api/agent/feed?agentId=<agentId>
 * Fetches the current autonomous feed for a given agent using its exact agentId.
 */
export async function getFeed(agentId) {
  if (!agentId) {
    throw new ApiError('No agentId available — initialize the agent first.', {
      kind: 'unknown',
    })
  }

  const data = await request(`/api/agent/feed?agentId=${encodeURIComponent(agentId)}`, {
    method: 'GET',
  })
  return Array.isArray(data?.posts) ? data.posts : []
}

// ---------------------------------------------------------------------------
// localStorage helpers — keep the agent's identity across page reloads
// ---------------------------------------------------------------------------

export function saveAgentId(agentId) {
  try {
    localStorage.setItem(AGENT_ID_STORAGE_KEY, agentId)
  } catch {
    // localStorage may be unavailable — non-fatal
  }
}

export function loadAgentId() {
  try {
    const id = localStorage.getItem(AGENT_ID_STORAGE_KEY)
    if (!id || id.includes('demo')) {
      localStorage.removeItem(AGENT_ID_STORAGE_KEY)
      return null
    }
    return id
  } catch {
    return null
  }
}

export function clearAgentId() {
  try {
    localStorage.removeItem(AGENT_ID_STORAGE_KEY)
  } catch {
    // ignore
  }
}

export function savePersona(persona) {
  try {
    localStorage.setItem(PERSONA_STORAGE_KEY, JSON.stringify(persona))
  } catch {
    // ignore
  }
}

export function loadPersona() {
  try {
    const raw = localStorage.getItem(PERSONA_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}
