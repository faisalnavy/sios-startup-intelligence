'use client'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabase'
import { getUserCredits } from '../../lib/api'
import { signOut } from '../../lib/auth'

const NAV = [
  { href: '/dashboard',         label: 'Dashboard',     icon: '⊞' },
  { href: '/dashboard/new',     label: 'New Analysis',  icon: '+' },
  { href: '/dashboard/credits', label: 'Buy Credits',   icon: '◎' },
  { href: '/dashboard/billing', label: 'Billing',       icon: '⊙' },
  { href: '/dashboard/usage',   label: 'Usage',         icon: '▦' },
]

function isLocalDev() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
  return !url || url.includes('YOUR_PROJECT_ID')
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const [credits, setCredits] = useState<number | null>(null)
  const [user, setUser] = useState<any>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user)
      if (!data.user && !isLocalDev()) router.push('/login')
    })
    getUserCredits().then(setCredits).catch(() => setCredits(0))
  }, [])

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  const initials = user?.email ? user.email[0].toUpperCase() : 'U'

  return (
    <div className="flex min-h-screen bg-[#0a0a0f]">
      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-64 bg-[#0d0d14] border-r border-[#1e1e2e] flex flex-col
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:relative lg:translate-x-0
        `}
      >
        {/* Logo */}
        <div className="p-5 border-b border-[#1e1e2e]">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white font-bold text-sm">S</div>
            <span className="font-bold text-white">SIOS</span>
          </Link>
        </div>

        {/* Credit balance */}
        <div className="p-4">
          <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg p-3">
            <div className="text-xs text-violet-400 mb-1">Available Credits</div>
            <div className="text-2xl font-bold text-white">{credits ?? '—'}</div>
            <Link href="/dashboard/credits" className="text-xs text-violet-400 hover:text-violet-300 transition-colors mt-1 inline-block">
              Buy more →
            </Link>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 pb-4 space-y-0.5">
          {NAV.map(item => {
            const active = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  active
                    ? 'bg-violet-500/15 text-violet-300 font-medium'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#1a1a28]'
                }`}
              >
                <span className="w-4 text-center text-base">{item.icon}</span>
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* User */}
        <div className="p-4 border-t border-[#1e1e2e]">
          {user ? (
            <>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-300 text-sm font-bold flex-shrink-0">
                  {initials}
                </div>
                <div className="min-w-0">
                  <div className="text-xs text-white truncate">{user.email}</div>
                  <div className="text-xs text-[#475569]">Signed in</div>
                </div>
              </div>
              <button
                onClick={handleSignOut}
                className="text-xs text-[#64748b] hover:text-red-400 transition-colors"
              >
                Sign out
              </button>
            </>
          ) : (
            <div className="text-xs text-[#475569]">Local dev mode</div>
          )}
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-[#1e1e2e] bg-[#0d0d14]">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-[#94a3b8] hover:text-white p-1"
            aria-label="Open menu"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
          <span className="font-bold text-white text-sm">SIOS</span>
          <div className="text-xs text-violet-400 font-bold">
            {credits ?? '—'} cr
          </div>
        </header>

        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
