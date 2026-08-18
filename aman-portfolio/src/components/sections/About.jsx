import RevealOnScroll from '../common/RevealOnScroll.jsx'
import StatCard from '../common/StatCard.jsx'
import Container from '../layout/Container.jsx'
import SectionHeading from './SectionHeading.jsx'
import BeyondCode from './BeyondCode.jsx'

function About({ content, beyondCode }) {
  return (<>
    <section className="section-space" id="about" aria-labelledby="about-title">
      <Container>
        <div className="grid gap-8 lg:grid-cols-[0.82fr_1.18fr] lg:gap-14">
          <RevealOnScroll>
            <SectionHeading eyebrow={content.eyebrow} title={content.heading} titleId="about-title" description={content.copy} />
            <blockquote className="about-pull-quote">{content.pullQuote}</blockquote>
          </RevealOnScroll>

          <RevealOnScroll delay={100}>
            <aside className="ai-workflow-card" aria-label="Product engineering workflow">
              <div className="ai-workflow-topline">
                <span>AI workflow</span>
                <i aria-hidden="true" />
              </div>
              <div className="ai-workflow-steps">
                {content.workflow.map((step, index) => (
                  <div className="ai-workflow-step" key={step}>
                    <span>{String(index + 1).padStart(2, '0')}</span>
                    <p>{step}</p>
                  </div>
                ))}
              </div>
              <div className="ai-workflow-line" aria-hidden="true"><span /><span /><span /></div>
            </aside>
          </RevealOnScroll>
        </div>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {content.informationCards.map((item, index) => (
            <RevealOnScroll delay={(index + 1) * 70} key={item.id}>
              <StatCard item={item} />
            </RevealOnScroll>
          ))}
        </div>

        <RevealOnScroll delay={120} className="mt-4">
          <article className="what-i-bring-card">
            <p className="eyebrow">What I bring</p>
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              {content.whatIBring.map((item) => (
                <p className="what-i-bring-item" key={item}><span aria-hidden="true">↗</span>{item}</p>
              ))}
            </div>
          </article>
        </RevealOnScroll>
      </Container>
    </section>
    <BeyondCode content={beyondCode} />
  </>)
}

export default About
