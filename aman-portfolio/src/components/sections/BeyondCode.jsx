import Container from '../layout/Container.jsx'
import RevealOnScroll from '../common/RevealOnScroll.jsx'
import SectionHeading from './SectionHeading.jsx'
import '../../creative-note.css'

function BeyondCode({ content }) {
  return (
    <section className="section-space" aria-labelledby="beyond-code-title">
      <Container>
        <div className="grid gap-8 lg:grid-cols-[1fr_0.92fr] lg:items-center lg:gap-16">
          <RevealOnScroll>
            <SectionHeading eyebrow={content.eyebrow} title={content.heading} titleId="beyond-code-title" description={content.story} />
            <p className="beyond-code-pull-quote">{content.pullQuote}</p>
            <p className="beyond-code-tech-tag">{content.technologyLine}</p>
          </RevealOnScroll>

          <RevealOnScroll delay={100}>
            <article className="poetry-card">
              <header className="poetry-card-header">POETIC PEBBLES / CREATIVE NOTE</header>
              <span className="poetry-card-quote-mark" aria-hidden="true">“</span>
              <span className="poetry-card-sweep" aria-hidden="true" />
              <blockquote className="poetry-excerpt">
                <p>“Between <span className="poetry-word-cyan">logic</span> and <span className="poetry-word-violet">longing</span>,</p>
                <p>I found a space to create—</p>
                <p>where <span className="poetry-word-cyan">code</span> builds the path,</p>
                <p>and <span className="poetry-word-violet">poetry</span> gives it meaning.”</p>
                <footer className="poetry-attribution"><cite>— Aman Kaushik · Poetic Pebbles</cite></footer>
              </blockquote>
            </article>
          </RevealOnScroll>
        </div>
      </Container>
    </section>
  )
}

export default BeyondCode
