'use client'
import { useEffect, useState } from 'react'
import {
  adminListCreditPacks,
  adminCreateCreditPack,
  adminUpdateCreditPack,
  adminDeleteCreditPack,
  adminListDiscounts,
  adminCreateDiscount,
  adminToggleDiscount,
  adminDeleteDiscount,
  adminGetCreditAdjustments,
} from '../../../lib/api'

// ── Credit Pack Modal ─────────────────────────────────────────────────────────
function PackModal({ pack, onSave, onClose }: {
  pack?: any
  onSave: (data: any) => Promise<void>
  onClose: () => void
}) {
  const [form, setForm] = useState({
    name:        pack?.name        ?? '',
    credits:     pack?.credits     ?? 10,
    price_usd:   pack?.price_usd   ?? 19.99,
    description: pack?.description ?? '',
    is_popular:  pack?.is_popular  ?? false,
    is_active:   pack?.is_active   ?? true,
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name.trim() || form.credits < 1 || form.price_usd <= 0) {
      setErr('Name, credits, and price are required')
      return
    }
    setSaving(true)
    try {
      await onSave({ ...form, credits: Number(form.credits), price_usd: Number(form.price_usd) })
      onClose()
    } catch (e: any) {
      setErr(e.message)
    }
    setSaving(false)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative bg-[#111118] border border-[#1e1e2e] rounded-2xl p-6 max-w-md w-full">
        <h3 className="text-white font-semibold mb-4">{pack ? 'Edit Credit Pack' : 'New Credit Pack'}</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            placeholder="Pack name (e.g. Starter)"
            className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50"
          />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#64748b] mb-1 block">Credits</label>
              <input
                type="number" min="1"
                value={form.credits}
                onChange={e => setForm(f => ({ ...f, credits: Number(e.target.value) }))}
                className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50"
              />
            </div>
            <div>
              <label className="text-xs text-[#64748b] mb-1 block">Price (USD)</label>
              <input
                type="number" min="0.01" step="0.01"
                value={form.price_usd}
                onChange={e => setForm(f => ({ ...f, price_usd: Number(e.target.value) }))}
                className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50"
              />
            </div>
          </div>
          <input
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Description (optional)"
            className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50"
          />
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_popular}
                onChange={e => setForm(f => ({ ...f, is_popular: e.target.checked }))}
                className="rounded"
              />
              <span className="text-sm text-[#94a3b8]">Mark as Popular</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
                className="rounded"
              />
              <span className="text-sm text-[#94a3b8]">Active</span>
            </label>
          </div>
          {err && <div className="text-xs text-red-400">{err}</div>}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border border-[#2e2e3e] text-[#94a3b8] py-2 rounded-lg text-sm">Cancel</button>
            <button type="submit" disabled={saving} className="flex-1 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-semibold">
              {saving ? 'Saving...' : 'Save Pack'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Discount Modal ────────────────────────────────────────────────────────────
function DiscountModal({ onSave, onClose }: {
  onSave: (data: any) => Promise<void>
  onClose: () => void
}) {
  const [form, setForm] = useState({
    code:         '',
    discount_pct: 10,
    max_uses:     '',
    expires_at:   '',
    description:  '',
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.code.trim() || form.discount_pct < 1 || form.discount_pct > 100) {
      setErr('Code and valid discount % (1-100) are required')
      return
    }
    setSaving(true)
    try {
      await onSave({
        code:         form.code.toUpperCase().trim(),
        discount_pct: Number(form.discount_pct),
        max_uses:     form.max_uses ? Number(form.max_uses) : null,
        expires_at:   form.expires_at ? new Date(form.expires_at).toISOString() : null,
        description:  form.description,
        is_active:    true,
      })
      onClose()
    } catch (e: any) {
      setErr(e.message)
    }
    setSaving(false)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative bg-[#111118] border border-[#1e1e2e] rounded-2xl p-6 max-w-md w-full">
        <h3 className="text-white font-semibold mb-4">Create Discount Code</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            value={form.code}
            onChange={e => setForm(f => ({ ...f, code: e.target.value.toUpperCase() }))}
            placeholder="CODE (e.g. LAUNCH20)"
            className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50 font-mono"
          />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#64748b] mb-1 block">Discount %</label>
              <input
                type="number" min="1" max="100"
                value={form.discount_pct}
                onChange={e => setForm(f => ({ ...f, discount_pct: Number(e.target.value) }))}
                className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50"
              />
            </div>
            <div>
              <label className="text-xs text-[#64748b] mb-1 block">Max Uses (optional)</label>
              <input
                type="number" min="1"
                value={form.max_uses}
                onChange={e => setForm(f => ({ ...f, max_uses: e.target.value }))}
                placeholder="Unlimited"
                className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#64748b] mb-1 block">Expires At (optional)</label>
            <input
              type="datetime-local"
              value={form.expires_at}
              onChange={e => setForm(f => ({ ...f, expires_at: e.target.value }))}
              className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50"
            />
          </div>
          <input
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Internal description (optional)"
            className="w-full bg-[#0a0a0f] border border-[#2e2e3e] rounded-lg px-3 py-2 text-sm text-white placeholder-[#475569] focus:outline-none focus:border-violet-500/50"
          />
          {err && <div className="text-xs text-red-400">{err}</div>}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border border-[#2e2e3e] text-[#94a3b8] py-2 rounded-lg text-sm">Cancel</button>
            <button type="submit" disabled={saving} className="flex-1 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-semibold">
              {saving ? 'Creating...' : 'Create Code'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function AdminPricing() {
  const [packs, setPacks]           = useState<any[]>([])
  const [discounts, setDiscounts]   = useState<any[]>([])
  const [adjustments, setAdj]       = useState<any[]>([])
  const [loading, setLoading]       = useState(true)
  const [showPackModal, setShowPack]  = useState(false)
  const [editPack, setEditPack]       = useState<any>(null)
  const [showDiscModal, setShowDisc]  = useState(false)
  const [deleting, setDeleting]       = useState<string | null>(null)

  async function loadAll() {
    setLoading(true)
    const [p, d, a] = await Promise.all([
      adminListCreditPacks(),
      adminListDiscounts(),
      adminGetCreditAdjustments(1, 20),
    ])
    setPacks(p)
    setDiscounts(d)
    setAdj(a.adjustments || [])
    setLoading(false)
  }

  useEffect(() => { loadAll() }, [])

  async function handleCreatePack(data: any) {
    await adminCreateCreditPack(data)
    await loadAll()
  }

  async function handleUpdatePack(packId: string, data: any) {
    await adminUpdateCreditPack(packId, data)
    await loadAll()
  }

  async function handleDeletePack(packId: string) {
    setDeleting(`pack:${packId}`)
    await adminDeleteCreditPack(packId)
    await loadAll()
    setDeleting(null)
  }

  async function handleCreateDiscount(data: any) {
    await adminCreateDiscount(data)
    await loadAll()
  }

  async function handleToggleDiscount(id: string) {
    await adminToggleDiscount(id)
    await loadAll()
  }

  async function handleDeleteDiscount(id: string) {
    setDeleting(`disc:${id}`)
    await adminDeleteDiscount(id)
    await loadAll()
    setDeleting(null)
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <span className="w-5 h-5 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
    </div>
  )

  return (
    <>
      {(showPackModal || editPack) && (
        <PackModal
          pack={editPack}
          onSave={editPack
            ? (data) => handleUpdatePack(editPack.id, data)
            : handleCreatePack}
          onClose={() => { setShowPack(false); setEditPack(null) }}
        />
      )}
      {showDiscModal && (
        <DiscountModal
          onSave={handleCreateDiscount}
          onClose={() => setShowDisc(false)}
        />
      )}

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-10">
        <div>
          <h1 className="text-2xl font-bold text-white">Pricing Management</h1>
          <p className="text-[#64748b] text-sm mt-1">Credit packs, discount codes, and adjustment history</p>
        </div>

        {/* ── Credit Packs ────────────────────────────────────────────── */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Credit Packs</h2>
            <button
              onClick={() => { setEditPack(null); setShowPack(true) }}
              className="bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              + New Pack
            </button>
          </div>

          {packs.length === 0 ? (
            <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-8 text-center text-[#475569]">
              No credit packs. Create your first one.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {packs.map(pack => (
                <div
                  key={pack.id}
                  className={`bg-[#111118] border rounded-xl p-5 relative ${
                    pack.is_popular ? 'border-violet-500/40' : 'border-[#1e1e2e]'
                  } ${!pack.is_active ? 'opacity-50' : ''}`}
                >
                  {pack.is_popular && (
                    <div className="absolute -top-2.5 left-4">
                      <span className="bg-violet-600 text-white text-xs font-bold px-2 py-0.5 rounded">
                        POPULAR
                      </span>
                    </div>
                  )}
                  {!pack.is_active && (
                    <div className="absolute -top-2.5 right-4">
                      <span className="bg-[#475569] text-white text-xs font-bold px-2 py-0.5 rounded">
                        INACTIVE
                      </span>
                    </div>
                  )}
                  <div className="text-2xl font-bold text-white">${pack.price_usd}</div>
                  <div className="text-lg font-semibold text-violet-300 mt-1">{pack.name}</div>
                  <div className="text-sm text-[#64748b] mt-0.5">{pack.credits} credits</div>
                  {pack.description && (
                    <div className="text-xs text-[#475569] mt-2">{pack.description}</div>
                  )}
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => setEditPack(pack)}
                      className="flex-1 text-xs border border-[#2e2e3e] hover:border-violet-500/40 text-[#94a3b8] hover:text-violet-300 py-1.5 rounded-lg transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleUpdatePack(pack.id, { is_active: !pack.is_active })}
                      className="flex-1 text-xs border border-[#2e2e3e] hover:border-yellow-500/40 text-[#94a3b8] hover:text-yellow-300 py-1.5 rounded-lg transition-colors"
                    >
                      {pack.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleDeletePack(pack.id)}
                      disabled={deleting === `pack:${pack.id}`}
                      className="text-xs border border-[#2e2e3e] hover:border-red-500/30 text-[#64748b] hover:text-red-400 px-2.5 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                    >
                      {deleting === `pack:${pack.id}` ? '…' : '🗑'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── Discount Codes ───────────────────────────────────────────── */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Discount Codes</h2>
            <button
              onClick={() => setShowDisc(true)}
              className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              + New Code
            </button>
          </div>

          {discounts.length === 0 ? (
            <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-8 text-center text-[#475569]">
              No discount codes.
            </div>
          ) : (
            <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#1e1e2e]">
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Code</th>
                    <th className="text-center px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Discount</th>
                    <th className="text-center px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Uses</th>
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Expires</th>
                    <th className="text-center px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Status</th>
                    <th className="text-right px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {discounts.map(d => (
                    <tr key={d.id} className="border-b border-[#1e1e2e] last:border-0 hover:bg-[#0d0d14] transition-colors">
                      <td className="px-4 py-3">
                        <span className="text-white font-mono font-semibold">{d.code}</span>
                        {d.description && <div className="text-xs text-[#475569] mt-0.5">{d.description}</div>}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="text-emerald-400 font-bold font-mono">{d.discount_pct}%</span>
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-[#94a3b8]">
                        {d.uses_count ?? 0}{d.max_uses ? `/${d.max_uses}` : ''}
                      </td>
                      <td className="px-4 py-3 text-xs text-[#64748b]">
                        {d.expires_at ? new Date(d.expires_at).toLocaleDateString() : '—'}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                          d.is_active
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : 'bg-[#1e1e2e] text-[#64748b]'
                        }`}>
                          {d.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleToggleDiscount(d.id)}
                            className="text-xs border border-[#2e2e3e] hover:border-yellow-500/30 text-[#64748b] hover:text-yellow-300 px-2 py-1 rounded transition-colors"
                          >
                            {d.is_active ? 'Disable' : 'Enable'}
                          </button>
                          <button
                            onClick={() => handleDeleteDiscount(d.id)}
                            disabled={deleting === `disc:${d.id}`}
                            className="text-xs border border-[#2e2e3e] hover:border-red-500/30 text-[#64748b] hover:text-red-400 px-2 py-1 rounded transition-colors disabled:opacity-50"
                          >
                            {deleting === `disc:${d.id}` ? '…' : '🗑'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* ── Credit Adjustment History ─────────────────────────────────── */}
        {adjustments.length > 0 && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-white">Recent Credit Adjustments</h2>
            <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#1e1e2e]">
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">User</th>
                    <th className="text-center px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Delta</th>
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Reason</th>
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Admin</th>
                    <th className="text-left px-4 py-3 text-xs text-[#64748b] font-medium uppercase tracking-wide">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {adjustments.map((a: any) => (
                    <tr key={a.id} className="border-b border-[#1e1e2e] last:border-0 hover:bg-[#0d0d14] transition-colors">
                      <td className="px-4 py-3 text-xs text-[#64748b] font-mono">
                        {a.user_id?.slice(0, 10)}…
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-bold font-mono text-sm ${a.delta > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {a.delta > 0 ? '+' : ''}{a.delta}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-[#94a3b8]">{a.reason}</td>
                      <td className="px-4 py-3 text-xs text-[#64748b] font-mono">
                        {a.admin_id?.slice(0, 10)}…
                      </td>
                      <td className="px-4 py-3 text-xs text-[#64748b]">
                        {new Date(a.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </>
  )
}
