import { useCallback, useRef, useState } from 'react'
import ChatButton from './ChatButton.jsx'
import ChatWindow from './ChatWindow.jsx'
import { useAskAman } from './useAskAman.js'

function AskAman() {
  const [isOpen, setIsOpen] = useState(false)
  const [input, setInput] = useState('')
  const triggerRef = useRef(null)
  const { isCoolingDown, messages, retryLastQuestion, status, submitQuestion, suggestions } = useAskAman()

  const close = useCallback(() => {
    setIsOpen(false)
    window.setTimeout(() => triggerRef.current?.focus(), 180)
  }, [])

  const sendQuestion = useCallback(async (question) => {
    const submitted = await submitQuestion(question)
    if (submitted) setInput('')
  }, [submitQuestion])

  const open = () => setIsOpen(true)
  const toggle = () => (isOpen ? close() : open())

  return (
    <aside className="ask-aman" aria-label="Ask Aman portfolio assistant">
      {isOpen && <ChatWindow input={input} isCoolingDown={isCoolingDown} isOpen={isOpen} messages={messages} onClose={close} onInputChange={setInput} onRetry={retryLastQuestion} onSend={sendQuestion} onSuggestion={sendQuestion} status={status} suggestions={suggestions} />}
      <ChatButton isOpen={isOpen} onClick={toggle} triggerRef={triggerRef} />
    </aside>
  )
}

export default AskAman
