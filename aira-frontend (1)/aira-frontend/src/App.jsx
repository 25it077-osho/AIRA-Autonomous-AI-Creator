import { useMemo, useState } from 'react'
import { useAgent } from './hooks/useAgent.js'
import { useLiveActivity } from './hooks/useLiveActivity.js'
import TopBar from './components/TopBar.jsx'
import InitScreen from './components/InitScreen.jsx'
import AgentOverview from './components/AgentOverview.jsx'
import LiveActivity from './components/LiveActivity.jsx'
import Feed from './components/Feed.jsx'
import EditorialIntelligence from './components/EditorialIntelligence.jsx'
import AgentMemory from './components/AgentMemory.jsx'
import PersonaPanel from './components/PersonaPanel.jsx'
import './App.css'

export default function App() {
  const {
    agentId,
    persona,
    initStatus,
    initError,
    initAgent,
    resetAgent,
    posts,
    feedStatus,
    feedError,
    lastFetchedAt,
    nextCycleAt,
    refreshNow,
  } = useAgent()

  const isAutonomous = Boolean(agentId) && feedStatus !== 'error'
  const { events, stats } = useLiveActivity(isAutonomous)

  const memoryTopics = useMemo(() => {
    return posts
      .map((p) => (p.text || '').split(/[.!?]/)[0].trim())
      .filter(Boolean)
      .slice(0, 8)
  }, [posts])

  if (!agentId) {
    return (
      <div className="app-shell">
        <InitScreen onInitialize={initAgent} status={initStatus} error={initError} />
      </div>
    )
  }

  return (
    <div className="app-shell">
      <TopBar
        persona={persona}
        agentId={agentId}
        postCount={posts.length}
        lastFetchedAt={lastFetchedAt}
        nextCycleAt={nextCycleAt}
        isAutonomous={isAutonomous}
        onReset={resetAgent}
        onRefresh={refreshNow}
        feedStatus={feedStatus}
      />

      <main className="dashboard-grid">
        <div className="col col-left">
          <AgentOverview persona={persona} postCount={posts.length} isAutonomous={isAutonomous} />
          <PersonaPanel persona={persona} />
          <AgentMemory topics={memoryTopics} feedStatus={feedStatus} />
        </div>

        <div className="col col-center">
          <Feed
            posts={posts}
            status={feedStatus}
            error={feedError}
            agentName={persona?.name}
            onRetry={refreshNow}
          />
        </div>

        <div className="col col-right">
          <LiveActivity events={events} active={isAutonomous} />
          <EditorialIntelligence stats={stats} publishedCount={posts.length} />
        </div>
      </main>

      <footer className="app-footer">
        <span className="mono">AIRA · autonomous editorial agent</span>
        <span className="dot-sep">·</span>
        <span>Frontend connected to <code className="mono">http://localhost:8000</code></span>
      </footer>
    </div>
  )
}
