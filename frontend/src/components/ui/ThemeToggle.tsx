import { Sun, Moon } from 'lucide-react'
import { useState, useEffect } from 'react'
import './ThemeToggle.css'

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const savedTheme = localStorage.getItem('apuradito_theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const initialDark = savedTheme === 'dark' || (!savedTheme && prefersDark)
    setIsDark(initialDark)
    document.documentElement.setAttribute('data-theme', initialDark ? 'dark' : 'light')
  }, [])

  const toggle = () => {
    const newDark = !isDark
    setIsDark(newDark)
    const theme = newDark ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('apuradito_theme', theme)
  }

  return (
    <button
      className="theme-toggle"
      onClick={toggle}
      title={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      aria-label={isDark ? 'Modo claro' : 'Modo oscuro'}
    >
      <span className={`theme-icon ${!isDark ? 'active' : ''}`}>
        <Sun size={18} />
      </span>
      <span className={`theme-icon ${isDark ? 'active' : ''}`}>
        <Moon size={18} />
      </span>
    </button>
  )
}
