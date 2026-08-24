import React from 'react'

export default function KeywordSection({ keywords }) {
  if (!keywords || keywords.length === 0) {
    return null
  }

  return (
    <div className="glass-card p-6 animate-slide-up">
      <h3 className="text-white font-semibold text-base mb-4 flex items-center gap-2">
        <span className="text-lg">🔑</span>
        Top Keywords
        <span className="ml-1 text-xs text-slate-500 font-normal">(TF-IDF extracted)</span>
      </h3>
      <div className="flex flex-wrap gap-2">
        {keywords.map((keyword, index) => (
          <span
            key={index}
            className="chip"
            style={{
              // Gradient opacity based on rank
              opacity: Math.max(0.6, 1 - index * 0.05),
            }}
          >
            <span className="text-xs text-slate-500">#{index + 1}</span>
            {keyword}
          </span>
        ))}
      </div>
    </div>
  )
}
