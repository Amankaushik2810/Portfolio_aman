function ArrowIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></svg>
}

function ProjectLinks({ links, variant = 'card' }) {
  const linkItems = [
    { label: 'GitHub', href: links.github },
    { label: 'Live demo', href: links.liveDemo },
    { label: 'View on Play Store', href: links.playStore, playStore: true },
  ].filter((link) => link.href && link.href !== 'NOT_APPLICABLE' && !link.href.startsWith('REPLACE_WITH'))

  if (linkItems.length === 0) return null

  return (
    <div className={`project-links project-links-${variant}`}>
      {linkItems.map((link) => <a className={link.playStore ? 'play-store-link' : ''} href={link.href} key={link.label} target="_blank" rel="noopener noreferrer">{link.label}<ArrowIcon /></a>)}
    </div>
  )
}

export default ProjectLinks
