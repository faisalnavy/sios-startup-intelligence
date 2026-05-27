'use client'
import Link from 'next/link'
import { useEffect, useState, useRef } from 'react'
import { useParams } from 'next/navigation'
import { subscribeToProgress, getReport, FullReport, ProgressEvent } from '../../../lib/api'

const TOTAL_AGENTS = 9

const VERDICT_CONFIG: Record<string, { color: string; bg: string; border: string }> = {
  'STRONG BUY':       { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/30' },
  'BUY WITH CAUTION': { color: 'text-yellow-400',  bg: 'bg-yellow-400/10',  border: 'border-yellow-400/30' },
  'WAIT & WATCH':     { color: 'text-blue-400',    bg: 'bg-blue-400/10',    border: 'border-blue-400/30'  },
  'PIVOT REQUIRED':   { color: 'text-orange-400',  bg: 'bg-orange-400/10',  border: 'border-orange-400/30'},
  'DO NOT INVEST':    { color: 'text-red-400',      bg: 'bg-red-400/10',     border: 'border-red-400/30'  },
}

const SCORE_FIELDS = [
  { key: 'market_demand',        label: 'Market Demand',    weight: '20%' },
  { key: 'founder_capability',   label: 'Founder',          weight: '15%' },
  { key: 'unit_economics',       label: 'Unit Economics',   weight: '15%' },
  { key: 'scalability',          label: 'Scalability',      weight: '15%' },
  { key: 'competition_advantage',label: 'Competition Edge', weight: '10%' },
  { key: 'timing',               label: 'Market Timing',    weight: '10%' },
  { key: 'financial_stability',  label: 'Financial',        weight: '10%' },
  { key: 'execution_capability', label: 'Execution',        weight: '5%'  },
]

function ScoreBar({ score }: { score: number }) {
  const color = score >= 75 ? 'bg-emerald-400' : score >= 55 ? 'bg-yellow-400' : 'bg-red-400'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-[#1e1e2e] rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full transition-all duration-700`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm font-mono w-8 text-right text-[#94a3b8]">{score}</span>
    </div>
  )
}

function AgentItem({ event }: { event: ProgressEvent }) {
  const done = event.status === 'completed' || event.status === 'complete'
  const running = event.status === 'running'
  const errored = event.status.startsWith('error')

  return (
    <div className="flex items-center gap-3 py-2 border-b border-[#1e1e2e] last:border-0">
      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
        done ? 'bg-emerald-400' : running ? 'bg-violet-400 animate-pulse' : errored ? 'bg-red-400' : 'bg-[#2e2e3e]'
      }`} />
      <span className="text-sm text-[#94a3b8] flex-1">{event.agent}</span>
      <span className={`text-xs font-mono ${
        done ? 'text-emerald-400' : running ? 'text-violet-400' : errored ? 'text-red-400' : 'text-[#475569]'
      }`}>{event.status}</span>
    </div>
  )
}

function Section({ title, content }: { title: string; content: string }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6">
      <button onClick={() => setOpen(o => !o)} className="w-full flex items-center justify-between mb-4 text-left">
        <h3 className="font-semibold text-white">{title}</h3>
        <span className="text-[#475569] text-lg">{open ? '−' : '+'}</span>
      </button>
      {open && (
        <div className="text-[#94a3b8] text-sm leading-relaxed whitespace-pre-wrap">
          {content || 'No data available.'}
        </div>
      )}
    </div>
  )
}

// PDF generation — opens a styled print window
function downloadPDF(report: FullReport) {
  const win = window.open('', '_blank')
  if (!win) { alert('Allow pop-ups to download the PDF.'); return }

  const sections = [
    { title: '1. Executive Summary',         content: report.executive_summary },
    { title: '2. Startup Overview',           content: report.startup_overview },
    { title: '3. Founder Analysis',           content: report.founder_analysis },
    { title: '4. Market Analysis',            content: report.market_analysis },
    { title: '5. Financial Analysis',         content: report.financial_analysis },
    { title: '6. Investment Recommendation',  content: report.investment_recommendation },
    { title: '7. Growth Strategy',            content: report.growth_strategy },
    { title: '8. Scaling Roadmap',            content: report.scaling_roadmap },
    { title: '9. Funding Recommendation',     content: report.funding_recommendation },
  ]

  const scoreItems = SCORE_FIELDS
  const sectionsHTML = sections.map(s =>
    `<div class="section">
      <div class="section-title">${s.title}</div>
      <div class="section-body">${(s.content || 'N/A').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
    </div>`
  ).join('')

  const scoreHTML = scoreItems.map(f =>
    `<div class="si">
      <div class="si-val">${(report.score_breakdown as any)[f.key] || 0}</div>
      <div class="si-lbl">${f.label}</div>
    </div>`
  ).join('')

  const verdictColor: Record<string, string> = {
    'STRONG BUY': '#10b981', 'BUY WITH CAUTION': '#f59e0b',
    'WAIT & WATCH': '#3b82f6', 'PIVOT REQUIRED': '#f97316', 'DO NOT INVEST': '#ef4444',
  }
  const vColor = verdictColor[report.final_verdict] || '#94a3b8'

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SIOS Report — ${report.startup_name}</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a1a2e;line-height:1.6}
  .header{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:40px}
  .header h1{font-size:30px;margin-bottom:6px}
  .header .sub{opacity:.8;font-size:13px}
  .verdict{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);
    color:#fff;padding:8px 20px;border-radius:24px;font-weight:700;font-size:15px;margin-top:14px;
    border-left:4px solid ${vColor}}
  .score-band{background:#f8fafc;border-bottom:2px solid #e2e8f0;padding:24px 40px;display:flex;gap:32px;align-items:flex-start}
  .score-num{font-size:56px;font-weight:700;color:#4f46e5;line-height:1}
  .score-sub{color:#64748b;font-size:13px;margin-top:4px}
  .score-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;flex:1}
  .si{text-align:center;background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 4px}
  .si-val{font-size:20px;font-weight:700;color:#1a1a2e}
  .si-lbl{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:.04em;margin-top:2px}
  .content{padding:32px 40px}
  .section{margin-bottom:20px;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;page-break-inside:avoid}
  .section-title{background:#f8fafc;padding:12px 20px;font-weight:600;font-size:14px;border-bottom:1px solid #e2e8f0}
  .section-body{padding:16px 20px;font-size:13px;color:#374151;white-space:pre-wrap;line-height:1.7}
  .footer{text-align:center;padding:20px;color:#94a3b8;font-size:11px;border-top:1px solid #e2e8f0}
  .prob{display:inline-block;background:${vColor}22;color:${vColor};border:1px solid ${vColor}44;
    padding:4px 12px;border-radius:20px;font-weight:600;font-size:13px;margin-top:8px}
  @media print{body{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
</style>
</head>
<body>
<div class="header">
  <h1>${report.startup_name}</h1>
  <div class="sub">Startup Intelligence Report · Generated ${new Date(report.generated_at).toLocaleDateString('en-IN',{day:'numeric',month:'long',year:'numeric'})}</div>
  <div class="verdict">${report.final_verdict}</div>
</div>
<div class="score-band">
  <div>
    <div class="score-num">${report.score_breakdown.total_score}</div>
    <div class="score-sub">/ 100 Total Score</div>
    <div class="prob">${report.success_probability}% Success Probability</div>
  </div>
  <div class="score-grid">${scoreHTML}</div>
</div>
<div class="content">${sectionsHTML}</div>
<div class="footer">
  Analysis ID: ${report.analysis_id} &nbsp;·&nbsp; Powered by Claude (Anthropic) + GPT-4 (OpenAI) + Tavily &nbsp;·&nbsp; SIOS v2.0
</div>
<script>window.onload=function(){setTimeout(function(){window.print()},600)}</script>
</body>
</html>`

  win.document.write(html)
  win.document.close()
}

// PDF popup modal
function PDFModal({ report, onClose }: { report: FullReport; onClose: () => void }) {
  const vc = VERDICT_CONFIG[report.final_verdict] || { color: 'text-[#94a3b8]', bg: 'bg-[#111118]', border: 'border-[#1e1e2e]' }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-[#111118] border border-[#1e1e2e] rounded-2xl p-8 max-w-md w-full shadow-2xl text-center">
        {/* Success animation */}
        <div className="w-16 h-16 rounded-full bg-emerald-500/20 border-2 border-emerald-400/40 flex items-center justify-center mx-auto mb-5">
          <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h2 className="text-xl font-bold text-white mb-1">Analysis Complete!</h2>
        <p className="text-sm text-[#94a3b8] mb-5">
          Your SIOS report for <span className="text-white font-medium">{report.startup_name}</span> is ready.
        </p>

        {/* Score + verdict */}
        <div className="flex items-center justify-center gap-4 mb-6">
          <div className="bg-[#0d0d14] border border-[#2e2e3e] rounded-xl px-5 py-3">
            <div className="text-3xl font-bold text-white">{report.score_breakdown.total_score}</div>
            <div className="text-xs text-[#64748b]">/ 100</div>
          </div>
          <div className={`${vc.bg} ${vc.border} border rounded-xl px-5 py-3`}>
            <div className={`font-bold text-sm ${vc.color}`}>{report.final_verdict}</div>
            <div className="text-xs text-[#64748b] mt-0.5">{report.success_probability}% success</div>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <button
            onClick={() => downloadPDF(report)}
            className="w-full btn-primary py-3 flex items-center justify-center gap-2 text-sm font-semibold"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
            </svg>
            Download PDF Report
          </button>
          <button
            onClick={onClose}
            className="w-full border border-[#2e2e3e] hover:border-[#3e3e4e] text-[#94a3b8] hover:text-white py-3 rounded-lg text-sm transition-colors"
          >
            View Full Report
          </button>
        </div>

        <p className="text-xs text-[#475569] mt-4">
          PDF opens in a new tab. Use your browser's print dialog to save as PDF.
        </p>
      </div>
    </div>
  )
}

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>()
  const [events, setEvents]     = useState<ProgressEvent[]>([])
  const [report, setReport]     = useState<FullReport | null>(null)
  const [status, setStatus]     = useState<'running' | 'completed' | 'error'>('running')
  const [errorMsg, setErrorMsg] = useState('')
  const [showPDF, setShowPDF]   = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const completedCount = events.filter(e =>
    e.status === 'completed' || e.status === 'complete'
  ).length
  const progressPct = status === 'completed' ? 100 : Math.min(Math.round((completedCount / TOTAL_AGENTS) * 100), 95)

  useEffect(() => {
    if (!id) return
    const unsub = subscribeToProgress(
      id,
      (event) => {
        setEvents(prev => {
          const exists = prev.some(e => e.agent === event.agent && e.status === event.status)
          return exists ? prev : [...prev, event]
        })
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
      },
      async () => {
        setStatus('completed')
        try {
          const r = await getReport(id)
          setReport(r)
          setShowPDF(true)
        } catch (e: any) {
          setErrorMsg(e.message)
          setStatus('error')
        }
      },
      (err) => {
        setErrorMsg(err)
        setStatus('error')
      },
    )
    return unsub
  }, [id])

  const verdict = report?.final_verdict || ''
  const vc = VERDICT_CONFIG[verdict] || { color: 'text-[#94a3b8]', bg: 'bg-[#111118]', border: 'border-[#1e1e2e]' }

  return (
    <>
      {showPDF && report && <PDFModal report={report} onClose={() => setShowPDF(false)} />}

      <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
        {/* Top bar */}
        <div className="flex items-start gap-4">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-sm text-[#64748b] hover:text-white transition-colors border border-[#1e1e2e] hover:border-[#2e2e3e] rounded-lg px-3 py-2 flex-shrink-0"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7m-9 9V9"/>
            </svg>
            Home
          </Link>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-white truncate">
              {report?.startup_name || 'Analyzing startup...'}
            </h1>
            <p className="text-xs text-[#64748b] mt-0.5">ID: {id}</p>
          </div>
          {status === 'completed' && verdict && (
            <div className={`${vc.bg} ${vc.border} border rounded-lg px-4 py-2 flex-shrink-0`}>
              <span className={`font-bold text-sm ${vc.color}`}>{verdict}</span>
            </div>
          )}
        </div>

        {/* Progress bar */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-white">
              {status === 'completed' ? 'Analysis Complete' : status === 'error' ? 'Analysis Failed' : 'Running Analysis...'}
            </span>
            <span className="text-sm font-bold text-violet-400">{progressPct}%</span>
          </div>
          <div className="w-full bg-[#1e1e2e] rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                status === 'completed' ? 'bg-emerald-500' :
                status === 'error' ? 'bg-red-500' :
                'bg-gradient-to-r from-violet-600 to-purple-500'
              } ${status === 'running' && progressPct < 95 ? 'animate-pulse' : ''}`}
              style={{ width: `${progressPct}%` }}
            />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-xs text-[#475569]">
              {completedCount} of {TOTAL_AGENTS} agents done
              {status === 'running' && ' · est. 2–5 min total'}
            </span>
            {status === 'completed' && report && (
              <button
                onClick={() => setShowPDF(true)}
                className="text-xs text-violet-400 hover:text-violet-300 transition-colors font-medium"
              >
                ↓ Download PDF
              </button>
            )}
          </div>
        </div>

        {/* Agent progress list */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6">
          <h2 className="text-sm font-semibold text-[#64748b] uppercase tracking-wider mb-4">Agent Pipeline</h2>
          {events.length === 0 && (
            <div className="flex items-center gap-2 text-[#475569] text-sm">
              <span className="w-3 h-3 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
              Initializing AI agents...
            </div>
          )}
          {events.map((e, i) => <AgentItem key={i} event={e} />)}
          <div ref={bottomRef} />
        </div>

        {/* Error */}
        {status === 'error' && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400">
            <strong>Analysis failed:</strong> {errorMsg}
          </div>
        )}

        {/* Report */}
        {report && (
          <>
            {/* Score Dashboard */}
            <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-semibold text-white">Startup Score</h2>
                <div className="text-right">
                  <div className="text-4xl font-bold text-white">
                    {report.score_breakdown.total_score}
                    <span className="text-lg text-[#64748b]">/100</span>
                  </div>
                  <div className="text-xs text-[#64748b]">{report.success_probability}% success probability</div>
                </div>
              </div>
              <div className="space-y-3">
                {SCORE_FIELDS.map(f => (
                  <div key={f.key}>
                    <div className="flex justify-between text-xs text-[#64748b] mb-1">
                      <span>{f.label}</span>
                      <span>{f.weight} weight</span>
                    </div>
                    <ScoreBar score={(report.score_breakdown as any)[f.key] || 0} />
                  </div>
                ))}
              </div>
            </div>

            {/* Verdict card */}
            <div className={`${vc.bg} ${vc.border} border rounded-xl p-6`}>
              <span className={`text-2xl font-bold ${vc.color}`}>{verdict}</span>
              <p className="text-[#94a3b8] text-sm leading-relaxed mt-3">{report.funding_recommendation}</p>
            </div>

            {/* PDF download button */}
            <div className="flex justify-center">
              <button
                onClick={() => setShowPDF(true)}
                className="btn-primary px-8 py-3 flex items-center gap-2 text-sm"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                </svg>
                Download Full PDF Report
              </button>
            </div>

            {/* Report sections */}
            <div className="space-y-4">
              <Section title="1. Executive Summary"          content={report.executive_summary} />
              <Section title="2. Startup Overview"           content={report.startup_overview} />
              <Section title="3. Founder Analysis"           content={report.founder_analysis} />
              <Section title="4. Market Analysis"            content={report.market_analysis} />
              <Section title="5. Financial Analysis"         content={report.financial_analysis} />
              <Section title="6. Investment Recommendation"  content={report.investment_recommendation} />
              <Section title="7. Growth Strategy"            content={report.growth_strategy} />
              <Section title="8. Scaling Roadmap"            content={report.scaling_roadmap} />
            </div>

            {/* Footer */}
            <div className="text-center text-xs text-[#475569] py-4 border-t border-[#1e1e2e]">
              Generated {new Date(report.generated_at).toLocaleString()} &bull;
              Powered by Claude (Anthropic) + GPT-4 (OpenAI) + Tavily
            </div>
          </>
        )}
      </div>
    </>
  )
}
