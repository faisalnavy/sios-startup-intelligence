'use client'
import { useEffect, useState } from 'react'
import { adminListAnalyses, adminDeleteAnalysis } from '../../../lib/api'

const VERDICTS = ['', 'STRONG BUY', 'BUY WITH CAUTION', 'WAIT & WATCH', 'PIVOT REQUIRED', 'DO NOT INVEST']

const VERDICT_STYLE: Record<string, string> = {
  'STRONG BUY':       'bg-emerald-500/20 text-emerald-300',
  'BUY WITH CAUTION': 'bg-yellow-500/20 text-yellow-300',
  'WAIT & WATCH':     'bg-blue-500/20 text-blue-300',
  'PIVOT REQUIRED':   'bg-orange-500/20 text-orange-300',
  'DO NOT INVEST':    'bg-red-500/20 text-red-300',
}

export default function AdminAnalyses() {
  const [items, setItems]             = useState<any[]>([])
  const [total, setTotal]             = useState(0)
  const [page, setPage]               = useState(1)
  const [verdict, setVerdict]         = useState('')
  const [loading, setLoading]         = useState(true)
  const [deleting, setDeleting]       = useState<string | null>(null)
  const [confirmDelete, setConfirm]   = useState<string | null>(null)

  const PER_PAGE = 50

  async function load(p = page, v = verdict) {
    setLoading(true)
    try {
      const data = await adminListAnalyses(p, PER_PAGE, v || undefined)
      setItems(data.analyses || [])
      setTotal(data.total || 0)
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load(1, '') }, [])

  async function handleDelete(id: string) {
    setDeleting(id)
    try {
      await adminDeleteAnalysis(id)
      setConfirm(null)
      await load(page, verdict)
    } catch {}
    setDeleting(null)
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analysis Moderation</h1>
          <p className="text-[#64748b] text-sm mt-1">{total} total analyses</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {VERDICTS.map(v => (
          <button
            key={v || 'all'}
            onClick={() => { setVerdict(v); setPage(1); load(1, v) }}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
              verdict === v
                ? 'bg-violet-600 border-violet-600 text-white'
                : 'border-[#1e1e2e] text-[#94a3b8] hover:border-[#2e2e3e] hover:text-white'
            }`}
          >
            {v || 'All Verdicts'}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20 text-[#64748b]">
            <span className="w-5 h-5 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin mr-3" />
            Loading...
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20 text-[#475569]">No analyses found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#1e1e2e]">
                  <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Startup</th>
                  <th className="text-center px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Score</th>
                  <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Verdict</th>
                  <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">User</th>
                  <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Date</th>
                  <th className="text-right px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id} className="border-b border-[#1e1e2e] last:border-0 hover:bg-[#0d0d14] transition-colors">
                    <td className="px-4 py-3">
                      <a
                        href={`/analysis/${item.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-white hover:text-violet-300 text-sm font-medium transition-colors"
                      >
                        {item.startup_name}
                      </a>
                      <div className="text-xs text-[#475569] mt-0.5 font-mono">{item.id.slice(0, 8)}…</div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {item.score != null ? (
                        <span className={`font-bold font-mono text-sm ${
                          item.score >= 70 ? 'text-emerald-400' :
                          item.score >= 50 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                          {item.score}
                        </span>
                      ) : <span className="text-[#475569]">—</span>}
                    </td>
                    <td className="px-4 py-3">
                      {item.verdict ? (
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${VERDICT_STYLE[item.verdict] || 'bg-[#1e1e2e] text-[#94a3b8]'}`}>
                          {item.verdict}
                        </span>
                      ) : (
                        <span className="text-xs text-[#475569]">{item.status}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-[#64748b] font-mono">
                      {item.user_id?.slice(0, 8)}…
                    </td>
                    <td className="px-4 py-3 text-xs text-[#64748b]">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <a
                          href={`/analysis/${item.id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-violet-400 hover:text-violet-300 border border-violet-500/30 hover:border-violet-500/50 px-2 py-1 rounded transition-colors"
                        >
                          View
                        </a>
                        <button
                          onClick={() => setConfirm(item.id)}
                          className="text-xs text-[#64748b] hover:text-red-400 border border-[#2e2e3e] hover:border-red-500/30 px-2 py-1 rounded transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {total > PER_PAGE && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-[#64748b]">
            Showing {(page - 1) * PER_PAGE + 1}–{Math.min(page * PER_PAGE, total)} of {total}
          </span>
          <div className="flex gap-2">
            <button
              disabled={page === 1}
              onClick={() => { setPage(p => p - 1); load(page - 1, verdict) }}
              className="border border-[#1e1e2e] hover:border-[#2e2e3e] text-[#94a3b8] hover:text-white px-3 py-1.5 rounded-lg disabled:opacity-30 transition-colors"
            >
              ← Prev
            </button>
            <button
              disabled={page * PER_PAGE >= total}
              onClick={() => { setPage(p => p + 1); load(page + 1, verdict) }}
              className="border border-[#1e1e2e] hover:border-[#2e2e3e] text-[#94a3b8] hover:text-white px-3 py-1.5 rounded-lg disabled:opacity-30 transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/70" onClick={() => setConfirm(null)} />
          <div className="relative bg-[#111118] border border-[#1e1e2e] rounded-2xl p-6 max-w-sm w-full text-center">
            <div className="text-3xl mb-3">⚠️</div>
            <h3 className="text-white font-semibold mb-2">Delete Analysis?</h3>
            <p className="text-[#94a3b8] text-sm mb-5">
              This will permanently delete the analysis and its report. This cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirm(null)}
                className="flex-1 border border-[#2e2e3e] text-[#94a3b8] hover:text-white py-2 rounded-lg text-sm transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(confirmDelete)}
                disabled={deleting === confirmDelete}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-semibold transition-colors"
              >
                {deleting === confirmDelete ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
