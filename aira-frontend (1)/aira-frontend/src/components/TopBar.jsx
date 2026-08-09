import { useEffect, useState } from 'react'
import './TopBar.css'

export default function TopBar({
  persona,
  agentId,
  postCount,
  lastFetchedAt,
  nextCycleAt,
  isAutonomous,
  onReset,
  onRefresh,
  feedStatus,
}) {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  const nextCycleIn = nextCycleAt ? Math.max(0, Math.round((nextCycleAt.getTime() - now.getTime()) / 1000)) : 0
  const mm = String(Math.floor(nextCycleIn / 60)).padStart(2, '0')
  const ss = String(nextCycleIn % 60).padStart(2, '0')

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="topbar-heading">
          <div className="topbar-radar" aria-hidden="true">
            <span className="radar-sweep" />
          </div>
          <div>
            <h1 className="topbar-title">
              {persona?.name || 'AIRA'} <span className="topbar-title-fade">— Autonomous AI Creator</span>
            </h1>
            <p className="topbar-subtitle">
              An AI persona that discovers, thinks, decides, and publishes autonomously.
            </p>
          </div>
        </div>

        <div className="topbar-actions">
          <span
            className={
              'pill ' +
              (isAutonomous ? 'pill-live' : feedStatus === 'error' ? 'pill-error' : 'pill-warn')
            }
          >
            <span className="pill-dot" />
            {isAutonomous ? 'AUTONOMOUS' : feedStatus === 'error' ? 'DISCONNECTED' : 'STANDBY'}
          </span>
          <button className="btn btn-sm" onClick={onRefresh} title="Refresh feed & trigger cycle now">
            ⟳ Refresh
          </button>
          <button className="btn btn-sm btn-ghost" onClick={onReset} title="Disconnect this agent">
            End session
          </button>
        </div>
      </div>

      <div className="topbar-stats">
        <Stat label="Domain" value={persona?.domain || '—'} />
        <Stat label="Agent ID" value={shorten(agentId)} mono />
        <Stat label="Posts published" value={postCount} />
        <Stat label="Last synced" value={lastFetchedAt ? formatTime(lastFetchedAt) : '—'} mono />
        <Stat label="Next autonomous cycle" value={`${mm}:${ss}`} mono accent />
      </div>

      <div className="waveform" aria-hidden="true">
        {Array.from({ length: 64 }).map((_, i) => (
          <span
            key={i}
            className="waveform-bar"
            style={{
              animationDelay: `${(i % 16) * 0.09}s`,
              opacity: isAutonomous ? 1 : 0.25,
            }}
          />
        ))}
      </div>
    </header>
  )
}

function Stat({ label, value, mono, accent }) {
  return (
    <div className="topbar-stat">
      <span className="topbar-stat-label">{label}</span>
      <span className={'topbar-stat-value' + (mono ? ' mono' : '') + (accent ? ' accent' : '')}>
        {value}
      </span>
    </div>
  )
}

function shorten(id) {
  if (!id) return '—'
  return id.length > 14 ? `${id.slice(0, 6)}…${id.slice(-4)}` : id
}

function formatTime(date) {
  return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
