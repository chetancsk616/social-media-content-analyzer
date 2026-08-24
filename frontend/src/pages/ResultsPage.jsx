import React from 'react'
import OverallScore from '../components/OverallScore'
import ScoreCards from '../components/ScoreCards'
import { SentimentCard } from '../components/SentimentCard'
import MetricsCard from '../components/MetricsCard'
import KeywordSection from '../components/KeywordSection'
import HashtagSection from '../components/HashtagSection'
import Recommendations from '../components/Recommendations'
import ImprovedPost from '../components/ImprovedPost'
import ExtractedText from '../components/ExtractedText'

export default function ResultsPage({ results, onReset }) {
  const {
    filename,
    file_type,
    extraction_method,
    extracted_text,
    char_count,
    sentiment,
    metrics,
    keywords,
    hashtags,
    hook_analysis,
    cta_analysis,
    scores,
    ai_recommendations,
  } = results

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Page header */}
        <div className="mb-8 animate-fade-in">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Analysis Results</h1>
              <div className="flex flex-wrap items-center gap-2 mt-1">
                <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">{filename}</span>
                <span className="text-slate-300 dark:text-slate-700">·</span>
                <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                  extraction_method === 'pymupdf'
                    ? 'text-sky-700 bg-sky-100 border border-sky-200 dark:text-sky-400 dark:bg-sky-500/10 dark:border-sky-500/20'
                    : extraction_method === 'tesseract_ocr'
                    ? 'text-violet-700 bg-violet-100 border border-violet-200 dark:text-violet-400 dark:bg-violet-500/10 dark:border-violet-500/20'
                    : 'text-emerald-700 bg-emerald-100 border border-emerald-200 dark:text-emerald-400 dark:bg-emerald-500/10 dark:border-emerald-500/20'
                }`}>
                  Extraction: {extraction_method === 'pymupdf' ? 'PyMuPDF' : extraction_method === 'tesseract_ocr' ? 'Tesseract OCR' : 'Direct Text'}
                </span>
              </div>
            </div>
            <button onClick={onReset} className="btn-secondary flex-shrink-0">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              New Analysis
            </button>
          </div>
        </div>

        {/* Top section: Overall score + Sentiment + Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1">
            <OverallScore score={scores.overall} />
          </div>
          <div className="lg:col-span-2 space-y-4">
            <SentimentCard sentiment={sentiment} />
            <MetricsCard metrics={metrics} />
          </div>
        </div>

        {/* Hook & CTA info cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <div className="glass-card p-5 border border-violet-200 dark:border-violet-500/15 animate-slide-up">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-slate-900 dark:text-white font-semibold text-sm flex items-center gap-2">
                <span>🪝</span> Hook Analysis
              </h3>
              <span className={`text-lg font-black ${
                hook_analysis.score >= 70 ? 'text-emerald-600 dark:text-emerald-400' : hook_analysis.score >= 45 ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400'
              }`}>
                {hook_analysis.score}
              </span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{hook_analysis.feedback}</p>
          </div>
          <div className="glass-card p-5 border border-sky-200 dark:border-sky-500/15 animate-slide-up">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-slate-900 dark:text-white font-semibold text-sm flex items-center gap-2">
                <span>📣</span> CTA Analysis
              </h3>
              <span className={`text-lg font-black ${
                cta_analysis.score >= 70 ? 'text-emerald-600 dark:text-emerald-400' : cta_analysis.score >= 40 ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400'
              }`}>
                {cta_analysis.score}
              </span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{cta_analysis.feedback}</p>
            {cta_analysis.detected_phrases?.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {cta_analysis.detected_phrases.slice(0, 4).map((phrase, i) => (
                  <span key={i} className="text-xs px-2.5 py-0.5 rounded-full bg-sky-100 dark:bg-sky-500/10 border border-sky-200 dark:border-sky-500/20 text-sky-700 dark:text-sky-400 font-medium">
                    "{phrase}"
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Score breakdown */}
        <div className="mb-6">
          <ScoreCards scores={scores} />
        </div>

        {/* Keywords + Hashtags */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <KeywordSection keywords={keywords} />
          <HashtagSection hashtags={hashtags} />
        </div>

        {/* AI Recommendations */}
        <div className="mb-6">
          <Recommendations aiRecommendations={ai_recommendations} />
        </div>

        {/* Improved post */}
        {ai_recommendations?.improved_post && (
          <div className="mb-6">
            <ImprovedPost improvedPost={ai_recommendations.improved_post} />
          </div>
        )}

        {/* Extracted text */}
        <div className="mb-8">
          <ExtractedText
            text={extracted_text}
            extractionMethod={extraction_method}
            charCount={char_count}
          />
        </div>

        {/* Bottom CTA */}
        <div className="text-center pb-8">
          <button onClick={onReset} className="btn-primary mx-auto shadow-md">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Analyze Another Post
          </button>
        </div>
      </div>
    </div>
  )
}
