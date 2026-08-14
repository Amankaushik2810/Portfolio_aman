function SuggestedQuestions({ questions, disabled, onSelect }) {
  return (
    <section className="ask-aman-suggestions" aria-label="Suggested questions">
      <p>Try asking</p>
      <div>
        {questions.map((question) => (
          <button className="ask-aman-chip" type="button" key={question} disabled={disabled} onClick={() => onSelect(question)}>
            {question}
          </button>
        ))}
      </div>
    </section>
  )
}

export default SuggestedQuestions
