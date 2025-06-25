# Architecture Diagrams

This directory contains C4 model diagrams that illustrate the architecture of the FastAPI RealWorld Demo project using PlantUML and the C4-PlantUML library.

## Diagrams Overview

The diagrams are organized into logical folders for better navigation:

```
diagrams/
├── architecture/     # System architecture (C4 model)
├── domain/          # Domain models and data structures
├── flow/            # Process and interaction flows
└── testing/         # Testing strategies and architecture
```

### Architecture Diagrams (`architecture/`)

#### 1. Context Diagram (`c4-context.puml`)
Shows the system context and how users interact with the RealWorld API through various client applications.

**Key Elements:**
- **Users**: End users of the blogging platform
- **Admins**: System administrators monitoring the application
- **RealWorld API**: The main system being documented
- **Client Applications**: Frontend applications consuming the API
- **Monitoring Tools**: External monitoring and logging systems

#### 2. Container Diagram (`c4-container.puml`)
Shows the high-level technology choices and how containers communicate within the system.

**Key Elements:**
- **FastAPI Web Application**: The main application container built with FastAPI and Python 3.12
- **PostgreSQL Database**: The data storage container
- **External Client Applications**: Frontend applications that consume the API

#### 3. Component Diagram (`c4-component.puml`)
Shows the internal structure of the FastAPI Web Application container, organized by architectural layers.

**Key Elements:**
- **API Layer**: FastAPI routers handling HTTP requests/responses
- **Service Layer**: Application services orchestrating business operations
- **Domain Layer**: Core business logic and domain models
- **Infrastructure Layer**: Repositories and ORM for data access
- **Shared Components**: Cross-cutting concerns (events, JWT, transactions)

### Domain Diagrams (`domain/`)

#### 4. Domain Model Diagram (`domain-model.puml`)
Shows the relationships between domain aggregates, value objects, and domain services.

**Key Elements:**
- **Domain Aggregates**: User, Article, Comment, Tag, Profile
- **Value Objects**: Slug, Email, Password
- **Domain Services**: Authentication, Feed Generation, Slug Generation
- **Domain Events**: User, Article, and Comment events

#### 5. Database Schema Diagram (`database-schema.puml`)
Shows the complete database structure with tables, relationships, constraints, and indexes.

**Key Elements:**
- **5 Tables**: user, article, comment, follower, article_favorite
- **Relationships**: Foreign keys, junction tables for many-to-many
- **Constraints**: Primary keys, unique constraints, cascade deletes
- **PostgreSQL Features**: Array columns for tags, composite primary keys

### Flow Diagrams (`flow/`)

#### 6. Data Flow Diagram (`data-flow.puml`)
Illustrates how requests flow through the application layers from HTTP request to database and back.

**Key Elements:**
- **Request Pipeline**: HTTP → Auth → Validation → Service → Domain → Repository → Database
- **Response Pipeline**: Database → Repository → Service → Response Mapping → HTTP
- **Transaction Management**: Automatic UoW pattern with `@transactional` decorator
- **Event Publishing**: Domain events for cross-cutting concerns

#### 7. Request Flow Sequence Diagram (`request-flow-sequence.puml`)
Shows the dynamic interaction between components during request processing.

**Key Elements:**
- **Success Flow**: Complete request lifecycle from client to database
- **Error Handling**: Various failure scenarios and exception handling
- **Transaction Management**: UoW pattern and rollback behavior
- **Event Publishing**: Domain event lifecycle

#### 8. Event Flow Diagram (`event-flow.puml`)
Demonstrates how domain events propagate through the event-driven architecture.

**Key Elements:**
- **Event Publishers**: Service layer publishing domain events
- **Event Bus**: Central dispatcher with sync/async handler support
- **Event Handlers**: Domain, cross-domain, and system event handlers
- **External Systems**: Search, email, metrics, audit systems affected by events

#### 9. Authentication Flow Diagram (`authentication-flow.puml`)
Shows the complete JWT authentication and authorization process.

