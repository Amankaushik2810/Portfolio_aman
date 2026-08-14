import { useCallback, useEffect, useRef, useState } from 'react'
import { AskAmanApiError, askAmanApi } from './askAmanApi.js'

// This must exceed the backend provider timeout so the API can return its
// structured timeout error instead of the browser aborting first.
const REQUEST_TIMEOUT_MS = 25_000
const COOLDOWN_MS = 900

const SAFE_ERROR_MESSAGES = {
  offline: 'Please check your internet connection.',
  timeout: 'The response took too long. Please try again.',
  quota: 'Ask Aman has reached its current AI usage limit.',
  index: 'Ask Aman’s knowledge base is temporarily unavailable.',
  unavailable: "That information is not available in Aman's portfolio. Please use the Contact section for a direct question.",
  validation: 'Please enter a question of up to 300 characters.',
  server: 'Ask Aman is unavailable right now.',
}

export const DEFAULT_SUGGESTIONS = [
  'Tell me about Aman',
  'What are his AI/ML skills?',
  'What is Poetic Pebbles?',
  'Tell me about his experience',
  'Show me his projects',
  'How can I contact him?',
]

function makeMessage(role, content, extras = {}) {
  return { id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, role, content, ...extras }
}

export function useAskAman() {
  const [messages, setMessages] = useState([
    makeMessage('assistant', 'Hi, I’m Ask Aman — an AI guide to Aman Kaushik’s portfolio. You can ask me about his experience, education, skills and projects.'),
  ])
  const [status, setStatus] = useState({ kind: 'idle', message: '' })
  const [suggestions, setSuggestions] = useState(DEFAULT_SUGGESTIONS)
  const [isCoolingDown, setIsCoolingDown] = useState(false)
  const activeRequestRef = useRef(null)
  const isRequestActiveRef = useRef(false)
  const historyRef = useRef([])
  const failedQuestionRef = useRef('')
  const cooldownTimerRef = useRef(null)
  const isMountedRef = useRef(true)

  const startCooldown = useCallback(() => {
    window.clearTimeout(cooldownTimerRef.current)
    setIsCoolingDown(true)
    cooldownTimerRef.current = window.setTimeout(() => {
      if (isMountedRef.current) setIsCoolingDown(false)
    }, COOLDOWN_MS)
  }, [])

  const submitQuestion = useCallback(async (rawQuestion, { isRetry = false } = {}) => {
    const question = rawQuestion.trim()
    if (!question || question.length > 300 || isRequestActiveRef.current || isCoolingDown) return false

    if (!isRetry) setMessages((current) => [...current, makeMessage('visitor', question)])
    isRequestActiveRef.current = true
    failedQuestionRef.current = ''
    setStatus({ kind: 'loading', message: '' })

    const controller = new AbortController()
    activeRequestRef.current = controller
    let timedOut = false
    const timeoutId = window.setTimeout(() => {
      timedOut = true
      controller.abort()
    }, REQUEST_TIMEOUT_MS)

    try {
      const response = await askAmanApi(question, historyRef.current.slice(-2), controller.signal)
      if (!isMountedRef.current) return false
      setMessages((current) => [...current, makeMessage('assistant', response.answer, { sources: response.sources, links: response.links })])
      if (response.suggestions.length > 0) setSuggestions(response.suggestions)
      historyRef.current = [...historyRef.current, { question, answer: response.answer }].slice(-2)
      setStatus({ kind: 'idle', message: '' })
      startCooldown()
      return true
    } catch (error) {
      if (!isMountedRef.current || (error?.name === 'AbortError' && !timedOut)) return false
      const kind = timedOut ? 'timeout' : error instanceof AskAmanApiError ? error.kind : 'server'
      failedQuestionRef.current = question
      setStatus({ kind, message: SAFE_ERROR_MESSAGES[kind] || SAFE_ERROR_MESSAGES.server })
      startCooldown()
      return false
    } finally {
      window.clearTimeout(timeoutId)
      if (activeRequestRef.current === controller) activeRequestRef.current = null
      isRequestActiveRef.current = false
    }
  }, [isCoolingDown, startCooldown])

  const retryLastQuestion = useCallback(() => {
    if (!failedQuestionRef.current) return
    submitQuestion(failedQuestionRef.current, { isRetry: true })
  }, [submitQuestion])

  useEffect(() => {
    // React StrictMode remounts effects in development; reset this marker so
    // the real request lifecycle remains functional after that check.
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
      activeRequestRef.current?.abort()
      window.clearTimeout(cooldownTimerRef.current)
    }
  }, [])

  return {
    isCoolingDown,
    messages,
    retryLastQuestion,
    status,
    submitQuestion,
    suggestions,
  }
}
