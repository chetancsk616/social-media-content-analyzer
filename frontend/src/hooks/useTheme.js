import { useState, useEffect, useCallback } from 'react'

export function useTheme() {
  // 'system' | 'dark' | 'light'
  const [theme, setThemeState] = useState(() => {
    return localStorage.getItem('theme-preference') || 'system'
  })

  const [resolvedTheme, setResolvedTheme] = useState('dark')

  const applyTheme = useCallback((targetTheme) => {
    const root = document.documentElement
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const isDark = targetTheme === 'dark' || (targetTheme === 'system' && systemPrefersDark)

    if (isDark) {
      root.classList.add('dark')
      setResolvedTheme('dark')
    } else {
      root.classList.remove('dark')
      setResolvedTheme('light')
    }
  }, [])

  const setTheme = useCallback((newTheme) => {
    setThemeState(newTheme)
    localStorage.setItem('theme-preference', newTheme)
    applyTheme(newTheme)
  }, [applyTheme])

  useEffect(() => {
    applyTheme(theme)

    // Listen for system theme changes if in 'system' mode
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      const current = localStorage.getItem('theme-preference') || 'system'
      if (current === 'system') {
        applyTheme('system')
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme, applyTheme])

  return {
    theme,
    resolvedTheme,
    setTheme,
    isDark: resolvedTheme === 'dark',
  }
}
