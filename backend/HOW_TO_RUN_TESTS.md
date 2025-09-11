# How to Run the Workflow Integration Tests

This guide shows you exactly how to run the integration tests I created for your workflow automation platform.

## 🚀 Quick Start

### Option 1: Interactive Test Runner (Recommended)
```bash
cd flowmaker/backend
python run_simple_test.py
```

This will give you a menu with options to:
- Run simple tests (no Redis required)
- Run full integration tests (requires Redis)
- Check Redis connection
- Get help installing Redis

### Option 2: Direct Command Line

#### Run Simple Tests (No Redis Required)
```bash
cd flowmaker/backend
python -m pytest tests/test_workflows_simple.py -v
```

#### Run Full Integration Tests (Requires Redis)
```bash
cd flowmaker/backend
python -m pytest tests/test_workflows.py -v
```

## 📋 Test Categories

### 1. Simple Tests (`test_workflows_simple.py`)
**No Redis required** - Tests core functionality:
- ✅ User registration and login
- ✅ JWT token generation and validation
- ✅ Workflow creation and management
- ✅ Database persistence
- ✅ Error handling

### 2. Full Integration Tests (`test_workflows.py`)
**Requires Redis** - Tests complete workflow execution:
- ✅ All simple test functionality
- ✅ Workflow execution with Celery tasks
- ✅ End-to-end workflow processing
- ✅ Execution logging and monitoring
- ✅ Error handling with invalid configurations

## 🔧 Prerequisites

### Required (Always)
- Python 3.8+
- All dependencies from `requirements.txt` (already installed)
- SQLite (included with Python)

### Required for Full Integration Tests
- Redis server running on `localhost:6379`

## 🐳 Setting Up Redis

### Option 1: Docker (Easiest)
```bash
# Start Redis container
docker run -d -p 6379:6379 --name redis-test redis:alpine

# Verify it's running
docker ps

# Stop when done
docker stop redis-test
docker rm redis-test
```

### Option 2: Windows Installation
1. Download Redis for Windows: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Keep the command window open

### Option 3: WSL (Windows Subsystem for Linux)
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis
sudo service redis-server start

# Verify
redis-cli ping
```

### Option 4: Redis Cloud (Free)
1. Sign up at https://redis.com/try-free/
2. Create a free database
3. Get connection details
4. Update test configuration (advanced)

## 🧪 Running Specific Tests

### Run Individual Test Classes
```bash
# Test only user authentication
python -m pytest tests/test_workflows_simple.py::TestUserAuthentication -v

# Test only workflow management
python -m pytest tests/test_workflows_simple.py::TestWorkflowManagement -v

# Test only error handling
python -m pytest tests/test_workflows_simple.py::TestErrorHandling -v
```

### Run Individual Test Methods
```bash
# Test user registration only
python -m pytest tests/test_workflows_simple.py::TestUserAuthentication::test_user_registration -v

# Test workflow creation only
python -m pytest tests/test_workflows_simple.py::TestWorkflowManagement::test_workflow_creation -v
```

### Run with Coverage
```bash
python -m pytest tests/test_workflows_simple.py --cov=app --cov-report=html
```

## 📊 Expected Test Results

### Simple Tests (No Redis)
```
tests/test_workflows_simple.py::TestUserAuthentication::test_user_registration PASSED
tests/test_workflows_simple.py::TestUserAuthentication::test_user_login PASSED
tests/test_workflows_simple.py::TestUserAuthentication::test_authenticated_endpoint_access PASSED
tests/test_workflows_simple.py::TestUserAuthentication::test_unauthenticated_endpoint_access PASSED
tests/test_workflows_simple.py::TestWorkflowManagement::test_workflow_creation PASSED
tests/test_workflows_simple.py::TestWorkflowManagement::test_workflow_retrieval PASSED
tests/test_workflows_simple.py::TestWorkflowManagement::test_workflow_list PASSED
tests/test_workflows_simple.py::TestDatabaseIntegration::test_workflow_persistence PASSED
tests/test_workflows_simple.py::TestErrorHandling::test_workflow_not_found PASSED
tests/test_workflows_simple.py::TestErrorHandling::test_unauthorized_workflow_access PASSED

