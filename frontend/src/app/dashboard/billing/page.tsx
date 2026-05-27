'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { getPaymentHistory } from '../../../lib/api'

export default function BillingPage() {
  const [payments, setPayments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getPaymentHistory()
      .then(setPayments)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Billing History</h1>
          <p className="text-sm text-[#64748b]">All credit purchases and transactions</p>
        </div>
        <Link href="/dashboard/credits" className="btn-primary text-sm px-5 py-2.5">
          + Buy Credits
        </Link>
      </div>

      <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl overflow-hidden">
        {/* Table header */}
        <div className="grid grid-cols-4 gap-4 px-6 py-3 border-b border-[#1e1e2e] bg-[#0d0d14]">
          <div className="text-xs font-medium text-[#64748b] uppercase tracking-wider">Date</div>
          <div className="text-xs font-medium text-[#64748b] uppercase tracking-wider">Pack</div>
          <div className="text-xs font-medium text-[#64748b] uppercase tracking-wider">Credits</div>
          <div className="text-xs font-medium text-[#64748b] uppercase tracking-wider">Amount</div>
        </div>

        {loading ? (
          <div className="px-6 py-10 text-center text-[#64748b] text-sm">Loading billing history...</div>
        ) : payments.length === 0 ? (
          <div className="px-6 py-14 text-center">
            <div className="text-4xl mb-3">💳</div>
            <p className="text-[#94a3b8] mb-1 font-medium">No payments yet</p>
            <p className="text-[#64748b] text-sm mb-5">Purchase credits to start analyzing startups.</p>
            <Link href="/dashboard/credits" className="btn-primary text-sm px-5 py-2.5 inline-block">
              Buy Credits
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-[#1e1e2e]">
            {payments.map((p: any, i: number) => (
              <div key={p.id || i} className="grid grid-cols-4 gap-4 px-6 py-4 items-center">
                <div className="text-sm text-[#94a3b8]">
                  {p.created_at ? new Date(p.created_at).toLocaleDateString('en-IN', {
                    day: 'numeric', month: 'short', year: 'numeric'
                  }) : '—'}
                </div>
                <div className="text-sm text-white capitalize">{p.pack_id || '—'}</div>
                <div className="text-sm text-violet-400 font-medium">
                  +{p.credits_added ?? p.credits ?? '—'} credits
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white font-medium">
                    ${typeof p.amount_usd === 'number' ? p.amount_usd.toFixed(2) : p.amount || '—'}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    p.status === 'completed'
                      ? 'text-emerald-400 bg-emerald-400/10'
                      : 'text-yellow-400 bg-yellow-400/10'
                  }`}>
                    {p.status || 'completed'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info section */}
      {!loading && payments.length > 0 && (
        <div className="mt-6 bg-[#111118] border border-[#1e1e2e] rounded-xl p-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-white">Total Spent</div>
              <div className="text-xs text-[#64748b] mt-0.5">Across all purchases</div>
            </div>
            <div className="text-2xl font-bold text-white">
              ${payments.reduce((sum, p) => sum + (p.amount_usd || p.amount || 0), 0).toFixed(2)}
            </div>
          </div>
        </div>
      )}

      <p className="mt-4 text-xs text-[#475569]">
        For billing disputes or refunds, contact support. All payments are processed via Stripe.
      </p>
    </div>
  )
}
