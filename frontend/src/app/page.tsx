'use client'
import Link from 'next/link'

const FEATURES = [
  {
    icon: '🤖',
    title: 'Dual-AI Cross-Validation',
    desc: 'Claude (Anthropic) analyzes every dimension. GPT-4 critiques and challenges. Claude synthesizes — eliminating hallucinations through adversarial consensus.',
  },
  {
    icon: '🔍',
    title: 'Live Market Research',
    desc: 'Tavily-powered real-time web search fetches current market data, competitor moves, funding rounds, and regulatory changes — not outdated training data.',
  },
  {
    icon: '⚡',
    title: '15 Parallel AI Agents',
    desc: 'Market, VC, competitor, failure risk, financial, country feasibility, trend, moat, execution simulation, build vs partner, investor fit, startup autopsy, GTM intelligence, founder psychology — all run simultaneously.',
  },
  {
    icon: '📊',
    title: 'Weighted Scoring Engine',
    desc: 'Proprietary 8-dimension scoring model: market demand, unit economics, scalability, founder capability, timing, competition edge — scored 0–100.',
  },
  {
    icon: '🌍',
    title: 'Country Feasibility',
    desc: 'SEBI, RBI, and global regulatory analysis. Localized intelligence for India, UAE, USA, Singapore, and 50+ markets.',
  },
  {
    icon: '📄',
    title: 'Institutional-Grade Reports',
    desc: 'Download a 15-section PDF with executive summary, risk matrix, growth roadmap, moat analysis, and a definitive invest/no-invest verdict.',
  },
]

