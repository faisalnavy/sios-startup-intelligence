'use client'
import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { getCreditPacks, createCheckoutSession, getUserCredits } from '../../../lib/api'
import { Suspense } from 'react'

const FALLBACK_FEATURES: Record<string, string[]> = {
  starter: ['5 AI reports', 'PDF download', '12-section analysis', 'Email notification'],
  popular: ['25 AI reports', 'PDF download', 'Priority processing', 'Email reports', 'Analysis history'],
  pro:     ['70 AI reports', 'PDF download', 'Priority processing', 'Email reports', 'Bulk analysis', 'Premium support'],
}

const FALLBACK_PACKS = [
  { id: 'starter', credits: 5,  amount_usd: 5,  label: 'Starter', popular: false },
  { id: 'popular', credits: 25, amount_usd: 20, label: 'Popular', popular: true  },
  { id: 'pro',     credits: 70, amount_usd: 50, label: 'Pro',     popular: false },
]

function CreditsContent() {
  const searchParams = useSearchParams()
  const success = searchParams.get('success') === 'true'
  const cancelled = searchParams.get('cancelled') === 'true'

  const [packs, setPacks] = useState(FALLBACK_PACKS)
  const [credits, setCredits] = useState(0)
  const [purchasing, setPurchasing] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getUserCredits().then(setCredits).catch(() => {})
    getCreditPacks().then(data => {
      const list: any[] = data.packs || []
      if (list.length) {
        setPacks(list.map((p: any) => ({
          id: p.id,
          credits: p.credits,
          amount_usd: p.amount_usd,
          label: p.label || p.id,
          popular: p.popular ?? p.id === 'popular',
        })))
      }
    }).catch(() => {})
  }, [])

  const handleBuy = async (packId: string) => {
    setPurchasing(packId)
    setError('')
    try {
      const { checkout_url } = await createCheckoutSession(packId)
      window.location.href = checkout_url
    } catch (e: any) {
      setError(e.message || 'Failed to start checkout. Make sure you are signed in.')
      setPurchasing(null)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Buy Credits</h1>
        <p className="text-sm text-[#64748b]">
          Current balance:{' '}
          <span className="text-violet-400 font-bold">{credits} credits</span>
          {' '}· 1 credit = 1 full AI startup report
        </p>
      </div>

      {/* Success banner */}
      {success && (
        <div className="mb-6 bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <div>
            <div className="text-emerald-400 font-semibold text-sm">Payment successful!</div>
            <div className="text-[#94a3b8] text-sm">Your credits have been added. You can now run new analyses.</div>
          </div>
        </div>
      )}

      {/* Cancelled banner */}
      {cancelled && (
        <div className="mb-6 bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 text-yellow-400 text-sm">
          Payment cancelled. Your credits were not charged.
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-6 bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Pack cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {packs.map(p => {
          const features = FALLBACK_FEATURES[p.id] ?? []
          return (
            <div
              key={p.id}
              className={`relative bg-[#111118] rounded-xl border p-6 ${
                p.popular ? 'border-violet-500 ring-1 ring-violet-500/30' : 'border-[#1e1e2e]'
              }`}
            >
              {p.popular && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  <span className="bg-gradient-to-r from-violet-600 to-purple-600 text-white text-xs font-bold px-4 py-1 rounded-full whitespace-nowrap">
                    BEST VALUE
                  </span>
                </div>
              )}
              <div className="text-sm text-[#64748b] mb-1">{p.label}</div>
              <div className="flex items-end gap-2 mb-1">
                <span className="text-4xl font-bold text-white">${p.amount_usd}</span>
                <span className="text-[#64748b] text-sm pb-1">USD</span>
              </div>
              <div className="text-sm text-violet-400 font-medium mb-1">{p.credits} credits</div>
              <div className="text-xs text-[#64748b] mb-5">
                ${(p.amount_usd / p.credits).toFixed(2)} per report
              </div>
              <ul className="space-y-2 mb-6">
                {features.map((f: string) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-[#94a3b8]">
                    <span className="text-emerald-400 flex-shrink-0 mt-0.5">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleBuy(p.id)}
                disabled={!!purchasing}
                className={`w-full py-2.5 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                  p.popular
                    ? 'btn-primary'
                    : 'border border-[#2e2e3e] hover:border-violet-500/40 text-white hover:text-violet-300'
                }`}
              >
                {purchasing === p.id ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Redirecting to Stripe...
                  </span>
                ) : `Buy ${p.credits} Credits`}
              </button>
            </div>
          )
        })}
      </div>

      {/* Info */}
      <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6">
        <h2 className="font-semibold text-white mb-4">How Credits Work</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {[
            { icon: '◎', title: '1 Credit = 1 Report', desc: 'Each full AI startup analysis costs exactly 1 credit. No hidden charges.' },
            { icon: '♾', title: 'Credits Never Expire', desc: 'Your purchased credits are valid forever. Use them at your own pace.' },
            { icon: '🔒', title: 'Secure via Stripe', desc: 'All payments processed securely via Stripe. We never store card details.' },
          ].map(item => (
            <div key={item.title} className="flex gap-3">
              <span className="text-xl flex-shrink-0">{item.icon}</span>
              <div>
                <div className="text-sm font-medium text-white mb-1">{item.title}</div>
                <div className="text-xs text-[#64748b] leading-relaxed">{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function CreditsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-[#64748b]">Loading...</div>}>
      <CreditsContent />
    </Suspense>
  )
}
