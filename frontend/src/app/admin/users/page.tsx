'use client'
import { useEffect, useState } from 'react'
import {
  adminListUsers,
  adminAdjustCredits,
  adminToggleSuspend,
  adminGetUserDetail,
} from '../../../lib/api'

interface User {
  id: string
  email: string
  credits: number
  is_admin: boolean
  is_suspended: boolean
  created_at: string
}

function Badge({ children, color }: { children: React.ReactNode; color: string }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded font-medium ${color}`}>{children}</span>
  )
}

// ── User Detail Drawer ────────────────────────────────────────────────────────
function UserDrawer({ userId, onClose }: { userId: string; onClose: () => void }) {
  const [detail, setDetail]           = useState<any>(null)
  const [loading, setLoading]         = useState(true)
  const [delta, setDelta]             = useState('')
  const [reason, setReason]           = useState('')
  const [adjusting, setAdjusting]     = useState(false)
  const [adjustMsg, setAdjustMsg]     = useState('')

  useEffect(() => {
    adminGetUserDetail(userId).then(setDetail).finally(() => setLoading(false))
  }, [userId])

  async function handleAdjust() {
    const d = parseInt(delta)
    if (!d || !reason.trim()) return
    setAdjusting(true)
    try {
      await adminAdjustCredits(userId, d, reason.trim())
      setAdjustMsg(`Credits adjusted by ${d > 0 ? '+' : ''}${d}`)
      setDelta('')
      setReason('')
      // Reload detail
      const updated = await adminGetUserDetail(userId)
      setDetail(updated)
    } catch (e: any) {
      setAdjustMsg(`Error: ${e.message}`)
    } finally {
      setAdjusting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative ml-auto w-full max-w-lg bg-[#0d0d14] border-l border-[#1e1e2e] flex flex-col overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b border-[#1e1e2e]">
          <h2 className="font-semibold text-white">User Detail</h2>
          <button onClick={onClose} className="text-[#64748b] hover:text-white text-xl px-2">×</button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center text-[#64748b]">
            <span className="w-5 h-5 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
          </div>
        ) : detail ? (
          <div className="p-5 space-y-6">
            {/* User info */}
            <div>
              <div className="text-white font-semibold">{detail.user?.email}</div>
              <div className="text-xs text-[#64748b] mt-0.5">ID: {detail.user?.id}</div>
              <div className="flex gap-2 mt-2">
                <Badge color="bg-violet-500/20 text-violet-300">
                  {detail.user?.credits ?? 0} credits
                </Badge>
                {detail.user?.is_admin && <Badge color="bg-red-500/20 text-red-300">Admin</Badge>}
                {detail.user?.is_suspended && <Badge color="bg-yellow-500/20 text-yellow-300">Suspended</Badge>}
              </div>
              <div className="text-xs text-[#475569] mt-1">
                Joined {new Date(detail.user?.created_at).toLocaleDateString()}
              </div>
            </div>

            {/* Credit adjustment */}
            <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-4">
              <h3 className="text-sm font-semibold text-white mb-3">Adjust Credits</h3>
              <div className="flex gap-2 mb-2">
                <input
                  type="number"
                  value={delta}
                  onChange={e => setDelta(e.target.value)}
                  placeholder="+5 or -2"
                  className="flex-1 bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50"
                />
              </div>
              <input
                type="text"
                value={reason}
                onChange={e => setReason(e.target.value)}
                placeholder="Reason for adjustment..."
                className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50 mb-2"
              />
              <button
                onClick={handleAdjust}
                disabled={adjusting || !delta || !reason.trim()}
                className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
              >
                {adjusting ? 'Applying...' : 'Apply Adjustment'}
              </button>
              {adjustMsg && (
                <div className={`text-xs mt-2 ${adjustMsg.startsWith('Error') ? 'text-red-400' : 'text-emerald-400'}`}>
                  {adjustMsg}
                </div>
              )}
            </div>

            {/* Recent analyses */}
            {detail.analyses?.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-white mb-3">Recent Analyses ({detail.analyses.length})</h3>
                <div className="space-y-2">
                  {detail.analyses.slice(0, 10).map((a: any) => (
                    <a
                      key={a.id}
                      href={`/analysis/${a.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block bg-[#111118] border border-[#1e1e2e] rounded-lg px-3 py-2.5 hover:border-[#2e2e3e] transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-white text-sm">{a.startup_name}</span>
                        <span className="text-xs text-[#64748b]">{a.verdict || a.status}</span>
                      </div>
                      <div className="text-xs text-[#475569] mt-0.5">
                        {new Date(a.created_at).toLocaleDateString()} · Score: {a.score ?? '—'}
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Payment history */}
            {detail.payments?.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-white mb-3">Payment History ({detail.payments.length})</h3>
                <div className="space-y-2">
                  {detail.payments.slice(0, 5).map((p: any) => (
                    <div key={p.id} className="bg-[#111118] border border-[#1e1e2e] rounded-lg px-3 py-2.5">
                      <div className="flex justify-between">
                        <span className="text-white text-sm">${p.amount_usd}</span>
                        <Badge color={p.status === 'completed' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-yellow-500/20 text-yellow-300'}>
                          {p.status}
                        </Badge>
                      </div>
                      <div className="text-xs text-[#475569] mt-0.5">
                        +{p.credits_added} credits · {new Date(p.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-[#64748b]">No data</div>
        )}
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function AdminUsers() {
  const [users, setUsers]           = useState<User[]>([])
  const [total, setTotal]           = useState(0)
  const [page, setPage]             = useState(1)
  const [search, setSearch]         = useState('')
  const [loading, setLoading]       = useState(true)
  const [selectedUser, setSelectedUser] = useState<string | null>(null)
  const [suspending, setSuspending] = useState<string | null>(null)

  const PER_PAGE = 50

  async function load(p = page, q = search) {
    setLoading(true)
    try {
      const data = await adminListUsers(p, PER_PAGE, q || undefined)
      setUsers(data.users || [])
      setTotal(data.total || 0)
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load(1, '') }, [])

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    load(1, search)
  }

  async function handleSuspend(userId: string) {
    setSuspending(userId)
    try {
      await adminToggleSuspend(userId)
      await load(page, search)
    } catch {}
    setSuspending(null)
  }

  return (
    <>
      {selectedUser && (
        <UserDrawer
          userId={selectedUser}
          onClose={() => { setSelectedUser(null); load(page, search) }}
        />
      )}

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">User Management</h1>
            <p className="text-[#64748b] text-sm mt-1">{total} total users</p>
          </div>
        </div>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by email..."
            className="flex-1 max-w-sm bg-[#111118] border border-[#1e1e2e] rounded-lg px-4 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50"
          />
          <button
            type="submit"
            className="bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
          >
            Search
          </button>
          {search && (
            <button
              type="button"
              onClick={() => { setSearch(''); setPage(1); load(1, '') }}
              className="text-[#64748b] hover:text-white border border-[#1e1e2e] px-3 py-2 rounded-lg text-sm transition-colors"
            >
              Clear
            </button>
          )}
        </form>

        {/* Table */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-20 text-[#64748b]">
              <span className="w-5 h-5 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin mr-3" />
              Loading...
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-20 text-[#475569]">No users found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#1e1e2e]">
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Email</th>
                    <th className="text-center px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Credits</th>
                    <th className="text-center px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Status</th>
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Joined</th>
                    <th className="text-right px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} className="border-b border-[#1e1e2e] last:border-0 hover:bg-[#0d0d14] transition-colors">
                      <td className="px-4 py-3">
                        <button
                          onClick={() => setSelectedUser(u.id)}
                          className="text-white hover:text-violet-300 text-sm font-medium text-left transition-colors"
                        >
                          {u.email}
                        </button>
                        <div className="text-xs text-[#475569] mt-0.5 font-mono">{u.id.slice(0, 8)}…</div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="text-white font-bold font-mono">{u.credits}</span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          {u.is_suspended && <Badge color="bg-red-500/20 text-red-300">Suspended</Badge>}
                          {u.is_admin    && <Badge color="bg-orange-500/20 text-orange-300">Admin</Badge>}
                          {!u.is_suspended && !u.is_admin && <Badge color="bg-emerald-500/20 text-emerald-300">Active</Badge>}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-xs text-[#64748b]">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setSelectedUser(u.id)}
                            className="text-xs text-violet-400 hover:text-violet-300 border border-violet-500/30 hover:border-violet-500/50 px-2 py-1 rounded transition-colors"
                          >
                            Details
                          </button>
                          <button
                            onClick={() => handleSuspend(u.id)}
                            disabled={suspending === u.id}
                            className="text-xs text-[#64748b] hover:text-yellow-300 border border-[#2e2e3e] hover:border-yellow-500/30 px-2 py-1 rounded transition-colors disabled:opacity-50"
                          >
                            {suspending === u.id ? '…' : u.is_suspended ? 'Unsuspend' : 'Suspend'}
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
                onClick={() => { setPage(p => p - 1); load(page - 1, search) }}
                className="border border-[#1e1e2e] hover:border-[#2e2e3e] text-[#94a3b8] hover:text-white px-3 py-1.5 rounded-lg disabled:opacity-30 transition-colors"
              >
                ← Prev
              </button>
              <button
                disabled={page * PER_PAGE >= total}
                onClick={() => { setPage(p => p + 1); load(page + 1, search) }}
                className="border border-[#1e1e2e] hover:border-[#2e2e3e] text-[#94a3b8] hover:text-white px-3 py-1.5 rounded-lg disabled:opacity-30 transition-colors"
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
