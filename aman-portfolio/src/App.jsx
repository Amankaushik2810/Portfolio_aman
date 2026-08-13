import Tag from './components/common/Tag.jsx'
import Container from './components/layout/Container.jsx'
import BackToTop from './components/layout/BackToTop.jsx'
import CursorGlow from './components/layout/CursorGlow.jsx'
import Footer from './components/layout/Footer.jsx'
import Navbar from './components/layout/Navbar.jsx'
import PageIntro from './components/layout/PageIntro.jsx'
import About from './components/sections/About.jsx'
import BackgroundEffects from './components/layout/BackgroundEffects.jsx'
import Contact from './components/sections/Contact.jsx'
import Experience from './components/sections/Experience.jsx'
import Education from './components/sections/Education.jsx'
import Hero from './components/sections/Hero.jsx'
import Projects from './components/sections/Projects.jsx'
import SectionHeading from './components/sections/SectionHeading.jsx'
import RevealOnScroll from './components/common/RevealOnScroll.jsx'
import { experiences } from './data/experience.js'
import { education } from './data/education.js'
import profile from './data/profile.js'
import projects from './data/projects.js'
import skillCategories from './data/skills.js'

function App() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-portfolio-bg text-portfolio-text">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <BackgroundEffects />
      <PageIntro />
      <CursorGlow />
      <Navbar />
      <main className="relative z-10" id="main-content" tabIndex="-1">
        <Hero profile={profile} />
        <About content={profile.about} beyondCode={profile.beyondCode} />
        <Education education={education} />

        <Container>
          <section className="section-space" id="skills" aria-labelledby="skills-title">
            <SectionHeading eyebrow="Capabilities" title="A practical toolkit for intelligent products." description="Focused on building useful AI systems and shipping the interfaces around them." />
            <RevealOnScroll className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3" stagger>
              {skillCategories.map((category, index) => (
                <article className="design-card skill-card p-6" key={category.id} style={{ '--stagger-index': index }}>
                  <h3 className="font-display text-xl font-semibold tracking-[-0.03em]">{category.name}</h3>
                  <div className="mt-5 flex flex-wrap gap-2">{category.skills.map((skill) => <Tag key={skill}>{skill}</Tag>)}</div>
                </article>
              ))}
            </RevealOnScroll>
          </section>
        </Container>
        <Projects projects={projects} profile={profile} />
        <Experience experiences={experiences} />
        <Contact contact={profile.contact} content={profile.contactContent} />
      </main>
      <Footer />
      <BackToTop />
    </div>
  )
}

export default App