**Key Elements:**
- **User Registration**: Account creation with password hashing
- **User Login**: Email/password authentication with JWT generation
- **Protected Endpoints**: Token validation and user injection
- **Security Features**: bcrypt hashing, JWT signing, middleware protection

### Testing Diagrams (`testing/`)

#### 9. Testing Architecture Diagram (`testing-architecture.puml`)
Demonstrates the test pyramid implementation with different test types and their relationships.

**Key Elements:**
- **E2E Tests**: Complete user workflows with real HTTP and database
- **Integration Tests**: Multi-layer testing with real database
- **Unit Tests**: Component isolation with mocked dependencies
- **Test Infrastructure**: Fixtures, factories, and test database setup

## Architecture Principles

The diagrams illustrate the following key architectural principles:

### Domain-Driven Design (DDD)
- **Domain Layer**: Contains pure business logic and domain models
- **Application Services**: Orchestrate use cases and coordinate between layers
- **Infrastructure**: Handles external concerns like database access
- **API Layer**: Handles HTTP-specific concerns and request/response mapping

### Clean Architecture
- **Dependency Inversion**: Domain layer has no dependencies on infrastructure
- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Business logic can be tested independently of infrastructure

### Event-Driven Architecture
- **Event Bus**: Handles domain events for cross-cutting concerns
- **Decoupling**: Components communicate through events where appropriate

## How to Generate Images

### Using PlantUML CLI
```bash
# Option 1: Install PlantUML locally following the official documentation:
# https://plantuml.com/starting

# Option 2: Use Docker (no local installation required)
# Generate PNG images with Docker
docker run --rm -v $(pwd):/data plantuml/plantuml -tpng /data/diagrams/c4-context.puml

# Generate SVG images with Docker (recommended for documentation)
docker run --rm -v $(pwd):/data plantuml/plantuml -tsvg /data/diagrams/c4-context.puml

# Generate specific diagram with Docker
docker run --rm -v $(pwd):/data plantuml/plantuml -tsvg /data/diagrams/c4-context.puml

# If you have PlantUML installed locally:
# Generate PNG images
plantuml -tpng diagrams/c4-context.puml
plantuml -tpng diagrams/c4-container.puml
plantuml -tpng diagrams/c4-component.puml

# Generate SVG images (recommended for documentation)
plantuml -tsvg diagrams/c4-context.puml
plantuml -tsvg diagrams/c4-container.puml
plantuml -tsvg diagrams/c4-component.puml
```

