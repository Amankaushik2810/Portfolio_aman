import PrimaryButton from '../common/PrimaryButton.jsx'
import SecondaryButton from '../common/SecondaryButton.jsx'
import SocialLinks from '../common/SocialLinks.jsx'
import ScrollIndicator from '../common/ScrollIndicator.jsx'
import Container from '../layout/Container.jsx'
import CredibilityStrip from './CredibilityStrip.jsx'
import amanPortrait from '../../assets/images/aman_pic.png'

function Hero({ profile }) {
  const resumeIsReady = profile.contact.resumeUrl && !profile.contact.resumeUrl.startsWith('REPLACE_WITH')

  return (<>
    <section className="hero-section" id="home" aria-labelledby="hero-name">
      <Container className="flex min-h-[100svh] flex-col justify-center pt-28 pb-10 sm:pt-32 lg:pt-24">
        <div className="hero-layout">
          <div className="hero-intro max-w-3xl">
            <p className="availability-badge animate-fade-up"><span aria-hidden="true" />{profile.availability}</p>
            <p className="mt-7 text-sm font-semibold uppercase tracking-[0.2em] text-portfolio-cyan animate-fade-up" style={{ '--delay': '90ms' }}>{profile.name}</p>
            <h1 id="hero-name" className="mt-4 font-display text-[clamp(2.8rem,7vw,5.9rem)] font-semibold leading-[0.98] tracking-[-0.065em] animate-fade-up" style={{ '--delay': '150ms' }}>
              {profile.heroTitle}
            </h1>
            <p className="mt-7 max-w-2xl text-base leading-8 text-portfolio-muted sm:text-lg animate-fade-in" style={{ '--delay': '280ms' }}>
              {profile.brandStatement}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm font-medium text-slate-300 animate-fade-in" style={{ '--delay': '360ms' }}>
              {profile.heroTechnologies.map((technology, index) => (
                <span className="flex items-center gap-x-2" key={technology}>
                  {technology}{index < profile.heroTechnologies.length - 1 && <b className="font-normal text-portfolio-cyan" aria-hidden="true">•</b>}
                </span>
              ))}
            </div>
          </div>

          <div className="hero-visual hero-layout-visual animate-visual-in" style={{ '--delay': '310ms' }}>
            <div className="hero-orbit" aria-hidden="true"><i /><i /><i /></div>
            <div className="hero-image-frame">
              <img src={amanPortrait} width="1122" height="1402" alt="Aman Kaushik" decoding="async" fetchPriority="high" />
            </div>
            {profile.heroBadges.map((badge, index) => <span className={`hero-tech-badge hero-tech-badge-${index + 1} animate-float`} key={badge}>{badge}</span>)}
          </div>
          <div className="hero-actions mt-2 flex gap-3 animate-fade-up" style={{ '--delay': '440ms' }}>
            <PrimaryButton className="flex-1" href="#projects">{profile.heroActions.primary}</PrimaryButton>
            {resumeIsReady ? <SecondaryButton className="flex-1" href={profile.contact.resumeUrl} target="_blank" rel="noreferrer">{profile.heroActions.secondary}</SecondaryButton> : <SecondaryButton className="flex-1" aria-disabled="true" title="Add a resume URL in src/data/profile.js to enable this button">{profile.heroActions.secondary}</SecondaryButton>}
          </div>
          <div className="hero-socials mt-6 animate-fade-in" style={{ '--delay': '540ms' }}><SocialLinks contact={profile.contact} /></div>
        </div>
        <ScrollIndicator />
      </Container>
    </section>
    <CredibilityStrip items={profile.credibility} />
  </>)
}

export default Hero
