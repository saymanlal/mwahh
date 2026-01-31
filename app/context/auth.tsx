'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  user_uuid: string
  anonymous_handle: string
  gender: string
  age: number
  height_cm: number
  degree: string
  profession: string
  city: string
  state: string
  bio: string
  interests: string[]
  photos: string[]
  tokens_balance: number
  is_verified: boolean
  created_at: string
}

interface AuthContextType {
  user: User | null
  tokens: { access: string; refresh: string } | null
  isLoading: boolean
  register: (email: string, password: string) => Promise<void>
  verifyOtp: (email: string, otp: string) => Promise<void>
  resendOtp: (email: string) => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [tokens, setTokens] = useState<{ access: string; refresh: string } | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    const stored = localStorage.getItem('auth_tokens')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setTokens(parsed)
      } catch {
        localStorage.removeItem('auth_tokens')
      }
    }
    setIsLoading(false)
  }, [])

  const register = async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/api/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) throw new Error('Registration failed')
  }

  const verifyOtp = async (email: string, otp: string) => {
    const res = await fetch(`${API_URL}/api/auth/verify-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, otp }),
    })
    if (!res.ok) throw new Error('OTP verification failed')

    const data = await res.json()
    setUser(data.user)
    setTokens({ access: data.access, refresh: data.refresh })
    localStorage.setItem('auth_tokens', JSON.stringify({ access: data.access, refresh: data.refresh }))
  }

  const resendOtp = async (email: string) => {
    const res = await fetch(`${API_URL}/api/auth/resend-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    if (!res.ok) throw new Error('Failed to resend OTP')
  }

  const updateProfile = async (data: Partial<User>) => {
    const res = await fetch(`${API_URL}/api/users/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tokens?.access}`,
      },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Profile update failed')

    const updated = await res.json()
    setUser(updated)
  }

  const logout = () => {
    setUser(null)
    setTokens(null)
    localStorage.removeItem('auth_tokens')
  }

  return (
    <AuthContext.Provider value={{ user, tokens, isLoading, register, verifyOtp, resendOtp, updateProfile, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
