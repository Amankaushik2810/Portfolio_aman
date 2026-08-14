function ChatMessage({ message }) {
  const isVisitor = message.role === 'visitor'

  return (
    <article className={`ask-aman-message ask-aman-message-${message.role}`}>
      {!isVisitor && <span className="ask-aman-message-avatar" aria-hidden="true">A</span>}
      <div className="min-w-0">
        {!isVisitor && <p className="ask-aman-message-name">Ask Aman</p>}
        <div className="ask-aman-message-bubble">{message.content}</div>
        {!isVisitor && message.links?.length > 0 && (
          <div className="mt-2 flex flex-col gap-2">
            {message.links.map((link) => (
              <a
                className="inline-flex min-h-10 w-fit max-w-full items-center gap-2 rounded-xl border border-cyan-300/30 bg-cyan-300/10 px-3 py-2 text-xs font-bold text-cyan-100 shadow-[0_8px_18px_rgb(34_211_238_/_10%)] transition duration-180 ease-out hover:-translate-y-0.5 hover:border-cyan-300/60 hover:bg-cyan-300/16 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
                href={link.url}
                key={`${link.type}-${link.url}`}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`${link.label} (opens in a new tab)`}
              >
                {link.type === 'play_store' ? (
                  <svg aria-hidden="true" className="h-4 w-4 shrink-0" viewBox="0 0 24 24"><path fill="#34A853" d="m3 3 10.7 9L3 21V3Z" /><path fill="#4285F4" d="m13.7 12 2.8 2.35L6.1 20.3 3 21l10.7-9Z" /><path fill="#FBBC04" d="m3 3 3.1.7 10.4 5.95L13.7 12 3 3Z" /><path fill="#EA4335" d="m16.5 9.65 3.3 1.9c1 .58 1 1.3 0 1.88l-3.3 1.92L13.7 12l2.8-2.35Z" /></svg>
                ) : <span aria-hidden="true">↗</span>}
                <span>{link.label} ↗</span>
              </a>
            ))}
          </div>
        )}
        {!isVisitor && message.sources?.length > 0 && (
          <div className="ask-aman-sources" aria-label="Portfolio sources">
            {message.sources.map((source) => <span className="ask-aman-source" key={`${source.title}-${source.section}`}><i aria-hidden="true" />{source.title}</span>)}
          </div>
        )}
      </div>
    </article>
  )
}

export default ChatMessage
