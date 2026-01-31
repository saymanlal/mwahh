'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/app/context/auth'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'

export function AppLayoutClient({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { user, isLoading, logout } = useAuth()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/register')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold text-foreground">MatchHub</div>
          <div className="flex items-center gap-4">
            <a
              href="/app/discover"
              className="text-foreground hover:text-muted-foreground transition"
            >
              Discover
            </a>
            <a
              href="/app/chats"
              className="text-foreground hover:text-muted-foreground transition"
            >
              Messages
            </a>
            <a
              href="/app/profile"
              className="text-foreground hover:text-muted-foreground transition"
            >
              Profile
            </a>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                logout()
                router.push('/')
              }}
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </nav>

      {children}
    </div>
  )
}
