import React from 'react'
import ThemeToggle from './ThemeToggle'

export default function Header({ onReset, hasResults, theme, setTheme }) {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 dark:border-white/[0.06] bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button
            onClick={onReset}
            className="flex items-center gap-3 group cursor-pointer"
            aria-label="Go to home"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center shadow-glow-sm group-hover:shadow-glow transition-all duration-300">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="text-left">
              <span className="font-bold text-slate-900 dark:text-white text-sm">Content Analyzer</span>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-medium tracking-wider uppercase">
                Social Media
              </div>
            </div>
          </button>

          {/* Nav & Theme Toggle */}
          <nav className="flex items-center gap-2.5 sm:gap-3">
            <span className="hidden sm:flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.06] px-3 py-1.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Local NLP · Groq AI
            </span>

            {/* Theme Toggle */}
            <ThemeToggle theme={theme} setTheme={setTheme} />

            {hasResults && (
              <button
                onClick={onReset}
                className="btn-secondary text-xs"
                id="new-analysis-btn"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Analysis
              </button>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}
