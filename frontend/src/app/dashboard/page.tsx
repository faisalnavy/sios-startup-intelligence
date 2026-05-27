'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { getUserAnalyses, getUserCredits } from '../../lib/api'

const VERDICT_CONFIG: Record<string, { color: string; bg: string }> = {
  'STRONG BUY':       { color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
  'BUY WITH CAUTION': { color: 'text-yellow-400',  bg: 'bg-yellow-400/10'  },
  'WAIT & WATCH':     { color: 'text-blue-400',    bg: 'bg-blue-400/10'    },
  'PIVOT REQUIRED':   { color: 'text-orange-400',  bg: 'bg-orange-400/10'  },
  'DO NOT INVEST':    { color: 'text-red-400',     bg: 'bg-red-400/10'     },
}

export default function DashboardHome() {
  const [analyses, setAnalyses] = useState<any[]>([])
  const [credits, setCredits] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getUserAnalyses(), getUserCredits()])
      .then(([a, c]) => { setAnalyses(a); setCredits(c) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const thisMonth = analyses.filter(a =>
    new Date(a.created_at) > new Date(Date.now() - 30 * 86_400_000)
  ).length
  const completed = analyses.filter(a => a.status === 'completed').length

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-[#64748b] mt-1">Your startup intelligence overview</p>
        </div>
        <Link href="/dashboard/new" className="btn-primary text-sm px-5 py-2.5">
          + New Analysis
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { l: 'Credits',    v: credits,     sub: 'available',  accent: 'text-violet-400' },
          { l: 'Reports',    v: analyses.length, sub: 'total',  accent: 'text-white' },
          { l: 'This Month', v: thisMonth,   sub: 'analyses',   accent: 'text-white' },
          { l: 'Completed',  v: completed,   sub: 'finished',   accent: 'text-emerald-400' },
        ].map(s => (
          <div key={s.l} className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-4">
            <div className="text-xs text-[#64748b] mb-1">{s.l}</div>
            <div className={`text-3xl font-bold ${s.accent}`}>{loading ? '…' : s.v}</div>
            <div className="text-xs text-[#475569] mt-1">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Low credit warning */}
      {credits < 2 && !loading && (
        <div className="mb-6 bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-amber-400 font-medium text-sm">Low credits</div>
            <div className="text-[#94a3b8] text-sm mt-0.5">You have {credits} credit{credits !== 1 ? 's' : ''} remaining. Purchase more to continue analyzing.</div>
          </div>
          <Link href="/dashboard/credits" className="btn-primary text-sm px-4 py-2 flex-shrink-0">
            Buy Credits
          </Link>
        </div>
      )}

      {/* Recent analyses */}
      <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-[#1e1e2e]">
          <h2 className="font-semibold text-white">Recent Analyses</h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-[#64748b] text-sm">Loading your analyses...</div>
        ) : analyses.length === 0 ? (
          <div className="p-14 text-center">
            <div className="text-5xl mb-4">🚀</div>
            <p className="text-[#94a3b8] mb-2 font-medium">No analyses yet</p>
            <p className="text-[#64748b] text-sm mb-6">Submit your first startup idea and get a full AI intelligence report.</p>
            <Link href="/dashboard/new" className="btn-primary text-sm px-6 py-2.5 inline-block">
              Start Your First Analysis
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-[#1e1e2e]">
            {analyses.map((a: any) => {
              const vc = VERDICT_CONFIG[a.verdict] || { color: 'text-[#94a3b8]', bg: 'bg-[#1e1e2e]' }
              return (
                <Link
                  href={`/analysis/${a.id}`}
                  key={a.id}
                  className="flex items-center gap-4 px-6 py-4 hover:bg-[#0d0d18] transition-colors"
                >
                  <div className="w-9 h-9 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-300 font-bold text-sm flex-shrink-0">
                    {a.startup_name?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white truncate">{a.startup_name}</div>
                    <div className="text-xs text-[#64748b] mt-0.5">
                      {new Date(a.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                      {a.score ? ` · Score: ${a.score}/100` : ''}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {a.verdict && (
                      <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${vc.bg} ${vc.color}`}>
                        {a.verdict}
                      </span>
                    )}
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      a.status === 'completed' ? 'text-emerald-400 bg-emerald-400/10' : 'text-yellow-400 bg-yellow-400/10'
                    }`}>
                      {a.status}
                    </span>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
