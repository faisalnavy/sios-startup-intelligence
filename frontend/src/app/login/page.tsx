'use client'
import Link from 'next/link'
import { useState } from 'react'
import { signInWithGoogle, signInWithMicrosoft, signInWithFacebook } from '../../lib/auth'

export default function LoginPage() {
  const [loading, setLoading] = useState<string | null>(null)
  const [error, setError] = useState('')

  const handleAuth = async (provider: 'google' | 'microsoft' | 'facebook') => {
    setLoading(provider)
    setError('')
    try {
      const fn =
        provider === 'google' ? signInWithGoogle
        : provider === 'microsoft' ? signInWithMicrosoft
        : signInWithFacebook
      const { error: authError } = await fn()
      if (authError) setError(authError.message)
    } catch (e: any) {
      setError(e.message || 'Authentication failed. Please check your Supabase configuration.')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-[#0a0a0f]">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-3 mb-6">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white font-bold text-lg">S</div>
            <span className="font-bold text-white text-2xl">SIOS</span>
          </Link>
          <h1 className="text-2xl font-bold text-white mb-2">Welcome to SIOS</h1>
          <p className="text-[#94a3b8] text-sm">Sign in to access your startup intelligence dashboard</p>
        </div>

        {/* Auth card */}
        <div className="bg-[#111118] border border-[#1e1e2e] rounded-xl p-8">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm mb-5">
              {error}
            </div>
          )}

          <div className="space-y-3">
            {/* Google */}
            <button
              onClick={() => handleAuth('google')}
              disabled={!!loading}
              className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-50 text-gray-900 font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading === 'google' ? (
                <span className="w-5 h-5 border-2 border-gray-300 border-t-gray-700 rounded-full animate-spin" />
              ) : <GoogleIcon />}
              Continue with Google
            </button>

            {/* Microsoft */}
            <button
              onClick={() => handleAuth('microsoft')}
              disabled={!!loading}
              className="w-full flex items-center justify-center gap-3 bg-[#0078d4] hover:bg-[#006cbd] text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading === 'microsoft' ? (
                <span className="w-5 h-5 border-2 border-blue-300 border-t-white rounded-full animate-spin" />
              ) : <MicrosoftIcon />}
              Continue with Microsoft
            </button>

            {/* Facebook */}
            <button
              onClick={() => handleAuth('facebook')}
              disabled={!!loading}
              className="w-full flex items-center justify-center gap-3 bg-[#1877f2] hover:bg-[#166fe5] text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading === 'facebook' ? (
                <span className="w-5 h-5 border-2 border-blue-300 border-t-white rounded-full animate-spin" />
              ) : <FacebookIcon />}
              Continue with Facebook
            </button>
          </div>

          <div className="mt-6 pt-5 border-t border-[#1e1e2e] text-center">
            <p className="text-xs text-[#475569] leading-relaxed">
              By signing in, you agree to our Terms of Service and Privacy Policy.
              <br />
              <span className="text-violet-400">New users get 1 free report credit.</span>
            </p>
          </div>
        </div>

        <div className="text-center mt-6">
          <Link href="/" className="text-sm text-[#64748b] hover:text-white transition-colors inline-flex items-center gap-1">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  )
}

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  )
}

function MicrosoftIcon() {
  return (
    <svg viewBox="0 0 21 21" width="20" height="20" aria-hidden="true">
      <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
      <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
      <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
      <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
    </svg>
  )
}

function FacebookIcon() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="white" aria-hidden="true">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
  )
}
