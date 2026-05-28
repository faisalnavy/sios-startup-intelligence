'use client'
import { useEffect, useState } from 'react'
import { adminGetStats } from '../../lib/api'

interface StatCard {
  label: string
  value: string | number
  sub?: string
  color?: string
}

function Card({ label, value, sub, color = 'text-white' }: StatCard) {
  return (
    <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-5">
      <div className="text-xs text-[#64748b] mb-2 uppercase tracking-wide">{label}</div>
      <div className={`text-3xl font-bold ${color}`}>{value}</div>
      {sub && <div className="text-xs text-[#475569] mt-1">{sub}</div>}
    </div>
  )
}

const VERDICT_COLOR: Record<string, string> = {
  'STRONG BUY':       'bg-emerald-400',
  'BUY WITH CAUTION': 'bg-yellow-400',
  'WAIT & WATCH':     'bg-blue-400',
  'PIVOT REQUIRED':   'bg-orange-400',
  'DO NOT INVEST':    'bg-red-400',
  'unknown':          'bg-[#475569]',
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState('')

  useEffect(() => {
    adminGetStats()
      .then(setStats)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="flex items-center gap-3 text-[#64748b]">
        <span className="w-5 h-5 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
        Loading stats...
      </div>
    </div>
  )

  if (error) return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400">{error}</div>
    </div>
  )

  const a = stats?.analyses || {}
  const u = stats?.users || {}
  const r = stats?.revenue || {}
  const verdicts: Record<string, number> = a.by_verdict || {}

  const totalVerdict = Object.values(verdicts).reduce((s: number, v: number) => s + v, 0)

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Platform Overview</h1>
        <p className="text-[#64748b] text-sm mt-1">Real-time statistics for SIOS admin</p>
      </div>

      {/* Top KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card label="Total Users"        value={u.total ?? '—'}  color="text-white" />
        <Card label="Total Analyses"     value={a.total ?? '—'}  color="text-white" />
        <Card label="This Month"         value={a.this_month ?? '—'} sub="analyses" color="text-violet-400" />
        <Card label="Total Revenue"      value={r.total_usd != null ? `$${r.total_usd.toLocaleString()}` : '—'} color="text-emerald-400" />
      </div>

      {/* Analyses over time */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card label="Today"     value={a.today     ?? '—'} sub="analyses today"     color="text-white" />
        <Card label="This Week" value={a.this_week ?? '—'} sub="analyses this week" color="text-white" />
        <Card label="This Month" value={a.this_month ?? '—'} sub="analyses this month" color="text-violet-400" />
      </div>

      {/* Verdict Distribution */}
      {Object.keys(verdicts).length > 0 && (
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6">
          <h2 className="font-semibold text-white mb-5">Verdict Distribution</h2>
          <div className="space-y-3">
            {Object.entries(verdicts)
              .sort((a, b) => b[1] - a[1])
              .map(([verdict, count]) => {
                const pct = totalVerdict ? Math.round((count / totalVerdict) * 100) : 0
                const bar = VERDICT_COLOR[verdict] || 'bg-[#475569]'
                return (
                  <div key={verdict}>
                    <div className="flex items-center justify-between text-sm mb-1.5">
                      <span className="text-[#94a3b8]">{verdict || 'Unknown'}</span>
                      <span className="text-[#64748b] font-mono text-xs">{count} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-[#1e1e2e] rounded-full h-2">
                      <div className={`${bar} h-2 rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      )}

      {/* Quick links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { href: '/admin/users',     label: 'Manage Users',    icon: '👥', sub: `${u.total ?? 0} users` },
          { href: '/admin/analyses',  label: 'View Analyses',   icon: '🔍', sub: `${a.total ?? 0} total` },
          { href: '/admin/pricing',   label: 'Pricing & Codes', icon: '💳', sub: 'Packs + Discounts' },
          { href: '/dashboard',       label: 'User Dashboard',  icon: '⬅',  sub: 'Back to app' },
        ].map(item => (
          <a
            key={item.href}
            href={item.href}
            className="bg-[#111118] border border-[#1e1e2e] hover:border-[#2e2e3e] rounded-xl p-5 transition-colors group"
          >
            <div className="text-2xl mb-2">{item.icon}</div>
            <div className="font-semibold text-white text-sm group-hover:text-violet-300 transition-colors">{item.label}</div>
            <div className="text-xs text-[#475569] mt-0.5">{item.sub}</div>
          </a>
        ))}
      </div>
    </div>
  )
}
