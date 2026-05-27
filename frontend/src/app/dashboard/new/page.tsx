'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { startAnalysis, StartupInput } from '../../../lib/api'

const STAGES = [
  { value: 'idea',           label: 'Idea Stage' },
  { value: 'mvp',            label: 'MVP Built' },
  { value: 'early_traction', label: 'Early Traction' },
  { value: 'growth',         label: 'Growth Stage' },
  { value: 'scaling',        label: 'Scaling' },
]

export default function NewAnalysisPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState<StartupInput>({
    startup_name:             '',
    idea_description:         '',
    geography:                'India',
    business_stage:           'idea',
    founder_background:       '',
    founder_experience_years: undefined,
    target_market:            '',
    revenue_model:            '',
    funding_required:         '',
    current_revenue:          '',
    competitors_known:        '',
    unique_advantage:         '',
    gtm_strategy:             '',
  })

  const set = (field: keyof StartupInput, value: any) =>
    setForm(prev => ({ ...prev, [field]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (form.idea_description.length < 50) {
      setError('Please describe your startup idea in at least 50 characters.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const { analysis_id } = await startAnalysis(form)
      router.push(`/analysis/${analysis_id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to start analysis')
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">New Startup Analysis</h1>
        <p className="text-sm text-[#64748b]">
          Fill in your startup details and 8 AI agents will research and score it. Takes 2–5 minutes.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Startup Name *</label>
            <input
              className="input-field"
              required
              value={form.startup_name}
              onChange={e => set('startup_name', e.target.value)}
              placeholder="e.g. PayFlow"
            />
          </div>
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Geography / Launch Country *</label>
            <input
              className="input-field"
              required
              value={form.geography}
              onChange={e => set('geography', e.target.value)}
              placeholder="e.g. India, UAE, USA"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm text-[#94a3b8] mb-1.5">
            Startup Idea Description *{' '}
            <span className="text-[#64748b]">(minimum 50 characters)</span>
          </label>
          <textarea
            className="input-field min-h-[120px] resize-none"
            required
            value={form.idea_description}
            onChange={e => set('idea_description', e.target.value)}
            placeholder="Describe your startup idea: What problem does it solve? Who are your customers? How does it work?"
          />
          <p className={`text-xs mt-1 ${form.idea_description.length >= 50 ? 'text-emerald-400' : 'text-[#64748b]'}`}>
            {form.idea_description.length} characters {form.idea_description.length < 50 ? `(${50 - form.idea_description.length} more needed)` : '✓'}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Business Stage *</label>
            <select
              className="input-field"
              value={form.business_stage}
              onChange={e => set('business_stage', e.target.value as any)}
            >
              {STAGES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Target Market</label>
            <input
              className="input-field"
              value={form.target_market || ''}
              onChange={e => set('target_market', e.target.value)}
              placeholder="e.g. SMEs, urban millennials"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Revenue Model</label>
            <input
              className="input-field"
              value={form.revenue_model || ''}
              onChange={e => set('revenue_model', e.target.value)}
              placeholder="e.g. SaaS, marketplace, D2C"
            />
          </div>
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Funding Required</label>
            <input
              className="input-field"
              value={form.funding_required || ''}
              onChange={e => set('funding_required', e.target.value)}
              placeholder="e.g. ₹50 Lakhs, $200K"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm text-[#94a3b8] mb-1.5">Founder Background</label>
          <textarea
            className="input-field min-h-[80px] resize-none"
            value={form.founder_background || ''}
            onChange={e => set('founder_background', e.target.value)}
            placeholder="Your experience, domain expertise, previous companies..."
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Years of Experience</label>
            <input
              className="input-field"
              type="number"
              min={0}
              max={50}
              value={form.founder_experience_years || ''}
              onChange={e => set('founder_experience_years', parseInt(e.target.value) || undefined)}
              placeholder="e.g. 8"
            />
          </div>
          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Current Revenue</label>
            <input
              className="input-field"
              value={form.current_revenue || ''}
              onChange={e => set('current_revenue', e.target.value)}
              placeholder="e.g. ₹0, ₹5L/month"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm text-[#94a3b8] mb-1.5">Known Competitors</label>
          <input
            className="input-field"
            value={form.competitors_known || ''}
            onChange={e => set('competitors_known', e.target.value)}
            placeholder="e.g. Razorpay, Paytm, or 'None known'"
          />
        </div>

        <div>
          <label className="block text-sm text-[#94a3b8] mb-1.5">Your Unique Advantage</label>
          <textarea
            className="input-field min-h-[80px] resize-none"
            value={form.unique_advantage || ''}
            onChange={e => set('unique_advantage', e.target.value)}
            placeholder="What makes your startup different? What's your moat?"
          />
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        <button type="submit" className="btn-primary w-full text-base py-3.5" disabled={loading}>
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Starting Analysis...
            </span>
          ) : 'Run SIOS Analysis — 1 Credit →'}
        </button>

        <p className="text-center text-xs text-[#475569]">
          Analysis takes 2–5 minutes. 8 AI agents will research your startup using Claude + GPT-4 + Tavily web search.
        </p>
      </form>
    </div>
  )
}
