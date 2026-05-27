import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SIOS — Startup Intelligence Operating System',
  description: 'AI-powered startup analysis with dual Claude + OpenAI intelligence',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  )
}
