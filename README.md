# FastAPI RealWorld Demo

A comprehensive FastAPI reference implementation demonstrating modern development practices with the [RealWorld API specification](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/) using Domain-Driven Design principles.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd fastapi-realworld-demo
poetry install

# Start databases and apply migrations
make setup-dev
make migrate

# Run the application
make run
```

**🌐 Visit**: http://localhost:8000/docs for interactive API documentation

**📚 New here?** → [Development Quickstart](docs/guides/DEVELOPMENT_QUICKSTART.md) (5-minute setup)

## 📖 Documentation Hub

### 🏃‍♂️ Getting Started
- **[Development Quickstart](docs/guides/DEVELOPMENT_QUICKSTART.md)** - 5-minute setup
- **[Getting Started Guide](docs/guides/GETTING_STARTED.md)** - Detailed setup with troubleshooting
- **[API Usage Guide](docs/guides/API_USAGE.md)** - Complete API reference with examples

### 🏗️ Architecture & Design
- **[Project Overview](docs/PROJECT_OVERVIEW.md)** - Technology stack and design principles
- **[Domain-Driven Design](docs/architecture/DOMAIN_DRIVEN_DESIGN.md)** - DDD architecture patterns
- **[Event-Driven Architecture](docs/architecture/EVENT_DRIVEN_ARCHITECTURE.md)** - Event system design
- **[Exception Handling](docs/architecture/EXCEPTION_HANDLING.md)** - Standardized error handling
- **[Transaction Management](docs/architecture/TRANSACTION_MANAGEMENT.md)** - Database transaction patterns

### 🛠️ Development & Testing
- **[Development Workflow](docs/development/DEVELOPMENT_WORKFLOW.md)** - Complete development process
- **[Testing Guide](docs/guides/TESTING.md)** - Comprehensive testing strategies
- **[Commit Guidelines](docs/development/COMMIT_GUIDELINES.md)** - Git commit conventions

### 🚀 Deployment & Production
- **[Production Deployment](docs/deployment/PRODUCTION.md)** - Complete deployment guide

**📋 [Browse All Documentation](docs/README.md)**

## ⚡ What You Get

### 🌍 RealWorld API Implementation
- ✅ **User Management**: Registration, authentication, profile management
- ✅ **Article System**: CRUD operations with slug-based URLs  
- ✅ **Social Features**: Following users, favoriting articles
- ✅ **Content Features**: Comments, tags, personalized feeds
- ✅ **Pagination**: Efficient list pagination across endpoints

### 🏗️ Development-Ready Architecture
- ✅ **Domain-Driven Design**: Clean separation of concerns with clear layer boundaries
- ✅ **Event-Driven Architecture**: Loose coupling via domain events with extensible framework
- ✅ **Type Safety**: Full MyPy validation for compile-time error detection
- ✅ **Comprehensive Testing**: Unit, integration, and E2E tests with optimized fixtures
- ✅ **Transaction Management**: Automatic UoW pattern with `@transactional()` decorator

### 🛠️ Modern Development Stack
- **FastAPI 0.115+** with Pydantic v2
- **PostgreSQL** with async SQLAlchemy 2.0
- **JWT Authentication** with bcrypt
- **Docker** for development databases
- **Poetry** for dependency management
- **pytest** with async support

## 🧪 Testing

```bash
# Run all tests  
make test

# Run specific test types
poetry run pytest tests/unit/         # Unit tests
poetry run pytest tests/integration/  # Integration tests  
poetry run pytest tests/e2e/         # End-to-end tests

# Run with coverage
make test-cov
```

> **🎯 Development Focus**: This project prioritizes development experience, code quality, and architectural patterns. While it includes deployment-ready code, additional configuration is needed for full production deployment (monitoring, security hardening, performance optimization, etc.).

## 🚀 Development Commands

```bash
# Essential commands
make run            # Start with auto-reload
make test           # Run all tests
make lint           # Format and lint code
make type-check     # MyPy type checking

# Database management
make migrate                    # Apply migrations
make migration msg="Add field"  # Create migration
make db-check                  # Test connection

# Quality assurance
make format         # Auto-format code
make health-all     # Check all systems
```

## 🎯 Key Features

> **🎯 Development Focus**: This project prioritizes development experience, code quality, and architectural patterns. While it includes deployment-ready code and solid architectural foundations, additional configuration is needed for full production deployment (monitoring, security hardening, etc.).

### Automatic Transaction Management
```python
@transactional()
async def create_article(uow: AsyncUnitOfWork, article_data: ArticleCreate, user: User) -> Article:
    # Business logic - automatic commit/rollback
```

### Standardized Exception Handling
```python
# Domain layer raises business exceptions
raise ArticleNotFoundError(slug)

# API layer automatically converts to HTTP responses
# → 404 {"errors": {"body": ["Article not found"]}}
```

### Event-Driven Architecture
```python
# Publish domain events from service layer
shared_event_bus.publish(ArticleCreated(
    article_id=article.id,
    title=article.title,
    slug=article.slug
))
```

## 🏗️ Project Structure

```
app/
├── api/           # 🌐 HTTP endpoints (FastAPI routers)
├── service_layer/ # ⚙️ Use cases and orchestration
├── domain/        # 🏛️ Business logic and entities
├── adapters/      # 🔌 Infrastructure (repositories, ORM)
├── events/        # 📡 Event-driven architecture
└── shared/        # 🛠️ Common utilities

tests/
├── unit/          # Pure business logic tests
├── integration/   # Database and API tests
└── e2e/          # Complete workflow tests
```

## 🔗 API Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)
- **Health Check**: http://localhost:8000/healthcheck (Basic status endpoint)
- **OpenAPI Spec**: http://localhost:8000/openapi.json (Machine-readable specification)

**📊 RealWorld Spec**: Fully implements the [RealWorld API specification](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/)

## 🤝 Contributing

1. **Setup**: Follow the [Development Quickstart](docs/guides/DEVELOPMENT_QUICKSTART.md)
2. **Standards**: Review [Development Workflow](docs/development/DEVELOPMENT_WORKFLOW.md)
3. **Commits**: Use [Conventional Commits](docs/development/COMMIT_GUIDELINES.md)
4. **Testing**: Ensure comprehensive test coverage
5. **Type Safety**: All code must pass MyPy validation

## 📚 Learn More

- **[📖 Project Overview](docs/PROJECT_OVERVIEW.md)** - Complete technology overview
- **[🏗️ Architecture Guides](docs/architecture/)** - Detailed design patterns
- **[🛠️ Development Guides](docs/development/)** - Complete development workflow
- **[📋 All Documentation](docs/README.md)** - Browse complete documentation

---

**💡 Questions?** Check the [documentation](docs/README.md) or open an issue!
