import Container from '../layout/Container.jsx'
import RevealOnScroll from '../common/RevealOnScroll.jsx'

function CredibilityStrip({ items }) {
  return (
    <section className="relative z-10" aria-label="Professional highlights">
      <Container>
        <RevealOnScroll>
          <div className="credibility-strip">
            {items.map((item) => (
              <div className="credibility-item" key={item.id}>
                <span aria-hidden="true" />
                <p>{item.label}</p>
              </div>
            ))}
          </div>
        </RevealOnScroll>
      </Container>
    </section>
  )
}

export default CredibilityStrip
