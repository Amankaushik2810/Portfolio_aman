import ProjectArchitecture from './ProjectArchitecture.jsx'
import ProjectLinks from './ProjectLinks.jsx'

function NarrativeSection({ title, paragraphs, variant }) {
  return (
    <article className={`pp-narrative pp-narrative-${variant} pp-reveal rounded-3xl p-5 sm:p-7`}>
      <h3 className="pp-heading font-display text-2xl font-semibold tracking-[-0.03em]">{title}</h3>
      <div className="pp-body mt-4 max-w-3xl space-y-4 text-sm leading-7 sm:text-base">
        {paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
      </div>
    </article>
  )
}

function PoeticPebblesCaseStudy({ project }) {
  const { caseStudy } = project

  return (
    <div className="pp-case-study mt-8 space-y-10">
      <section aria-label="Poetic Pebbles project summary" className="pp-summary pp-reveal rounded-3xl p-5 sm:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="pp-kicker text-xs font-semibold uppercase tracking-[0.18em]">Case study</p>
            <h3 className="pp-heading mt-1 font-display text-2xl font-semibold tracking-[-0.03em]">A moderated home for poetry</h3>
          </div>
          <span className="pp-status-badge rounded-full px-3 py-1 text-xs font-semibold">Actively maintained</span>
        </div>
        <p className="pp-body mt-4 max-w-3xl text-sm leading-7 sm:text-base" id="project-modal-overview">{caseStudy.overview}</p>
        <dl className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {caseStudy.summary.map(([label, value], index) => (
            <div className={`pp-stat-card pp-stat-card-${index % 3} rounded-2xl p-3.5`} key={label}>
              <dt className="pp-muted text-[0.68rem] font-bold uppercase tracking-[0.13em]">{label}</dt>
              <dd className="pp-stat-value mt-1.5 text-sm font-semibold leading-5">{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="pp-section pp-reveal">
        <h3 className="pp-heading font-display text-2xl font-semibold tracking-[-0.03em]">Main features</h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {project.features.map((feature) => <span className="pp-feature-tag rounded-full px-3 py-1.5 text-xs font-medium" key={feature}>{feature}</span>)}
        </div>
        <h4 className="pp-muted mt-7 text-sm font-semibold uppercase tracking-[0.14em]">Technology</h4>
        <div className="mt-3 flex flex-wrap gap-2">
          {project.stack.map((item) => <span className="pp-tech-tag rounded-full px-3 py-1.5 text-xs font-medium" key={item}>{item}</span>)}
        </div>
      </section>

      <section className="pp-section pp-reveal">
        <h3 className="pp-heading font-display text-2xl font-semibold tracking-[-0.03em]">Architecture / workflow</h3>
        <ProjectArchitecture architecture={caseStudy.architecture} />
      </section>

      <NarrativeSection title="Problem" paragraphs={caseStudy.problem} variant="problem" />
      <NarrativeSection title="Solution" paragraphs={caseStudy.solution} variant="solution" />

      <section className="pp-section pp-reveal">
        <div className="max-w-3xl">
          <h3 className="pp-heading font-display text-2xl font-semibold tracking-[-0.03em]">Challenges</h3>
          <p className="pp-body mt-3 text-sm leading-7">Four parts of the work that required product as well as technical judgement.</p>
        </div>
        <ol className="mt-6 grid gap-4 lg:grid-cols-2">
          {caseStudy.challenges.map(([title, ...paragraphs], index) => (
            <li className={`pp-challenge-card pp-challenge-card-${index} rounded-2xl p-5`} key={title}>
              <span className="pp-challenge-marker flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold">{index + 1}</span>
              <h4 className="pp-card-heading mt-4 text-base font-semibold">{title}</h4>
              <div className="pp-body mt-3 space-y-3 text-sm leading-6">{paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
            </li>
          ))}
        </ol>
      </section>

      <section className="pp-section pp-reveal">
        <h3 className="pp-heading font-display text-2xl font-semibold tracking-[-0.03em]">Lessons learned</h3>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {caseStudy.lessonsLearned.map(([title, content], index) => (
            <article className="pp-lesson-card rounded-2xl p-5" key={title}>
              <span className="pp-lesson-index text-xs font-bold">0{index + 1}</span>
              <h4 className="pp-card-heading mt-2 text-base font-semibold">{title}</h4>
              <p className="pp-body mt-2 text-sm leading-6">{content}</p>
            </article>
          ))}
        </div>
      </section>

      <div className="pp-section pp-reveal">
        <ProjectLinks links={project.links} variant="modal" />
      </div>
    </div>
  )
}

export default PoeticPebblesCaseStudy
