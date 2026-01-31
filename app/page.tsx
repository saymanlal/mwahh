import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Heart, Shield, Zap, Users } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-foreground">MatchHub</div>
            <Link href="/auth/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-16">
        <section className="text-center mb-20">
          <h1 className="text-5xl font-bold text-foreground mb-4">
            Real Connections, Verified Community
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Campus-verified anonymous matchmaking. Find friends and dates in your college community.
          </p>
          <Link href="/auth/register">
            <Button size="lg" className="text-base h-12">
              Create Account
            </Button>
          </Link>
        </section>

        <section className="grid md:grid-cols-2 gap-8 mb-20">
          <Card>
            <CardHeader>
              <Shield className="w-8 h-8 text-primary mb-2" />
              <CardTitle>Verified Community</CardTitle>
              <CardDescription>
                Only institutional email addresses allowed. Real people, real connections.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Heart className="w-8 h-8 text-primary mb-2" />
              <CardTitle>Dual Modes</CardTitle>
              <CardDescription>
                Find friends or dates. You choose the mode before matching.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Users className="w-8 h-8 text-primary mb-2" />
              <CardTitle>Anonymous & Private</CardTitle>
              <CardDescription>
                Your real email is hidden. Use an anonymous handle. Stay in control.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="w-8 h-8 text-primary mb-2" />
              <CardTitle>Real-Time Chat</CardTitle>
              <CardDescription>
                Instant messaging with typing indicators and read receipts.
              </CardDescription>
            </CardHeader>
          </Card>
        </section>

        <section className="bg-muted p-8 rounded-lg text-center mb-20">
          <h2 className="text-3xl font-bold text-foreground mb-4">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-4 mt-8">
            <div className="text-sm">
              <div className="text-2xl font-bold text-primary mb-2">1</div>
              <p className="text-muted-foreground">Register with your college email</p>
            </div>
            <div className="text-sm">
              <div className="text-2xl font-bold text-primary mb-2">2</div>
              <p className="text-muted-foreground">Verify via OTP</p>
            </div>
            <div className="text-sm">
              <div className="text-2xl font-bold text-primary mb-2">3</div>
              <p className="text-muted-foreground">Complete your profile</p>
            </div>
            <div className="text-sm">
              <div className="text-2xl font-bold text-primary mb-2">4</div>
              <p className="text-muted-foreground">Start matching & chatting</p>
            </div>
          </div>
        </section>

        <section className="text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Ready to Connect?</h2>
          <p className="text-muted-foreground mb-8">Join thousands of students finding genuine connections.</p>
          <Link href="/auth/register">
            <Button size="lg" className="text-base h-12">
              Get Started Free
            </Button>
          </Link>
        </section>
      </main>

      <footer className="border-t bg-card mt-20">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2024 MatchHub. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
