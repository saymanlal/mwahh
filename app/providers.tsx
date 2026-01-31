'use client'

import { AuthProvider } from './context/auth'
import { Analytics } from '@vercel/analytics/next'
import { ReactNode } from 'react'

export function RootProvider({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
      <Analytics />
    </AuthProvider>
  )
}
