function ArrowIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></svg>
}

function GitHubIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.58 2 12.23c0 4.52 2.87 8.35 6.84 9.71.5.1.68-.22.68-.49 0-.24-.01-1.04-.01-1.88-2.78.62-3.37-1.2-3.37-1.2-.45-1.19-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .07 1.54 1.06 1.54 1.06.9 1.57 2.35 1.12 2.92.86.09-.67.35-1.12.64-1.38-2.22-.26-4.56-1.14-4.56-5.08 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.31.1-2.72 0 0 .84-.28 2.75 1.05A9.37 9.37 0 0 1 12 6.85c.85 0 1.7.12 2.5.35 1.9-1.33 2.74-1.05 2.74-1.05.55 1.41.2 2.46.1 2.72.64.72 1.03 1.63 1.03 2.75 0 3.95-2.34 4.81-4.57 5.07.36.32.68.92.68 1.86 0 1.34-.01 2.42-.01 2.75 0 .27.18.59.69.49A10.23 10.23 0 0 0 22 12.23C22 6.58 17.52 2 12 2Z" /></svg>
}

function ProjectLinks({ links, variant = 'card' }) {
  const linkItems = [
    { label: variant === 'card' ? 'GitHub ↗' : 'View on GitHub ↗', href: links.github, github: true },
    links.liveDemo && { label: 'Live Demo', href: links.liveDemo },
    { label: 'Download on Google Play \u2197', href: links.playStore, playStore: true },
  ].filter((link) => link && link.href && link.href !== 'NOT_APPLICABLE' && !link.href.startsWith('REPLACE_WITH'))
  if (variant === 'agri-card') linkItems.sort((left, right) => (left.playStore ? 0 : left.label.startsWith('Live') ? -1 : left.github ? 1 : 0) - (right.playStore ? 0 : right.label.startsWith('Live') ? -1 : right.github ? 1 : 0))

  if (linkItems.length === 0) return null

  return (
    <div className={`project-links project-links-${variant}`}>
      {linkItems.map((link) => <a className={`${link.playStore ? 'play-store-link ' : ''}${link.github ? 'github-link' : ''}`} href={link.href} key={link.label} target="_blank" rel="noopener noreferrer" aria-label={`${link.label.replace(' ↗', '')} (opens in a new tab)`}>{link.github && <GitHubIcon />}{link.label}{!link.github && <ArrowIcon />}</a>)}
    </div>
  )
}

export default ProjectLinks
