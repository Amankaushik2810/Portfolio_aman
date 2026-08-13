import Container from '../layout/Container.jsx'
import RevealOnScroll from '../common/RevealOnScroll.jsx'
import SectionHeading from './SectionHeading.jsx'

function BeyondCode({ content }) {
  return (
    <section className="section-space" aria-labelledby="beyond-code-title">
      <Container>
        <div className="grid gap-8 lg:grid-cols-[1fr_0.92fr] lg:items-center lg:gap-16">
          <RevealOnScroll>
            <SectionHeading eyebrow={content.eyebrow} title={content.heading} description={content.story} />
            <p className="beyond-code-pull-quote">{content.pullQuote}</p>
            <p className="beyond-code-tech-tag">{content.technologyLine}</p>
          </RevealOnScroll>

          <RevealOnScroll delay={100}>
            <article className="poetry-card">
              <svg className="poetry-quote-mark" aria-hidden="true" viewBox="0 0 120 90"><path d="M11 75c0-27 11-47 34-60l10 13c-11 8-17 16-18 25 15 0 25 8 25 21 0 12-8 20-20 20C19 94 11 87 11 75Zm54 0c0-27 11-47 34-60l10 13c-11 8-17 16-18 25 15 0 25 8 25 21 0 12-8 20-20 20-13 0-21-7-21-19Z" fill="currentColor"/></svg>
              <p className="poetry-card-kicker">Poetic Pebbles / Creative note</p>
              <p className="poetry-excerpt">{content.excerpt}</p>
              <p className="poetry-excerpt-label">{content.excerptLabel}</p>
            </article>
          </RevealOnScroll>
        </div>
      </Container>
    </section>
  )
}

export default BeyondCode
