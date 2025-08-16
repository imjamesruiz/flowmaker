# Worqly Workflow Connections & Execution Setup

This document provides setup instructions for the fixed Worqly workflow system with reliable connections, persistence, and execution.

## 🎯 What's Fixed

### Frontend Issues Resolved
- ✅ **Connection Persistence**: Edges now properly save to backend and survive refresh
- ✅ **Connection Validation**: Proper validation with user-friendly error messages
- ✅ **Handle Management**: Larger, more visible handles with proper positioning
- ✅ **State Management**: Zustand store with proper autosave (800ms debounce)
- ✅ **Error Handling**: Toast notifications for user feedback
- ✅ **TypeScript Support**: Full type safety with proper interfaces

### Backend Issues Resolved
- ✅ **API Consistency**: Unified frontend/backend data format
- ✅ **Workflow Execution**: Topological sorting with proper node execution
- ✅ **Validation**: Graph validation (cycles, orphaned nodes, valid types)
- ✅ **Persistence**: Transactional saves with proper error handling
- ✅ **Testing**: Synchronous test execution with detailed logs

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd flowmaker/backend

# Option 1: Use the setup script (recommended)
python setup.py

# Option 2: Manual installation
pip install -r requirements.txt

# If you get pydantic-settings errors, run:
python install_deps.py

# Start the backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd flowmaker/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 3. Create Test User

```bash
cd flowmaker/backend
python create_test_user.py
```

### 4. Test the System

```bash
# Run the comprehensive test
python test_workflow_connections.py
```

## 🔧 Troubleshooting

### Common Backend Issues

**ModuleNotFoundError: No module named 'pydantic_settings'**
```bash
# Solution 1: Install missing dependencies
cd flowmaker/backend
python install_deps.py

# Solution 2: Manual installation
pip install pydantic-settings fastapi uvicorn[standard] sqlalchemy

# Solution 3: Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Database connection errors**
```bash
# The system uses SQLite by default, which should work out of the box
# If you see database errors, check that the worqly.db file exists
ls -la worqly.db
```

**Port already in use**
```bash
# Change the port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Common Frontend Issues

**API connection errors**
- Check that the backend is running on port 8000
- Verify the API base URL in `src/services/api.ts`
- Check CORS settings in the backend

**Authentication errors**
- Ensure the test user was created: `python create_test_user.py`
- Check that the backend is running and accessible

## 📁 Key Files

### Frontend
- `src/stores/useWorkflowStore.ts` - Zustand store with autosave
- `src/components/WorkflowCanvas.tsx` - Main canvas with connection handling
- `src/components/NodeCard.tsx` - Node component with proper handles
- `src/services/api.ts` - TypeScript API client
- `src/hooks/useToast.ts` - Toast notifications
- `src/types/workflow.ts` - TypeScript interfaces

### Backend
- `app/services/workflow_executor.py` - Workflow execution engine
- `app/routers/workflows.py` - API endpoints
- `app/schemas/workflow.py` - Pydantic schemas
- `app/models/workflow.py` - Database models
- `setup.py` - Backend setup script
- `install_deps.py` - Dependency installer

## 🔧 Configuration

### Frontend Configuration

The frontend is configured to connect to `http://localhost:8000/api/v1`. Update the base URL in:
- `src/services/api.ts`
- `src/services/api.js`

### Backend Configuration

Database and other settings are in:
- `app/config.py`

## 🧪 Testing

### Manual Testing

1. **Create a Workflow**:
   - Navigate to the workflow editor
   - Drag nodes from the palette
   - Connect nodes by dragging from output to input handles

2. **Test Connections**:
   - Try connecting to an already connected input (should show error)
   - Try connecting a node to itself (should show error)
   - Try creating duplicate connections (should show error)

3. **Test Persistence**:
   - Create connections
   - Refresh the page
   - Verify connections are still there

4. **Test Execution**:
   - Click the "Test" button
   - Check the console for execution logs
   - Verify the workflow executes in topological order

### Automated Testing

Run the comprehensive test script:

```bash
python test_workflow_connections.py
```

