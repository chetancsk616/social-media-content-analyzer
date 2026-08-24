import React, { useState } from 'react'

function CopyButton({ text, label = 'Copy' }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      const el = document.createElement('textarea')
      el.value = text
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="text-xs px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-white/[0.06] dark:hover:bg-white/[0.1] dark:text-slate-400 dark:hover:text-white border border-slate-300/80 dark:border-white/[0.08] transition-all duration-200 flex items-center gap-1 cursor-pointer"
      aria-label={`Copy ${label}`}
    >
      {copied ? (
        <>
          <svg className="w-3 h-3 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-emerald-600 dark:text-emerald-400 font-medium">Copied!</span>
        </>
      ) : (
        <>
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          {label}
        </>
      )}
    </button>
  )
}

export default function HashtagSection({ hashtags }) {
  if (!hashtags || hashtags.length === 0) {
    return null
  }

  const allHashtags = hashtags.join(' ')

  return (
    <div className="glass-card p-6 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-slate-900 dark:text-white font-semibold text-base flex items-center gap-2">
          <span className="text-lg">#️⃣</span>
          Hashtag Suggestions
        </h3>
        <CopyButton text={allHashtags} label="Copy all" />
      </div>
      <div className="flex flex-wrap gap-2">
        {hashtags.map((tag, index) => (
          <div
            key={index}
            className="group flex items-center gap-1"
          >
            <span className="chip cursor-default">
              {tag}
            </span>
            <CopyButton text={tag} label="" />
          </div>
        ))}
      </div>
    </div>
  )
}

export { CopyButton }