### Using Online PlantUML Server
1. Visit [PlantText](https://www.planttext.com/) or [PlantUML Online Server](http://www.plantuml.com/plantuml/)
2. Copy and paste the content of any `.puml` file
3. Generate and download the diagram image

### Using VS Code Extension
1. Install the "PlantUML" extension by jebbs
2. Open any `.puml` file
3. Use `Ctrl+Shift+P` → "PlantUML: Preview Current Diagram"
4. Export to various formats using the preview panel

## File Descriptions

| Category | File | Purpose | Level |
|----------|------|---------|-------|
| **Architecture** | `architecture/c4-context.puml` | System context and external interactions | Level 1 |
| **Architecture** | `architecture/c4-container.puml` | High-level technology choices and containers | Level 2 |
| **Architecture** | `architecture/c4-component.puml` | Internal structure of the FastAPI application | Level 3 |
| **Domain** | `domain/domain-model.puml` | Domain relationships and business model | Supplementary |
| **Domain** | `domain/database-schema.puml` | Complete database structure with relationships | Supplementary |
| **Flow** | `flow/data-flow.puml` | Request/response flow through application layers | Supplementary |
| **Flow** | `flow/request-flow-sequence.puml` | Dynamic request flow interactions | Supplementary |
| **Flow** | `flow/event-flow.puml` | Domain event propagation through event bus | Supplementary |
| **Flow** | `flow/authentication-flow.puml` | JWT authentication and authorization process | Supplementary |
| **Testing** | `testing/testing-architecture.puml` | Test pyramid and testing strategy | Supplementary |

## Integration with Documentation

These diagrams are integrated throughout the project documentation:

| Diagram | Used In Documentation | Purpose |
|---------|----------------------|---------|
| [C4 Context](architecture/c4-context.svg) | [Project Overview](../docs/PROJECT_OVERVIEW.md) | System boundaries and external actors |
| [C4 Container](architecture/c4-container.svg) | [Project Overview](../docs/PROJECT_OVERVIEW.md) | High-level technology choices |
| [C4 Component](architecture/c4-component.svg) | [Project Overview](../docs/PROJECT_OVERVIEW.md), [DDD Guide](../docs/architecture/DOMAIN_DRIVEN_DESIGN.md) | Internal application structure |
| [Domain Model](domain/domain-model.svg) | [Domain-Driven Design](../docs/architecture/DOMAIN_DRIVEN_DESIGN.md) | Business entity relationships |
| [Database Schema](domain/database-schema.svg) | [Domain-Driven Design](../docs/architecture/DOMAIN_DRIVEN_DESIGN.md) | Complete database structure with relationships |
| [Data Flow](flow/data-flow.svg) | [Event-Driven Architecture](../docs/architecture/EVENT_DRIVEN_ARCHITECTURE.md) | Request/response pipeline |
| [Request Flow Sequence](flow/request-flow-sequence.svg) | [Event-Driven Architecture](../docs/architecture/EVENT_DRIVEN_ARCHITECTURE.md) | Detailed interaction flows |
| [Event Flow](flow/event-flow.svg) | [Event-Driven Architecture](../docs/architecture/EVENT_DRIVEN_ARCHITECTURE.md) | Domain event propagation |
| [Authentication Flow](flow/authentication-flow.svg) | [API Usage Guide](../docs/guides/API_USAGE.md) | JWT authentication and authorization process |
| [Testing Architecture](testing/testing-architecture.svg) | [Testing Guide](../docs/guides/TESTING.md) | Test pyramid and strategy |

### Related Documentation
- **[Domain-Driven Design](../docs/architecture/DOMAIN_DRIVEN_DESIGN.md)**: Detailed explanation of DDD implementation
- **[Event-Driven Architecture](../docs/architecture/EVENT_DRIVEN_ARCHITECTURE.md)**: Event system design and patterns  
- **[Project Overview](../docs/PROJECT_OVERVIEW.md)**: High-level project description and features
- **[Testing Guide](../docs/guides/TESTING.md)**: Comprehensive testing strategies

## Maintenance

When updating the architecture:

1. **Update diagrams first**: Modify the appropriate `.puml` files
2. **Generate new images**: Use PlantUML to create updated visuals
3. **Update documentation**: Ensure written documentation reflects changes
4. **Validate consistency**: Check that code structure matches diagrams

### Diagram Versioning Strategy

- **Source Control**: All `.puml` source files are version controlled
- **Generated Images**: SVG files are committed to enable GitHub viewing
- **Sync Requirements**: Always regenerate images when source files change
- **Branch Management**: Update diagrams in feature branches alongside code changes
- **Review Process**: Include diagram updates in pull request reviews

### Performance and Complexity Guidelines

**Diagram Complexity Recommendations:**
- **Context Diagrams**: Keep to 5-10 external systems maximum
- **Container Diagrams**: Limit to 8-12 containers for readability
- **Component Diagrams**: Consider splitting if more than 20 components
- **Sequence Diagrams**: Focus on one primary flow per diagram

**Rendering Performance:**
- SVG format provides best balance of quality and file size
- Large diagrams (>50 elements) may render slowly in some viewers
- Consider splitting complex diagrams into multiple focused views
- Use PNG for presentations, SVG for documentation

**GitHub Integration:**
- PlantUML diagrams are generated as SVG files for GitHub viewing
- Generated images are committed to repository for easy viewing
- No external dependencies required for viewing diagrams

## C4 Model References

- **[C4 Model](https://c4model.com/)**: Official C4 model documentation
- **[C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)**: PlantUML library for C4 diagrams
- **[PlantUML](https://plantuml.com/)**: Official PlantUML documentation
