function SocialIcon({ type }) {
  const iconProps = { 'aria-hidden': true, fill: 'none', viewBox: '0 0 24 24' }

  if (type === 'github') {
    return <svg {...iconProps}><path d="M15 22v-3.87c.04-.5-.13-.99-.48-1.35 3.94-.44 8.08-1.93 8.08-8.76a6.84 6.84 0 0 0-1.82-4.75 6.37 6.37 0 0 0-.17-4.69s-1.5-.48-4.89 1.82a16.88 16.88 0 0 0-8.9 0c-3.39-2.3-4.89-1.82-4.89-1.82a6.37 6.37 0 0 0-.17 4.69A6.84 6.84 0 0 0 0 8.02c0 6.82 4.13 8.32 8.07 8.77-.35.35-.52.83-.48 1.32V22" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6" /></svg>
  }

  if (type === 'linkedin') {
    return <svg {...iconProps}><path d="M6.5 8.5V18M6.5 5.5v.01M10.5 18v-5.25a4.25 4.25 0 0 1 8.5 0V18M10.5 10.5V18M3 3h18v18H3z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6" /></svg>
  }

  return <svg {...iconProps}><path d="M3.5 6.5 12 12l8.5-5.5M4.5 5h15A1.5 1.5 0 0 1 21 6.5v11a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5v-11A1.5 1.5 0 0 1 4.5 5Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6" /></svg>
}

function SocialLinks({ contact }) {
  const socialItems = [
    { label: 'GitHub', type: 'github', value: contact.githubUrl },
    { label: 'LinkedIn', type: 'linkedin', value: contact.linkedInUrl },
    { label: 'Email', type: 'email', value: contact.email },
  ]

  return (
    <div className="flex items-center gap-3" aria-label="Social links">
      {socialItems.map((item) => {
        const href = item.type === 'email' ? `mailto:${item.value}` : item.value
        return <a className="social-link" href={href} key={item.type} target={item.type === 'email' ? undefined : '_blank'} rel={item.type === 'email' ? undefined : 'noopener noreferrer'} aria-label={item.label}><SocialIcon type={item.type} /></a>
      })}
    </div>
  )
}

export default SocialLinks
