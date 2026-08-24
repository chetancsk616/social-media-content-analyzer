import React from 'react'
import { CopyButton } from './HashtagSection'

export default function ImprovedPost({ improvedPost }) {
  if (!improvedPost) {
    return null
  }

  return (
    <div className="glass-card p-6 border border-accent-500/20 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold text-base flex items-center gap-2">
          <span className="text-lg">✍️</span>
          Improved Version
          <span className="text-xs text-slate-500 font-normal bg-white/[0.04] px-2 py-0.5 rounded-full border border-white/[0.06]">
            Gemini rewrite
          </span>
        </h3>
        <CopyButton text={improvedPost} label="Copy post" />
      </div>

      <div className="relative">
        {/* Decorative left border */}
        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b from-accent-500 to-violet-500 rounded-full" />
        <div className="pl-4">
          <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
            {improvedPost}
          </p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-white/[0.04] flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-accent-400" />
        <p className="text-xs text-slate-500">
          AI-generated rewrite. Review and personalise before publishing.
        </p>
      </div>
    </div>
  )
}
