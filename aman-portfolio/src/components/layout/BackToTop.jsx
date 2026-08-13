import { useEffect, useState } from 'react'

function BackToTop() {
  const [isVisible, setIsVisible] = useState(false)
  useEffect(() => {
    const updateVisibility = () => setIsVisible(window.scrollY > 560)
    updateVisibility()
    window.addEventListener('scroll', updateVisibility, { passive: true })
    return () => window.removeEventListener('scroll', updateVisibility)
  }, [])

  return <button className={`back-to-top ${isVisible ? 'back-to-top-visible' : ''}`} type="button" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} aria-label="Back to top">↑</button>
}

export default BackToTop
