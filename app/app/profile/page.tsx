'use client'

import React from "react"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/app/context/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ProfileSetupPage() {
  const router = useRouter()
  const { user, updateProfile, tokens } = useAuth()
  const [formData, setFormData] = useState({
    gender: user?.gender || '',
    age: user?.age || '',
    height_cm: user?.height_cm || '',
    degree: user?.degree || '',
    profession: user?.profession || '',
    city: user?.city || '',
    state: user?.state || '',
    bio: user?.bio || '',
    interests: user?.interests || [],
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const interestOptions = [
    'Sports',
    'Music',
    'Art',
    'Technology',
    'Food',
    'Travel',
    'Books',
    'Movies',
    'Gaming',
    'Fitness',
    'Cooking',
    'Photography',
    'Fashion',
    'Hiking',
    'Dancing',
  ]

  const handleInterestToggle = (interest: string) => {
    setFormData((prev) => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter((i) => i !== interest)
        : [...prev.interests, interest],
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await updateProfile({
        ...formData,
        age: formData.age ? parseInt(formData.age) : undefined,
        height_cm: formData.height_cm ? parseInt(formData.height_cm) : undefined,
      })
      router.push('/app/discover')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Complete Your Profile</CardTitle>
            <CardDescription>Tell us about yourself to get better matches</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Gender</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  >
                    <option value="">Select gender</option>
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="NB">Non-Binary</option>
                    <option value="O">Other</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">Age</label>
                  <Input
                    type="number"
                    min="18"
                    max="100"
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">Height (cm)</label>
                  <Input
                    type="number"
                    value={formData.height_cm}
                    onChange={(e) => setFormData({ ...formData, height_cm: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">Degree</label>
                  <Input
                    type="text"
                    placeholder="e.g., B.Tech Computer Science"
                    value={formData.degree}
                    onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium mb-1 block">Profession</label>
                <Input
                  type="text"
                  placeholder="e.g., Software Engineer"
                  value={formData.profession}
                  onChange={(e) => setFormData({ ...formData, profession: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">City</label>
                  <Input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">State</label>
                  <Input
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Bio</label>
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  maxLength={500}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                  rows={4}
                  placeholder="Tell others about yourself"
                />
                <p className="text-xs text-muted-foreground mt-1">{formData.bio.length}/500</p>
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">Interests</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {interestOptions.map((interest) => (
                    <button
                      key={interest}
                      type="button"
                      onClick={() => handleInterestToggle(interest)}
                      className={`px-3 py-2 rounded-full text-sm font-medium transition ${
                        formData.interests.includes(interest)
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground hover:bg-muted'
                      }`}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </div>

              {error && <div className="text-sm text-destructive">{error}</div>}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Saving...' : 'Continue to Discover'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
