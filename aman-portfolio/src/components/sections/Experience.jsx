import Container from '../layout/Container.jsx'
import RevealOnScroll from '../common/RevealOnScroll.jsx'
import ExperienceCard from './ExperienceCard.jsx'
import SectionHeading from './SectionHeading.jsx'

function Experience({ experiences }) {
  return (
    <section className="section-space" id="experience" aria-labelledby="experience-title">
      <Container>
        <RevealOnScroll threshold={0.18}>
          <SectionHeading
            eyebrow="Professional Journey"
            title="Experience that shapes my engineering"
            description="Building intelligent software through hands-on experience with data, machine learning and Generative AI."
          />
        </RevealOnScroll>

        <RevealOnScroll className="experience-timeline-reveal mt-10" delay={90} threshold={0.12}>
          <div className="experience-timeline-layout">
            <div className="experience-timeline-rail" aria-hidden="true"><span /></div>
            <div className="grid gap-5">
              {experiences.map((experience) => <ExperienceCard experience={experience} key={experience.id} />)}
            </div>
          </div>
        </RevealOnScroll>
      </Container>
    </section>
  )
}

export default Experience
