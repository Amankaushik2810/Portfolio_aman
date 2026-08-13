import { useEffect, useState } from 'react'

function CursorGlow() {
  const [isEnabled, setIsEnabled] = useState(false)

  useEffect(() => {
    const pointerQuery = window.matchMedia('(hover: hover) and (pointer: fine)')
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const updateEnabled = () => setIsEnabled(pointerQuery.matches && !motionQuery.matches)
    updateEnabled()
    pointerQuery.addEventListener('change', updateEnabled)
    motionQuery.addEventListener('change', updateEnabled)
    return () => {
      pointerQuery.removeEventListener('change', updateEnabled)
      motionQuery.removeEventListener('change', updateEnabled)
    }
  }, [])

  useEffect(() => {
    if (!isEnabled) return undefined
    let frameId = 0
    let x = -200
    let y = -200
    const updatePosition = () => {
      document.documentElement.style.setProperty('--cursor-x', `${x}px`)
      document.documentElement.style.setProperty('--cursor-y', `${y}px`)
      frameId = 0
    }
    const onPointerMove = (event) => {
      x = event.clientX
      y = event.clientY
      if (!frameId) frameId = window.requestAnimationFrame(updatePosition)
    }
    window.addEventListener('pointermove', onPointerMove, { passive: true })
    return () => {
      window.removeEventListener('pointermove', onPointerMove)
      if (frameId) window.cancelAnimationFrame(frameId)
    }
  }, [isEnabled])

  return isEnabled ? <span className="cursor-glow" aria-hidden="true" /> : null
}

export default CursorGlow
