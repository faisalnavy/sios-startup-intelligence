const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface StartupInput {
  startup_name: string
  idea_description: string
  founder_background?: string
  founder_experience_years?: number
  target_market?: string
  geography: string
  revenue_model?: string
  pricing_strategy?: string
  funding_required?: string
  business_stage: 'idea' | 'mvp' | 'early_traction' | 'growth' | 'scaling'
  current_revenue?: string
  competitors_known?: string
  gtm_strategy?: string
  unique_advantage?: string
  // v2 fields
  business_plan_text?: string
  custom_questions?: string[]
  founder_profile_urls?: string[]
}

export interface ProgressEvent {
  agent: string
  status: string
  timestamp: string
}

export interface ScoreBreakdown {
  market_demand: number
  founder_capability: number
  unit_economics: number
  scalability: number
  competition_advantage: number
  timing: number
  financial_stability: number
  execution_capability: number
  total_score: number
}

export interface PivotPath {
  path_name: string
  description: string
  effort: string
  potential: string
}

export interface BuildVsPartnerItem {
  capability: string
  decision: 'BUILD' | 'PARTNER' | 'BUY'
  reason: string
  suggested_partners?: string
}

export interface ExecutionRiskItem {
  risk: string
  probability_pct: number
  timeline: string
  impact: string
}

export interface InvestorArchetype {
  archetype: string
  fit_score: number
  why_would_invest: string
  why_would_reject: string
  example_funds?: string
}

export interface CustomQA {
  question: string
  answer: string
}

export interface FullReport {
  analysis_id: string
  startup_name: string
  executive_summary: string
  startup_overview: string
  founder_analysis: string
  market_analysis: string
  financial_analysis: string
  investment_recommendation: string
  growth_strategy: string
  scaling_roadmap: string
  final_verdict: string
  score_breakdown: ScoreBreakdown
  success_probability: number
  funding_recommendation: string
  generated_at: string
  // v2 agent fields
  alternative_strategies?: string
  pivot_paths?: PivotPath[]
  moat_analysis?: string
  moat_score?: number
  execution_simulation?: string
  execution_risks?: ExecutionRiskItem[]
  build_vs_partner?: string
  build_vs_partner_matrix?: BuildVsPartnerItem[]
  investor_fit?: string
  investor_archetypes?: InvestorArchetype[]
  fundraising_difficulty?: string
  custom_qa?: CustomQA[]
  amended_plan?: string
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  try {
    const { supabase } = await import('./supabase')

    // Primary: use Supabase SDK getSession()
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`
      return headers
    }

    // Fallback: read Supabase SSR chunked cookies directly.
    // @supabase/ssr splits large tokens across multiple cookies (.0, .1, …)
    // with the format: sb-<projectRef>-auth-token.N=base64-<data> (first chunk)
    if (typeof document !== 'undefined') {
      const projectRef = (process.env.NEXT_PUBLIC_SUPABASE_URL || '')
        .replace('https://', '')
        .split('.')[0]
      if (projectRef) {
        const allCookies = document.cookie.split(';').map(c => c.trim())
        const parts: string[] = []
        for (let i = 0; i < 10; i++) {
          const prefix = `sb-${projectRef}-auth-token.${i}=`
          const match = allCookies.find(c => c.startsWith(prefix))
          if (!match) break
          let val = match.slice(prefix.length)
          if (i === 0) val = val.replace(/^base64-/, '')
          parts.push(val)
        }
        if (parts.length > 0) {
          // Add padding if needed
          const raw = parts.join('')
          const padded = raw + '='.repeat((4 - raw.length % 4) % 4)
          const combined = atob(padded)
          const sessionData = JSON.parse(combined)
          if (sessionData?.access_token) {
            headers['Authorization'] = `Bearer ${sessionData.access_token}`
          }
        }
      }
    }
  } catch {}
  return headers
}

export async function startAnalysis(startup: StartupInput): Promise<{ analysis_id: string }> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    headers,
    body: JSON.stringify(startup),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as any).detail || `Failed to start analysis: ${res.statusText}`)
  }
  return res.json()
}

export async function getReport(analysisId: string): Promise<FullReport> {
  const res = await fetch(`${API_URL}/api/analysis/${analysisId}/report`)
  if (!res.ok) throw new Error(`Failed to fetch report: ${res.statusText}`)
  return res.json()
}

export async function getAnalysisStatus(analysisId: string): Promise<{
  status: string
  progress: ProgressEvent[]
  error?: string
}> {
  const res = await fetch(`${API_URL}/api/analysis/${analysisId}/status`)
  if (!res.ok) throw new Error(`Status check failed: ${res.statusText}`)
  return res.json()
}

export function subscribeToProgress(
  analysisId: string,
  onProgress: (event: ProgressEvent) => void,
  onComplete: () => void,
  onError: (error: string) => void,
): () => void {
  let evtSource: EventSource | null = null
  let pollTimer: ReturnType<typeof setInterval> | null = null
  let done = false
  const seenEvents = new Set<string>()

  function cleanup() {
    done = true
    if (evtSource) { evtSource.close(); evtSource = null }
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
  }

  // Polling fallback — kicks in when SSE drops or fails to connect
  function startPolling() {
    if (pollTimer || done) return
    pollTimer = setInterval(async () => {
      if (done) return
      try {
        const data = await getAnalysisStatus(analysisId)
        // Replay any progress events we haven't seen yet
        if (Array.isArray(data.progress)) {
          data.progress.forEach((evt: ProgressEvent) => {
            const key = `${evt.agent}:${evt.status}`
            if (!seenEvents.has(key)) {
              seenEvents.add(key)
              onProgress(evt)
            }
          })
        }
        if (data.status === 'completed') {
          cleanup()
          onComplete()
        } else if (data.status === 'error') {
          cleanup()
          onError(data.error || 'Analysis failed')
        }
      } catch {
        // Network blip — keep polling silently
      }
    }, 4000)
  }

  // Try SSE first (real-time updates)
  try {
    evtSource = new EventSource(`${API_URL}/api/analysis/${analysisId}/stream`)

    evtSource.addEventListener('progress', (e) => {
      try {
        const evt = JSON.parse(e.data) as ProgressEvent
        const key = `${evt.agent}:${evt.status}`
        if (!seenEvents.has(key)) {
          seenEvents.add(key)
          onProgress(evt)
        }
      } catch {}
    })

    evtSource.addEventListener('complete', () => {
      cleanup()
      onComplete()
    })

    evtSource.addEventListener('error', (e: any) => {
      // Check if this is a server-sent error (has data) vs a connection drop (no data)
      try {
        if (e.data) {
          const data = JSON.parse(e.data)
          if (data.error) {
            cleanup()
            onError(data.error)
            return
          }
        }
      } catch {}
      // Connection dropped — close SSE and fall back to polling silently
      if (evtSource) { evtSource.close(); evtSource = null }
      startPolling()
    })
  } catch {
    // SSE not supported or failed to open — go straight to polling
    startPolling()
  }

  return cleanup
}

export async function getUserProfile(): Promise<any> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}/api/user/profile`, { headers })
  if (!res.ok) throw new Error('Failed to fetch profile')
  return res.json()
}

