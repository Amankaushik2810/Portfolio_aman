import Tag from '../common/Tag.jsx'
import RevealOnScroll from '../common/RevealOnScroll.jsx'

function ExperienceCard({ experience }) {
  return (
    <article className="experience-card" aria-labelledby={`experience-role-${experience.id}`}>
      <div className="experience-card-header">
        <div>
          <h3 className="font-display text-[clamp(1.5rem,3vw,2.25rem)] font-semibold tracking-[-0.045em]" id={`experience-role-${experience.id}`}>
            {experience.role}
          </h3>
          <p className="mt-4 text-base font-semibold text-portfolio-text sm:text-lg">{experience.company}</p>
          <p className="parent-company-label">{experience.parentCompany}</p>
        </div>
        {experience.current && <span className="current-role-badge"><i aria-hidden="true" />Current Role</span>}
      </div>

      <div className="experience-metadata" aria-label="Role details">
        <p>{experience.startDate} <span aria-hidden="true">{'\u2013'}</span> {experience.endDate}</p>
        <span aria-hidden="true" />
        <p>{experience.location}</p>
      </div>

      <p className="experience-summary">{experience.summary}</p>

      <div className="mt-8 border-t border-portfolio-border pt-7">
        <h4 className="text-sm font-semibold text-portfolio-text">Core responsibilities</h4>
        <RevealOnScroll className="experience-responsibility-grid mt-5" stagger threshold={0.1}>
          {experience.responsibilities.map((responsibility, index) => (
            <p key={responsibility} style={{ '--stagger-index': index }}><span aria-hidden="true">{'\u2197'}</span>{responsibility}</p>
          ))}
        </RevealOnScroll>
      </div>

      <div className="mt-8 border-t border-portfolio-border pt-7">
        <h4 className="text-sm font-semibold text-portfolio-text">Technologies and focus</h4>
        <div className="mt-4 flex flex-wrap gap-2">
          {experience.skills.map((skill) => <Tag key={skill}>{skill}</Tag>)}
        </div>
      </div>
    </article>
  )
}

export default ExperienceCard