This test:
- Creates a test workflow with 5 nodes
- Tests all connection types
- Validates the workflow structure
- Executes the workflow
- Verifies execution logs

## 🔍 API Endpoints

### Workflow Management
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/workflows` - Create workflow
- `GET /api/v1/workflows/{id}` - Get workflow
- `PUT /api/v1/workflows/{id}/bulk` - Save workflow (nodes + edges)
- `DELETE /api/v1/workflows/{id}` - Delete workflow

### Execution
- `POST /api/v1/workflows/{id}/test` - Test execute workflow
- `POST /api/v1/workflows/{id}/execute` - Execute workflow (async)
- `POST /api/v1/workflows/{id}/validate` - Validate workflow

## 📊 Data Flow

### Frontend → Backend
1. User creates/edits workflow in React Flow
2. Zustand store tracks changes and marks as dirty
3. Autosave triggers after 800ms of inactivity
4. API call to `PUT /workflows/{id}/bulk` with complete workflow data
5. Backend validates and saves in transaction

### Backend → Frontend
1. Frontend loads workflow on mount
2. API call to `GET /workflows/{id}`
3. Backend returns workflow with nodes and connections
4. Frontend converts to React Flow format
5. Canvas displays with proper connections

### Execution Flow
1. User clicks "Test" button
2. Frontend sends current workflow state to `POST /workflows/{id}/test`
3. Backend builds graph and performs topological sort
4. Each node executes in order with proper input/output
5. Results returned with detailed logs

## 🐛 Troubleshooting

### Common Issues

**Connections not saving**:
- Check browser console for API errors
- Verify backend is running on port 8000
- Check authentication token is valid

**Execution failing**:
- Check workflow validation passes
- Verify no cycles in the graph
- Check node types are valid

**Frontend not loading**:
- Check CORS settings in backend
- Verify API base URL is correct
- Check authentication is working

### Debug Mode

Enable debug logging in the backend:

```python
# In app/config.py
DEBUG = True
```

Check the browser console for frontend logs and the backend terminal for API logs.

## 🎨 Customization

### Adding New Node Types

1. **Frontend**:
   - Add to `NodeKind` type in `src/types/workflow.ts`
   - Add icon and color in `src/components/NodeCard.tsx`
   - Add to `nodeTypes` in `src/components/WorkflowCanvas.tsx`

2. **Backend**:
   - Add runner function in `app/services/workflow_executor.py`
   - Add to `RUNNERS` dictionary
   - Update validation logic

### Custom Edge Styles

Modify the edge styling in:
- `src/stores/useWorkflowStore.ts` - Default edge options
- `src/components/WorkflowCanvas.tsx` - Edge styling

### Custom Validation

Add custom validation rules in:
- `src/components/WorkflowCanvas.tsx` - `isValidConnection` function
- `app/services/workflow_executor.py` - `validate_workflow` method

## 📈 Performance

### Optimizations Implemented
- Debounced autosave (800ms)
- Efficient state updates with Zustand
- Proper React Flow optimization
- Backend transaction handling

### Monitoring
- Check browser performance tab for frontend metrics
- Monitor backend logs for API response times
- Use the test script to benchmark execution

## 🔒 Security

### Authentication
- JWT-based authentication
- Token refresh handling
- Protected API endpoints

### Validation
- Input validation on all endpoints
- Graph structure validation
- Node type validation

## 📝 Development Notes

### Key Design Decisions
1. **Unified Data Format**: Frontend and backend use the same node/edge structure
2. **Deterministic IDs**: Edge IDs generated from source/target for consistency
3. **Topological Execution**: Ensures proper execution order
4. **Transaction Safety**: All saves are atomic

### Future Enhancements
- Real-time collaboration
- Version control for workflows
- Advanced node types (HTTP, database, etc.)
- Workflow templates
- Execution history and rollback

## 🤝 Contributing

When contributing to the workflow system:

1. Follow the existing code patterns
2. Add proper TypeScript types
3. Include error handling
4. Add tests for new features
5. Update this documentation

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the test script for examples
3. Check the API documentation at `/docs` when backend is running
4. Review the browser console and backend logs
