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
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  try {
    const { supabase } = await import('./supabase')
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`
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
