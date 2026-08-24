import React from 'react'
import DropZone from '../components/DropZone'
import ProcessingState from '../components/ProcessingState'

const FEATURES = [
  { icon: '🧠', label: 'Local Sentiment', desc: 'DistilBERT / VADER inference' },
  { icon: '📊', label: 'TF-IDF Keywords', desc: 'scikit-learn extraction' },
  { icon: '👁️', label: 'OpenCV + OCR', desc: 'Image preprocessing pipeline' },
  { icon: '⚡', label: 'Groq LPU AI', desc: 'Ultra-fast recommendations' },
]

export default function UploadPage({
  onFileSelect,
  onTextSubmit,
  status,
  error,
  processingSteps,
  currentStep,
  completedSteps,
  uploadProgress,
}) {
  const isProcessing = status === 'uploading' || status === 'processing'

  return (
    <div className="min-h-screen bg-glow-top transition-colors duration-300">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16 lg:py-24">
        {/* Hero */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-2 bg-accent-50 text-accent-700 border border-accent-200 dark:bg-accent-500/10 dark:border-accent-500/20 dark:text-accent-300 rounded-full px-4 py-1.5 text-xs font-medium mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-500 dark:bg-accent-400 animate-pulse" />
            Local NLP · No cloud for analysis
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-white leading-tight mb-4 tracking-tight">
            Analyze Your{' '}
            <span className="gradient-text">Social Media</span>{' '}
            Content
          </h1>
          <p className="text-slate-600 dark:text-slate-400 text-lg max-w-xl mx-auto leading-relaxed">
            Upload a PDF or image of your post. Get engagement scores, sentiment analysis,
            keyword insights, and AI-powered recommendations.
          </p>
        </div>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-2 mb-10">
          {FEATURES.map((f) => (
            <div
              key={f.label}
              className="flex items-center gap-1.5 bg-white dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.06] rounded-full px-3 py-1.5 text-xs shadow-sm dark:shadow-none"
            >
              <span>{f.icon}</span>
              <span className="text-slate-800 dark:text-white font-medium">{f.label}</span>
              <span className="text-slate-500 dark:text-slate-400">{f.desc}</span>
            </div>
          ))}
        </div>

        {/* Upload / Processing */}
        {isProcessing ? (
          <ProcessingState
            steps={processingSteps}
            currentStep={currentStep}
            completedSteps={completedSteps}
            uploadProgress={uploadProgress}
          />
        ) : (
          <DropZone
            onFileSelect={onFileSelect}
            onTextSubmit={onTextSubmit}
            disabled={isProcessing}
          />
        )}

        {/* Error state */}
        {status === 'error' && error && (
          <div className="mt-4 flex items-start gap-3 bg-rose-50 border border-rose-200 dark:bg-rose-500/10 dark:border-rose-500/20 rounded-xl p-4 animate-fade-in">
            <svg className="w-5 h-5 text-rose-500 dark:text-rose-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-rose-700 dark:text-rose-300 font-medium text-sm">Analysis failed</p>
              <p className="text-rose-600 dark:text-rose-400/80 text-xs mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Footer note */}
        <p className="text-center text-xs text-slate-500 dark:text-slate-500 mt-8">
          Files are processed locally and deleted immediately after analysis.
          Never stored or sent to third parties (except AI for recommendations).
        </p>
      </div>
    </div>
  )
}
