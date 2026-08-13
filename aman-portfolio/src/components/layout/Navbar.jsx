import { useEffect, useState } from 'react'
import MobileMenu from './MobileMenu.jsx'

const navigationItems = [
  { label: 'Home', href: '#home' },
  { label: 'About', href: '#about' },
  { label: 'Education', href: '#education' },
  { label: 'Skills', href: '#skills' },
  { label: 'Projects', href: '#projects' },
  { label: 'Experience', href: '#experience' },
  { label: 'Contact', href: '#contact' },
]

function Navbar() {
  const [activeSection, setActiveSection] = useState('home')
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    let animationFrame = 0
    const updateNavigation = () => {
      animationFrame = 0
      setIsScrolled((current) => {
        const next = window.scrollY > 18
        return current === next ? current : next
      })

      const currentSection = navigationItems.reduce((active, item) => {
        const id = item.href.slice(1)
        const section = document.getElementById(id)
        return section && section.getBoundingClientRect().top <= 160 ? id : active
      }, 'home')

      setActiveSection((current) => (current === currentSection ? current : currentSection))
    }

    updateNavigation()
    const onScroll = () => {
      if (!animationFrame) animationFrame = window.requestAnimationFrame(updateNavigation)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (animationFrame) window.cancelAnimationFrame(animationFrame)
    }
  }, [])

  return (
    <header className="fixed inset-x-0 top-0 z-50 px-4 pt-4 sm:px-6">
      <nav className={`navbar-shell ${isScrolled ? 'navbar-shell-scrolled' : ''}`} aria-label="Primary navigation">
        <a className="navbar-logo" href="#home" aria-label="Aman Kaushik home">
          AK<span>.</span>
        </a>

        <div className="hidden items-center gap-1 lg:flex">
          {navigationItems.map((item) => (
            <a className={`nav-link ${activeSection === item.href.slice(1) ? 'nav-link-active' : ''}`} href={item.href} key={item.href}>
              {item.label}
            </a>
          ))}
        </div>

        <button className={`menu-toggle lg:hidden ${isMenuOpen ? 'menu-toggle-open' : ''}`} type="button" aria-expanded={isMenuOpen} aria-controls="mobile-navigation" aria-label={isMenuOpen ? 'Close navigation menu' : 'Open navigation menu'} onClick={() => setIsMenuOpen((isOpen) => !isOpen)}>
          <span />
          <span />
          <span />
        </button>
      </nav>

      <MobileMenu
        activeSection={activeSection}
        isOpen={isMenuOpen}
        items={navigationItems}
        onClose={() => setIsMenuOpen(false)}
      />
    </header>
  )
}

export default Navbar
