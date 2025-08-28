# 🚀 Worqly - Workflow Automation Platform

A powerful, open-source workflow automation platform built with Vue.js, FastAPI, and Celery. Create, manage, and execute complex workflows with drag-and-drop ease.

![Worqly Workflow Editor](https://img.shields.io/badge/Status-Production%20Ready-green)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-green)

## ✨ Features

- **🎨 Drag-and-Drop Workflow Editor** - Intuitive visual workflow builder
- **🔌 Plugin-Based Integrations** - Easy to add new services (Gmail, Slack, etc.)
- **⚡ Real-time Execution** - Monitor workflow runs in real-time
- **🔒 Secure OAuth** - Enterprise-grade authentication
- **📊 Monitoring & Analytics** - Built-in Prometheus & Grafana
- **🐳 Docker Ready** - Production-ready containerization
- **🔄 Scalable Architecture** - Celery workers for high throughput

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js        │    │   FastAPI       │    │   Celery        │
│   Frontend      │◄──►│   Backend       │◄──►│   Workers       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   PostgreSQL    │    │   Redis         │
│   Reverse Proxy │    │   Database      │    │   Message Queue │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.10+ (for development)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/worqly.git
cd worqly
```

### 2. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```env
# Database
POSTGRES_PASSWORD=your_secure_password

# Security
SECRET_KEY=your-super-secret-key

# OAuth (for integrations)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SLACK_CLIENT_ID=your_slack_client_id
SLACK_CLIENT_SECRET=your_slack_client_secret
```

### 3. Production Deployment

```bash
# Make deployment script executable (Linux/Mac)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 4. Development Setup

```bash
# Start development environment
docker-compose up -d

# Install frontend dependencies
cd frontend
npm install

# Start frontend development server
npm run dev

# Install backend dependencies
cd ../backend
pip install -r requirements.txt

# Start backend development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Usage Guide

### Creating Your First Workflow

1. **Access the Editor**
   - Navigate to `http://localhost:3000`
   - Sign up or log in
   - Click "Create New Workflow"

2. **Add Trigger Node**
   - Drag a "Trigger" node from the palette
   - Configure it (e.g., Gmail new email trigger)
   - Connect your Gmail account via OAuth

3. **Add Action Node**
   - Drag an "Action" node
   - Choose an action (e.g., send Slack message)
   - Configure the action parameters

4. **Connect Nodes**
   - Click and drag from trigger output to action input
   - The connection represents data flow

5. **Test & Deploy**
   - Click "Test Workflow" to validate
   - Click "Deploy" to activate

### Example Workflow: Email to Slack Alert

```
Gmail Trigger → Filter Condition → Slack Action
     │              │                    │
  New Email    Subject contains    Send Alert
     │           "urgent"              │
     └─────────────┴────────────────────┘
```

## 🔌 Integrations

### Available Integrations

| Service | Triggers | Actions | Status |
|---------|----------|---------|--------|
| Gmail | ✅ New Email | ✅ Send Email | Production |
| Slack | ✅ New Message | ✅ Send Message | Production |
| Google Sheets | 🔄 Coming Soon | 🔄 Coming Soon | Development |
| HTTP Webhooks | ✅ Incoming | ✅ Outgoing | Production |

### Adding New Integrations

1. **Create Integration Class**
```python
# backend/app/services/integrations/my_service.py
from app.services.integrations.base_integration import BaseIntegration

class MyService(BaseIntegration):
    def get_provider_name(self) -> str:
        return "my_service"
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "my_action",
                "name": "My Action",
                "description": "Description of my action",
                "schema": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "title": "Parameter 1"}
                    }
                }
            }
        ]
    
    def execute_action(self, action_type: str, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation here
        pass
```

2. **Register Integration**
```python
# backend/app/services/integrations/__init__.py
from .my_service import MyService
from .base_integration import integration_registry

integration_registry.register(MyService)
```

## 🏭 Production Deployment

### Cloud Platforms

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker build -t worqly .
docker tag worqly:latest your-account.dkr.ecr.us-east-1.amazonaws.com/worqly:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/worqly:latest

# Deploy to ECS
aws ecs update-service --cluster worqly-cluster --service worqly-service --force-new-deployment
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_PASSWORD` | Database password | ✅ | - |
| `SECRET_KEY` | JWT secret key | ✅ | - |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | ❌ | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | ❌ | - |
| `SLACK_CLIENT_ID` | Slack OAuth client ID | ❌ | - |
| `SLACK_CLIENT_SECRET` | Slack OAuth client secret | ❌ | - |
| `ENVIRONMENT` | Environment name | ❌ | `development` |
| `CORS_ORIGINS` | Allowed CORS origins | ❌ | `http://localhost:3000` |

### Scaling

#### Horizontal Scaling
```yaml
# docker-compose.prod.yml
services:
  celery_worker:
    deploy:
      replicas: 3  # Scale to 3 workers
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

#### Database Scaling
```yaml
# Use managed PostgreSQL service
DATABASE_URL=postgresql://user:pass@managed-db.amazonaws.com:5432/worqly
```

#### Redis Scaling
```yaml
# Use managed Redis service
REDIS_URL=redis://managed-redis.amazonaws.com:6379
```

## 🔧 Development

### Project Structure
```
worqly/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routers/        # API routes
│   │   ├── services/       # Business logic
│   │   └── core/           # Core configuration
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── services/       # API services
│   │   └── stores/         # State management
│   ├── package.json        # Node dependencies
│   └── Dockerfile         # Frontend container
├── docker-compose.yml      # Development setup
├── docker-compose.prod.yml # Production setup
└── deploy.sh              # Deployment script
```

### API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

### Code Quality

```bash
# Backend linting
cd backend
black .
flake8 .
mypy .

# Frontend linting
cd frontend
npm run lint
npm run format
```

## 📊 Monitoring

### Built-in Monitoring

- **Prometheus**: Metrics collection at `http://localhost:9090`
- **Grafana**: Dashboards at `http://localhost:3001`
- **Health Checks**: `/health` endpoint

### Key Metrics

- Workflow execution time
- Node success/failure rates
- API response times
- Queue depths
- Database performance

### Alerts

Configure alerts in Grafana for:
- High error rates
- Slow response times
- Queue backlogs
- Database connection issues

## 🔒 Security

### Authentication
- JWT-based authentication
- Refresh token rotation
- OAuth 2.0 for integrations

### Data Protection
- All sensitive data encrypted at rest
- HTTPS enforced in production
- Rate limiting on API endpoints
- Input validation and sanitization

### OAuth Security
- Secure token storage
- Automatic token refresh
- Scope validation
- Token revocation support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation
- Follow conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.worqly.com](https://docs.worqly.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/worqly/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/worqly/discussions)
- **Email**: support@worqly.com

## 🙏 Acknowledgments

- [React Flow](https://reactflow.dev/) for the workflow editor
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Vue.js](https://vuejs.org/) for the frontend framework
- [Celery](https://docs.celeryproject.org/) for task queue management

---

**Made with ❤️ by the Worqly Team**
