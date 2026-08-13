import { useEffect, useState } from 'react'

function PageIntro() {
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setIsComplete(true), 620)
    return () => window.clearTimeout(timer)
  }, [])

  return <div className={`page-intro ${isComplete ? 'page-intro-complete' : ''}`} aria-hidden="true"><span>AK.</span></div>
}

export default PageIntro
