import PostCard from './PostCard.jsx'
import './Feed.css'

export default function Feed({ posts, status, error, agentName, onRetry }) {
  return (
    <section className="feed-section">
      <div className="feed-header">
        <div>
          <h2 className="section-title">Autonomous feed</h2>
          <p className="feed-subtitle">Posts {agentName || 'AIRA'} has published on its own, most recent first.</p>
        </div>
        {status === 'ready' ? <span className="pill pill-live">{posts.length} live</span> : null}
      </div>

      {status === 'loading' && posts.length === 0 ? <FeedSkeleton /> : null}

      {status === 'error' ? <FeedError error={error} onRetry={onRetry} /> : null}

      {status === 'ready' && posts.length === 0 ? <FeedEmpty /> : null}

      {posts.length > 0 ? (
        <div className="feed-list">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} agentName={agentName} />
          ))}
        </div>
      ) : null}
    </section>
  )
}

function FeedSkeleton() {
  return (
    <div className="feed-list">
      {[0, 1, 2].map((i) => (
        <div className="glass-card post-card skeleton" key={i}>
          <div className="skeleton-line w-40" />
          <div className="skeleton-line w-90" />
          <div className="skeleton-line w-70" />
          <div className="skeleton-line w-50" />
        </div>
      ))}
    </div>
  )
}

function FeedError({ error, onRetry }) {
  const isNetwork = error?.kind === 'network'
  return (
    <div className="glass-card feed-state-card">
      <div className="empty-state">
        <span className="empty-icon">{isNetwork ? '🔌' : '⚠️'}</span>
        <h4>{isNetwork ? 'Backend unavailable' : "Couldn't load the feed"}</h4>
        <p>
          {isNetwork
            ? 'AIRA could not reach the backend at http://localhost:8000. Make sure the FastAPI server is running.'
            : error?.message || 'Something went wrong while fetching the latest posts.'}
        </p>
        <button className="btn btn-sm" onClick={onRetry}>
          Try again
        </button>
      </div>
    </div>
  )
}

function FeedEmpty() {
  return (
    <div className="glass-card feed-state-card">
      <div className="empty-state">
        <span className="empty-icon">📭</span>
        <h4>No posts yet</h4>
        <p>AIRA hasn't published anything on this cycle. Check back shortly — new posts appear automatically.</p>
      </div>
    </div>
  )
}
