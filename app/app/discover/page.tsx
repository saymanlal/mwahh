'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/app/context/auth'
import { apiCall } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Heart, X, Zap } from 'lucide-react'

interface Match {
  id: string
  user_a_handle: string
  user_b_handle: string
  mode: string
  created_at: string
}

interface Candidate {
  user_uuid: string
  anonymous_handle: string
  gender: string
  age: number
  height_cm: number
  degree: string
  profession: string
  city: string
  interests: string[]
}

export default function DiscoverPage() {
  const { tokens, user } = useAuth()
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [mode, setMode] = useState<'friend' | 'hookup'>('friend')

  useEffect(() => {
    loadCandidates()
  }, [mode])

  const loadCandidates = async () => {
    try {
      setLoading(true)
      const data = await apiCall<any>('/api/matching/', {
        token: tokens?.access,
      })
      setCandidates(data)
      setCurrentIndex(0)
    } catch (err) {
      console.error('Failed to load candidates:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleMatch = async (targetUuid: string, accept: boolean) => {
    if (!accept) {
      setCurrentIndex((prev) => prev + 1)
      return
    }

    try {
      await apiCall<Match>('/api/matching/create_match/', {
        method: 'POST',
        token: tokens?.access,
        body: JSON.stringify({
          target_user_id: targetUuid,
          mode,
        }),
      })

      setCurrentIndex((prev) => prev + 1)
    } catch (err) {
      console.error('Failed to create match:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading matches...</p>
        </div>
      </div>
    )
  }

  const currentCandidate = candidates[currentIndex]
  const hasMoreCandidates = currentIndex < candidates.length

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6 flex gap-2">
          <Button
            variant={mode === 'friend' ? 'default' : 'outline'}
            onClick={() => setMode('friend')}
            className="flex-1"
          >
            <Zap className="w-4 h-4 mr-2" />
            Friends
          </Button>
          <Button
            variant={mode === 'hookup' ? 'default' : 'outline'}
            onClick={() => setMode('hookup')}
            className="flex-1"
          >
            <Heart className="w-4 h-4 mr-2" />
            Dating
          </Button>
        </div>

        {!hasMoreCandidates ? (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-muted-foreground mb-4">No more matches available</p>
              <Button onClick={loadCandidates} variant="outline">
                Refresh
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            <Card className="overflow-hidden">
              <CardContent className="p-0">
                <div className="bg-gradient-to-br from-primary/20 to-accent/20 h-96 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-foreground mb-2">
                      {currentCandidate?.anonymous_handle}
                    </p>
                    <div className="flex gap-4 justify-center text-sm text-muted-foreground">
                      {currentCandidate?.age && <span>{currentCandidate.age}y</span>}
                      {currentCandidate?.city && <span>{currentCandidate.city}</span>}
                      {currentCandidate?.degree && <span>{currentCandidate.degree}</span>}
                    </div>
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {currentCandidate?.profession && (
                    <div>
                      <p className="text-sm text-muted-foreground">Profession</p>
                      <p className="font-medium">{currentCandidate.profession}</p>
                    </div>
                  )}

                  {currentCandidate?.interests && currentCandidate.interests.length > 0 && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Interests</p>
                      <div className="flex flex-wrap gap-2">
                        {currentCandidate.interests.map((interest) => (
                          <span key={interest} className="px-3 py-1 bg-muted rounded-full text-sm">
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-4">
              <Button
                variant="outline"
                className="flex-1 h-12 bg-transparent"
                onClick={() => handleMatch(currentCandidate?.user_uuid, false)}
              >
                <X className="w-5 h-5" />
              </Button>
              <Button
                className="flex-1 h-12"
                onClick={() => handleMatch(currentCandidate?.user_uuid, true)}
              >
                <Heart className="w-5 h-5 mr-2" />
                Match
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
