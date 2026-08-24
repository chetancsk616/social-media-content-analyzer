import React from 'react'
import { CopyButton } from './HashtagSection'

export default function ImprovedPost({ improvedPost }) {
  if (!improvedPost) {
    return null
  }

  return (
    <div className="glass-card p-6 border border-accent-300/80 dark:border-accent-500/20 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-slate-900 dark:text-white font-semibold text-base flex items-center gap-2">
          <span className="text-lg">✍️</span>
          Improved Version
          <span className="text-xs text-slate-600 dark:text-slate-400 font-normal bg-slate-100 dark:bg-white/[0.04] px-2.5 py-0.5 rounded-full border border-slate-200 dark:border-white/[0.06]">
            Groq AI rewrite
          </span>
        </h3>
        <CopyButton text={improvedPost} label="Copy post" />
      </div>

      <div className="relative">
        {/* Decorative left border */}
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-accent-500 to-violet-500 rounded-full" />
        <div className="pl-4">
          <p className="text-slate-800 dark:text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
            {improvedPost}
          </p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-100 dark:border-white/[0.04] flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-accent-500 dark:bg-accent-400" />
        <p className="text-xs text-slate-500 dark:text-slate-400">
          AI-generated rewrite. Review and personalise before publishing.
        </p>
      </div>
    </div>
  )
}
