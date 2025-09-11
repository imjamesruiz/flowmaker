# Workflow Automation Platform - Integration Tests

This directory contains comprehensive integration tests for the workflow automation platform, covering the complete end-to-end workflow execution flow.

## Test Structure

### Test Files

- `test_workflows.py` - Main integration test suite
- `conftest.py` - Shared pytest fixtures and configuration
- `README.md` - This documentation

### Test Categories

The tests are organized into the following categories:

#### 1. User Authentication (`TestUserAuthentication`)
- User registration via `/auth/register`
- User login via `/auth/login` with JWT token generation
- Protected endpoint access with valid/invalid tokens
- Authentication flow validation

#### 2. Workflow Management (`TestWorkflowManagement`)
- Workflow creation via `/workflows` endpoint
- Workflow retrieval and listing
- Workflow bulk updates with nodes and edges
- Database persistence validation

#### 3. Workflow Execution (`TestWorkflowExecution`) - **Integration Tests**
- End-to-end workflow execution with Celery tasks
- Synchronous test execution
- Error handling with invalid configurations
- Execution status monitoring

#### 4. Error Handling (`TestErrorHandling`)
- Non-existent workflow access
- Unauthorized workflow access
- Invalid execution requests

#### 5. Database Integration (`TestDatabaseIntegration`)
- Data persistence validation
- Execution logging verification
- Database transaction handling

## Test Fixtures

### Database Fixtures
- `test_engine` - SQLite test database engine
- `test_db_session` - Fresh database session with rollback
- `db_session` - Database session for direct DB access

### Redis Fixtures
- `test_redis` - Redis client with separate test namespace
- `test_celery_app` - Celery app configured for eager execution

### HTTP Client Fixtures
- `client` - HTTPX test client with database override
- `authenticated_user` - Pre-authenticated user with JWT token
- `created_workflow` - Pre-created test workflow

### Data Fixtures
- `test_user_data` - Test user registration data
- `test_workflow_data` - Test workflow creation data

## Running Tests

### Prerequisites

1. **Redis Server**: Ensure Redis is running on `localhost:6379`
2. **Dependencies**: Install test dependencies:
   ```bash
   pip install pytest pytest-asyncio pytest-cov httpx
   ```

### Test Execution

#### Run All Tests
```bash
# From backend directory
python -m pytest tests/ -v

# Or use the test runner
python run_tests.py
```

#### Run Specific Test Categories
```bash
# Unit tests only (fast)
python run_tests.py --unit

# Integration tests only (slower)
python run_tests.py --integration

# Quick tests (exclude slow/integration)
python run_tests.py --quick
```

#### Run with Coverage
```bash
python run_tests.py --coverage
```

#### Run Specific Test Classes
```bash
# Test only authentication
python -m pytest tests/test_workflows.py::TestUserAuthentication -v

# Test only workflow execution
python -m pytest tests/test_workflows.py::TestWorkflowExecution -v
```

#### Run Specific Test Methods
```bash
# Test specific functionality
python -m pytest tests/test_workflows.py::TestUserAuthentication::test_user_registration -v
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- Test discovery patterns
- Markers for test categorization
- Warning filters
- Output formatting

### Environment Variables
Tests automatically configure:
- `DATABASE_URL` - SQLite test database
- `REDIS_URL` - Redis test database (DB 1)
- `USE_SUPABASE_AUTH=false` - Use local JWT auth
- `SECRET_KEY` - Test secret key

### Test Database
- Uses SQLite in-memory database for fast execution
- Automatic table creation/cleanup per test
- Transaction rollback for isolation

### Test Redis
- Uses Redis DB 1 (separate from production)
- Automatic cleanup between tests
- Eager Celery task execution

## Test Markers

Tests are marked for selective execution:

- `@pytest.mark.integration` - Integration tests (slower, require full stack)
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.unit` - Unit tests (fast)

## Test Data

### User Data
- Unique email addresses using UUID
- Valid password format (8+ chars, letters + numbers)
- Auto-verified users for testing

### Workflow Data
- Simple trigger-action workflows
- Valid node configurations
- Proper edge connections
- Canvas data structure

## Error Scenarios

Tests cover various error conditions:

1. **Authentication Errors**
   - Invalid credentials
   - Missing tokens
   - Expired tokens

2. **Workflow Errors**
   - Non-existent workflows
   - Invalid configurations
   - Unauthorized access

3. **Execution Errors**
   - Invalid node configurations
   - Missing dependencies
   - Timeout scenarios

## Performance Considerations

### Test Speed
- Unit tests: ~1-2 seconds
- Integration tests: ~5-10 seconds
- Full suite: ~30-60 seconds

### Resource Usage
- SQLite in-memory database
- Redis test namespace
- Eager Celery execution (no worker processes)

## Debugging Tests

### Verbose Output
```bash
python -m pytest tests/ -v -s
```

### Debug Specific Test
```bash
python -m pytest tests/test_workflows.py::TestUserAuthentication::test_user_registration -v -s --pdb
```

### Check Test Coverage
```bash
python run_tests.py --coverage
```

## Continuous Integration

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    cd backend
    python run_tests.py --coverage
    
- name: Run Integration Tests
  run: |
    cd backend
    python run_tests.py --integration
```

### Docker Testing
```bash
# Start Redis
docker run -d -p 6379:6379 redis:alpine

# Run tests
cd backend
python run_tests.py
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running on localhost:6379
   - Check Redis server status

2. **Database Lock Error**
   - SQLite file locks (rare with in-memory)
   - Check for concurrent test execution

3. **Import Errors**
   - Ensure PYTHONPATH includes backend directory
   - Check virtual environment activation

4. **Test Timeouts**
   - Integration tests may take longer
   - Check Celery task execution

### Test Isolation
- Each test gets fresh database session
- Redis namespace is cleared between tests
- No shared state between test methods

## Contributing

### Adding New Tests

1. **Follow naming conventions**:
   - Test classes: `TestFeatureName`
   - Test methods: `test_specific_behavior`

2. **Use appropriate markers**:
   - `@pytest.mark.integration` for full-stack tests
   - `@pytest.mark.slow` for time-consuming tests

3. **Maintain test isolation**:
   - Don't depend on other tests
   - Clean up test data
   - Use fixtures for setup

4. **Document test purpose**:
   - Clear docstrings
   - Assertion messages
   - Test data explanations

### Test Data Management
- Use fixtures for reusable data
- Generate unique identifiers
- Avoid hardcoded values
- Clean up after tests
