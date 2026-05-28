'use client'
import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { startAnalysis, uploadBusinessPlan, StartupInput } from '../../../lib/api'

const STAGES = [
  { value: 'idea',           label: 'Idea Stage' },
  { value: 'mvp',            label: 'MVP Built' },
  { value: 'early_traction', label: 'Early Traction' },
  { value: 'growth',         label: 'Growth Stage' },
  { value: 'scaling',        label: 'Scaling' },
]

function detectPlatform(url: string): { icon: string; label: string } {
  const u = url.toLowerCase()
  if (u.includes('linkedin.com'))  return { icon: '💼', label: 'LinkedIn' }
  if (u.includes('github.com'))    return { icon: '🐙', label: 'GitHub' }
  if (u.includes('twitter.com') || u.includes('x.com')) return { icon: '🐦', label: 'Twitter/X' }
  return { icon: '🌐', label: 'Website' }
}

export default function NewAnalysisPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Business plan PDF state
  const [pdfUploading, setPdfUploading] = useState(false)
  const [pdfFile, setPdfFile] = useState<{ name: string; pages: number; wordCount: number } | null>(null)
  const [pdfText, setPdfText] = useState('')
  const [pdfError, setPdfError] = useState('')

  // Custom questions
  const [questions, setQuestions] = useState<string[]>([''])

  // Founder profile URLs
  const [profileUrls, setProfileUrls] = useState<string[]>([''])

  const [form, setForm] = useState<Omit<StartupInput, 'business_plan_text' | 'custom_questions' | 'founder_profile_urls'>>({
    startup_name:             '',
    idea_description:         '',
    geography:                'India',
    business_stage:           'idea',
    founder_background:       '',
    founder_experience_years: undefined,
    target_market:            '',
    revenue_model:            '',
    pricing_strategy:         '',
    funding_required:         '',
    current_revenue:          '',
    competitors_known:        '',
    unique_advantage:         '',
    gtm_strategy:             '',
  })

  const set = (field: string, value: any) =>
    setForm(prev => ({ ...prev, [field]: value }))

  // ── PDF upload handler ────────────────────────────────────────────
  const handlePdfSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setPdfError('')
    setPdfUploading(true)
    try {
      const result = await uploadBusinessPlan(file)
      setPdfText(result.text)
      setPdfFile({ name: file.name, pages: result.pages, wordCount: result.word_count })
    } catch (err: any) {
      setPdfError(err.message || 'Failed to process PDF')
    } finally {
      setPdfUploading(false)
    }
  }

  const removePdf = () => {
    setPdfText('')
    setPdfFile(null)
    setPdfError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // ── Custom questions handlers ─────────────────────────────────────
  const addQuestion = () => {
    if (questions.length < 10) setQuestions(prev => [...prev, ''])
  }
  const updateQuestion = (i: number, val: string) =>
    setQuestions(prev => prev.map((q, idx) => idx === i ? val : q))
  const removeQuestion = (i: number) =>
    setQuestions(prev => prev.filter((_, idx) => idx !== i))

  // ── Profile URL handlers ──────────────────────────────────────────
  const addProfile = () => {
    if (profileUrls.length < 5) setProfileUrls(prev => [...prev, ''])
  }
  const updateProfile = (i: number, val: string) =>
    setProfileUrls(prev => prev.map((u, idx) => idx === i ? val : u))
  const removeProfile = (i: number) =>
    setProfileUrls(prev => prev.filter((_, idx) => idx !== i))

  // ── Submit ────────────────────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (form.idea_description.length < 50) {
      setError('Please describe your startup idea in at least 50 characters.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const payload: StartupInput = {
        ...form,
        business_plan_text: pdfText || undefined,
        custom_questions: questions.filter(q => q.trim().length > 0),
        founder_profile_urls: profileUrls.filter(u => u.trim().length > 0),
      }
      const { analysis_id } = await startAnalysis(payload)
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
          12 AI agents will research and score your startup. Takes 3–7 minutes.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* ── Core Fields ─────────────────────────────────────────── */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6 space-y-5">
          <h2 className="text-sm font-semibold text-[#64748b] uppercase tracking-wider">Startup Details</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Startup Name *</label>
              <input className="input-field" required value={form.startup_name}
                onChange={e => set('startup_name', e.target.value)} placeholder="e.g. PayFlow" />
            </div>
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Geography / Launch Country *</label>
              <input className="input-field" required value={form.geography}
                onChange={e => set('geography', e.target.value)} placeholder="e.g. India, UAE, USA" />
            </div>
          </div>

          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">
              Startup Idea Description *{' '}
              <span className="text-[#64748b]">(min 50 characters)</span>
            </label>
            <textarea className="input-field min-h-[120px] resize-none" required
              value={form.idea_description}
              onChange={e => set('idea_description', e.target.value)}
              placeholder="Describe your startup: What problem does it solve? Who are your customers? How does it work?" />
            <p className={`text-xs mt-1 ${form.idea_description.length >= 50 ? 'text-emerald-400' : 'text-[#64748b]'}`}>
              {form.idea_description.length} chars{form.idea_description.length < 50 ? ` (${50 - form.idea_description.length} more needed)` : ' ✓'}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Business Stage *</label>
              <select className="input-field" value={form.business_stage}
                onChange={e => set('business_stage', e.target.value as any)}>
                {STAGES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Target Market</label>
              <input className="input-field" value={form.target_market || ''}
                onChange={e => set('target_market', e.target.value)} placeholder="e.g. SMEs, urban millennials" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Revenue Model</label>
              <input className="input-field" value={form.revenue_model || ''}
                onChange={e => set('revenue_model', e.target.value)} placeholder="e.g. SaaS, marketplace, D2C" />
            </div>
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Funding Required</label>
              <input className="input-field" value={form.funding_required || ''}
                onChange={e => set('funding_required', e.target.value)} placeholder="e.g. ₹50 Lakhs, $200K" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Current Revenue</label>
              <input className="input-field" value={form.current_revenue || ''}
                onChange={e => set('current_revenue', e.target.value)} placeholder="e.g. ₹0, ₹5L/month" />
            </div>
            <div>
              <label className="block text-sm text-[#94a3b8] mb-1.5">Years of Experience</label>
              <input className="input-field" type="number" min={0} max={50}
                value={form.founder_experience_years || ''}
                onChange={e => set('founder_experience_years', parseInt(e.target.value) || undefined)}
                placeholder="e.g. 8" />
            </div>
          </div>

          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Founder Background</label>
            <textarea className="input-field min-h-[80px] resize-none"
              value={form.founder_background || ''}
              onChange={e => set('founder_background', e.target.value)}
              placeholder="Your experience, domain expertise, previous companies..." />
          </div>

          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Known Competitors</label>
            <input className="input-field" value={form.competitors_known || ''}
              onChange={e => set('competitors_known', e.target.value)}
              placeholder="e.g. Razorpay, Paytm, or 'None known'" />
          </div>

          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">Your Unique Advantage</label>
            <textarea className="input-field min-h-[80px] resize-none"
              value={form.unique_advantage || ''}
              onChange={e => set('unique_advantage', e.target.value)}
              placeholder="What makes your startup different? What's your moat?" />
          </div>

          <div>
            <label className="block text-sm text-[#94a3b8] mb-1.5">GTM Strategy</label>
            <textarea className="input-field min-h-[80px] resize-none"
              value={form.gtm_strategy || ''}
              onChange={e => set('gtm_strategy', e.target.value)}
              placeholder="How will you acquire your first 100 customers?" />
          </div>
        </div>

        {/* ── Business Plan PDF Upload ─────────────────────────────── */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6 space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-[#64748b] uppercase tracking-wider">Business Plan</h2>
            <p className="text-xs text-[#475569] mt-1">Upload your business plan PDF — all 12 agents will study it for deeper insights</p>
          </div>

          {!pdfFile ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-[#2e2e3e] hover:border-violet-500/50 rounded-xl p-8 text-center cursor-pointer transition-colors group"
            >
              <div className="w-12 h-12 rounded-xl bg-violet-500/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-violet-500/20 transition-colors">
                <svg className="w-6 h-6 text-violet-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
              </div>
              {pdfUploading ? (
                <div className="flex items-center justify-center gap-2 text-[#94a3b8]">
                  <span className="w-4 h-4 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
                  Extracting text from PDF...
                </div>
              ) : (
                <>
                  <p className="text-sm text-[#94a3b8]">Click or drag your business plan PDF here</p>
                  <p className="text-xs text-[#475569] mt-1">PDF only · Max 10MB · Up to 50 pages</p>
                </>
              )}
              <input ref={fileInputRef} type="file" accept=".pdf" className="hidden" onChange={handlePdfSelect} />
            </div>
          ) : (
            <div className="flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-emerald-400 truncate">{pdfFile.name}</p>
                <p className="text-xs text-[#64748b]">{pdfFile.pages} pages · {pdfFile.wordCount.toLocaleString()} words extracted</p>
              </div>
              <button type="button" onClick={removePdf} className="text-[#475569] hover:text-red-400 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          )}

          {pdfError && (
            <p className="text-xs text-red-400">{pdfError}</p>
          )}
        </div>

        {/* ── Founder Profile Links ────────────────────────────────── */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6 space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-[#64748b] uppercase tracking-wider">Founder Profiles <span className="text-[#475569] normal-case font-normal">(Optional)</span></h2>
            <p className="text-xs text-[#475569] mt-1">Add LinkedIn, GitHub, or website URLs — SIOS will verify and analyse founder credentials</p>
          </div>

          <div className="space-y-3">
            {profileUrls.map((url, i) => {
              const platform = url ? detectPlatform(url) : null
              return (
                <div key={i} className="flex items-center gap-2">
                  {platform && (
                    <span className="text-lg flex-shrink-0 w-8 text-center">{platform.icon}</span>
                  )}
                  {!platform && (
                    <span className="text-lg flex-shrink-0 w-8 text-center text-[#475569]">🔗</span>
                  )}
                  <input
                    className="input-field flex-1"
                    value={url}
                    onChange={e => updateProfile(i, e.target.value)}
                    placeholder={i === 0 ? 'https://linkedin.com/in/yourname or https://github.com/yourname' : 'Add another profile URL...'}
                  />
                  {profileUrls.length > 1 && (
                    <button type="button" onClick={() => removeProfile(i)}
                      className="text-[#475569] hover:text-red-400 transition-colors flex-shrink-0">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                    </button>
                  )}
                </div>
              )
            })}
          </div>

          {profileUrls.length < 5 && (
            <button type="button" onClick={addProfile}
              className="text-sm text-violet-400 hover:text-violet-300 transition-colors flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
              Add co-founder profile ({profileUrls.length}/5)
            </button>
          )}
        </div>

        {/* ── Custom Questions ─────────────────────────────────────── */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6 space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-[#64748b] uppercase tracking-wider">Your Specific Questions <span className="text-[#475569] normal-case font-normal">(Optional · Max 10)</span></h2>
            <p className="text-xs text-[#475569] mt-1">Ask SIOS anything specific — regulatory questions, market sizing, competitor deep-dives, etc.</p>
          </div>

          <div className="space-y-3">
            {questions.map((q, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="text-xs text-[#475569] font-mono mt-2.5 w-5 flex-shrink-0">{i + 1}.</span>
                <input
                  className="input-field flex-1"
                  value={q}
                  onChange={e => updateQuestion(i, e.target.value)}
                  placeholder={
                    i === 0
                      ? 'e.g. What regulatory license does this startup need in India?'
                      : i === 1
                      ? 'e.g. Which specific VC funds in India would be most interested?'
                      : 'Add your question...'
                  }
                  maxLength={500}
                />
                {questions.length > 1 && (
                  <button type="button" onClick={() => removeQuestion(i)}
                    className="text-[#475569] hover:text-red-400 transition-colors flex-shrink-0 mt-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                )}
              </div>
            ))}
          </div>

          {questions.length < 10 && (
            <button type="button" onClick={addQuestion}
              className="text-sm text-violet-400 hover:text-violet-300 transition-colors flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
              Add question ({questions.filter(q => q.trim()).length}/10)
            </button>
          )}
        </div>

        {/* ── Error + Submit ───────────────────────────────────────── */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        <button type="submit" className="btn-primary w-full text-base py-3.5" disabled={loading || pdfUploading}>
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Starting Analysis...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              Run SIOS Analysis — 1 Credit
              {pdfFile && <span className="text-xs opacity-70">· Business plan included</span>}
              {questions.filter(q => q.trim()).length > 0 && (
                <span className="text-xs opacity-70">· {questions.filter(q => q.trim()).length} questions</span>
              )}
            </span>
          )}
        </button>

        <p className="text-center text-xs text-[#475569]">
          Analysis takes 3–7 minutes. 12 AI agents research your startup using Claude + GPT-4 + Tavily.
        </p>
      </form>
    </div>
  )
}
