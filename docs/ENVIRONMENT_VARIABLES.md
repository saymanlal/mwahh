# Environment Variables Reference

## Backend Configuration

### Django Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | Yes | - | Secret key for Django (keep secret!) |
| `DEBUG` | No | False | Enable debug mode (never True in production) |
| `ALLOWED_HOSTS` | No | localhost,127.0.0.1 | Comma-separated allowed hosts |
| `ENVIRONMENT` | No | development | Environment name (development/staging/production) |

### Database (PostgreSQL)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_ENGINE` | No | django.db.backends.postgresql | Database engine |
| `DB_NAME` | No | matchmaking | Database name |
| `DB_USER` | No | postgres | Database user |
| `DB_PASSWORD` | No | postgres | Database password |
| `DB_HOST` | No | localhost | Database host |
| `DB_PORT` | No | 5432 | Database port |

### Redis Cache & Celery

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_HOST` | No | localhost | Redis host |
| `REDIS_PORT` | No | 6379 | Redis port |
| `REDIS_DB` | No | 0 | Redis database number |
| `REDIS_PASSWORD` | No | - | Redis password (if required) |

### Email Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_BACKEND` | No | django.core.mail.backends.smtp.EmailBackend | Email backend |
| `EMAIL_HOST` | No | smtp.gmail.com | SMTP server host |
| `EMAIL_PORT` | No | 587 | SMTP server port |
| `EMAIL_USE_TLS` | No | True | Use TLS encryption |
| `EMAIL_HOST_USER` | No | - | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | - | SMTP password/app password |
| `DEFAULT_FROM_EMAIL` | No | noreply@matchmaking.com | Default sender email |

### CORS & Security

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CORS_ORIGINS` | No | http://localhost:3000,http://127.0.0.1:3000 | Comma-separated allowed origins |
| `SECURE_SSL_REDIRECT` | No | False | Redirect HTTP to HTTPS |
| `SESSION_COOKIE_SECURE` | No | False | Only send cookies over HTTPS |
| `CSRF_COOKIE_SECURE` | No | False | CSRF cookie HTTPS only |

### Admin Authentication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ADMIN_EMAIL` | Yes | - | Admin user email |
| `ADMIN_PASSWORD_HASH` | Yes | - | Admin password hash (bcrypt) |

### Institution Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APPROVED_DOMAINS` | No | - | Comma-separated approved email domains |
| `OTP_VALID_DURATION` | No | 600 | OTP validity duration in seconds |

### Payment Gateways (Optional)

#### Razorpay

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RAZORPAY_KEY_ID` | No | - | Razorpay API Key |
| `RAZORPAY_KEY_SECRET` | No | - | Razorpay API Secret |

#### Stripe

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STRIPE_API_KEY` | No | - | Stripe API Key |
| `STRIPE_WEBHOOK_SECRET` | No | - | Stripe Webhook Secret |

### File Storage (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_S3` | No | False | Use AWS S3 for storage |
| `AWS_ACCESS_KEY_ID` | No | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS secret key |
| `AWS_STORAGE_BUCKET_NAME` | No | - | S3 bucket name |
| `AWS_S3_REGION_NAME` | No | us-east-1 | AWS region |

### Logging & Monitoring

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | INFO | Logging level |
| `SENTRY_DSN` | No | - | Sentry error tracking DSN |

---

## Frontend Configuration

### API Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | No | http://localhost:8000 | Backend API base URL |
| `NEXT_PUBLIC_WS_URL` | No | ws://localhost:8000 | WebSocket server URL |
| `NEXT_PUBLIC_APP_NAME` | No | MatchHub | Application name |

### Analytics (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_GA_ID` | No | - | Google Analytics ID |

### Third-Party Integrations

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_SENTRY_DSN` | No | - | Sentry DSN for frontend errors |

---

## Example Configuration Files

### Backend .env.example

```bash
# Django
DJANGO_SECRET_KEY=django-insecure-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME=matchmaking
DB_USER=postgres
DB_PASSWORD=your-secure-password
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
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@matchmaking.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD_HASH=$2b$12$hash...

# Approved Domains
APPROVED_DOMAINS=college.edu,university.edu

# Razorpay (if using)
RAZORPAY_KEY_ID=your-key-id
RAZORPAY_KEY_SECRET=your-key-secret
```

### Frontend .env.local.example

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=MatchHub
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

---

## Generating Admin Password Hash

```bash
# Using Python
python -c "from django.contrib.auth.hashers import make_password; print(make_password('your-admin-password'))"

# Using bcrypt directly
python -c "import bcrypt; print(bcrypt.hashpw(b'your-password', bcrypt.gensalt()).decode())"
```

---

## Security Best Practices

1. **Never commit .env files to Git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for documentation

2. **Use strong secrets**
   - `DJANGO_SECRET_KEY`: At least 50 random characters
   - Passwords: Mix of uppercase, lowercase, numbers, special chars

3. **Protect sensitive variables**
   - Store in environment variables, not in code
   - Use secrets management tools (HashiCorp Vault, AWS Secrets Manager)

4. **Rotate credentials regularly**
   - Change email passwords
   - Rotate API keys
   - Update database credentials

5. **Different configs for different environments**
   - Development: Relaxed security
   - Staging: Production-like
   - Production: Strict security

6. **Use HTTPS in production**
   - `SECURE_SSL_REDIRECT=True`
   - `SESSION_COOKIE_SECURE=True`
   - `CSRF_COOKIE_SECURE=True`

---

## Loading Variables

### Django Settings
Variables are loaded using `os.environ.get()`:
```python
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```

### Next.js
Variables prefixed with `NEXT_PUBLIC_` are available in browser:
```javascript
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

### Docker Compose
Load from .env file:
```yaml
env_file:
  - .env
```

### Python Dotenv
Load from .env automatically:
```python
from dotenv import load_dotenv
load_dotenv()
```
