# Matchmaking Platform

A campus-verified anonymous matchmaking and real-time chat platform with dual matching modes (Friend/Hookup), token economy, premium continuation model, and comprehensive admin dashboard.

**Status: Production-Ready. Fully deployable via Vercel + Railway/Render.**

---

## Tech Stack

### Backend
- **Django 4.2** + Django REST Framework
- **Django Channels** for real-time WebSocket chat
- **PostgreSQL** for data persistence
- **Redis** for caching, sessions, and pub/sub
- **Celery** for async tasks (emails, reminders, cleanup)
- **JWT** authentication

### Frontend
- **Next.js 16** with App Router
- **Tailwind CSS v4** for styling
- **WebSocket** client for real-time chat
- **React 19** with modern hooks

---

## Features

### User Authentication
- Email-based registration with OTP verification
- Institutional verification (domain-based or manual approval)
- Anonymous user handles (no names/emails exposed)
- JWT-based API authentication

### Matching System
- **Friend Mode**: Any ↔ Any gender, fully inclusive
- **Hookup Mode**: Opposite gender only (server-enforced)
- Infinite free matching
- Filters: Scope, degree/profession, age, height, interests
- Server-side match scoring

### Real-Time Chat
- WebSocket-powered instant messaging
- Message types: Text, Images, Voice, Stickers, Gifts
- Typing indicators
- Seen receipts
- Rate limiting for abuse prevention
- Auto-expire after 7 days (with payment reminder on day 5)

### Premium Model
- Free 7-day chat access
- ₹50/month to continue chat
- 200 free tokens on signup
- Token packs: ₹100 → 400 tokens
- Tokens for premium stickers and gifts

### Media & Stickers
- Thousands of stickers (free + premium mix)
- Gift animations via Lottie
- Voice message support
- Image compression and optimization
- Media serving via CDN

### Admin Dashboard
- View all users with real email addresses
- Ban/delete users
- Force lock/unlock chat rooms
- Extend chat access without payment
- Upload stickers, gifts, reminder media
- View payment history
- Moderate abuse reports
- Approve institute domains

### Privacy
- Real emails visible only to admin
- Users identified by anonymous handle and UUID
- No message content in notifications
- Secure password hashing (bcrypt)

---

## Project Structure

```
.
├── backend/
│   ├── config/
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # URL routing
│   │   ├── asgi.py              # WebSocket/ASGI config
│   │   └── celery.py            # Celery config
│   ├── api/
│   │   ├── models.py            # Data models
│   │   ├── views.py             # REST endpoints
│   │   ├── serializers.py       # Data serialization
│   │   ├── consumers.py         # WebSocket consumers
│   │   ├── matching.py          # Matching algorithm
│   │   ├── tasks.py             # Celery background jobs
│   │   └── migrations/          # DB migrations
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Container image
│   ├── Procfile                # Heroku/Railway deployment
│   └── manage_setup.py         # Management commands
│
├── app/
│   ├── page.tsx                # Home page
│   ├── layout.tsx              # Root layout
│   ├── globals.css             # Tailwind + design tokens
│   ├── context/
│   │   └── auth.tsx            # Auth state
│   ├── hooks/
│   │   ├── useChat.ts          # WebSocket hook
│   │   └── useFetch.ts         # Data fetching hook
│   ├── lib/
│   │   └── api.ts              # API utilities
│   ├── auth/
│   │   ├── register/page.tsx   # Registration
│   │   ├── verify/page.tsx     # OTP verification
│   │   └── layout.tsx          # Auth layout
│   ├── app/
│   │   ├── profile/page.tsx    # Profile setup
│   │   ├── discover/page.tsx   # Matching interface
│   │   ├── chats/page.tsx      # Chat list
│   │   ├── chat/[id]/page.tsx  # Chat detail
│   │   ├── subscribe/[id]/page.tsx # Payment page
│   │   └── layout.tsx          # App layout
│   └── components/
│       └── ChatMessage.tsx     # Message component
│
├── docs/
│   ├── API_DOCUMENTATION.md    # REST API reference
│   ├── WEBSOCKET_EVENTS.md     # WebSocket events
│   ├── ENVIRONMENT_VARIABLES.md # Env var reference
│   ├── ADMIN_GUIDE.md          # Admin dashboard guide
│   ├── DEPLOYMENT.md           # Local/Docker setup
│   └── VERCEL_DEPLOYMENT.md    # Production deployment
│
├── tests/
│   └── load_test.py            # Performance testing
│
├── docker-compose.yml          # Local development
├── vercel.json                 # Vercel config
├── .env.example                # Environment template
└── Dockerfile                  # Frontend (if needed)
```

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL & Redis (via Docker)

### Setup Backend

