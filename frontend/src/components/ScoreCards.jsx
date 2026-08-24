import React from 'react'

const SCORE_CONFIGS = [
  {
    key: 'hook',
    label: 'Hook Strength',
    icon: '🪝',
    description: 'Opening line impact',
    color: { bar: 'from-violet-600 to-violet-400', text: 'text-violet-600 dark:text-violet-400', bg: 'bg-violet-50 dark:bg-violet-500/10', border: 'border-violet-200 dark:border-violet-500/20' },
  },
  {
    key: 'cta',
    label: 'CTA Strength',
    icon: '📣',
    description: 'Call-to-action power',
    color: { bar: 'from-accent-600 to-accent-400', text: 'text-accent-600 dark:text-accent-400', bg: 'bg-accent-50 dark:bg-accent-500/10', border: 'border-accent-200 dark:border-accent-500/20' },
  },
  {
    key: 'clarity',
    label: 'Content Clarity',
    icon: '💡',
    description: 'Structure & brevity',
    color: { bar: 'from-sky-600 to-sky-400', text: 'text-sky-600 dark:text-sky-400', bg: 'bg-sky-50 dark:bg-sky-500/10', border: 'border-sky-200 dark:border-sky-500/20' },
  },
  {
    key: 'readability',
    label: 'Readability',
    icon: '📖',
    description: 'Reading ease score',
    color: { bar: 'from-emerald-600 to-emerald-400', text: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-500/10', border: 'border-emerald-200 dark:border-emerald-500/20' },
  },
  {
    key: 'structure',
    label: 'Structure',
    icon: '🏗️',
    description: 'Formatting & layout',
    color: { bar: 'from-amber-600 to-amber-400', text: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-500/10', border: 'border-amber-200 dark:border-amber-500/20' },
  },
]

function ScoreCard({ config, score }) {
  const { label, icon, description, color } = config

  return (
    <div className={`glass-card-hover p-5 border ${color.border} animate-slide-up`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <div>
            <p className="text-slate-900 dark:text-white font-semibold text-sm">{label}</p>
            <p className="text-slate-500 dark:text-slate-400 text-xs">{description}</p>
          </div>
        </div>
        <div className={`text-2xl font-black tabular-nums ${color.text}`}>
          {score}
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-bar mt-2">
        <div
          className={`progress-fill bg-gradient-to-r ${color.bar}`}
          style={{ width: `${score}%` }}
        />
      </div>

      {/* Score label */}
      <div className="mt-2 flex justify-between text-xs">
        <span className="text-slate-400 dark:text-slate-600">0</span>
        <span className={`font-semibold ${
          score >= 75 ? 'text-emerald-600 dark:text-emerald-400' : score >= 50 ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400'
        }`}>
          {score >= 75 ? 'Strong' : score >= 50 ? 'Moderate' : 'Weak'}
        </span>
        <span className="text-slate-400 dark:text-slate-600">100</span>
      </div>
    </div>
  )
}

export default function ScoreCards({ scores }) {
  return (
    <div>
      <h3 className="text-slate-900 dark:text-white font-semibold text-base mb-4 flex items-center gap-2">
        <svg className="w-4 h-4 text-accent-600 dark:text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Score Breakdown
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {SCORE_CONFIGS.map((config) => (
          <ScoreCard key={config.key} config={config} score={scores[config.key] ?? 0} />
        ))}
      </div>
    </div>
  )
}
