function TypingIndicator() {
  return (
    <div className="ask-aman-typing" role="status" aria-label="Ask Aman is composing an answer">
      <span className="ask-aman-message-avatar" aria-hidden="true">A</span>
      <span className="ask-aman-typing-dots" aria-hidden="true"><i /><i /><i /></span>
    </div>
  )
}

export default TypingIndicator
