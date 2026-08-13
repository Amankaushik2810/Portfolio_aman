import RevealOnScroll from '../common/RevealOnScroll.jsx'
import Container from '../layout/Container.jsx'
import EducationCard from './EducationCard.jsx'
import SectionHeading from './SectionHeading.jsx'

function Education({ education }) { return <section className="section-space" id="education" aria-labelledby="education-title"><Container><RevealOnScroll><SectionHeading eyebrow="Academic Journey" title="Education that built my foundation" titleId="education-title" description="A journey from foundational academics to software engineering, application development and intelligent technologies." /></RevealOnScroll><RevealOnScroll className="education-timeline mt-10" stagger threshold={0.1}>{education.map((item, index) => <div className="education-timeline-item" key={item.id} style={{ '--stagger-index': index }}><span className="education-marker" aria-hidden="true" /><EducationCard item={item} /></div>)}</RevealOnScroll></Container></section> }
export default Education
