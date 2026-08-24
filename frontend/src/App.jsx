import React from 'react'
import Header from './components/Header'
import UploadPage from './pages/UploadPage'
import ResultsPage from './pages/ResultsPage'
import { useAnalysis } from './hooks/useAnalysis'
import { useTheme } from './hooks/useTheme'

export default function App() {
  const { theme, setTheme } = useTheme()

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
    <div className="min-h-screen transition-colors duration-300">
      <Header
        onReset={reset}
        hasResults={showResults}
        theme={theme}
        setTheme={setTheme}
      />

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