```bash
# Clone repo
git clone <repo> && cd <repo>

# Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp ../.env.example ../.env
# Edit .env with your local DB credentials

# Run migrations
python manage.py migrate

# Create superuser/admin
python manage_setup.py create-admin

# Seed data
python manage_setup.py seed-domains
python manage_setup.py seed-stickers

# Start backend
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

In separate terminals:

```bash
# Celery worker
celery -A config worker -l info

# Celery beat (for scheduled tasks)
celery -A config beat -l info
```

### Setup Frontend

```bash
# In project root (not backend/)
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local

# Start dev server
npm run dev

# Open http://localhost:3000
```

### Using Docker Compose

```bash
# Copy environment template
cp .env.example .env

# Start all services
docker-compose up

# In another terminal, run migrations
docker-compose exec backend python manage.py migrate

# Create admin user
docker-compose exec backend python manage_setup.py create-admin
```

---

## Deployment

### Frontend: Vercel

1. Push code to GitHub
2. Connect repo to Vercel
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_WS_URL`
4. Deploy (automatic on push to main)

### Backend: Railway

1. Connect GitHub repo to Railway
2. Add PostgreSQL and Redis services
3. Configure environment variables
4. Deploy from `Procfile`

**See `/docs/VERCEL_DEPLOYMENT.md` for detailed production deployment.**

---

## API Reference

Full REST API documentation: `/docs/API_DOCUMENTATION.md`

Key endpoints:

```
POST   /api/auth/register           # User registration
POST   /api/auth/verify-otp         # OTP verification
POST   /api/auth/login              # JWT login
GET    /api/profile/                # User profile
PATCH  /api/profile/                # Update profile
POST   /api/matches/                # Get matches
GET    /api/chats/                  # List chats
WS     /ws/chat/{room_id}/          # WebSocket chat
POST   /api/payments/               # Create payment
GET    /api/notifications/          # Get notifications
```

---

## WebSocket Events

Full WebSocket documentation: `/docs/WEBSOCKET_EVENTS.md`

Key events:

```json
// Client sends
{"type": "message", "message_type": "text", "content": "Hello"}
{"type": "typing"}
{"type": "seen", "message_id": "uuid"}

// Server sends
{"type": "message", "message": {...}}
{"type": "typing", "user_handle": "anon_xyz"}
{"type": "chat_locked", "reason": "expired"}
```

---

## Admin Dashboard

Access via `/admin` (Django built-in) or custom admin panel.

Functions:
- User management (view, ban, delete)
- Chat management (lock, unlock, delete)
- Media uploads (stickers, gifts, reminders)
- Payment verification
- Institute domain approval
- Abuse report moderation

**See `/docs/ADMIN_GUIDE.md` for complete admin guide.**

---

## Environment Variables

Required for production:

```
# Backend
DJANGO_SECRET_KEY=<random-secret>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DB_NAME=matchmaking
DB_USER=postgres
DB_PASSWORD=<secure-password>
DB_HOST=<db-host>
DB_PORT=5432
REDIS_URL=redis://<redis-host>:6379/0
CELERY_BROKER_URL=redis://<redis-host>:6379/1

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD_HASH=<hashed-password>

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<app-password>

# AWS S3 (optional)
USE_S3=True
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_STORAGE_BUCKET_NAME=<bucket>
```

**See `/docs/ENVIRONMENT_VARIABLES.md` for complete reference.**

---

## Performance & Scaling

- Redis caching for frequently accessed data
- Database connection pooling
- Pagination on all list endpoints
- WebSocket connection pooling via Channels
- Message rate limiting (prevents spam)
- Celery task queue for heavy operations

**See `/tests/load_test.py` for performance benchmarks.**

---

## Testing

```bash
# Load testing
python tests/load_test.py --users 100 --duration 60

# Backend tests
python backend/manage.py test

# Frontend tests
npm test
```

---

## Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- CORS configured for frontend domains
- Rate limiting on sensitive endpoints
- SQL injection prevention (Django ORM)
- XSS protection (React sanitization)
- CSRF tokens for state-changing operations
- Institutional email verification required
- Admin credentials in environment variables

---

## Monitoring

Recommended services:
- **Errors**: Sentry (`SENTRY_DSN`)
- **Analytics**: Vercel Analytics (free with Vercel)
- **Logs**: Railway/Render built-in logging
- **Uptime**: Pingdom, Monitoring.io

---

## Support & Documentation

- **API Docs**: `/docs/API_DOCUMENTATION.md`
- **WebSocket**: `/docs/WEBSOCKET_EVENTS.md`
- **Admin**: `/docs/ADMIN_GUIDE.md`
- **Deployment**: `/docs/VERCEL_DEPLOYMENT.md`
- **Environment**: `/docs/ENVIRONMENT_VARIABLES.md`

---

## License

Proprietary. All rights reserved.

---

## Next Steps

1. Clone repository
2. Copy `.env.example` → `.env`
3. `docker-compose up`
4. Visit `http://localhost:3000`
5. Deploy to production (see VERCEL_DEPLOYMENT.md)

Happy matching! 🎉
