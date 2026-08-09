import './EditorialIntelligence.css'

export default function EditorialIntelligence({ stats, publishedCount }) {
  const rows = [
    { key: 'discovered', label: 'Discovered', value: stats.discovered, color: 'var(--accent-cyan)' },
    { key: 'evaluated', label: 'Evaluated', value: stats.evaluated, color: 'var(--accent-violet)' },
    { key: 'rejected', label: 'Rejected', value: stats.rejected, color: 'var(--accent-rose)' },
    { key: 'published', label: 'Published', value: publishedCount, color: 'var(--accent-green)' },
  ]
  const max = Math.max(1, ...rows.map((r) => r.value))

  return (
    <section className="glass-card editorial-card">
      <div className="card-eyebrow">
        <span className="eyebrow-icon">📊</span> Editorial intelligence
      </div>

      <div className="editorial-stats">
        {rows.map((r) => (
          <div className="editorial-stat" key={r.key}>
            <span className="editorial-stat-value mono">{r.value}</span>
            <span className="editorial-stat-label">{r.label}</span>
          </div>
        ))}
      </div>

      <div className="editorial-chart" role="img" aria-label="Bar chart of topics discovered, evaluated, rejected and published">
        {rows.map((r) => (
          <div className="editorial-bar-row" key={r.key}>
            <span className="editorial-bar-label">{r.label}</span>
            <div className="editorial-bar-track">
              <div
                className="editorial-bar-fill"
                style={{ width: `${(r.value / max) * 100}%`, background: r.color }}
              />
            </div>
            <span className="editorial-bar-value mono">{r.value}</span>
          </div>
        ))}
      </div>

      <p className="editorial-note">This session's discovery pipeline, updating live as AIRA works.</p>
    </section>
  )
}
