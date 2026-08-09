import './PersonaPanel.css'

const PRINCIPLES = [
  'Security impact over hype',
  'Technical substance over buzzwords',
  'Prefer emerging developments',
  'Avoid repetitive news',
  'Explain why developments matter',
  'Focus exclusively on AI and technology',
]

export default function PersonaPanel({ persona }) {
  return (
    <section className="glass-card persona-card">
      <div className="card-eyebrow">
        <span className="eyebrow-icon">🎙️</span> Persona
      </div>

      <h3 className="persona-name">{persona?.name || 'AIRA'}</h3>
      <p className="persona-role">Autonomous AI Security Researcher</p>

      <p className="persona-label">Editorial principles</p>
      <ul className="persona-principles">
        {PRINCIPLES.map((p) => (
          <li key={p}>
            <span className="principle-mark">•</span> {p}
          </li>
        ))}
      </ul>
    </section>
  )
}