const VERDICTS = [
  { v: 'STRONG BUY', color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/30' },
  { v: 'BUY WITH CAUTION', color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/30' },
  { v: 'WAIT & WATCH', color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/30' },
  { v: 'PIVOT REQUIRED', color: 'text-orange-400', bg: 'bg-orange-400/10', border: 'border-orange-400/30' },
  { v: 'DO NOT INVEST', color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/30' },
]

const PACKS = [
  {
    id: 'starter', label: 'Starter', credits: 5, price: '$5', per: '$1.00 / report', popular: false,
    features: ['5 AI reports', 'Full PDF download', '12-section analysis', 'Email notification'],
  },
  {
    id: 'popular', label: 'Popular', credits: 25, price: '$20', per: '$0.80 / report', popular: true,
    features: ['25 AI reports', 'Full PDF download', 'Priority processing', 'Email reports', 'Analysis history'],
  },
  {
    id: 'pro', label: 'Pro', credits: 70, price: '$50', per: '$0.71 / report', popular: false,
    features: ['70 AI reports', 'Full PDF download', 'Priority processing', 'Email reports', 'Bulk analysis', 'Premium support'],
  },
]

const STEPS = [
  { n: '01', t: 'Submit Your Idea', d: 'Fill in your startup details: name, description, target market, stage, and founder background.' },
  { n: '02', t: '15 Agents Deploy', d: 'Market, VC, competitor, financial, risk, moat, execution simulation, startup autopsy, GTM intelligence, founder psychology, investor fit — all run in parallel.' },
  { n: '03', t: 'Dual-AI Analysis', d: 'Claude analyzes each dimension. GPT-4 cross-validates. Claude synthesizes a final consensus report.' },
  { n: '04', t: 'Download Report', d: 'Get a 15-section PDF with score, verdict, risk matrix, moat analysis, strategic alternatives — in under 6 minutes.' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-[#e2e8f0]">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-[#1e1e2e]/80 bg-[#0a0a0f]/90 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white font-bold text-sm">S</div>
              <span className="font-bold text-white text-lg">SIOS</span>
              <span className="hidden md:block text-[#475569] text-sm">Startup Intelligence OS</span>
            </div>
            <div className="hidden md:flex items-center gap-8 text-sm text-[#94a3b8]">
              <a href="#features" className="hover:text-white transition-colors">Features</a>
              <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
              <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/login" className="text-sm text-[#94a3b8] hover:text-white transition-colors hidden sm:block px-3 py-2">
                Sign In
              </Link>
              <Link href="/login" className="btn-primary text-sm px-5 py-2.5">
                Get Started →
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-36 pb-24 px-4 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-24 left-1/2 -translate-x-1/2 w-[900px] h-[600px] bg-violet-600/8 rounded-full blur-[140px]" />
        </div>
        <div className="relative max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 rounded-full px-4 py-1.5 text-sm text-violet-400 mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
            15 AI Agents · Dual-AI Cross-Validation · Real-Time Web Research
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white leading-tight mb-6">
            Know If Your Startup<br />
            <span className="gradient-text">Will Succeed</span>
          </h1>
          <p className="text-xl text-[#94a3b8] max-w-2xl mx-auto mb-10 leading-relaxed">
            SIOS deploys 12 specialized AI agents to analyze market size, financials, competition,
            and regulatory risk — then delivers an institutional-grade verdict in minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link href="/login" className="btn-primary text-base px-8 py-4 inline-flex items-center justify-center gap-2">
              Analyze My Startup →
            </Link>
            <a href="#how-it-works" className="text-[#94a3b8] hover:text-white border border-[#1e1e2e] hover:border-[#2e2e3e] rounded-lg px-8 py-4 text-base transition-all inline-flex items-center justify-center">
              See How It Works
            </a>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-2xl mx-auto">
            {[
              { n: '15', l: 'AI Agents' },
              { n: '2', l: 'AI Models' },
              { n: '21+', l: 'Data Sources' },
              { n: '<5min', l: 'Avg. Report Time' },
            ].map(s => (
              <div key={s.l} className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-4">
                <div className="text-2xl font-bold text-white">{s.n}</div>
                <div className="text-xs text-[#64748b] mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Verdict showcase */}
      <div className="py-6 border-y border-[#1e1e2e] bg-[#0d0d14]">
        <div className="max-w-5xl mx-auto px-4">
          <p className="text-center text-xs text-[#475569] uppercase tracking-widest mb-4">5 Investment Verdicts</p>
          <div className="flex flex-wrap gap-3 justify-center">
            {VERDICTS.map(v => (
              <div key={v.v} className={`${v.bg} ${v.border} border rounded-lg px-4 py-2`}>
                <span className={`font-bold text-sm ${v.color}`}>{v.v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <section id="features" className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Built for Founders & Investors</h2>
            <p className="text-[#94a3b8] text-lg max-w-xl mx-auto">
              Every dimension of startup viability, analyzed by AI that thinks like a seasoned VC.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map(f => (
              <div key={f.title} className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-6 hover:border-violet-500/30 transition-colors">
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-[#94a3b8] leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Agent pipeline */}
      <section className="py-12 px-4 bg-[#0d0d14] border-y border-[#1e1e2e]">
        <div className="max-w-5xl mx-auto">
          <p className="text-center text-xs text-[#475569] uppercase tracking-widest mb-6">Agent Pipeline</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              'Market Research', 'VC Intelligence', 'Competitor Analysis', 'Failure Risk',
              'Financial & CA', 'Country Feasibility', 'Trend Analysis',
              'Alternative Strategy', 'Moat Analysis', 'Execution Simulation',
              'Build vs Partner', 'Investor Fit',
              'Startup Autopsy', 'GTM Intelligence', 'Founder Psychology',
              'Scoring Engine', 'Investment Recommendation',
            ].map(a => (
              <span key={a} className="text-xs bg-[#0a0a0f] border border-[#1e1e2e] text-[#94a3b8] px-3 py-1.5 rounded-full">
                {a}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-[#94a3b8] text-lg">From startup idea to intelligence report in 4 steps</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {STEPS.map(s => (
              <div key={s.n}>
                <div className="text-5xl font-bold text-violet-500/20 mb-3 font-mono">{s.n}</div>
                <h3 className="font-semibold text-white mb-2">{s.t}</h3>
                <p className="text-sm text-[#94a3b8] leading-relaxed">{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-4 bg-[#0d0d14]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Simple, Pay-Per-Report Pricing</h2>
            <p className="text-[#94a3b8] text-lg">1 credit = 1 full AI startup analysis. No subscriptions. Buy once, use anytime.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PACKS.map(p => (
              <div
                key={p.id}
                className={`relative bg-[#0a0a0f] rounded-xl border p-6 ${
                  p.popular ? 'border-violet-500 ring-1 ring-violet-500/30' : 'border-[#1e1e2e]'
                }`}
              >
                {p.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <span className="bg-gradient-to-r from-violet-600 to-purple-600 text-white text-xs font-bold px-4 py-1 rounded-full whitespace-nowrap">
                      MOST POPULAR
                    </span>
                  </div>
                )}
                <div className="text-sm text-[#64748b] mb-1">{p.label}</div>
                <div className="flex items-end gap-2 mb-1">
                  <span className="text-4xl font-bold text-white">{p.price}</span>
                  <span className="text-[#64748b] text-sm pb-1">USD</span>
                </div>
                <div className="text-xs text-violet-400 mb-5">{p.credits} credits · {p.per}</div>
                <ul className="space-y-2.5 mb-6">
                  {p.features.map(f => (
                    <li key={f} className="flex items-center gap-2 text-sm text-[#94a3b8]">
                      <span className="text-emerald-400 flex-shrink-0">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/login"
                  className={`w-full text-center block py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    p.popular
                      ? 'btn-primary'
                      : 'border border-[#2e2e3e] hover:border-violet-500/40 text-white hover:text-violet-300'
                  }`}
                >
                  Get Started
                </Link>
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-[#475569] mt-8">
            New users get 1 free report to try SIOS. Payments secured by Stripe. No hidden fees.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Analyze Your Startup?</h2>
          <p className="text-[#94a3b8] text-lg mb-8">
            Join founders and investors using AI-powered intelligence to make smarter decisions.
          </p>
          <Link href="/login" className="btn-primary text-base px-10 py-4 inline-flex items-center gap-2">
            Start Free Analysis →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#1e1e2e] py-10 px-4 bg-[#0d0d14]">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white font-bold text-xs">S</div>
            <span className="font-semibold text-white">SIOS</span>
            <span className="text-[#475569] text-sm">Startup Intelligence Operating System</span>
          </div>
          <div className="text-sm text-[#475569]">
            Powered by Claude · GPT-4 · Tavily
          </div>
          <div className="text-sm text-[#475569]">© 2026 SIOS. All rights reserved.</div>
        </div>
      </footer>
    </div>
  )
}
