# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+
- Python 3.10+
- Node.js 18+

---

## Environment Configuration

### Backend (.env)

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=matchmaking
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
DEFAULT_FROM_EMAIL=noreply@matchmaking.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Admin
ADMIN_EMAIL=admin@matchmaking.com
ADMIN_PASSWORD_HASH=hashed-password

# Approved Domains
APPROVED_DOMAINS=college.edu,university.edu

# Payment (if using Razorpay)
RAZORPAY_KEY_ID=your-key-id
RAZORPAY_KEY_SECRET=your-key-secret

# Payment (if using Stripe)
STRIPE_API_KEY=your-stripe-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

---

## Docker Deployment

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    command: >
      sh -c "
        python manage.py migrate &&
        daphne -b 0.0.0.0 -p 8000 config.asgi:application
      "
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app

  celery:
    build: ./backend
    command: celery -A config worker -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

  celery-beat:
    build: ./backend
    command: celery -A config beat -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      args:
        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    ports:
      - "3000:3000"
    depends_on:
      - backend
    env_file:
      - .env.local

volumes:
  postgres_data:
  redis_data:
```

### Build & Run

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser (for Django admin)
docker-compose exec backend python manage.py createsuperuser

# View logs
docker-compose logs -f backend
```

---

## Production Deployment (Heroku/Railway/Render)

### Backend Deployment

1. **Create Procfile:**
```
release: python manage.py migrate
web: daphne -b 0.0.0.0 -p $PORT config.asgi:application
worker: celery -A config worker -l info
beat: celery -A config beat -l info
```

2. **Create runtime.txt:**
```
python-3.10.12
```

3. **Deploy:**
```bash
git push heroku main
```

### Frontend Deployment (Vercel)

```bash
# Link project
vercel link

# Deploy
vercel deploy --prod
```

Or use GitHub integration for automatic deployments.

---

## Database Migrations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate api 0001
```

---

## Static Files & Media

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Serve via CDN
- Upload `staticfiles/` to AWS S3 or similar
- Update `STATIC_URL` and `STATIC_ROOT` in settings
- Install `django-storages` for S3 integration

---

## Celery Setup

### Start Celery Worker
```bash
celery -A config worker -l info
```

### Start Celery Beat (Scheduler)
```bash
celery -A config beat -l info
```

### Monitor Celery Tasks
```bash
celery -A config events
```

---

## SSL/TLS Certificate

### Let's Encrypt with Certbot
```bash
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
```

---

## Monitoring & Logging

### Application Logging
Configure in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/matchmaking/app.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Database Backups
```bash
# Backup
pg_dump -U postgres matchmaking > backup.sql

# Restore
psql -U postgres matchmaking < backup.sql
```

### Redis Monitoring
```bash
redis-cli monitor
redis-cli info stats
```

---

## Health Checks

### Backend Health
```bash
curl https://api.yourdomain.com/health/
```

### Database Connection
```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
```

---

## Scaling

### Horizontal Scaling (Multiple Backend Instances)
1. Use load balancer (Nginx, HAProxy)
2. Deploy multiple backend instances
3. Share Redis and PostgreSQL

### Vertical Scaling
- Increase server RAM/CPU
- Optimize database queries
- Enable caching strategies

---

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `DJANGO_SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Set secure CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable database backups
- [ ] Setup monitoring and alerts
- [ ] Rate limiting enabled
- [ ] SQL injection protection (ORM usage)
- [ ] XSS protection enabled
- [ ] CSRF protection enabled
- [ ] Regular security updates

---

## Troubleshooting

### WebSocket Connection Issues
- Check firewall rules
- Verify reverse proxy WebSocket support
- Check CORS headers

### Database Connection Errors
- Verify PostgreSQL is running
- Check DB credentials
- Verify network connectivity

### Celery Task Delays
- Check Redis connection
- Monitor Celery worker logs
- Check task queue length

### High Memory Usage
- Review running processes
- Check for memory leaks
- Optimize database queries
- Enable connection pooling
