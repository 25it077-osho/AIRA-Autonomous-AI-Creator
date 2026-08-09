import { useState } from 'react'
import './InitScreen.css'

export default function InitScreen({ onInitialize, status, error }) {
  const [name, setName] = useState('AIRA')
  const [domain, setDomain] = useState('AI Security')

  const isPending = status === 'pending'

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!name.trim() || !domain.trim() || isPending) return
    onInitialize({ name: name.trim(), domain: domain.trim() })
  }

  return (
    <div className="init-screen">
      <div className="init-glow" aria-hidden="true" />

      <div className="init-content">
        <div className="init-badge mono">
          <span className="init-badge-dot" />
          AUTONOMOUS AI CREATOR
        </div>

        <h1 className="init-title">
          AIRA <span className="init-title-dash">—</span> Autonomous AI Creator
        </h1>
        <p className="init-subtitle">
          An AI persona that discovers, thinks, decides, and publishes autonomously.
        </p>

        <form className="init-card glass-card" onSubmit={handleSubmit}>
          <div className="card-eyebrow">
            <span className="eyebrow-icon">🛰️</span> Agent configuration
          </div>

          <label className="init-field">
            <span>Persona name</span>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="AIRA"
              maxLength={40}
              required
            />
          </label>

          <label className="init-field">
            <span>Domain</span>
            <input
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="AI Security"
              maxLength={60}
              required
            />
          </label>

          <button className="btn btn-primary init-submit" type="submit" disabled={isPending}>
            {isPending ? (
              <>
                <span className="spinner" /> Initializing agent…
              </>
            ) : (
              'Initialize Agent'
            )}
          </button>

          {status === 'error' && error ? (
            <div className="init-error" role="alert">
              <strong>Couldn't initialize the agent.</strong>
              <span>{friendlyMessage(error)}</span>
            </div>
          ) : null}

          <p className="init-hint">
            Connects to <code className="mono">POST /api/agent/init</code> on your backend at{' '}
            <code className="mono">http://localhost:8000</code>. Automatically runs in standalone mode if backend is offline.
          </p>
        </form>
      </div>
    </div>
  )
}

function friendlyMessage(error) {
  if (error?.kind === 'network') {
    return 'The backend at http://localhost:8000 is not reachable. Make sure it is running, then try again.'
  }
  if (error?.kind === 'http') {
    return `The backend rejected the request${error.status ? ` (status ${error.status})` : ''}. ${error.message || ''}`.trim()
  }
  return error?.message || 'Something unexpected happened. Please try again.'
}
