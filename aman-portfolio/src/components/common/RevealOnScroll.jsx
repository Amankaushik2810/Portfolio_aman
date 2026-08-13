import { useEffect, useRef, useState } from 'react'

function RevealOnScroll({ children, className = '', delay = 0, stagger = false, threshold = 0.14 }) {
  const elementRef = useRef(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return undefined

    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    if (motionQuery.matches) {
      setIsVisible(true)
      return undefined
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold },
    )

    observer.observe(element)
    return () => observer.disconnect()
  }, [threshold])

  return (
    <div className={`reveal-on-scroll ${stagger ? 'reveal-stagger' : ''} ${isVisible ? 'reveal-on-scroll-visible' : ''} ${className}`} ref={elementRef} style={{ '--reveal-delay': `${delay}ms` }}>
      {children}
    </div>
  )
}

export default RevealOnScroll
