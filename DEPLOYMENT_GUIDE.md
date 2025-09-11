# 🚀 Flowmaker Deployment Guide

## 📋 Prerequisites

- Docker & Docker Compose
- Domain name (for production)
- SSL certificate (or use Let's Encrypt)
- OAuth app credentials (Google, Slack)

## 🔧 Quick Start (Development)

### 1. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start Development Environment
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏭 Production Deployment

### 1. Server Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ 
- **Storage**: 20GB+ SSD
- **OS**: Ubuntu 20.04+ or similar

### 2. Environment Configuration
```bash
# Edit production environment
nano .env

# Required variables:
POSTGRES_PASSWORD=your_secure_password_here
SECRET_KEY=your-super-secret-key-change-this-in-production
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SLACK_CLIENT_ID=your_slack_client_id
SLACK_CLIENT_SECRET=your_slack_client_secret
CORS_ORIGINS=https://yourdomain.com
VITE_API_BASE_URL=https://yourdomain.com/api/v1
```

### 3. SSL Certificate Setup
```bash
# For development (self-signed)
chmod +x generate-ssl.sh
./generate-ssl.sh

# For production (Let's Encrypt)
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
```

### 4. Deploy with Docker Compose
```bash
# Deploy production stack
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Database Setup
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create admin user
docker-compose -f docker-compose.prod.yml exec backend python create_admin_user.py
```

### 6. Verify Deployment
- **Frontend**: https://yourdomain.com
- **API**: https://yourdomain.com/api/v1
- **Monitoring**: https://yourdomain.com/monitoring
- **Health Check**: https://yourdomain.com/health

## 🔌 OAuth Setup

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `https://yourdomain.com/oauth/google/callback`
6. Copy Client ID and Secret to `.env`

### Slack OAuth
1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app
3. Add OAuth scopes:
   - `chat:write`
   - `channels:read`
   - `users:read`
4. Add redirect URLs:
   - `https://yourdomain.com/oauth/slack/callback`
5. Copy Client ID and Secret to `.env`

## 📊 Monitoring

### Access Monitoring
- **Grafana**: https://yourdomain.com/monitoring
- **Prometheus**: http://yourdomain.com:9090
- **Default Grafana Login**: admin/admin

### Key Metrics to Monitor
- API response times
- Workflow execution success rate
- Database connection pool
- Redis memory usage
- Celery queue depth

## 🔒 Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up backup strategy
- [ ] Enable log monitoring
- [ ] Regular security updates

## 🚨 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check logs
docker-compose logs [service_name]

# Restart services
docker-compose restart [service_name]

# Rebuild containers
docker-compose up -d --build
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d
```

#### SSL Certificate Issues
```bash
# Check certificate
openssl x509 -in ssl/cert.pem -text -noout

# Regenerate certificates
./generate-ssl.sh
```

### Performance Optimization

#### Database
```sql
-- Add indexes for better performance
CREATE INDEX idx_workflows_owner_id ON workflows(owner_id);
CREATE INDEX idx_executions_workflow_id ON executions(workflow_id);
CREATE INDEX idx_executions_created_at ON executions(created_at);
```

#### Redis
```bash
# Monitor Redis memory
docker-compose exec redis redis-cli info memory

# Clear cache if needed
docker-compose exec redis redis-cli flushall
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# Add more Celery workers
celery_worker_2:
  extends: celery_worker
  command: celery -A app.core.celery_app worker --loglevel=info --concurrency=4

celery_worker_3:
  extends: celery_worker
  command: celery -A app.core.celery_app worker --loglevel=info --concurrency=4
```

### Load Balancing
```nginx
# Add multiple backend instances
upstream backend {
    server backend:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## 🔄 Backup & Recovery

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U worqly_user worqly > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U worqly_user worqly < backup.sql
```

### Automated Backups
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

## 📞 Support

- **Documentation**: Check README.md
- **Issues**: Create GitHub issue
- **Logs**: Check Docker logs for errors
- **Health**: Use `/health` endpoint

---

## 🎉 Success!

Your Flowmaker instance is now deployed and ready to use!

**Next Steps:**
1. Create your first workflow
2. Set up integrations
3. Monitor performance
4. Scale as needed
