import './LiveActivity.css'

export default function LiveActivity({ events, active }) {
  return (
    <section className="glass-card activity-card">
      <div className="card-eyebrow">
        <span className="eyebrow-icon">📡</span> Live activity
        <span className={'activity-live-tag' + (active ? ' on' : '')}>
          {active ? 'live' : 'paused'}
        </span>
      </div>

      {events.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">🌙</span>
          <h4>Quiet for now</h4>
          <p>AIRA's autonomous activity will stream here once the agent is running.</p>
        </div>
      ) : (
        <ul className="activity-timeline">
          {events.map((event, i) => (
            <li key={event.id} className={'activity-item type-' + event.type} style={{ '--i': i }}>
              <span className="activity-icon">{event.icon}</span>
              <div className="activity-text">
                <span className="activity-label">{event.label}</span>
                <span className="activity-time mono">{formatTime(event.at)}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function formatTime(date) {
  return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
