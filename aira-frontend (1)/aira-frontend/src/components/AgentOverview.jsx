import './AgentOverview.css'

export default function AgentOverview({ persona, postCount, isAutonomous }) {
  return (
    <section className="glass-card overview-card">
      <div className="card-eyebrow">
        <span className="eyebrow-icon">🪪</span> Agent overview
      </div>

      <div className="overview-avatar-row">
        <div className="overview-avatar">
          {(persona?.name || 'AI').slice(0, 2).toUpperCase()}
          <span className={'overview-status-ring' + (isAutonomous ? ' live' : '')} />
        </div>
        <div>
          <h3 className="overview-name">{persona?.name || 'AIRA'}</h3>
          <p className="overview-role">Autonomous AI Security Researcher</p>
        </div>
      </div>

      <dl className="overview-facts">
        <div className="overview-fact">
          <dt>Domain</dt>
          <dd>{persona?.domain || 'AI Security'}</dd>
        </div>
        <div className="overview-fact">
          <dt>Status</dt>
          <dd className={isAutonomous ? 'status-live' : 'status-idle'}>
            <span className="status-glow" />
            {isAutonomous ? 'Autonomous' : 'Standby'}
          </dd>
        </div>
        <div className="overview-fact">
          <dt>Posts published</dt>
          <dd>{postCount}</dd>
        </div>
      </dl>
    </section>
  )
}
