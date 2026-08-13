import { useEffect, useRef } from 'react'
import Tag from '../common/Tag.jsx'
import ProjectArchitecture from './ProjectArchitecture.jsx'
import ProjectLinks from './ProjectLinks.jsx'

function ProjectModal({ project, onClose }) {
  const closeButtonRef = useRef(null)
  const modalRef = useRef(null)
  const returnFocusRef = useRef(null)

  useEffect(() => {
    if (!project) return undefined
    returnFocusRef.current = document.activeElement
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const frameId = window.requestAnimationFrame(() => closeButtonRef.current?.focus())

    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose()
        return
      }

      if (event.key !== 'Tab') return
      const focusableElements = [...modalRef.current.querySelectorAll('a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])')]
      if (focusableElements.length === 0) return
      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault()
        lastElement.focus()
      } else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault()
        firstElement.focus()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
      window.cancelAnimationFrame(frameId)
      returnFocusRef.current?.focus?.()
    }
  }, [project, onClose])

  if (!project) return null

  const details = [
    ['Problem', project.caseStudy.problem],
    ['Solution', project.caseStudy.solution],
    ['Challenges', project.caseStudy.challenges],
    ['Lessons learned', project.caseStudy.lessonsLearned],
  ]

  return (
    <div className="project-modal-backdrop" onMouseDown={onClose} role="presentation">
      <section className="project-modal" aria-modal="true" aria-describedby="project-modal-overview" aria-labelledby="project-modal-title" ref={modalRef} role="dialog" onMouseDown={(event) => event.stopPropagation()}>
        <button className="project-modal-close" ref={closeButtonRef} type="button" onClick={onClose} aria-label="Close case study">{'×'}</button>
        <p className="project-category">{project.type}</p>
        <h2 className="mt-3 font-display text-[clamp(2rem,5vw,3.6rem)] font-semibold leading-tight tracking-[-0.05em]" id="project-modal-title">{project.title}</h2>
        {project.visual.image && <div className="project-modal-logo-frame"><img src={project.visual.image} width="1200" height="700" loading="lazy" decoding="async" alt={project.visual.imageAlt || `${project.title} project preview`} /></div>}
        <div className="project-modal-content">
          <article><h3>Overview</h3><p id="project-modal-overview">{project.caseStudy.overview}</p></article>
          <article><h3>Main features</h3><ul>{project.features.map((feature) => <li key={feature}>{feature}</li>)}</ul></article>
          <article><h3>Technology</h3><div className="flex flex-wrap gap-2">{project.stack.map((item) => <Tag key={item}>{item}</Tag>)}</div></article>
          <article><h3>Architecture / workflow</h3><ProjectArchitecture architecture={project.caseStudy.architecture} /></article>
          {details.map(([title, value]) => <article key={title}><h3>{title}</h3><p className={value.startsWith('CASE_STUDY') ? 'case-study-placeholder' : ''}>{value}</p></article>)}
          <ProjectLinks links={project.links} variant="modal" />
          <button className="modal-bottom-close" type="button" onClick={onClose}>Close Case Study</button>
        </div>
      </section>
    </div>
  )
}

export default ProjectModal
