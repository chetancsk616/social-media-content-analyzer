import React from 'react'
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts'

function getScoreColor(score) {
  if (score >= 75) return '#10B981' // emerald
  if (score >= 55) return '#F59E0B' // amber
  return '#F43F5E' // rose
}

function getScoreLabel(score) {
  if (score >= 85) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 55) return 'Moderate'
  if (score >= 40) return 'Needs Work'
  return 'Poor'
}

export default function OverallScore({ score }) {
  const color = getScoreColor(score)
  const label = getScoreLabel(score)

  const data = [{ value: score, fill: color }]

  return (
    <div className="glass-card p-8 flex flex-col items-center text-center animate-slide-up">
      {/* Title */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-300">Engagement Optimization Score</h2>
        <p className="text-xs text-slate-500 mt-1">
          Heuristic analytical score — not a guarantee of actual engagement
        </p>
      </div>

      {/* Radial chart */}
      <div className="relative w-56 h-56">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="70%"
            outerRadius="90%"
            barSize={12}
            data={data}
            startAngle={90}
            endAngle={-270}
          >
            <PolarAngleAxis
              type="number"
              domain={[0, 100]}
              angleAxisId={0}
              tick={false}
            />
            {/* Background track */}
            <RadialBar
              background={{ fill: 'rgba(255,255,255,0.04)' }}
              dataKey="value"
              cornerRadius={8}
            />
          </RadialBarChart>
        </ResponsiveContainer>

        {/* Centre text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-5xl font-black tabular-nums"
            style={{ color }}
          >
            {score}
          </span>
          <span className="text-slate-400 text-sm font-medium mt-1">/ 100</span>
        </div>

        {/* Glow ring */}
        <div
          className="absolute inset-8 rounded-full opacity-20 blur-2xl pointer-events-none"
          style={{ background: color }}
        />
      </div>

      {/* Score label badge */}
      <div
        className="mt-6 px-5 py-2 rounded-full font-semibold text-sm border"
        style={{
          color,
          borderColor: color + '40',
          background: color + '15',
        }}
      >
        {label}
      </div>

      {/* Score tier description */}
      <p className="mt-3 text-xs text-slate-500 max-w-xs">
        {score >= 75
          ? 'This content is well-optimized. Minor tweaks can push it further.'
          : score >= 55
          ? 'Solid foundation. Apply the recommendations to boost engagement.'
          : 'Significant improvements available. Review all recommendations below.'}
      </p>
    </div>
  )
}
