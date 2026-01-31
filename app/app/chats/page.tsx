'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/app/context/auth'
import { apiCall } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MessageCircle, Lock, Clock } from 'lucide-react'

interface ChatRoom {
  id: string
  user_a_handle: string
  user_b_handle: string
  created_at: string
  expires_at: string
  is_locked: boolean
  days_remaining: number
  last_activity: string
}

export default function ChatsPage() {
  const router = useRouter()
  const { tokens } = useAuth()
  const [rooms, setRooms] = useState<ChatRoom[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadChatRooms()
  }, [])

  const loadChatRooms = async () => {
    try {
      setLoading(true)
      const data = await apiCall<ChatRoom[]>('/api/chat-rooms/', {
        token: tokens?.access,
      })
      setRooms(data)
    } catch (err) {
      console.error('Failed to load chats:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading chats...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground">Messages</h1>
        </div>

        {rooms.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <MessageCircle className="w-12 h-12 mx-auto text-muted-foreground mb-4 opacity-50" />
              <p className="text-muted-foreground mb-4">No active chats yet</p>
              <Button onClick={() => router.push('/app/discover')} variant="outline">
                Start Matching
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {rooms.map((room) => (
              <Card
                key={room.id}
                className="cursor-pointer hover:bg-muted/50 transition"
                onClick={() => router.push(`/app/chat/${room.id}`)}
              >
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-foreground">
                        {room.user_a_handle === 'You' ? room.user_b_handle : room.user_a_handle}
                      </h3>
                      {room.is_locked && <Lock className="w-4 h-4 text-destructive" />}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                      {room.days_remaining > 0 ? (
                        <>
                          <Clock className="w-4 h-4" />
                          <span>{room.days_remaining} days remaining</span>
                        </>
                      ) : (
                        <span className="text-destructive">Expired</span>
                      )}
                    </div>
                  </div>
                  {room.is_locked && (
                    <Button size="sm" variant="outline" onClick={(e) => {
                      e.stopPropagation()
                      router.push(`/app/subscribe/${room.id}`)
                    }}>
                      Unlock
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
