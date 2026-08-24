import React from 'react'
import Header from './components/Header'
import UploadPage from './pages/UploadPage'
import ResultsPage from './pages/ResultsPage'
import { useAnalysis } from './hooks/useAnalysis'

export default function App() {
  const {
    status,
    results,
    error,
    uploadProgress,
    currentStep,
    completedSteps,
    processingSteps,
    runFileAnalysis,
    runTextAnalysis,
    reset,
  } = useAnalysis()

  const showResults = status === 'success' && results !== null

  return (
    <div className="min-h-screen">
      <Header onReset={reset} hasResults={showResults} />

      <main>
        {showResults ? (
          <ResultsPage results={results} onReset={reset} />
        ) : (
          <UploadPage
            onFileSelect={runFileAnalysis}
            onTextSubmit={runTextAnalysis}
            status={status}
            error={error}
            processingSteps={processingSteps}
            currentStep={currentStep}
            completedSteps={completedSteps}
            uploadProgress={uploadProgress}
          />
        )}
      </main>
    </div>
  )
}
