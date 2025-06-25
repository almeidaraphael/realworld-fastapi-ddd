# Getting Started Guide

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

This guide will help you get the FastAPI RealWorld Demo project up and running on your local machine in minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
- **Poetry** - [Install Poetry](https://python-poetry.org/docs/#installation)
- **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Make** (optional but recommended) - Usually pre-installed on macOS/Linux
- **Git** - [Install Git](https://git-scm.com/downloads)

## Quick Setup (5 minutes)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-realworld-demo
```

### 2. Install Dependencies

```bash
# Install Python dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 3. Set Up Environment Variables

```bash
# Copy example environment files
cp .env.example .env
cp .env.test.example .env.test

# Edit .env with your preferred settings (optional for development)
# The defaults will work for local development
```

### 4. Start Database Services

```bash
# Start PostgreSQL databases (development and test)
make setup-dev

# Or manually with Docker Compose
docker-compose up -d
```

### 5. Run Database Migrations

```bash
# Apply database migrations
make migrate

# Or manually
poetry run alembic upgrade head
```

### 6. Start the Application

```bash
# Start with auto-reload for development
make run

# Or manually
poetry run uvicorn app.main:app --reload
```

### 7. Verify Installation

Open your browser and visit:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthcheck
- **OpenAPI Spec**: http://localhost:8000/openapi.json

If you see the Swagger UI documentation, you're ready to go! 🎉

## Next Steps

Now that you have the project running:

1. **Explore the API**: Visit http://localhost:8000/docs to interact with the API
2. **Run Tests**: Execute `make test` to run the full test suite
3. **Read the Architecture Guide**: Check out [docs/architecture/](../architecture/) for detailed information
4. **Start Contributing**: See the [Development Workflow](../development/) guide

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database services
docker-compose down
docker-compose up -d
```

#### Poetry Installation Issues

```bash
# If poetry command not found, add to PATH or use:
python -m poetry install
python -m poetry shell
```

#### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Or use a different port
poetry run uvicorn app.main:app --reload --port 8001
```

#### Migration Errors

```bash
# Reset database and re-run migrations
make reset-db
make migrate
```

## Development Environment Setup

For a complete development setup including testing, linting, and debugging:

```bash
# Install all development dependencies
poetry install --with dev

# Set up pre-commit hooks (if available)
pre-commit install

# Run all tests to verify setup
make test

# Run linting and type checking
make lint
make type-check
```

## Alternative Setup Methods

### Using Make Commands

```bash
# Complete setup in one command
make setup-dev

# Individual steps
make install      # Install dependencies
make up-db        # Start databases
make migrate      # Run migrations
make test         # Run tests
make run          # Start application
```

### Manual Setup

```bash
# Without Make - step by step
poetry install
poetry shell
docker-compose up -d
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

## What's Next?

- **API Testing**: Use the interactive docs at http://localhost:8000/docs
- **Code Exploration**: Start with `app/main.py` and explore the domain structure
- **Testing**: Run `make test` to see the comprehensive test suite
- **Development**: Check out the [Development Workflow](../development/DEVELOPMENT_WORKFLOW.md) guide

For detailed architectural information and advanced usage, see the full [Documentation Index](../README.md).