export async function getUserCredits(): Promise<number> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}/api/user/credits`, { headers })
  if (!res.ok) return 0
  const data = await res.json()
  return (data as any).credits ?? 0
}

export async function getUserAnalyses(): Promise<any[]> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}/api/user/analyses`, { headers })
  if (!res.ok) return []
  const data = await res.json()
  return (data as any).analyses ?? []
}

export async function getCreditPacks(): Promise<any> {
  const res = await fetch(`${API_URL}/api/payments/packs`)
  if (!res.ok) return {}
  return res.json()
}

export async function createCheckoutSession(packId: string): Promise<{ checkout_url: string }> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}/api/payments/checkout?pack_id=${encodeURIComponent(packId)}`, {
    method: 'POST',
    headers,
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as any).detail || 'Failed to create checkout session')
  }
  return res.json()
}

export async function getPaymentHistory(): Promise<any[]> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}/api/payments/history`, { headers })
  if (!res.ok) return []
  const data = await res.json()
  return (data as any).payments ?? []
}

// ── Business Plan PDF Upload ───────────────────────────────────────────────────

export async function uploadBusinessPlan(file: File): Promise<{
  text: string
  pages: number
  word_count: number
  filename: string
}> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_URL}/api/upload/business-plan`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as any).detail || 'Failed to upload business plan')
  }
  return res.json()
}

// ── Amended Business Plan ─────────────────────────────────────────────────────

export async function generateAmendedPlan(analysisId: string): Promise<{
  analysis_id: string
  startup_name: string
  amended_plan: string
  generated_at: string
}> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}/api/analysis/${analysisId}/generate-plan`, {
    method: 'POST',
    headers,
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as any).detail || 'Failed to generate amended plan')
  }
  return res.json()
}

// ── Dynamic Credit Packs ──────────────────────────────────────────────────────

export async function getDynamicCreditPacks(): Promise<any[]> {
  const res = await fetch(`${API_URL}/api/payments/packs-dynamic`)
  if (!res.ok) return []
  const data = await res.json()
  return (data as any).packs ?? []
}

