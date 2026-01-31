# Quick Start Guide

## Local Development (5 minutes)

### Prerequisites
- Docker & Docker Compose installed
- Node.js 18+ (for frontend development)
- Git

### Run Everything Locally

```bash
# 1. Clone the repository
git clone <repo-url>
cd <repo-name>

# 2. Copy environment variables
cp .env.example .env

# 3. Start all services (PostgreSQL, Redis, Django, Celery)
docker-compose up

# In another terminal:

# 4. Run migrations
docker-compose exec backend python manage.py migrate

# 5. Create admin user
docker-compose exec backend python manage_setup.py create-admin

# 6. Seed initial data
docker-compose exec backend python manage_setup.py seed-domains
docker-compose exec backend python manage_setup.py seed-stickers

# 7. Start frontend (in project root)
npm install
npm run dev

# 8. Access the app
# Frontend: http://localhost:3000
# Admin: http://localhost:8000/admin (use admin@example.com credentials)
# API: http://localhost:8000/api/
```

---

## Backend Setup (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export DATABASE_URL=postgresql://user:password@localhost/matchmaking
export REDIS_URL=redis://localhost:6379/0

# Ensure PostgreSQL & Redis are running, then:
python manage.py migrate
python manage.py runserver

# In separate terminals:
celery -A config worker -l info
celery -A config beat -l info
```

---

## Frontend Setup (without Docker)

```bash
# In project root (not backend/)
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local

# Start dev server
npm run dev

# Open http://localhost:3000
```

---

## Production Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

**Frontend:**
1. Push code to GitHub
2. Connect repo to Vercel
3. Set env vars: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`
4. Deploy (automatic)

**Backend:**
1. Connect GitHub repo to Railway
2. Add PostgreSQL service
3. Add Redis service
4. Set all environment variables (see `/docs/ENVIRONMENT_VARIABLES.md`)
5. Deploy from `Procfile`

### Option 2: Docker Hub + AWS/Heroku

```bash
# Build Docker image
docker build -t your-username/matchmaking-backend ./backend

# Push to Docker Hub
docker push your-username/matchmaking-backend

# Deploy to Heroku/AWS/Render using the image
```

### Option 3: Full Docker Compose on VPS

```bash
# On VPS:
git clone <repo>
cd <repo>

# Set production .env
nano .env

# Start with reverse proxy (Nginx)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Database Setup

### Backup
```bash
docker-compose exec postgres pg_dump -U postgres matchmaking > backup.sql
```

### Restore
```bash
docker-compose exec -T postgres psql -U postgres matchmaking < backup.sql
```

---

## Admin Dashboard

Access at: `http://localhost:8000/admin`

Login with credentials set in `.env`:
- Email: `ADMIN_EMAIL`
- Password: `ADMIN_PASSWORD_HASH`

Functions:
- View/ban users
- Manage chat rooms
- Upload stickers and gifts
- View payments
- Approve institute domains

---

## Testing

### Load Test
```bash
python tests/load_test.py --users 50 --duration 60
```

### Backend Tests
```bash
python backend/manage.py test
```

### Frontend Tests
```bash
npm test
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 3000/8000
lsof -i :3000
kill -9 <PID>
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Verify credentials in .env
```

### WebSocket Connection Failed
```bash
# Ensure backend is running with Daphne
docker-compose logs backend

# Check frontend env vars point to correct WS URL
```

### Celery Tasks Not Running
```bash
# Check Celery worker
docker-compose logs celery_worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

---

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS`
- [ ] Change `DJANGO_SECRET_KEY`
- [ ] Configure real email service
- [ ] Setup payment gateway
- [ ] Configure error tracking (Sentry)
- [ ] Enable HTTPS
- [ ] Setup database backups
- [ ] Configure monitoring/alerts
- [ ] Update admin credentials
- [ ] Test full workflow end-to-end

---

## Documentation

- **API**: `/docs/API_DOCUMENTATION.md`
- **WebSocket**: `/docs/WEBSOCKET_EVENTS.md`
- **Admin**: `/docs/ADMIN_GUIDE.md`
- **Deployment**: `/docs/DEPLOYMENT.md`
- **Env Vars**: `/docs/ENVIRONMENT_VARIABLES.md`
- **Vercel**: `/docs/VERCEL_DEPLOYMENT.md`

---

## Support

- Issues? Check logs: `docker-compose logs [service-name]`
- Need help? Read the full README.md
- Production issues? See VERCEL_DEPLOYMENT.md

---

**Ready to ship!** 🚀
