'use client'

import React from "react"

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/app/context/auth'
import { apiCall, getWebSocketUrl } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, Send, Loader2 } from 'lucide-react'

interface ChatMessage {
  id: string
  sender_handle: string
  message_type: string
  content: string
  media_url: string
  is_seen: boolean
  created_at: string
}

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
  const roomId = params.id as string
  const { tokens, user } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadMessages()
    connectWebSocket()

    return () => {
      ws?.close()
    }
  }, [roomId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadMessages = async () => {
    try {
      const data = await apiCall<ChatMessage[]>(`/api/chat-rooms/${roomId}/messages/`, {
        token: tokens?.access,
      })
      setMessages(data)
    } catch (err) {
      console.error('Failed to load messages:', err)
    }
  }

  const connectWebSocket = () => {
    try {
      const wsUrl = getWebSocketUrl(`/ws/chat/${roomId}/`)
      const socket = new WebSocket(wsUrl)

      socket.onopen = () => {
        console.log('Connected to chat')
      }

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'message') {
          setMessages((prev) => [...prev, data])
        }
      }

      socket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      setWs(socket)
    } catch (err) {
      console.error('Failed to connect WebSocket:', err)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !ws) return

    setLoading(true)

    try {
      ws.send(
        JSON.stringify({
          type: 'message',
          message_type: 'text',
          content: input,
        })
      )

      setInput('')
    } catch (err) {
      console.error('Failed to send message:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="border-b bg-card p-4">
        <div className="max-w-2xl mx-auto flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.back()}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold text-foreground flex-1">Chat</h1>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No messages yet. Start the conversation!</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender_handle === user?.anonymous_handle ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    message.sender_handle === user?.anonymous_handle
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  <p className="text-sm break-words">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t bg-card p-4">
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              type="text"
              placeholder="Type a message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading || !ws}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={loading || !ws || !input.trim()}
              size="icon"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
