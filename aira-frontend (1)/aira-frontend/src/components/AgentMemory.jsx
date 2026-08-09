import './AgentMemory.css'

export default function AgentMemory({ topics, feedStatus }) {
  return (
    <section className="glass-card memory-card">
      <div className="card-eyebrow">
        <span className="eyebrow-icon">💾</span> Agent memory
      </div>

      {topics.length === 0 ? (
        <div className="empty-state memory-empty">
          <span className="empty-icon">🗂️</span>
          <h4>No memory yet</h4>
          <p>
            {feedStatus === 'loading'
              ? 'Loading previously published topics…'
              : 'Once AIRA publishes posts, their topics will appear here so future cycles avoid repeating them.'}
          </p>
        </div>
      ) : (
        <>
          <p className="memory-caption">Previously published</p>
          <ul className="memory-list">
            {topics.map((topic, i) => (
              <li key={i} className="memory-item">
                <span className="memory-index mono">{String(i + 1).padStart(2, '0')}</span>
                <span className="memory-topic">{topic}</span>
              </li>
            ))}
          </ul>
          <p className="memory-note">
            Memory prevents AIRA from re-covering the same ground — each new cycle is checked
            against this list before a topic is selected.
          </p>
        </>
      )}
    </section>
  )
}
