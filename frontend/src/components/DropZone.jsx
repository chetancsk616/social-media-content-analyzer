import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

const MAX_SIZE_MB = 10
const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'image/png': ['.png'],
  'image/jpeg': ['.jpg', '.jpeg'],
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function FileTypeIcon({ type }) {
  if (type === 'application/pdf') {
    return (
      <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center">
        <span className="text-rose-400 font-bold text-xs">PDF</span>
      </div>
    )
  }
  return (
    <div className="w-10 h-10 rounded-lg bg-accent-500/10 border border-accent-500/20 flex items-center justify-center">
      <svg className="w-5 h-5 text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  )
}

export default function DropZone({ onFileSelect, onTextSubmit, disabled }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileError, setFileError] = useState(null)
  const [textMode, setTextMode] = useState(false)
  const [textInput, setTextInput] = useState('')

  const onDrop = useCallback((acceptedFiles, rejections) => {
    setFileError(null)

    if (rejections.length > 0) {
      const rej = rejections[0]
      if (rej.errors[0]?.code === 'file-too-large') {
        setFileError(`File is too large. Maximum size is ${MAX_SIZE_MB} MB.`)
      } else if (rej.errors[0]?.code === 'file-invalid-type') {
        setFileError('Unsupported file type. Please upload a PDF, PNG, JPG, or JPEG.')
      } else {
        setFileError(rej.errors[0]?.message || 'Invalid file.')
      }
      return
    }

    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_SIZE_MB * 1024 * 1024,
    maxFiles: 1,
    disabled,
  })

  const handleAnalyze = () => {
    if (selectedFile) {
      onFileSelect(selectedFile)
    }
  }

  const handleTextAnalyze = () => {
    if (textInput.trim().length > 0) {
      onTextSubmit(textInput.trim())
    }
  }

  const clearFile = (e) => {
    e.stopPropagation()
    setSelectedFile(null)
    setFileError(null)
  }

  const borderClass = isDragReject || fileError
    ? 'border-rose-500/50 bg-rose-500/5'
    : isDragActive
    ? 'border-accent-400 bg-accent-500/10'
    : selectedFile
    ? 'border-emerald-500/40 bg-emerald-500/5'
    : 'border-white/[0.1] hover:border-accent-500/40 hover:bg-white/[0.02]'

  return (
    <div className="w-full space-y-6">
      {/* Tab switcher */}
      <div className="flex gap-1 p-1 bg-white/[0.04] rounded-xl border border-white/[0.06] w-fit">
        <button
          onClick={() => setTextMode(false)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
            !textMode
              ? 'bg-accent-600 text-white shadow-glow-sm'
              : 'text-slate-400 hover:text-slate-300'
          }`}
          id="tab-file"
        >
          📎 Upload File
        </button>
        <button
          onClick={() => setTextMode(true)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
            textMode
              ? 'bg-accent-600 text-white shadow-glow-sm'
              : 'text-slate-400 hover:text-slate-300'
          }`}
          id="tab-text"
        >
          ✏️ Paste Text
        </button>
      </div>

      {!textMode ? (
        <>
          {/* Drop zone */}
          <div
            {...getRootProps()}
            className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-300 ${borderClass}`}
            id="drop-zone"
          >
            <input {...getInputProps()} id="file-input" />

            {selectedFile ? (
              /* File preview */
              <div className="space-y-4">
                <div className="flex items-center justify-center gap-3">
                  <FileTypeIcon type={selectedFile.type} />
                  <div className="text-left">
                    <p className="text-white font-semibold text-sm truncate max-w-[280px]">
                      {selectedFile.name}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-slate-400">{formatBytes(selectedFile.size)}</span>
                      <span className="text-slate-600">·</span>
                      <span className="text-xs text-slate-400 uppercase">{selectedFile.type.split('/')[1]}</span>
                    </div>
                  </div>
                  <button
                    onClick={clearFile}
                    className="ml-2 w-6 h-6 rounded-full bg-white/[0.08] hover:bg-white/[0.14] flex items-center justify-center text-slate-400 hover:text-white transition-colors"
                    aria-label="Remove file"
                  >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <p className="text-emerald-400 text-sm font-medium">
                  ✓ File ready for analysis
                </p>
              </div>
            ) : (
              /* Empty state */
              <div className="space-y-4">
                <div className={`w-16 h-16 mx-auto rounded-2xl flex items-center justify-center transition-all duration-300 ${
                  isDragActive ? 'bg-accent-500/20 scale-110' : 'bg-white/[0.04]'
                }`}>
                  <svg className={`w-8 h-8 transition-colors duration-300 ${isDragActive ? 'text-accent-400' : 'text-slate-500'}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p className="text-white font-semibold">
                    {isDragActive ? 'Drop your file here' : 'Drag & drop your file here'}
                  </p>
                  <p className="text-slate-500 text-sm mt-1">
                    or <span className="text-accent-400 hover:text-accent-300 cursor-pointer">browse to upload</span>
                  </p>
                </div>
                <div className="flex items-center justify-center gap-4 text-xs text-slate-600">
                  <span className="flex items-center gap-1">
                    <span className="text-rose-400">PDF</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-accent-400">PNG</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-accent-400">JPG</span>
                  </span>
                  <span className="text-slate-700">·</span>
                  <span>Max {MAX_SIZE_MB} MB</span>
                </div>
              </div>
            )}
          </div>

          {/* File error */}
          {fileError && (
            <div className="flex items-start gap-2 text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-xl p-3 text-sm">
              <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {fileError}
            </div>
          )}

          {/* Analyze button */}
          {selectedFile && !fileError && (
            <button
              onClick={handleAnalyze}
              disabled={disabled}
              className="btn-primary w-full text-base py-4"
              id="analyze-file-btn"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Analyze Content
            </button>
          )}
        </>
      ) : (
        /* Text input mode */
        <div className="space-y-4">
          <div className="relative">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your social media post here...&#10;&#10;Example: Did you know that 80% of posts fail to get engagement? Here's how to fix it.&#10;Comment below with your biggest challenge! 👇"
              className="w-full h-48 bg-white/[0.03] border border-white/[0.08] rounded-2xl p-4 text-slate-200 text-sm
                         placeholder:text-slate-600 resize-none focus:outline-none focus:border-accent-500/40
                         focus:bg-white/[0.05] transition-all duration-200"
              id="text-input"
              disabled={disabled}
            />
            <div className="absolute bottom-3 right-3 text-xs text-slate-600">
              {textInput.length} chars
            </div>
          </div>
          <button
            onClick={handleTextAnalyze}
            disabled={disabled || textInput.trim().length === 0}
            className="btn-primary w-full text-base py-4 disabled:opacity-40 disabled:cursor-not-allowed"
            id="analyze-text-btn"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Analyze Text
          </button>
        </div>
      )}
    </div>
  )
}
