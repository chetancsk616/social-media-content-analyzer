import { useState, useCallback } from 'react'
import { analyzeFile, analyzeText } from '../services/api'

/**
 * Processing steps shown in the UI loading state.
 * Each step has an id, label, and optional description.
 */
const PROCESSING_STEPS = [
  { id: 'upload',    label: 'Uploading file',           icon: '⬆️' },
  { id: 'extract',   label: 'Extracting text',           icon: '📄' },
  { id: 'ocr',       label: 'Running OCR',               icon: '🔍' },
  { id: 'nlp',       label: 'Analyzing content',         icon: '🧠' },
  { id: 'score',     label: 'Computing scores',          icon: '📊' },
  { id: 'gemini',    label: 'Generating recommendations', icon: '✨' },
]

export function useAnalysis() {
  const [status, setStatus] = useState('idle') // idle | uploading | processing | success | error
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(null) // step id
  const [completedSteps, setCompletedSteps] = useState([])

  const _completeStep = useCallback((stepId) => {
    setCurrentStep(null)
    setCompletedSteps((prev) => [...prev, stepId])
  }, [])

  const _startStep = useCallback((stepId) => {
    setCurrentStep(stepId)
  }, [])

  const reset = useCallback(() => {
    setStatus('idle')
    setResults(null)
    setError(null)
    setUploadProgress(0)
    setCurrentStep(null)
    setCompletedSteps([])
  }, [])

  const runFileAnalysis = useCallback(async (file) => {
    setStatus('uploading')
    setError(null)
    setResults(null)
    setCompletedSteps([])
    setUploadProgress(0)

    try {
      _startStep('upload')

      const data = await analyzeFile(file, (pct) => {
        setUploadProgress(pct)
        if (pct === 100) {
          _completeStep('upload')
          setStatus('processing')

          // Simulate step progression while backend processes
          _startStep('extract')
          setTimeout(() => {
            _completeStep('extract')
            const needsOcr = file.type !== 'application/pdf'
            if (needsOcr) {
              _startStep('ocr')
              setTimeout(() => {
                _completeStep('ocr')
                _startStep('nlp')
              }, 1500)
            } else {
              _startStep('nlp')
            }
          }, 800)

          setTimeout(() => {
            _completeStep('nlp')
            _startStep('score')
          }, 2500)

          setTimeout(() => {
            _completeStep('score')
            _startStep('gemini')
          }, 3500)
        }
      })

      _completeStep('gemini')
      setResults(data)
      setStatus('success')
    } catch (err) {
      const message = err.response?.data?.detail
        || err.message
        || 'An unexpected error occurred. Please try again.'
      setError(message)
      setStatus('error')
    }
  }, [_startStep, _completeStep])

  const runTextAnalysis = useCallback(async (text) => {
    setStatus('processing')
    setError(null)
    setResults(null)
    setCompletedSteps([])

    try {
      _startStep('nlp')
      setTimeout(() => { _completeStep('nlp'); _startStep('score') }, 500)
      setTimeout(() => { _completeStep('score'); _startStep('gemini') }, 1500)

      const data = await analyzeText(text)

      _completeStep('gemini')
      setResults(data)
      setStatus('success')
    } catch (err) {
      const message = err.response?.data?.detail
        || err.message
        || 'An unexpected error occurred. Please try again.'
      setError(message)
      setStatus('error')
    }
  }, [_startStep, _completeStep])

  return {
    status,
    results,
    error,
    uploadProgress,
    currentStep,
    completedSteps,
    processingSteps: PROCESSING_STEPS,
    runFileAnalysis,
    runTextAnalysis,
    reset,
  }
}
