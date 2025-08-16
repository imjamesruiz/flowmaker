# Worqly Workflow Editor

A powerful workflow editor with drag-and-drop connections, real-time execution, and persistent storage.

## Features

- **Visual Workflow Editor**: Drag-and-drop interface for creating workflows
- **Real-time Connections**: Connect nodes with validation and visual feedback
- **Autosave**: Automatic saving with debouncing (800ms)
- **Workflow Execution**: Test workflows with topological sorting
- **Multiple Node Types**: Trigger, Action, Condition, Transformer, Webhook
- **Persistent Storage**: Save and load workflows from database
- **Modern UI**: Built with Tailwind CSS and shadcn/ui

## Tech Stack

### Backend
- **FastAPI** (Python) - High-performance web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database
- **Celery** - Background task processing
- **JWT** - Authentication

### Frontend
- **Vue.js 3** (Current) - Progressive JavaScript framework
- **React + TypeScript** (Alternative) - Modern React with TypeScript
- **React Flow** - Flow chart library
- **Zustand** - State management
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - UI component library

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis (for Celery)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flowmaker
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis settings
   ```

4. **Initialize database**
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

5. **Create test user**
   ```bash
   python create_user_direct.py
   ```

6. **Start the backend**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/logout` - User logout

### Workflows
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/workflows` - Create workflow
- `GET /api/v1/workflows/{id}` - Get workflow
- `PUT /api/v1/workflows/{id}/bulk` - Update workflow (bulk)
- `DELETE /api/v1/workflows/{id}` - Delete workflow
- `POST /api/v1/workflows/{id}/test` - Test workflow execution

### Nodes & Connections
- `GET /api/v1/workflows/{id}/nodes` - List nodes
- `POST /api/v1/workflows/{id}/nodes` - Create node
- `PUT /api/v1/workflows/{id}/nodes/{node_id}` - Update node
- `DELETE /api/v1/workflows/{id}/nodes/{node_id}` - Delete node

## Database Schema

### Workflows
```sql
CREATE TABLE workflows (
  id          SERIAL PRIMARY KEY,
  name        VARCHAR(255) NOT NULL,
  description TEXT,
  owner_id    INTEGER REFERENCES users(id),
  is_active   BOOLEAN DEFAULT true,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);
```

### Workflow Nodes
```sql
CREATE TABLE workflow_nodes (
  id          SERIAL PRIMARY KEY,
  workflow_id INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
  node_id     VARCHAR(255) NOT NULL,
  node_type   VARCHAR(50) NOT NULL,
  name        VARCHAR(255) NOT NULL,
  position_x  FLOAT NOT NULL,
  position_y  FLOAT NOT NULL,
  config      JSONB DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT now()
);
```

### Workflow Connections
```sql
CREATE TABLE workflow_connections (
  id              SERIAL PRIMARY KEY,
  workflow_id     INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
  connection_id   VARCHAR(255) NOT NULL,
  source_node_id  VARCHAR(255) NOT NULL,
  target_node_id  VARCHAR(255) NOT NULL,
  source_port     VARCHAR(50),
  target_port     VARCHAR(50),
  condition       JSONB,
  created_at      TIMESTAMPTZ DEFAULT now()
);
```

## Workflow Execution

The workflow executor uses topological sorting to determine execution order:

1. **Build Graph**: Create adjacency list from nodes and connections
2. **Find Start Nodes**: Nodes with no incoming connections
3. **Topological Sort**: Kahn's algorithm to determine execution order
4. **Execute Nodes**: Run each node in order, passing context between nodes
5. **Handle Conditions**: Route to true/false paths based on condition results

### Node Types

- **Trigger**: Start workflow execution
- **Action**: Perform operations (email, API calls, etc.)
- **Condition**: Make decisions (if/else logic)
- **Transformer**: Transform data between nodes
- **Webhook**: External triggers and callbacks

## Development

### Adding New Node Types

1. **Backend**: Add runner in `WorkflowExecutor`
2. **Frontend**: Add node type to `NodeKind` type
3. **UI**: Add node to palette and styling

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

- **Backend**: Black, isort, flake8
- **Frontend**: ESLint, Prettier

## Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production

1. Set `DEBUG=False` in environment
2. Configure production database
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

## Troubleshooting

### Common Issues

1. **Connection errors**: Check database and Redis connections
2. **Authentication issues**: Verify JWT secret and token expiration
3. **CORS errors**: Configure CORS settings in backend
4. **Node not found**: Check node type registration

### Logs

- Backend logs: `backend/logs/`
- Frontend logs: Browser console
- Celery logs: `celery.log`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`
