import React, { useState } from 'react'

const METHOD_LABELS = {
  pymupdf: { label: 'PyMuPDF', color: 'text-sky-700 dark:text-sky-400', bg: 'bg-sky-100 dark:bg-sky-500/10', border: 'border-sky-200 dark:border-sky-500/20', desc: 'Direct PDF text extraction' },
  tesseract_ocr: { label: 'Tesseract OCR', color: 'text-violet-700 dark:text-violet-400', bg: 'bg-violet-100 dark:bg-violet-500/10', border: 'border-violet-200 dark:border-violet-500/20', desc: 'OpenCV preprocessing + OCR' },
  direct_text: { label: 'Direct Text', color: 'text-emerald-700 dark:text-emerald-400', bg: 'bg-emerald-100 dark:bg-emerald-500/10', border: 'border-emerald-200 dark:border-emerald-500/20', desc: 'Plain text input' },
}

export default function ExtractedText({ text, extractionMethod, charCount }) {
  const [expanded, setExpanded] = useState(false)

  const method = METHOD_LABELS[extractionMethod] || METHOD_LABELS.direct_text
  const preview = text.slice(0, 300)
  const isLong = text.length > 300

  return (
    <div className="glass-card overflow-hidden animate-slide-up">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-5 hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
        id="extracted-text-toggle"
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">📄</span>
          <div className="text-left">
            <span className="text-slate-900 dark:text-white font-semibold text-sm">Extracted Text</span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${method.color} ${method.bg} ${method.border}`}>
                {method.label}
              </span>
              <span className="text-slate-500 dark:text-slate-400 text-xs">{method.desc}</span>
              <span className="text-slate-300 dark:text-slate-600 text-xs">·</span>
              <span className="text-slate-500 dark:text-slate-400 text-xs">{charCount?.toLocaleString()} chars</span>
            </div>
          </div>
        </div>
        <svg
          className={`w-4 h-4 text-slate-400 dark:text-slate-500 transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Content */}
      {expanded && (
        <div className="px-5 pb-5 border-t border-slate-100 dark:border-white/[0.04]">
          <div className="mt-4 p-4 rounded-xl bg-slate-100 dark:bg-black/30 border border-slate-200 dark:border-white/[0.04]">
            <pre className="text-slate-800 dark:text-slate-300 text-xs leading-relaxed whitespace-pre-wrap font-mono overflow-auto max-h-80">
              {text}
            </pre>
          </div>
        </div>
      )}

      {/* Collapsed preview */}
      {!expanded && (
        <div className="px-5 pb-4">
          <p className="text-slate-500 dark:text-slate-400 text-xs leading-relaxed line-clamp-2 font-mono">
            {preview}{isLong ? '…' : ''}
          </p>
        </div>
      )}
    </div>
  )
}
