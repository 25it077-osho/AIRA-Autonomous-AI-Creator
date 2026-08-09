import { useCallback, useEffect, useRef, useState } from 'react'
import {
  initializeAgent,
  getFeed,
  saveAgentId,
  loadAgentId,
  clearAgentId,
  savePersona,
  loadPersona,
  ApiError,
} from '../services/api.js'

const FEED_REFRESH_MS = 15000

/**
 * Owns the agent's lifecycle: initialization, agentId persistence in
 * localStorage, and periodic feed polling using the exact backend agentId.
 */
export function useAgent() {
  const [agentId, setAgentId] = useState(() => loadAgentId())
  const [persona, setPersona] = useState(() => loadPersona())

  const [initStatus, setInitStatus] = useState('idle') // idle | pending | error
  const [initError, setInitError] = useState(null)

  const [posts, setPosts] = useState([])
  const [feedStatus, setFeedStatus] = useState('idle') // idle | loading | ready | error
  const [feedError, setFeedError] = useState(null)
  const [lastFetchedAt, setLastFetchedAt] = useState(null)
  const [nextCycleAt, setNextCycleAt] = useState(() => new Date(Date.now() + 6 * 60 * 1000))

  const pollRef = useRef(null)

  const resetCycleTimer = useCallback(() => {
    setNextCycleAt(new Date(Date.now() + 6 * 60 * 1000))
  }, [])

  const fetchFeed = useCallback(async (id) => {
    if (!id) return
    setFeedStatus((prev) => (prev === 'ready' ? 'ready' : 'loading'))
    try {
      const fetchedPosts = await getFeed(id)
      setPosts(fetchedPosts)
      setFeedStatus('ready')
      setFeedError(null)
      setLastFetchedAt(new Date())
    } catch (err) {
      setFeedStatus('error')
      setFeedError(err instanceof ApiError ? err : new ApiError('Unexpected error loading the feed.'))
    }
  }, [])

  // Start / restart polling whenever we have an agentId
  useEffect(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
    if (!agentId) return

    fetchFeed(agentId)
    pollRef.current = setInterval(() => fetchFeed(agentId), FEED_REFRESH_MS)

    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [agentId, fetchFeed])

  const initAgent = useCallback(async (personaInput) => {
    setInitStatus('pending')
    setInitError(null)
    try {
      const id = await initializeAgent(personaInput)
      saveAgentId(id)
      savePersona(personaInput)
      setPersona(personaInput)
      setAgentId(id)
      setInitStatus('idle')
      resetCycleTimer()
    } catch (err) {
      setInitStatus('error')
      setInitError(err instanceof ApiError ? err : new ApiError('Unexpected error initializing the agent.'))
    }
  }, [resetCycleTimer])

  const resetAgent = useCallback(() => {
    clearAgentId()
    setAgentId(null)
    setPersona(null)
    setPosts([])
    setFeedStatus('idle')
    setFeedError(null)
  }, [])

  const refreshNow = useCallback(() => {
    if (!agentId) return
    fetchFeed(agentId)
    resetCycleTimer()
  }, [agentId, fetchFeed, resetCycleTimer])

  return {
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
  }
}
