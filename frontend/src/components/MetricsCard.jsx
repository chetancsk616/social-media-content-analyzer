import React from 'react'

function MetricItem({ label, value, unit, icon }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-100 dark:border-white/[0.04] last:border-0">
      <div className="flex items-center gap-2">
        <span className="text-base">{icon}</span>
        <span className="text-slate-600 dark:text-slate-400 text-sm">{label}</span>
      </div>
      <span className="text-slate-900 dark:text-white font-semibold text-sm">
        {value}
        {unit && <span className="text-slate-400 dark:text-slate-500 font-normal text-xs ml-1">{unit}</span>}
      </span>
    </div>
  )
}

export default function MetricsCard({ metrics }) {
  const {
    word_count,
    sentence_count,
    avg_sentence_length,
    avg_word_length,
    readability_score,
    readability_label,
    paragraph_count,
  } = metrics

  return (
    <div className="glass-card p-6 animate-slide-up">
      <h3 className="text-slate-900 dark:text-white font-semibold text-base mb-4 flex items-center gap-2">
        <span className="text-lg">📊</span>
        Text Metrics
      </h3>

      <MetricItem label="Word Count"            value={word_count.toLocaleString()}  unit="words" icon="📝" />
      <MetricItem label="Sentences"             value={sentence_count}               unit=""      icon="💬" />
      <MetricItem label="Paragraphs"            value={paragraph_count}              unit=""      icon="¶"  />
      <MetricItem label="Avg Sentence Length"   value={avg_sentence_length}          unit="words" icon="📏" />
      <MetricItem label="Avg Word Length"       value={avg_word_length}              unit="chars" icon="🔤" />

      <div className="mt-4 pt-4 border-t border-slate-100 dark:border-white/[0.04]">
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-600 dark:text-slate-400 text-sm flex items-center gap-1">
            <span>📖</span> Flesch Reading Ease
          </span>
          <div className="flex items-center gap-2">
            <span className="text-slate-900 dark:text-white font-semibold text-sm">{readability_score}</span>
            <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
              readability_label === 'Easy'
                ? 'text-emerald-700 bg-emerald-100 dark:text-emerald-400 dark:bg-emerald-500/10'
                : readability_label === 'Moderate'
                ? 'text-amber-700 bg-amber-100 dark:text-amber-400 dark:bg-amber-500/10'
                : 'text-rose-700 bg-rose-100 dark:text-rose-400 dark:bg-rose-500/10'
            }`}>
              {readability_label}
            </span>
          </div>
        </div>
        <div className="progress-bar">
          <div
            className={`progress-fill ${
              readability_label === 'Easy'
                ? 'bg-gradient-to-r from-emerald-600 to-emerald-400'
                : readability_label === 'Moderate'
                ? 'bg-gradient-to-r from-amber-600 to-amber-400'
                : 'bg-gradient-to-r from-rose-600 to-rose-400'
            }`}
            style={{ width: `${readability_score}%` }}
          />
        </div>
      </div>
    </div>
  )
}
