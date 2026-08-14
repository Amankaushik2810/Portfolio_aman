const API_PATH = '/api/ask'
const APPROVED_LINK_HOSTS = new Set(['play.google.com', 'github.com', 'linkedin.com'])
const SUPPORTED_LINK_TYPES = new Set(['play_store', 'github', 'linkedin'])

export class AskAmanApiError extends Error {
  constructor(kind) {
    super(kind)
    this.kind = kind
  }
}

function errorKindForResponse(response, payload) {
  const code = backendErrorCode(payload)
  if (response.status === 422 || code === 'invalid_question') return 'validation'
  if (response.status === 429 || code === 'gemini_quota_exhausted' || code === 'rate_limited') return 'quota'
  if (response.status === 504 || code === 'gemini_timeout') return 'timeout'
  if (code === 'information_unavailable') return 'unavailable'
  if (code === 'index_unavailable' || code === 'retrieval_unavailable') return 'index'
  return 'server'
}

function backendErrorCode(payload) {
  if (typeof payload?.error?.code === 'string') return payload.error.code
  if (typeof payload?.code === 'string') return payload.code
  const detail = typeof payload?.detail === 'string' ? payload.detail : ''
  const message = typeof payload?.message === 'string' ? payload.message : ''
  const fallback = detail || message
  if (/quota|rate.limit|resource.exhausted/i.test(fallback)) return 'gemini_quota_exhausted'
  if (/timeout|timed.out/i.test(fallback)) return 'gemini_timeout'
  return ''
}

function logLocalFailure(status, code) {
  if (import.meta.env.DEV) {
    console.warn('[Ask Aman] request failed', { status, code: code || 'unstructured_error' })
  }
}

function sanitizeSources(sources) {
  if (!Array.isArray(sources)) return []
  return sources
    .filter((source) => source && typeof source.title === 'string' && typeof source.section === 'string')
    .slice(0, 3)
    .map((source) => ({ title: source.title.trim(), section: source.section.trim() }))
    .filter((source) => source.title && source.section)
}

function sanitizeSuggestions(suggestions) {
  if (!Array.isArray(suggestions)) return []
  return suggestions
    .filter((suggestion) => typeof suggestion === 'string')
    .map((suggestion) => suggestion.trim())
    .filter(Boolean)
    .slice(0, 3)
}

function sanitizeLinks(links) {
  if (!Array.isArray(links)) return []
  return links
    .filter((link) => link && typeof link.label === 'string' && typeof link.url === 'string' && typeof link.type === 'string')
    .map((link) => {
      try {
        const parsed = new URL(link.url)
        if (parsed.protocol !== 'https:' || !APPROVED_LINK_HOSTS.has(parsed.hostname.toLowerCase()) || !SUPPORTED_LINK_TYPES.has(link.type)) return null
        return { label: link.label.trim(), url: parsed.href, type: link.type }
      } catch {
        return null
      }
    })
    .filter((link) => link?.label)
    .slice(0, 3)
}

export async function askAmanApi(question, history, signal) {
  let response
  try {
    response = await fetch(API_PATH, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, history }),
      signal,
    })
  } catch (error) {
    if (error?.name === 'AbortError') throw error
    const kind = navigator.onLine === false ? 'offline' : 'server'
    logLocalFailure(0, kind)
    throw new AskAmanApiError(kind)
  }

  let payload = null
  try {
    payload = await response.json()
  } catch {
    const kind = response.ok ? 'server' : errorKindForResponse(response, null)
    logLocalFailure(response.status, 'non_json_response')
    throw new AskAmanApiError(kind)
  }

  if (!response.ok) {
    const code = backendErrorCode(payload)
    logLocalFailure(response.status, code)
    throw new AskAmanApiError(errorKindForResponse(response, payload))
  }
  if (!payload || typeof payload.answer !== 'string' || !payload.answer.trim()) {
    logLocalFailure(response.status, 'malformed_success_response')
    throw new AskAmanApiError('server')
  }

  return {
    answer: payload.answer.trim(),
    sources: sanitizeSources(payload.sources),
    links: sanitizeLinks(payload.links),
    suggestions: sanitizeSuggestions(payload.suggestions),
    intent: typeof payload.intent === 'string' ? payload.intent : 'general',
  }
}
