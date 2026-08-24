import React from 'react'

function StepIcon({ status }) {
  if (status === 'completed') {
    return (
      <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center flex-shrink-0">
        <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
        </svg>
      </div>
    )
  }
  if (status === 'active') {
    return (
      <div className="w-8 h-8 rounded-full bg-accent-500/20 border border-accent-500/40 flex items-center justify-center flex-shrink-0">
        <div className="w-3 h-3 rounded-full bg-accent-400 animate-ping absolute" />
        <div className="w-3 h-3 rounded-full bg-accent-500" />
      </div>
    )
  }
  return (
    <div className="w-8 h-8 rounded-full bg-white/[0.04] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
      <div className="w-2 h-2 rounded-full bg-slate-700" />
    </div>
  )
}

export default function ProcessingState({
  steps,
  currentStep,
  completedSteps,
  uploadProgress,
}) {
  return (
    <div className="glass-card p-6 space-y-1 animate-fade-in">
      <h3 className="text-white font-semibold text-sm mb-4 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-accent-400 animate-pulse" />
        Processing your content…
      </h3>

      {steps.map((step) => {
        const isCompleted = completedSteps.includes(step.id)
        const isActive = currentStep === step.id
        const isPending = !isCompleted && !isActive

        // Skip OCR step visual if not needed (it won't be made active unless triggered)
        const status = isCompleted ? 'completed' : isActive ? 'active' : 'pending'

        return (
          <div
            key={step.id}
            className={`step-indicator ${
              isActive ? 'active' : isCompleted ? 'completed' : 'pending'
            }`}
          >
            <div className="relative flex items-center justify-center">
              <StepIcon status={status} />
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium transition-colors duration-300 ${
                isActive ? 'text-accent-300' : isCompleted ? 'text-emerald-400' : 'text-slate-600'
              }`}>
                {step.label}
              </p>
            </div>
            {isActive && (
              <div className="flex gap-0.5">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-1 h-1 rounded-full bg-accent-400 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            )}
          </div>
        )
      })}

      {/* Upload progress bar */}
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="mt-4 space-y-1.5">
          <div className="flex justify-between text-xs text-slate-500">
            <span>Uploading…</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill bg-gradient-to-r from-accent-600 to-accent-400"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
