function Tag({ children, className = '' }) {
  return <span className={`tag ${className}`}>{children}</span>
}

export default Tag