========== 10 passed in 2.34s ==========
```

### Full Integration Tests (With Redis)
```
tests/test_workflows.py::TestUserAuthentication::test_user_registration PASSED
tests/test_workflows.py::TestUserAuthentication::test_user_login PASSED
tests/test_workflows.py::TestUserAuthentication::test_authenticated_endpoint_access PASSED
tests/test_workflows.py::TestUserAuthentication::test_unauthenticated_endpoint_access PASSED
tests/test_workflows.py::TestWorkflowManagement::test_workflow_creation PASSED
tests/test_workflows.py::TestWorkflowManagement::test_workflow_retrieval PASSED
tests/test_workflows.py::TestWorkflowManagement::test_workflow_list PASSED
tests/test_workflows.py::TestWorkflowManagement::test_workflow_bulk_update PASSED
tests/test_workflows.py::TestWorkflowExecution::test_workflow_execution_success PASSED
tests/test_workflows.py::TestWorkflowExecution::test_workflow_test_execution PASSED
tests/test_workflows.py::TestWorkflowExecution::test_workflow_execution_with_invalid_config PASSED
tests/test_workflows.py::TestErrorHandling::test_workflow_not_found PASSED
tests/test_workflows.py::TestErrorHandling::test_unauthorized_workflow_access PASSED
tests/test_workflows.py::TestErrorHandling::test_invalid_workflow_execution PASSED
tests/test_workflows.py::TestDatabaseIntegration::test_workflow_persistence PASSED
tests/test_workflows.py::TestDatabaseIntegration::test_execution_logging PASSED

========== 17 passed in 5.67s ==========
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Redis Connection Error
```
redis.exceptions.ConnectionError: Error 10061 connecting to localhost:6379
```
**Solution**: Start Redis server or use simple tests instead

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Make sure you're in the `flowmaker/backend` directory

#### 3. Database Errors
```
sqlalchemy.exc.OperationalError: database is locked
```
**Solution**: Close any other processes using the database

#### 4. FastAPI Test Client Issues
```
TypeError: FastAPI.__call__() missing 1 required positional argument
```
**Solution**: Use the simple test version or update FastAPI

### Debug Mode
```bash
# Run with verbose output and debugging
python -m pytest tests/test_workflows_simple.py -v -s --pdb

# Run with maximum verbosity
python -m pytest tests/test_workflows_simple.py -vvv
```

## 🎯 What the Tests Validate

### User Authentication Flow
1. ✅ User registration via `/auth/register`
2. ✅ User login via `/auth/login` 
3. ✅ JWT token generation and validation
4. ✅ Protected endpoint access
5. ✅ Unauthorized access handling

### Workflow Management
1. ✅ Workflow creation via `/workflows`
2. ✅ Workflow retrieval and listing
3. ✅ Workflow updates with nodes and edges
4. ✅ Database persistence verification
5. ✅ User ownership validation

### Workflow Execution (Full Tests Only)
1. ✅ End-to-end workflow execution
2. ✅ Celery task integration
3. ✅ Execution status monitoring
4. ✅ Execution logging
5. ✅ Error handling with invalid configs

### Error Handling
1. ✅ Non-existent resource access
2. ✅ Unauthorized access attempts
3. ✅ Invalid request handling
4. ✅ Database constraint violations

## 🚀 Next Steps

1. **Start with Simple Tests**: Run `python run_simple_test.py` and choose option 1
2. **Set up Redis**: Use Docker or install Redis for full integration tests
3. **Run Full Suite**: Choose option 2 in the interactive runner
4. **Integrate with CI/CD**: Add to your GitHub Actions or other CI pipeline
5. **Extend Tests**: Add more test scenarios as your platform evolves

## 📞 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Run the interactive test runner: `python run_simple_test.py`
3. Check the test documentation: `tests/README.md`
4. Review the test files for examples

The tests are designed to be comprehensive yet easy to run. Start with the simple tests to validate your core functionality, then set up Redis for the full integration test suite!
