'use client'
import { useEffect, useState } from 'react'
import { getUserAnalyses, getUserCredits } from '../../../lib/api'

const VERDICT_CONFIG: Record<string, { color: string; bg: string }> = {
  'STRONG BUY':       { color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
  'BUY WITH CAUTION': { color: 'text-yellow-400',  bg: 'bg-yellow-400/10'  },
  'WAIT & WATCH':     { color: 'text-blue-400',    bg: 'bg-blue-400/10'    },
  'PIVOT REQUIRED':   { color: 'text-orange-400',  bg: 'bg-orange-400/10'  },
  'DO NOT INVEST':    { color: 'text-red-400',     bg: 'bg-red-400/10'     },
}

export default function UsagePage() {
  const [analyses, setAnalyses] = useState<any[]>([])
  const [credits, setCredits] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getUserAnalyses(), getUserCredits()])
      .then(([a, c]) => { setAnalyses(a); setCredits(c) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const completed = analyses.filter(a => a.status === 'completed')
  const thisMonth = analyses.filter(a => new Date(a.created_at) > new Date(Date.now() - 30 * 86_400_000))

  // Verdict distribution
  const verdictCounts: Record<string, number> = {}
  completed.forEach(a => {
    if (a.verdict) verdictCounts[a.verdict] = (verdictCounts[a.verdict] || 0) + 1
  })

  // Average score
  const avgScore = completed.length
    ? Math.round(completed.reduce((s, a) => s + (a.score || 0), 0) / completed.length)
    : 0

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Usage Analytics</h1>
        <p className="text-sm text-[#64748b]">Your SIOS activity and analysis statistics</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { l: 'Credits Left',     v: credits,             accent: 'text-violet-400' },
          { l: 'Total Analyses',   v: analyses.length,     accent: 'text-white' },
          { l: 'This Month',       v: thisMonth.length,    accent: 'text-white' },
          { l: 'Avg Score',        v: avgScore ? `${avgScore}/100` : '—', accent: 'text-white' },
        ].map(s => (
          <div key={s.l} className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-4">
            <div className="text-xs text-[#64748b] mb-1">{s.l}</div>
            <div className={`text-3xl font-bold ${s.accent}`}>{loading ? '…' : s.v}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Verdict breakdown */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6">
          <h2 className="font-semibold text-white mb-4">Verdict Distribution</h2>
          {completed.length === 0 ? (
            <p className="text-sm text-[#64748b]">No completed analyses yet.</p>
          ) : (
            <div className="space-y-3">
              {Object.entries(verdictCounts).map(([verdict, count]) => {
                const vc = VERDICT_CONFIG[verdict] || { color: 'text-[#94a3b8]', bg: 'bg-[#1e1e2e]' }
                const pct = Math.round((count / completed.length) * 100)
                return (
                  <div key={verdict}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className={vc.color}>{verdict}</span>
                      <span className="text-[#64748b]">{count} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 bg-[#1e1e2e] rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${vc.bg.replace('/10', '')}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Monthly activity */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6">
          <h2 className="font-semibold text-white mb-4">Monthly Activity</h2>
          {analyses.length === 0 ? (
            <p className="text-sm text-[#64748b]">No analyses yet. Start your first one!</p>
          ) : (
            <div className="space-y-2">
              {(() => {
                const months: Record<string, number> = {}
                analyses.forEach(a => {
                  const key = new Date(a.created_at).toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
                  months[key] = (months[key] || 0) + 1
                })
                const max = Math.max(...Object.values(months))
                return Object.entries(months).slice(-6).map(([month, count]) => (
                  <div key={month}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-[#94a3b8]">{month}</span>
                      <span className="text-[#64748b]">{count} {count === 1 ? 'analysis' : 'analyses'}</span>
                    </div>
                    <div className="h-1.5 bg-[#1e1e2e] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-violet-500 rounded-full transition-all duration-700"
                        style={{ width: `${(count / max) * 100}%` }}
                      />
                    </div>
                  </div>
                ))
              })()}
            </div>
          )}
        </div>
      </div>

      {/* Top startups by score */}
      {completed.length > 0 && (
        <div className="mt-6 bg-[#111118] border border-[#1e1e2e] rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-[#1e1e2e]">
            <h2 className="font-semibold text-white">Top Startups by Score</h2>
          </div>
          <div className="divide-y divide-[#1e1e2e]">
            {[...completed]
              .sort((a, b) => (b.score || 0) - (a.score || 0))
              .slice(0, 5)
              .map(a => {
                const vc = VERDICT_CONFIG[a.verdict] || { color: 'text-[#94a3b8]', bg: 'bg-[#1e1e2e]' }
                return (
                  <div key={a.id} className="flex items-center gap-4 px-6 py-3">
                    <div className="text-2xl font-bold text-[#2e2e3e] w-8 flex-shrink-0">
                      {a.score || '—'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-white truncate">{a.startup_name}</div>
                      <div className="text-xs text-[#64748b]">
                        {new Date(a.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    {a.verdict && (
                      <span className={`text-xs font-bold px-2.5 py-1 rounded-full flex-shrink-0 ${vc.bg} ${vc.color}`}>
                        {a.verdict}
                      </span>
                    )}
                  </div>
                )
              })}
          </div>
        </div>
      )}
    </div>
  )
}
