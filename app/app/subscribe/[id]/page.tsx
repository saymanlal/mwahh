'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/app/context/auth'
import { apiCall } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, Check } from 'lucide-react'

export default function SubscribePage() {
  const params = useParams()
  const router = useRouter()
  const roomId = params.id as string
  const { tokens } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handlePayment = async (method: 'upi' | 'card') => {
    setLoading(true)
    setError('')

    try {
      const response = await apiCall<any>('/api/payments/initiate/', {
        method: 'POST',
        token: tokens?.access,
        body: JSON.stringify({
          chat_room_id: roomId,
          amount_paise: 5000,
          currency: 'INR',
          payment_method: method,
        }),
      })

      if (method === 'upi') {
        if (response.upi_link) {
          window.location.href = response.upi_link
        }
      } else if (method === 'card') {
        if (response.checkout_url) {
          window.location.href = response.checkout_url
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment initiation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="mb-6"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Continue Chatting</CardTitle>
            <CardDescription>Unlock your chat room for 30 days</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-muted p-4 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <span className="text-foreground font-medium">Subscription</span>
                <span className="text-2xl font-bold text-primary">₹50</span>
              </div>
              <div className="space-y-2 text-sm text-muted-foreground">
                <div className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" />
                  <span>30 days of unlimited messaging</span>
                </div>
                <div className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" />
                  <span>Send gifts and stickers</span>
                </div>
                <div className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" />
                  <span>Voice messages and media</span>
                </div>
              </div>
            </div>

            {error && <div className="text-sm text-destructive">{error}</div>}

            <div className="space-y-3">
              <Button
                className="w-full h-12"
                onClick={() => handlePayment('upi')}
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Pay via UPI'}
              </Button>

              <Button
                variant="outline"
                className="w-full h-12 bg-transparent"
                onClick={() => handlePayment('card')}
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Pay via Card'}
              </Button>
            </div>

            <div className="text-xs text-muted-foreground text-center">
              Payment is secure and encrypted. Your payment details are never shared.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
