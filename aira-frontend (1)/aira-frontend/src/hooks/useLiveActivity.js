import { useEffect, useRef, useState } from 'react'

// This hook only drives *visual* presentation — a decorative activity
// ticker and the counters shown in the Editorial Intelligence panel. It
// does not discover topics, decide anything, or generate content. Once the
// real backend exposes an activity/analytics endpoint, this can be swapped
// for a fetch + poll of that endpoint without touching any component.

const CYCLE = [
  { type: 'discover', icon: '🔍', label: 'Discovering AI security topics' },
  { type: 'evaluate', icon: '🧠', label: 'Evaluating topic relevance' },
  { type: 'reject', icon: '❌', label: 'Rejecting repetitive topic' },
  { type: 'select', icon: '✅', label: 'Selecting high-value topic' },
  { type: 'generate', icon: '✍️', label: 'Generating post' },
  { type: 'memory', icon: '💾', label: 'Updating memory' },
  { type: 'publish', icon: '📡', label: 'Publishing to feed' },
]

const TICK_MS = 3200

export function useLiveActivity(active) {
  const [events, setEvents] = useState([])
  const [stats, setStats] = useState({ discovered: 0, evaluated: 0, rejected: 0, published: 0 })
  const cursorRef = useRef(0)

  useEffect(() => {
    if (!active) return undefined

    const tick = () => {
      const step = CYCLE[cursorRef.current % CYCLE.length]
      cursorRef.current += 1

      const entry = { ...step, id: `${Date.now()}-${cursorRef.current}`, at: new Date() }
      setEvents((prev) => [entry, ...prev].slice(0, 8))

      setStats((prev) => {
        const next = { ...prev }
        if (step.type === 'discover') next.discovered += 1
        if (step.type === 'evaluate') next.evaluated += 1
        if (step.type === 'reject') next.rejected += 1
        if (step.type === 'publish') next.published += 1
        return next
      })
    }

    tick()
    const id = setInterval(tick, TICK_MS)
    return () => clearInterval(id)
  }, [active])

  return { events, stats }
}
