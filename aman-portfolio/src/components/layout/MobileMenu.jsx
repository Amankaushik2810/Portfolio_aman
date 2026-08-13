import { useEffect, useRef, useState } from 'react'

function MobileMenu({ activeSection, isOpen, items, onClose }) {
  const [isMounted, setIsMounted] = useState(isOpen)
  const panelRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      setIsMounted(true)
      return undefined
    }

    const timer = window.setTimeout(() => setIsMounted(false), 220)
    return () => window.clearTimeout(timer)
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return undefined

    const focusFrame = window.requestAnimationFrame(() => panelRef.current?.querySelector('a[href]')?.focus())
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose()
        return
      }

      if (event.key !== 'Tab') return
      const focusableElements = [...panelRef.current.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])')]
      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]
      if (!firstElement || !lastElement) return

      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault()
        lastElement.focus()
      } else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault()
        firstElement.focus()
      }
    }

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', handleKeyDown)

    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', handleKeyDown)
      window.cancelAnimationFrame(focusFrame)
    }
  }, [isOpen, onClose])

  if (!isMounted) return null

  return (
    <div className={`mobile-menu-backdrop ${isOpen ? 'mobile-menu-open' : ''}`} role="presentation" onClick={onClose}>
      <div className="mobile-menu-panel" id="mobile-navigation" ref={panelRef} role="dialog" aria-modal="true" aria-label="Mobile navigation" onClick={(event) => event.stopPropagation()}>
        <nav className="flex flex-col gap-1" aria-label="Mobile navigation links">
          {items.map((item) => (
            <a className={`mobile-nav-link ${activeSection === item.href.slice(1) ? 'mobile-nav-link-active' : ''}`} href={item.href} key={item.href} onClick={onClose}>
              {item.label}
            </a>
          ))}
        </nav>
      </div>
    </div>
  )
}

export default MobileMenu
