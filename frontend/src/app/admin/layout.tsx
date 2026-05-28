'use client'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabase'

const NAV = [
  { href: '/admin',           label: 'Dashboard',   icon: '📊' },
  { href: '/admin/users',     label: 'Users',        icon: '👥' },
  { href: '/admin/analyses',  label: 'Analyses',     icon: '🔍' },
  { href: '/admin/pricing',   label: 'Pricing',      icon: '💳' },
]

function isLocalDev() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
  return !url || url.includes('YOUR_PROJECT_ID')
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname  = usePathname()
  const router    = useRouter()
  const [user, setUser]         = useState<any>(null)
  const [checking, setChecking] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    async function checkAdmin() {
      if (isLocalDev()) {
        // Local dev — allow access without auth check
        setUser({ email: 'admin@localhost', isAdmin: true })
        setChecking(false)
        return
      }
      const { data } = await supabase.auth.getUser()
      if (!data.user) {
        router.push('/login')
        return
      }
      // Check admin flag in JWT metadata
      const { data: { session } } = await supabase.auth.getSession()
      const meta = session?.user?.app_metadata || {}
      const userMeta = session?.user?.user_metadata || {}
      if (!meta.is_admin && !userMeta.is_admin) {
        router.push('/dashboard')
        return
      }
      setUser(data.user)
      setChecking(false)
    }
    checkAdmin()
  }, [])

  if (checking) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="flex items-center gap-3 text-[#64748b]">
          <span className="w-5 h-5 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
          Verifying access...
        </div>
      </div>
    )
  }

  const initials = user?.email ? user.email[0].toUpperCase() : 'A'

  return (
    <div className="flex min-h-screen bg-[#0a0a0f]">
      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-60 bg-[#0d0d14] border-r border-[#1e1e2e] flex flex-col
        transform transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:relative lg:translate-x-0
      `}>
        {/* Logo */}
        <div className="p-5 border-b border-[#1e1e2e]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center text-white font-bold text-xs">
              ADM
            </div>
            <div>
              <div className="font-bold text-white text-sm">SIOS Admin</div>
              <div className="text-xs text-red-400">Restricted Access</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {NAV.map(item => {
            const active = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  active
                    ? 'bg-red-500/15 text-red-300 font-medium'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#1a1a28]'
                }`}
              >
                <span className="text-base">{item.icon}</span>
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* Links to user dashboard */}
        <div className="px-3 py-2 border-t border-[#1e1e2e] space-y-0.5">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-[#64748b] hover:text-white hover:bg-[#1a1a28] transition-colors"
          >
            <span>⬅</span> User Dashboard
          </Link>
        </div>

        {/* User */}
        <div className="p-4 border-t border-[#1e1e2e]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-300 text-sm font-bold flex-shrink-0">
              {initials}
            </div>
            <div className="min-w-0">
              <div className="text-xs text-white truncate">{user?.email}</div>
              <div className="text-xs text-red-400">Admin</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-30 bg-black/60 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-[#1e1e2e] bg-[#0d0d14]">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-[#94a3b8] hover:text-white p-1"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
          <span className="font-bold text-white text-sm">SIOS Admin</span>
          <div className="text-xs text-red-400 font-bold">ADMIN</div>
        </header>

        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
