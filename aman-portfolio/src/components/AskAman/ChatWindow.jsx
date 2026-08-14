import { useEffect, useRef } from 'react'
import ChatHeader from './ChatHeader.jsx'
import ChatMessage from './ChatMessage.jsx'
import SuggestedQuestions from './SuggestedQuestions.jsx'
import TypingIndicator from './TypingIndicator.jsx'

function ChatWindow({ input, isCoolingDown, isOpen, messages, onClose, onInputChange, onRetry, onSend, onSuggestion, status, suggestions }) {
  const panelRef = useRef(null)
  const inputRef = useRef(null)
  const messageEndRef = useRef(null)
  const canSend = input.trim().length > 0 && input.length <= 300 && status.kind !== 'loading' && !isCoolingDown
  const characterCountClass = input.length > 270 ? 'ask-aman-counter-warning' : ''

  useEffect(() => {
    if (!isOpen) return undefined
    const frame = window.requestAnimationFrame(() => inputRef.current?.focus())
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose()
        return
      }
      if (event.key !== 'Tab') return
      const focusable = [...panelRef.current.querySelectorAll('button:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex="-1"])')]
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (!first || !last) return
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.cancelAnimationFrame(frame)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, onClose])

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, status.kind])

  const handleSubmit = (event) => {
    event.preventDefault()
    if (canSend) onSend(input)
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      if (canSend) onSend(input)
    }
  }

  return (
    <div className={`ask-aman-backdrop ${isOpen ? 'ask-aman-backdrop-open' : ''}`} onMouseDown={onClose}>
      <section
        className={`ask-aman-window ${isOpen ? 'ask-aman-window-open' : ''}`}
        id="ask-aman-dialog"
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="ask-aman-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <ChatHeader onClose={onClose} />
        <div className="ask-aman-conversation" aria-live="polite" aria-relevant="additions text">
          {messages.map((message) => <ChatMessage key={message.id} message={message} />)}
          {status.kind === 'loading' && <TypingIndicator />}
          {status.kind !== 'idle' && status.kind !== 'loading' && (
            <div className={`ask-aman-notice ask-aman-notice-${status.kind}`} role="status">
              <span aria-hidden="true">{status.kind === 'quota' ? '◷' : '!'}</span>
              <p>{status.message}</p>
              <button type="button" disabled={isCoolingDown} onClick={onRetry}>Try again</button>
            </div>
          )}
          <span ref={messageEndRef} />
        </div>
        <SuggestedQuestions
          questions={suggestions}
          disabled={status.kind === 'loading' || isCoolingDown}
          onSelect={onSuggestion}
        />
        <form className="ask-aman-composer" onSubmit={handleSubmit}>
          <label className="sr-only" htmlFor="ask-aman-input">Ask a question about Aman</label>
          <textarea
            id="ask-aman-input"
            ref={inputRef}
            rows="1"
            maxLength="300"
            value={input}
            onChange={(event) => onInputChange(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about experience, skills, or projects..."
            aria-describedby="ask-aman-counter"
            disabled={status.kind === 'loading'}
          />
          <div className="ask-aman-composer-footer">
            <span className={`ask-aman-counter ${characterCountClass}`} id="ask-aman-counter">{input.length}/300</span>
            <button className="ask-aman-send" type="submit" disabled={!canSend} aria-label="Send question">
              <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m4 4 16 8-16 8 3-8-3-8Z" /><path d="M7 12h13" /></svg>
              <span>Send</span>
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

export default ChatWindow
