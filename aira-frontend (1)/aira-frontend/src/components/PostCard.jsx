import { useState } from 'react'

export default function PostCard({ post, agentName }) {
  const [openPanel, setOpenPanel] = useState(null) // null | 'rationale' | 'sources' | 'memory'

  const toggle = (panel) => setOpenPanel((prev) => (prev === panel ? null : panel))

  return (
    <article className="glass-card post-card">
      <div className="post-header">
        <div className="post-avatar">{(agentName || 'AI').slice(0, 2).toUpperCase()}</div>
        <div className="post-header-text">
          <span className="post-author">{agentName || 'AIRA'}</span>
          <span className="post-time mono">{formatDate(post.createdAt)}</span>
        </div>
        <span className="pill post-domain-pill">published</span>
      </div>

      <p className="post-text">{post.text}</p>

      <div className="post-actions">
        <button
          className={'btn btn-sm' + (openPanel === 'rationale' ? ' btn-toggle-on' : '')}
          onClick={() => toggle('rationale')}
        >
          💡 View Rationale
        </button>
        <button
          className={'btn btn-sm' + (openPanel === 'sources' ? ' btn-toggle-on' : '')}
          onClick={() => toggle('sources')}
        >
          🔗 View Sources
        </button>
        <button
          className={'btn btn-sm' + (openPanel === 'memory' ? ' btn-toggle-on' : '')}
          onClick={() => toggle('memory')}
        >
          💾 Memory
        </button>
      </div>

      {openPanel === 'rationale' ? (
        <div className="post-panel">
          <p className="post-panel-label">Why this topic was selected</p>
          <p className="post-panel-body">{post.rationale || 'No rationale was provided for this post.'}</p>
        </div>
      ) : null}

      {openPanel === 'sources' ? (
        <div className="post-panel">
          <p className="post-panel-label">Sources</p>
          {post.sources?.length ? (
            <ul className="post-sources">
              {post.sources.map((src, i) => (
                <li key={i}>
                  <a href={src} target="_blank" rel="noreferrer noopener" className="mono">
                    {src}
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p className="post-panel-body">No sources were attached to this post.</p>
          )}
        </div>
      ) : null}

      {openPanel === 'memory' ? (
        <div className="post-panel">
          <p className="post-panel-label">Agent identity</p>
          <p className="post-panel-body">
            Published by <strong>{agentName || 'AIRA'}</strong>. This topic has been recorded in memory
            so future cycles won't cover the same ground again.
          </p>
        </div>
      ) : null}
    </article>
  )
}

function formatDate(iso) {
  if (!iso) return '—'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
