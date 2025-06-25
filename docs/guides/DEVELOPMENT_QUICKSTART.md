# Development Quickstart

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

Get the FastAPI RealWorld Demo running locally in under 5 minutes.

## ⚡ Quick Setup

### Prerequisites Check
```bash
# Verify you have the required tools
python --version    # Should be 3.12+
poetry --version    # Should be 1.0+
docker --version    # Should be 20.0+
make --version      # Should be available
```

### 1. Clone & Install
```bash
git clone <repository-url>
cd fastapi-realworld-demo
poetry install
```

### 2. Setup Environment
```bash
# Copy example environment files (defaults work for development)
cp .env.example .env
cp .env.test.example .env.test
```

### 3. Start Databases
```bash
# Start both development and test databases
make setup-dev
```

### 4. Run Migrations
```bash
# Apply database schema
make migrate
```

### 5. Start Application
```bash
# Start with auto-reload
make run
```

### 6. Verify Setup
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthcheck
- **Test Suite**: `make test`

## 🛠️ Essential Commands

### Daily Development
```bash
make run            # Start application with auto-reload
make test           # Run all tests
make test-cov       # Run tests with coverage report
make lint           # Format and lint code
make type-check     # Run MyPy type checking
```

### Database Management
```bash
make migrate                    # Apply migrations
make migration msg="Add field"  # Create new migration
make db-info                   # Show database connection info
make db-check                  # Test database connection
```

### Testing
```bash
make test                      # All tests
poetry run pytest tests/unit/          # Unit tests only
poetry run pytest tests/integration/   # Integration tests
poetry run pytest tests/e2e/          # End-to-end tests
poetry run pytest -x                  # Stop on first failure
```

## 🎯 What You Get

### ✅ Fully Functional API
- User registration and authentication
- Article CRUD with slug-based URLs
- Comments system
- User following and article favoriting
- Tag-based article filtering
- Paginated article feeds

### ✅ Interactive Documentation
- **Swagger UI**: Complete API exploration at `/docs`
- **ReDoc**: Alternative documentation at `/redoc`
- **OpenAPI Spec**: Machine-readable spec at `/openapi.json`

### ✅ Development-Focused Features
- JWT authentication with secure token handling
- Database migrations with Alembic
- Comprehensive test suite with fast execution
- Type checking and linting for code quality
- Basic health check endpoint for container deployments

## 🧪 Verify Your Setup

### Run Tests
```bash
make test
# Should see: All tests passing, ~50ms database cleanup
```

### Check API
```bash
curl http://localhost:8000/healthcheck
# Should return: {"status": "ok"}
```

### Create Your First User
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "username": "demo",
      "email": "demo@example.com", 
      "password": "password123"
    }
  }'
```

## 🚀 Next Steps

### Explore the Architecture
- **[Project Overview](../PROJECT_OVERVIEW.md)** - Understanding the big picture
- **[Domain-Driven Design](../architecture/DOMAIN_DRIVEN_DESIGN.md)** - Architecture patterns
- **[Event-Driven Architecture](../architecture/EVENT_DRIVEN_ARCHITECTURE.md)** - Event system

### Development Workflow
- **[Development Workflow](../development/DEVELOPMENT_WORKFLOW.md)** - Complete development process
- **[Testing Guide](TESTING.md)** - Comprehensive testing strategies
- **[API Usage Guide](API_USAGE.md)** - Complete API reference

### Contributing
- **[Commit Guidelines](../development/COMMIT_GUIDELINES.md)** - Git commit conventions
- **[Error Code Guidelines](ERROR_CODE_GUIDELINES.md)** - Error standardization
- **[Transaction Decorator Guidelines](TRANSACTION_DECORATOR_GUIDELINES.md)** - Using @transactional()

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check if databases are running
docker ps | grep postgres

# Start databases if not running
make up-db
make up-db-test

# Test connections
make db-check
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process or use different port
uvicorn app.main:app --reload --port 8001
```

### Poetry Issues
```bash
# Recreate virtual environment
poetry env remove python
poetry install

# Activate environment manually
poetry shell
```

### Test Database Issues
```bash
# Reset test database
make db-reset-test

# Check test database connection
make db-check-test
```

## 💡 Development Tips

### Fast Feedback Loop
1. **Run tests on save**: Use `pytest-watch` for continuous testing
2. **Hot reload**: Application automatically restarts on code changes
3. **Fast tests**: Database cleanup optimized for <50ms

### Debugging
```bash
# Run single test with detailed output
poetry run pytest tests/unit/test_users.py::test_create_user -v -s

# Debug database queries
# Check application logs for debugging information

# Interactive debugging
poetry run python -c "
import asyncio
from app.main import app
# Interactive testing code here
"
```

### Code Quality
```bash
# Auto-fix formatting issues
make format

# Check what needs fixing before committing
make lint
make type-check
```

---

> **Ready to build? Check out the [API Usage Guide](API_USAGE.md) for complete endpoint documentation!**
