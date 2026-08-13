function SecondaryButton({ children, className = '', href, ...props }) {
  const classes = `button-base button-secondary ${className}`

  if (href) {
    return <a className={classes} href={href} {...props}>{children}</a>
  }

  return <button className={classes} type="button" {...props}>{children}</button>
}

export default SecondaryButton
