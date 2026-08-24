import React from 'react'

export default function Recommendations({ aiRecommendations }) {
  const { available, recommendations, strengths, weaknesses, alternative_hooks, error_message } = aiRecommendations

  return (
    <div className="space-y-4 animate-slide-up">
      {/* Unavailability notice */}
      {!available && (
        <div className="flex items-start gap-3 bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 text-sm">
          <svg className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <p className="text-amber-300 font-medium">AI recommendations temporarily unavailable</p>
            <p className="text-amber-400/70 text-xs mt-0.5">
              {error_message || 'Local analysis is still complete and shown below.'}
            </p>
          </div>
        </div>
      )}

      {/* Main recommendations */}
      {available && recommendations && recommendations.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-white font-semibold text-base mb-5 flex items-center gap-2">
            <span className="text-lg">✨</span>
            AI Recommendations
            <span className="ml-1 text-xs text-slate-500 font-normal bg-white/[0.04] px-2 py-0.5 rounded-full border border-white/[0.06]">
              Powered by Gemini
            </span>
          </h3>
          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04] transition-colors"
              >
                <div className="w-6 h-6 rounded-full bg-accent-500/20 border border-accent-500/30 flex items-center justify-center flex-shrink-0 text-xs font-bold text-accent-400">
                  {index + 1}
                </div>
                <p className="text-slate-300 text-sm leading-relaxed">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      {available && (strengths?.length > 0 || weaknesses?.length > 0) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {strengths?.length > 0 && (
            <div className="glass-card p-5 border border-emerald-500/15">
              <h4 className="text-emerald-400 font-semibold text-sm mb-3 flex items-center gap-1.5">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Strengths
              </h4>
              <ul className="space-y-2">
                {strengths.map((s, i) => (
                  <li key={i} className="text-slate-400 text-xs flex items-start gap-1.5">
                    <span className="text-emerald-500 mt-0.5 flex-shrink-0">•</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {weaknesses?.length > 0 && (
            <div className="glass-card p-5 border border-rose-500/15">
              <h4 className="text-rose-400 font-semibold text-sm mb-3 flex items-center gap-1.5">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Areas to Improve
              </h4>
              <ul className="space-y-2">
                {weaknesses.map((w, i) => (
                  <li key={i} className="text-slate-400 text-xs flex items-start gap-1.5">
                    <span className="text-rose-500 mt-0.5 flex-shrink-0">•</span>
                    {w}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Alternative hooks */}
      {available && alternative_hooks?.length > 0 && (
        <div className="glass-card p-5 border border-violet-500/15">
          <h4 className="text-violet-400 font-semibold text-sm mb-3 flex items-center gap-2">
            <span>🪝</span> Alternative Hook Ideas
          </h4>
          <div className="space-y-2">
            {alternative_hooks.map((hook, i) => (
              <div key={i} className="text-slate-400 text-sm p-3 rounded-lg bg-white/[0.02] border border-white/[0.04] italic">
                "{hook}"
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
