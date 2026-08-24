import React from 'react'

function SentimentBar({ label, confidence }) {
  const isPositive = label === 'POSITIVE'
  const isNegative = label === 'NEGATIVE'

  const color = isPositive ? 'emerald' : isNegative ? 'rose' : 'amber'
  const emoji = isPositive ? '😊' : isNegative ? '😞' : '😐'

  const colorMap = {
    emerald: { text: 'text-emerald-600 dark:text-emerald-400', bar: 'from-emerald-600 to-emerald-400', bg: 'bg-emerald-100 dark:bg-emerald-500/10', border: 'border-emerald-200 dark:border-emerald-500/20' },
    rose:    { text: 'text-rose-600 dark:text-rose-400',       bar: 'from-rose-600 to-rose-400',       bg: 'bg-rose-100 dark:bg-rose-500/10',       border: 'border-rose-200 dark:border-rose-500/20'       },
    amber:   { text: 'text-amber-600 dark:text-amber-400',     bar: 'from-amber-600 to-amber-400',     bg: 'bg-amber-100 dark:bg-amber-500/10',     border: 'border-amber-200 dark:border-amber-500/20'     },
  }

  const c = colorMap[color]

  return (
    <div className={`glass-card p-6 border ${c.border} animate-slide-up`}>
      <h3 className="text-slate-900 dark:text-white font-semibold text-base mb-4 flex items-center gap-2">
        <span className="text-lg">🧠</span>
        Sentiment Analysis
      </h3>

      <div className="flex items-center gap-4">
        <div className={`w-14 h-14 rounded-2xl ${c.bg} border ${c.border} flex items-center justify-center text-2xl flex-shrink-0`}>
          {emoji}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline justify-between mb-2">
            <span className={`text-xl font-bold ${c.text} capitalize`}>
              {label.charAt(0) + label.slice(1).toLowerCase()}
            </span>
            <span className={`text-sm font-semibold ${c.text}`}>
              {Math.round(confidence * 100)}% confident
            </span>
          </div>
          <div className="progress-bar">
            <div
              className={`progress-fill bg-gradient-to-r ${c.bar}`}
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
            Detected via local NLP sentiment model (DistilBERT / VADER)
          </p>
        </div>
      </div>
    </div>
  )
}

export function SentimentCard({ sentiment }) {
  return (
    <SentimentBar
      label={sentiment.label}
      confidence={sentiment.confidence}
    />
  )
}

export default SentimentCard
