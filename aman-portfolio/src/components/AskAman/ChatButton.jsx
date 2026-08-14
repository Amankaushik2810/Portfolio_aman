function ChatButton({ isOpen, onClick, triggerRef }) {
  return (
    <button
      ref={triggerRef}
      className={`ask-aman-button ${isOpen ? 'ask-aman-button-open' : ''}`}
      type="button"
      aria-label={isOpen ? 'Close Ask Aman assistant' : 'Open Ask Aman assistant'}
      aria-expanded={isOpen}
      aria-controls="ask-aman-dialog"
      onClick={onClick}
    >
      <span className="ask-aman-button-icon" aria-hidden="true">
        {isOpen ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="m6 6 12 12M18 6 6 18" /></svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3a8.5 8.5 0 0 0-8.5 8.5c0 2.1.77 4.02 2.04 5.49L5 21l4.23-1.52A8.5 8.5 0 1 0 12 3Z" /><path d="M8.5 12h.01M12 12h.01M15.5 12h.01" strokeWidth="2.5" /></svg>
        )}
      </span>
      <span className="ask-aman-button-label">{isOpen ? 'Close' : 'Ask Aman'}</span>
      {!isOpen && <span className="ask-aman-button-ping" aria-hidden="true" />}
    </button>
  )
}

export default ChatButton
