# Vercel Deployment Guide

## Frontend Deployment (Next.js)

### Prerequisites
- Vercel account
- GitHub repository with your code
- Environment variables configured

### Step 1: Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Select the root directory as "/"
5. Framework: **Next.js**

### Step 2: Configure Environment Variables

In Vercel project settings > Environment Variables, add:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
NEXT_PUBLIC_WS_URL=wss://your-backend-api.com
```

### Step 3: Deploy

Click "Deploy" - Vercel automatically builds and deploys the Next.js app.

### Custom Domain

1. Go to Settings > Domains
2. Add your custom domain
3. Update DNS records as shown
4. HTTPS auto-enabled

---

## Backend Deployment (Django)

### Option A: Railway

1. Connect GitHub repo to Railway
2. Add PostgreSQL service
3. Add Redis service
4. Set environment variables:
   - `DJANGO_SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.com`
   - Database URLs auto-configured

5. Deploy button triggers build from `Dockerfile`

### Option B: Render

1. Create new Web Service
2. Connect GitHub
3. Build Command: `pip install -r requirements.txt && python manage.py migrate`
4. Start Command: `daphne -b 0.0.0.0 -p 10000 config.asgi:application`
5. Add PostgreSQL database
6. Add Redis instance
7. Set all environment variables

### Option C: AWS (ECS + RDS + ElastiCache)

```bash
# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com

docker build -t matchmaking:latest ./backend
docker tag matchmaking:latest <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/matchmaking:latest
docker push <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/matchmaking:latest
```

Then deploy to ECS with CloudFormation or Terraform.

---

## Database Backups

### PostgreSQL Backup

```bash
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup.sql
```

### Restore

```bash
psql -h $DB_HOST -U $DB_USER $DB_NAME < backup.sql
```

---

## Monitoring

### Vercel
- Dashboard shows deployments, errors, analytics
- Real-time logs in Deployments tab

### Railway/Render
- Built-in logs
- Metrics dashboard
- Email alerts for errors

### Application Level
- Use Sentry for error tracking
- Use Datadog/New Relic for APM

```bash
# Set SENTRY_DSN in environment variables
```

---

## Scaling

### Frontend (Vercel)
- Automatic scaling with serverless functions
- Global CDN for static assets
- Incremental Static Regeneration (ISR)

### Backend
- Horizontal scaling: Multiple Daphne instances behind load balancer
- Celery worker scaling: More workers for heavy tasks
- Database: Enable read replicas
- Redis: Use managed Redis cluster

---

## CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r backend/requirements.txt
          python backend/manage.py test

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: vercel/action@master
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up
```

---

## Production Checklist

- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured
- [ ] `SECRET_KEY` strong and unique
- [ ] HTTPS everywhere
- [ ] CORS properly configured
- [ ] Database backups automated
- [ ] Error tracking enabled
- [ ] Rate limiting configured
- [ ] Admin credentials secure
- [ ] Email verified for all users
- [ ] Payment gateway live credentials
- [ ] Monitoring and alerting setup

---

## Rollback

If deployment fails:

```bash
# Vercel
vercel rollback

# Railway
# Use dashboard to redeploy previous commit

# AWS
aws ecs update-service --cluster prod --service matchmaking --force-new-deployment
```

---

## Support

- Vercel: [vercel.com/support](https://vercel.com/support)
- Railway: [railway.app/docs](https://railway.app/docs)
- Render: [render.com/docs](https://render.com/docs)
