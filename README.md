# Worqly - No-Code Workflow Automation Platform

Worqly is a powerful, no-code workflow automation platform that enables users to create complex multi-step integrations between services like Gmail, Slack, and Google Sheets without writing any code. Built with modern technologies and designed for scalability, Worqly provides a visual drag-and-drop interface for building, testing, and executing workflows.

## 🚀 Features

### Core Functionality
- **Visual Workflow Builder**: Drag-and-drop interface using Joint.js for intuitive workflow creation
- **Multi-Service Integrations**: Connect Gmail, Slack, Google Sheets, and custom webhooks
- **Real-time Execution**: Live monitoring of workflow execution with detailed logs
- **OAuth Authentication**: Secure token management for third-party services
- **Workflow Templates**: Pre-built templates for common automation scenarios
- **Version Control**: Track workflow changes and rollback capabilities

### Advanced Features
- **Conditional Logic**: Advanced branching and decision-making in workflows
- **Data Transformation**: Built-in tools for data manipulation and formatting
- **Error Handling**: Comprehensive error handling with retry mechanisms
- **Scheduling**: Time-based workflow triggers and execution
- **Collaboration**: Team-based workflow sharing and editing
- **API Access**: RESTful API for programmatic workflow management

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
backend/
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic validation schemas
│   ├── routers/         # FastAPI route handlers
│   ├── services/        # Business logic services
│   │   └── integrations/ # Third-party service integrations
│   ├── auth/           # Authentication and security
│   ├── core/           # Core application modules
│   └── config.py       # Configuration management
├── requirements.txt    # Python dependencies
└── Dockerfile         # Container configuration
```

### Frontend (Vue.js 3 + TypeScript)
```
frontend/
├── src/
│   ├── components/     # Reusable Vue components
│   ├── views/          # Page components
│   ├── stores/         # Pinia state management
│   ├── services/       # API and external services
│   ├── router/         # Vue Router configuration
│   └── assets/         # Static assets
├── package.json        # Node.js dependencies
└── vite.config.mjs     # Build configuration
```

### Infrastructure
```
infrastructure/
├── docker-compose.yml  # Development environment
├── kubernetes/         # Production deployment
└── terraform/          # Infrastructure as Code
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **PostgreSQL**: Primary database for data persistence
- **Redis**: Caching and message broker for Celery
- **Celery**: Distributed task queue for async workflow execution
- **Pydantic**: Data validation and settings management
- **JWT**: JSON Web Tokens for authentication

### Frontend
- **Vue.js 3**: Progressive JavaScript framework with Composition API
- **Joint.js**: JavaScript diagramming library for workflow canvas
- **Pinia**: State management for Vue applications
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and development server
- **Socket.io**: Real-time communication for live updates

