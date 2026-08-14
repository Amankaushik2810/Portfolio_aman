function ChatHeader({ onClose }) {
  return (
    <header className="ask-aman-header">
      <div className="ask-aman-avatar" aria-hidden="true">A<span>?</span></div>
      <div className="min-w-0">
        <h2 className="font-display text-[1rem] font-semibold tracking-[-0.035em] text-portfolio-text" id="ask-aman-title">Ask Aman</h2>
        <p className="ask-aman-status"><i aria-hidden="true" />Portfolio guide <span>· Grounded answers</span></p>
      </div>
      <button className="ask-aman-icon-button" type="button" aria-label="Minimize Ask Aman" onClick={onClose}>
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M6 12h12" /></svg>
      </button>
    </header>
  )
}

export default ChatHeader
