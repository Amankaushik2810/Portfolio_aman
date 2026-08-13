import { useState } from 'react'
import Tag from '../common/Tag.jsx'
import ProjectLinks from './ProjectLinks.jsx'

function ArrowIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></svg>
}

function ProjectVisual({ project }) {
  const { visual } = project
  const [imageError, setImageError] = useState(false)
  if (visual.image && !imageError) return visual.logo ? <div className="project-logo-frame"><img className="project-logo-image" src={visual.image} width="1200" height="700" loading="lazy" decoding="async" alt={visual.imageAlt} onError={() => setImageError(true)} /></div> : <img className="project-card-image" src={visual.image} width="1200" height="700" sizes="(min-width: 768px) 50vw, 100vw" loading="lazy" decoding="async" alt={visual.imageAlt || `${project.title} project preview`} onError={() => setImageError(true)} />

  return (
    <div className={`project-visual project-visual-${visual.accent}`} aria-label={`${project.title} branded placeholder`} role="img">
      <div className="project-visual-grid" />
      <p>{visual.label}</p>
      <span>{project.title.split(' ').map((word) => word[0]).join('')}</span>
    </div>
  )
}

function ProjectCard({ project, onOpen }) {
  return (
    <article className={`project-card ${project.flagship ? 'project-card-flagship' : ''}`}>
      <div className="project-image-wrap"><ProjectVisual project={project} /></div>
      <div className="project-card-content">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="project-category">{project.type}</p>
          {project.flagship && <span className="flagship-label">Flagship</span>}
        </div>
        <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.04em] sm:text-3xl">{project.title}</h3>
        <p className="mt-4 leading-7 text-portfolio-muted">{project.description}</p>
        <div className="mt-6 flex flex-wrap gap-2">
          {project.stack.map((technology) => <Tag className="project-tag" key={technology}>{technology}</Tag>)}
        </div>
        <div className="mt-7 flex flex-wrap items-center gap-x-5 gap-y-3">
          <button className="case-study-button" type="button" onClick={() => onOpen(project)}>View Case Study <ArrowIcon /></button>
          <ProjectLinks links={project.links} />
        </div>
      </div>
    </article>
  )
}

export default ProjectCard
