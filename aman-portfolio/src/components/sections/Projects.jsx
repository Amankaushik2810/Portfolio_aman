import { useMemo, useState } from 'react'
import RevealOnScroll from '../common/RevealOnScroll.jsx'
import Container from '../layout/Container.jsx'
import ProjectCard from './ProjectCard.jsx'
import ProjectModal from './ProjectModal.jsx'
import SectionHeading from './SectionHeading.jsx'

const filters = ['All', 'AI/ML', 'Generative AI', 'Web', 'Android']

function Projects({ projects, profile }) {
  const [activeFilter, setActiveFilter] = useState('All')
  const [selectedProject, setSelectedProject] = useState(null)
  const filteredProjects = useMemo(() => projects.filter((project) => activeFilter === 'All' || project.categories.includes(activeFilter)), [activeFilter, projects])

  return (
    <section className="section-space" id="projects" aria-labelledby="projects-title">
      <Container>
        <RevealOnScroll>
          <SectionHeading eyebrow="Selected work" title={`Products built by ${profile.name}.`} titleId="projects-title" description="A selection of intelligent systems and product experiences across Android, web, and machine learning." />
          <div className="project-filters" aria-label="Project filters">
            {filters.map((filter) => <button className={activeFilter === filter ? 'project-filter-active' : ''} type="button" aria-pressed={activeFilter === filter} key={filter} onClick={() => setActiveFilter(filter)}>{filter}</button>)}
          </div>
        </RevealOnScroll>
        <div className="project-editorial-grid mt-10" aria-live="polite">
          {filteredProjects.map((project, index) => <RevealOnScroll delay={index * 80} key={project.id}><ProjectCard project={project} onOpen={setSelectedProject} /></RevealOnScroll>)}
        </div>
      </Container>
      <ProjectModal project={selectedProject} onClose={() => setSelectedProject(null)} />
    </section>
  )
}

export default Projects