// ── Admin API ─────────────────────────────────────────────────────────────────

async function getAdminHeaders(): Promise<Record<string, string>> {
  const headers = await getAuthHeaders()
  return headers
}

export async function adminGetStats(): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/stats`, { headers })
  if (!res.ok) throw new Error('Failed to fetch admin stats')
  return res.json()
}

export async function adminListUsers(page = 1, perPage = 50, search?: string): Promise<any> {
  const headers = await getAdminHeaders()
  const params = new URLSearchParams({ page: String(page), per_page: String(perPage) })
  if (search) params.set('search', search)
  const res = await fetch(`${API_URL}/api/admin/users?${params}`, { headers })
  if (!res.ok) throw new Error('Failed to fetch users')
  return res.json()
}

export async function adminGetUserDetail(userId: string): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/users/${userId}`, { headers })
  if (!res.ok) throw new Error('Failed to fetch user detail')
  return res.json()
}

export async function adminAdjustCredits(userId: string, delta: number, reason: string): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/users/${userId}/credits`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ delta, reason }),
  })
  if (!res.ok) throw new Error('Failed to adjust credits')
  return res.json()
}

export async function adminToggleSuspend(userId: string): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/users/${userId}/suspend`, {
    method: 'POST',
    headers,
  })
  if (!res.ok) throw new Error('Failed to toggle suspend')
  return res.json()
}

export async function adminListAnalyses(page = 1, perPage = 50, verdict?: string): Promise<any> {
  const headers = await getAdminHeaders()
  const params = new URLSearchParams({ page: String(page), per_page: String(perPage) })
  if (verdict) params.set('verdict', verdict)
  const res = await fetch(`${API_URL}/api/admin/analyses?${params}`, { headers })
  if (!res.ok) throw new Error('Failed to fetch analyses')
  return res.json()
}

export async function adminDeleteAnalysis(analysisId: string): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/analyses/${analysisId}`, {
    method: 'DELETE',
    headers,
  })
  if (!res.ok) throw new Error('Failed to delete analysis')
  return res.json()
}

export async function adminListCreditPacks(): Promise<any[]> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/credit-packs`, { headers })
  if (!res.ok) return []
  const data = await res.json()
  return Array.isArray(data) ? data : []
}

export async function adminCreateCreditPack(pack: any): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/credit-packs`, {
    method: 'POST',
    headers,
    body: JSON.stringify(pack),
  })
  if (!res.ok) throw new Error('Failed to create credit pack')
  return res.json()
}

export async function adminUpdateCreditPack(packId: string, updates: any): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/credit-packs/${packId}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(updates),
  })
  if (!res.ok) throw new Error('Failed to update credit pack')
  return res.json()
}

export async function adminDeleteCreditPack(packId: string): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/credit-packs/${packId}`, {
    method: 'DELETE',
    headers,
  })
  if (!res.ok) throw new Error('Failed to delete credit pack')
  return res.json()
}

export async function adminListDiscounts(): Promise<any[]> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/discounts`, { headers })
  if (!res.ok) return []
  const data = await res.json()
  return Array.isArray(data) ? data : []
}

export async function adminCreateDiscount(discount: any): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/discounts`, {
    method: 'POST',
    headers,
    body: JSON.stringify(discount),
  })
  if (!res.ok) throw new Error('Failed to create discount')
  return res.json()
}

export async function adminToggleDiscount(discountId: string): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/discounts/${discountId}/toggle`, {
    method: 'PUT',
    headers,
  })
  if (!res.ok) throw new Error('Failed to toggle discount')
  return res.json()
}

export async function adminDeleteDiscount(discountId: string): Promise<any> {
  const headers = await getAdminHeaders()
  const res = await fetch(`${API_URL}/api/admin/discounts/${discountId}`, {
    method: 'DELETE',
    headers,
  })
  if (!res.ok) throw new Error('Failed to delete discount')
  return res.json()
}

export async function adminGetCreditAdjustments(page = 1, perPage = 50): Promise<any> {
  const headers = await getAdminHeaders()
  const params = new URLSearchParams({ page: String(page), per_page: String(perPage) })
  const res = await fetch(`${API_URL}/api/admin/credit-adjustments?${params}`, { headers })
  if (!res.ok) return { adjustments: [], total: 0 }
  return res.json()
}

export async function validateDiscountCode(code: string): Promise<{
  code: string
  discount_pct: number
  description: string
} | null> {
  try {
    const res = await fetch(`${API_URL}/api/admin/discounts/validate/${encodeURIComponent(code)}`)
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}