### DevOps & Infrastructure
- **Docker**: Containerization for consistent deployments
- **Kubernetes**: Container orchestration for production
- **Terraform**: Infrastructure as Code for cloud resources
- **GitHub Actions**: CI/CD pipeline automation

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Quick Start (Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/worqly.git
   cd worqly
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

5. **Start the development servers**
   ```bash
   # Backend (from project root)
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Frontend (in another terminal)
   cd frontend
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Production Deployment

1. **Build the production images**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Deploy with Kubernetes**
   ```bash
   kubectl apply -f infrastructure/kubernetes/
   ```

3. **Set up monitoring and logging**
   ```bash
   kubectl apply -f infrastructure/monitoring/
   ```

## 🔧 Configuration

### Environment Variables


### Fixing .env Encoding Issues (Windows)

If the backend fails to start with a UnicodeDecodeError related to `.env`, it likely has a BOM or is not UTF-8 encoded.

Recommended options:

- VS Code / Cursor:
  1. Open `backend/.env`.
  2. Click the encoding label in the status bar (bottom-right).
  3. Click "Save with Encoding...".
  4. Choose "UTF-8" (not "UTF-8 with BOM").
  5. Save.

- PowerShell (may fail if the file is locked):
  ```powershell
  Get-Content .env -Raw | Set-Content -Encoding UTF8 .env
  ```
  If you see "The process cannot access the file because it is being used by another process.", close apps that might be holding the file, or use the automated fixer below.

- Automated fixer (preferred):
  ```bash
  cd backend
  python -c "from app.utils.fix_env_encoding import fix_env_file_encoding; fix_env_file_encoding()"
  ```
  You should see: "✅ .env file encoding fixed and saved as UTF-8 without BOM."

## 📚 Usage Guide

### Creating Your First Workflow

1. **Sign up and log in** to the Worqly platform
2. **Create an integration** for the services you want to connect (Gmail, Slack, etc.)
3. **Navigate to Workflows** and click "Create New Workflow"
4. **Add nodes** by dragging them from the palette to the canvas:
   - **Trigger nodes**: Start your workflow (webhook, schedule, email, etc.)
   - **Action nodes**: Perform actions (send email, post message, update sheet, etc.)
   - **Condition nodes**: Add logic and branching
   - **Transformer nodes**: Manipulate data between steps
5. **Connect nodes** by drawing connections between them
6. **Configure each node** using the properties panel
7. **Test your workflow** using the test button
8. **Save and activate** your workflow

### Workflow Examples

#### Email to Slack Notification
```
Gmail Trigger (New Email) → Condition (Check Subject) → Slack Action (Send Message)
```

#### Data Collection Pipeline
```
Webhook Trigger → Transformer (Format Data) → Google Sheets Action (Append Row)
```

#### Approval Workflow
```
Form Submission → Email Action (Send Approval Request) → Wait → Condition (Approved?) → Email Action (Send Confirmation)
```

## 🔌 API Reference

### Authentication
All API endpoints require authentication using JWT tokens.

```bash
# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Use token in headers
Authorization: Bearer <your-jwt-token>
```

### Core Endpoints

#### Workflows
```bash
GET    /api/v1/workflows          # List workflows
POST   /api/v1/workflows          # Create workflow
GET    /api/v1/workflows/{id}     # Get workflow
PUT    /api/v1/workflows/{id}     # Update workflow
DELETE /api/v1/workflows/{id}     # Delete workflow
POST   /api/v1/workflows/{id}/execute  # Execute workflow
```

#### Integrations
```bash
GET    /api/v1/integrations       # List integrations
POST   /api/v1/integrations       # Create integration
GET    /api/v1/integrations/{id}  # Get integration
PUT    /api/v1/integrations/{id}  # Update integration
DELETE /api/v1/integrations/{id}  # Delete integration
POST   /api/v1/integrations/{id}/test  # Test integration
```

#### Executions
```bash
GET    /api/v1/executions         # List executions
GET    /api/v1/executions/{id}    # Get execution details
GET    /api/v1/executions/{id}/logs  # Get execution logs
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### E2E Tests
```bash
npm run test:e2e
```

## 📊 Monitoring & Observability

### Metrics
- Workflow execution success/failure rates
- API response times and throughput
- Database query performance
- Celery task queue metrics

### Logging
- Structured logging with correlation IDs
- Error tracking and alerting
- Audit trails for workflow changes

### Health Checks
- Database connectivity
- Redis availability
- External service status
- Celery worker health

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- OAuth 2.0 for third-party integrations
- Secure token storage and refresh

### Data Protection
- Encryption at rest and in transit
- Secure OAuth token handling
- Input validation and sanitization
- SQL injection prevention

### API Security
- Rate limiting and throttling
- CORS configuration
- Request validation
- Audit logging

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow the existing code style and conventions
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.worqly.com](https://docs.worqly.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/worqly/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/worqly/discussions)
- **Email**: support@worqly.com

## 🗺️ Roadmap

### Upcoming Features
- [ ] Advanced workflow templates marketplace
- [ ] Real-time collaboration on workflows
- [ ] Advanced analytics and insights
- [ ] Mobile application
- [ ] Enterprise SSO integration
- [ ] Custom node development SDK
- [ ] Workflow versioning and branching
- [ ] Advanced scheduling and triggers

### Performance Improvements
- [ ] GraphQL API for efficient data fetching
- [ ] WebSocket-based real-time updates
- [ ] Caching layer for frequently accessed data
- [ ] Database query optimization
- [ ] CDN integration for static assets

---

**Built with ❤️ by the Worqly Team**
