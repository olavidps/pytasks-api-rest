# PyTasks API REST

A clean and modern task management API built with FastAPI, following clean architecture principles and best practices.

## 🎯 API Requirements

### Core Features

- **CRUD Operations**: Create, read, update, delete task lists and tasks
- **Task State Management**: Change task status (pending, in-progress, completed)
- **Advanced Filtering**: Filter tasks by state, priority with completion percentage
- **Clean Architecture**: Domain/Application/Infrastructure layers

### Bonus Features

- **JWT Authentication**: Login and protected endpoints
- **Task Assignment**: Assign users to tasks
- **Email Notifications**: Simulated email invitations

## 🛠️ Tech Stack

- **API Framework**: FastAPI + Uvicorn (ASGI server)
- **Database**: SQLAlchemy + PostgreSQL
- **Testing**: pytest (75% coverage target)
- **Code Quality**: black + isort + flake8
- **Containerization**: Docker + docker-compose
- **Dependencies**: Poetry

## 🔧 Project Tooling

- **Dependency Management**: Poetry for reliable package management
- **Code Formatting**:
  - Black for consistent code style
  - isort for organized imports
- **Linting**: flake8 with plugins for code quality checks
- **Testing**:
  - pytest for test running
  - pytest-cov for coverage reporting
- **Git Hooks**: pre-commit for automated quality checks
- **Docker**: For consistent development and deployment environments
- **Makefile**: Simple command interface for common development tasks
- **API Testing**: Postman collection with example requests for all main endpoints

## 🚀 Development Phases

### Phase 1: Foundation ✅

- [x] Project setup with Poetry
- [x] Code quality tools configuration
- [x] Documentation structure
- [x] Project planning
- [x] Initial API design
- [x] FastAPI project setup

### Phase 2: Core Domain ✅

- [x] Domain models (Task, TaskList, User)
- [x] Custom exceptions and validations
- [x] Repository interfaces

#### Domain Model Details

```mermaid
classDiagram
    class Task {
        +UUID id
        +String title
        +String description
        +TaskStatus status
        +TaskPriority priority
        +UUID task_list_id
        +UUID assigned_user_id
        +DateTime created_at
        +DateTime updated_at
        +DateTime due_date
        +DateTime completed_at
        +mark_as_in_progress()
        +mark_as_completed()
        +mark_as_pending()
        +change_priority(priority)
        +assign_to_user(user_id)
        +update_details(title, description, due_date)
        +is_completed()
        +is_overdue()
    }

    class TaskList {
        +UUID id
        +String name
        +String description
        +UUID owner_id
        +DateTime created_at
        +DateTime updated_at
        +Boolean is_active
        +update_details(name, description)
        +deactivate()
        +activate()
    }

    class User {
        +UUID id
        +String email
        +String username
        +String full_name
        +Boolean is_active
        +DateTime created_at
        +DateTime updated_at
        +DateTime last_login
        +update_profile(username, full_name, email)
        +deactivate()
        +activate()
        +record_login()
    }

    class TaskStatus {
        <<enumeration>>
        PENDING
        IN_PROGRESS
        COMPLETED
    }

    class TaskPriority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
        CRITICAL
    }

    Task --> TaskStatus
    Task --> TaskPriority
    Task "*" --> "1" TaskList: belongs to
    Task "*" --> "0..1" User: assigned to
    TaskList "*" --> "1" User: owned by
```

#### Exception Hierarchy

```
DomainException
├── ValidationError
├── NotFoundError
│   ├── TaskNotFoundError
│   ├── TaskListNotFoundError
│   └── UserNotFoundError
├── AlreadyExistsError
│   ├── TaskListAlreadyExistsError
│   └── UserAlreadyExistsError
├── BusinessRuleViolationError
└── UnauthorizedOperationError
```

#### Key Domain Concepts

- **Immutable Entities**: All domain entities are immutable, using Pydantic v2's frozen models
- **Rich Domain Model**: Business logic encapsulated in entity methods rather than anemic models
- **Method-Based State Changes**: All state changes happen through explicit methods like `mark_as_completed()`
- **Type Safety**: Strong typing throughout with validation via Pydantic
- **Clear Repository Interfaces**: Abstract base classes define contracts for data access

#### Database Infrastructure

The infrastructure layer implements the repository pattern using SQLAlchemy ORM:

**Database Models:**

- `UserModel`: User entity with email/username uniqueness constraints
- `TaskListModel`: Task list entity with foreign key to user (owner)
- `TaskModel`: Task entity with foreign keys to task list and optional assignee

**Key Features:**

- PostgreSQL database with proper relationships and constraints
- Repository pattern implementation for clean separation of concerns
- Async SQLAlchemy for high-performance database operations
- Automatic timestamp management (created_at, updated_at)
- Proper foreign key relationships and cascading deletes

### Phase 3: Infrastructure ✅

- [x] Database setup (SQLAlchemy + PostgreSQL)
- [x] Repository implementations
- [x] SQLAlchemy models with relationships and constraints
- [x] Repository pattern implementation

### Phase 4: API Layer ✅

- [x] FastAPI routes and schemas
- [x] Error handling middleware
- [x] Task and TaskList domain services
- [x] Database migrations for nullable owner_id
- [x] Enhanced test infrastructure with mocked endpoints

### Phase 5: Testing & Quality ✅

- [x] Unit and integration tests
- [x] Coverage report (71% achieved, targeting 75%+)
- [x] Comprehensive test infrastructure with database isolation
- [x] Pre-commit hooks with automated testing

### Phase 6: Authentication & Security 🚧

- [ ] JWT Authentication implementation
- [ ] User registration and login endpoints
- [ ] Password hashing with bcrypt
- [ ] Protected route middleware
- [ ] Role-based access control (RBAC)

#### Authentication Implementation Plan

**Libraries and Dependencies:**
```bash
# Core authentication libraries
poetry add python-jose[cryptography]  # JWT token handling
poetry add passlib[bcrypt]            # Password hashing
poetry add python-multipart           # Form data support
```

**Implementation Phases:**

1. **Password Security** (Week 1)
   - Implement password hashing with bcrypt
   - Add password validation rules
   - Update User model with hashed_password field
   - Create password utilities (hash, verify)

2. **JWT Token System** (Week 2)
   - JWT token generation and validation
   - Access token and refresh token logic
   - Token expiration and renewal
   - Secure token storage recommendations

3. **Authentication Endpoints** (Week 3)
   - POST /auth/register - User registration
   - POST /auth/login - User authentication
   - POST /auth/refresh - Token refresh
   - POST /auth/logout - Token invalidation

4. **Protected Routes** (Week 4)
   - Authentication dependency injection
   - Route protection middleware
   - Current user context
   - Permission-based access control

5. **Role-Based Access Control** (Week 5)
   - User roles and permissions
   - Resource ownership validation
   - Admin vs regular user capabilities
   - Task assignment permissions

### Phase 7: Advanced Features 📋

- [ ] Email notification system
- [ ] Task assignment workflows
- [ ] Real-time updates with WebSockets
- [ ] File attachments for tasks
- [ ] Task comments and activity logs

#### Advanced Features Implementation

**Email Notifications:**
- Integration with SendGrid or AWS SES
- Task deadline reminders
- Assignment notifications
- Daily/weekly digest emails

**Real-time Features:**
- WebSocket integration for live updates
- Task status change notifications
- Collaborative editing indicators
- Live user presence

**Enhanced Task Management:**
- File upload and attachment system
- Task comments and discussion threads
- Activity logs and audit trails
- Task templates and recurring tasks

### Phase 8: Deployment & Production 🚀

- [ ] Production Docker configuration
- [ ] CI/CD pipeline setup
- [ ] Environment configuration management
- [ ] Monitoring and logging
- [ ] Performance optimization

## 🧪 Testing Strategy

### Test Database Setup & Isolation

The project uses a comprehensive testing strategy with proper database isolation:

- **Isolated Sessions**: Each test runs in its own transaction with automatic rollback
- **No Data Persistence**: Test data doesn't leak between tests
- **Async Support**: Full async/await support with pytest-asyncio
- **Pre-commit Integration**: Tests run automatically on git commits with database lifecycle management

#### Key Testing Features

- **Transaction Isolation**: Uses `isolated_db_session` fixture for complete test isolation
- **Automatic Cleanup**: Database state is automatically rolled back after each test
- **Docker Integration**: Test database runs in Docker with automatic startup/teardown
- **Performance Testing**: Includes load tests for 100+ users and 200+ tasks

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/domain/             # Domain unit tests
│   ├── test_task.py         # Task entity tests
│   ├── test_task_list.py    # TaskList entity tests
│   ├── test_user.py         # User entity tests
│   └── test_edge_cases.py   # Edge case tests
├── integration/             # Integration tests
│   ├── test_database_integration.py  # Database tests
│   └── repositories/        # Repository tests
└── performance/             # Performance tests
    └── test_performance.py  # Concurrency and performance tests
```

### Running Tests

```bash
# Run all tests with automatic database setup
make test

# Run only unit tests (no database required)
make test-unit

# Run only integration tests (with database)
make test-integration

# Run tests with coverage report
make test-cov

# Watch mode for continuous testing
make test-watch

# Manual test execution with pytest
ENVIRONMENT=test poetry run pytest
```

### Test Features

- **Edge Cases**: Boundary and extreme case validations
- **Performance**: Load tests (100+ users, 200+ tasks)
- **Concurrency**: Concurrent operation tests
- **Integration**: Entity relationship tests
- **Coverage**: 75%+ target

## 🗄️ Database Management

### Migrations with Alembic

```bash
# Run migrations
make migrate

# Create new migration
make migration

# View migration history
make migration-history

# View current migration
make migration-current
```

### Database Setup

```bash
# Complete setup with Docker
make test-db

# Only create test database
python scripts/setup_test_db.py
```

## 🛠️ Development Commands

### Available Make Commands

```bash
# Development
make install          # Install dependencies and setup pre-commit hooks
make dev             # Start development server
make format          # Format code with black and isort
make lint            # Run linting with flake8
make check           # Run all quality checks (CI-friendly)
make clean           # Clean temporary files
make update          # Update dependencies

# Testing
make test            # Run all tests with database setup
make test-unit       # Run unit tests only
make test-integration # Run integration tests with database
make test-cov        # Run tests with coverage report
make test-watch      # Watch mode for continuous testing

# Database
make migrate         # Run database migrations
make migration       # Create new migration
make migration-history # Show migration history
make migration-current # Show current migration
make test-db-up      # Start test database
make test-db-down    # Stop test database

# Docker
make docker-dev      # Start development database
make docker-test     # Start test database
make docker-test-down # Stop test containers
make docker-prod     # Start production environment
make docker-down     # Stop all containers
make docker-down-all # Stop all containers (dev, test, prod)
```

### Pre-commit Integration

The project includes automated pre-commit hooks that:

- Start test database automatically
- Run database migrations
- Execute all tests
- Clean up test containers
- Ensure code quality before commits

## 📊 Current Status

**Completed Phases:**
- ✅ **Phase 1-4**: Core infrastructure, domain models, API endpoints
- ✅ **Phase 5**: Comprehensive testing with 71% coverage
- 🚧 **Phase 6**: Authentication (next priority)

**Ready for Production Features:**
- Complete CRUD operations for tasks and task lists
- Advanced filtering and pagination
- Robust error handling and validation
- Comprehensive test suite with database isolation
- Clean architecture with domain-driven design

## 🏃‍♂️ Quick Start

### Initial Setup

```bash
# Install dependencies and pre-commit hooks
make install

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 🎯 Next Steps

1. **Immediate Priority**: Implement JWT authentication system
2. **Short Term**: Add email notifications and real-time features
3. **Long Term**: Production deployment and monitoring

See the [Authentication Implementation Plan](#authentication-implementation-plan) for detailed next steps.

### Development

```bash
# Run development server
make dev

# Update dependencies
make update
```

### Code Quality

```bash
# Format code (DOESN'T fix imports/unused)
make format

# Check code quality issues (doesn't modify)
make lint

# Verify everything is correct (CI-friendly)
make check
```

### Development Workflow

```bash
# 1. Write code
# 2. Format and check code
make format
make check

# 3. Run tests
make test
```

### Testing

The project includes a comprehensive testing structure with clear separation between unit and integration tests.

```bash
# Run all tests (unit + integration)
make test

# Run only unit tests (fast, no database required)
make test-unit

# Run only integration tests (with database)
make test-integration

# Run with coverage report
make test-cov

# Watch mode for development
make test-watch
```

**Test Structure:**

- **Unit Tests** (`tests/unit/`): Fast tests that don't require a database

  - Domain model tests (User, Task, TaskList)
  - Business logic validation
  - No external dependencies

- **Integration Tests** (`tests/integration/`): Tests that require database connectivity
  - Repository implementations
  - Database operations
  - Full application workflows

**Key Features:**

- **Automatic Setup**: Integration tests handle all database setup and teardown
- **Test Isolation**: Each integration test run uses a fresh database instance
- **Fast Unit Tests**: Unit tests run without database overhead
- **Clear Separation**: Distinct test categories for different purposes
- **No Manual Setup**: No need to run separate database setup commands

### API Testing with Postman

The project includes a comprehensive Postman collection (`API.postman_collection.json`) with example requests for all main API endpoints.

**Features:**
- Pre-configured requests for all CRUD operations
- Example payloads for creating and updating resources
- Authentication examples (when implemented)
- Environment variables for easy endpoint management

**Usage:**
1. Import `API.postman_collection.json` into Postman
2. Set up environment variables (base URL: `http://localhost:8000`)
3. Start the development server with `make dev`
4. Test endpoints directly from Postman interface

**Available Endpoints:**
- User management (CRUD operations)
- Task list management
- Task operations with filtering
- Authentication flows (when implemented)

### Docker

#### Development Setup

```bash
# Start only PostgreSQL in Docker (API runs locally for debugging)
make docker-dev
```

With this setup:

- PostgreSQL runs in Docker (accessible at localhost:5432)
- API runs locally through your IDE for easy debugging
- Use the following connection string: `postgresql://postgres:postgres@localhost:5432/pytasks`

#### Production-like Environment

```bash
# Start both PostgreSQL and API in Docker
make docker-prod
```

With this setup:

- Both PostgreSQL and API run in Docker
- API is accessible at http://localhost:8000
- API uses internal Docker networking to connect to PostgreSQL

#### Cleanup

```bash
# Stop all Docker containers and remove volumes
make docker-down
```

## 🧰 Command Reference

### Essential Commands

| Command            | Description                          |
| ------------------ | ------------------------------------ |
| `make install`     | Install dependencies and setup hooks |
| `make dev`         | Run development server               |
| `make test`        | Run all tests (full lifecycle)       |
| `make test-cov`    | Run tests with coverage report       |
| `make test-unit`   | Run unit tests only                  |
| `make format`      | Format code with black and isort     |
| `make check`       | Verify code quality (CI-friendly)    |
| `make docker-dev`  | Start PostgreSQL in Docker           |
| `make docker-down` | Stop all Docker containers           |

## 📁 Project Structure

Here is a detailed project structure.

```
pytasks-api-rest/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── domain/                 # Business entities and rules
│   │   ├── __init__.py
│   │   ├── models/             # Domain entities
│   │   │   ├── __init__.py
│   │   │   ├── task.py         # Task entity
│   │   │   ├── task_list.py    # TaskList entity
│   │   │   └── user.py         # User entity
│   │   ├── exceptions/         # Domain-specific exceptions
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── task.py
│   │   │   ├── task_list.py
│   │   │   └── user.py
│   │   ├── repositories/       # Repository interfaces
│   │   │   ├── __init__.py
│   │   │   ├── task_repository.py
│   │   │   ├── task_list_repository.py
│   │   │   └── user_repository.py
│   │   └── services/           # Domain services
│   │       ├── __init__.py
│   │       ├── task_domain_service.py
│   │       ├── task_list_domain_service.py
│   │       └── user_domain_service.py
│   ├── application/            # Use cases and services
│   │   ├── services/           # Application validation services
│   │   │   ├── __init__.py
│   │   │   ├── task_validation_service.py
│   │   │   ├── task_list_validation_service.py
│   │   │   └── user_validation_service.py
│   │   └── use_cases/          # Application use cases
│   │       ├── __init__.py
│   │       ├── create_task.py
│   │       ├── create_task_list.py
│   │       ├── create_user.py
│   │       ├── get_task.py
│   │       ├── get_tasks.py
│   │       ├── update_task.py
│   │       └── ... (other use cases)
│   ├── infrastructure/         # Implementation details
│   │   ├── __init__.py
│   │   ├── database/           # Database related code
│   │   │   ├── __init__.py
│   │   │   ├── connection.py   # Database connection setup
│   │   │   └── models/         # SQLAlchemy ORM models
│   │   │       ├── __init__.py
│   │   │       ├── task.py
│   │   │       ├── task_list.py
│   │   │       └── user.py
│   │   ├── repositories/       # Repository implementations
│   │   │   ├── __init__.py
│   │   │   ├── task_repository_impl.py
│   │   │   ├── task_list_repository_impl.py
│   │   │   └── user_repository_impl.py
│   │   └── email/              # Email service implementation
│   │       ├── __init__.py
│   │       └── notification_service.py
│   └── api/                    # HTTP layer
│       ├── __init__.py
│       ├── dependencies.py     # FastAPI dependencies
│       ├── error_handlers.py   # Exception handlers
│       ├── routes/             # API endpoints
│       │   ├── __init__.py
│       │   ├── health.py       # Health check routes
│       │   ├── tasks.py        # Task routes
│       │   ├── task_lists.py   # TaskList routes
│       │   └── users.py        # User routes
│       └── schemas/            # Pydantic schemas
│           ├── __init__.py
│           ├── common_schemas.py
│           ├── task_schemas.py
│           ├── task_list_schemas.py
│           └── user_schemas.py
├── tests/                      # Test suite
│   ├── conftest.py             # Global pytest fixtures
│   ├── api/                    # API endpoint tests (integration)
│   │   ├── conftest.py         # API-specific fixtures
│   │   ├── test_task_lists_endpoints.py
│   │   ├── test_tasks_endpoints.py
│   │   └── test_users_endpoints.py
│   ├── unit/                   # Unit tests
│   │   ├── conftest.py         # Unit test fixtures
│   │   ├── domain/             # Domain layer tests
│   │   ├── application/        # Application layer tests
│   │   └── api/                # API layer unit tests
│   ├── integration/            # Integration tests
│   │   └── repositories/       # Repository integration tests
│   ├── factories/              # Test data factories
│   └── performance/            # Performance tests
├── migrations/                 # Database migrations
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
├── scripts/                    # Utility scripts
│   ├── run_tests.py
│   ├── setup_test_db.py
│   └── test_runner.py
├── .env.example                # Environment variables template
├── .flake8                     # Flake8 configuration
├── .gitignore                  # Git ignore file
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Main Docker compose
├── docker-compose.dev.yml      # Development environment
├── docker-compose.test.yml     # Test environment
├── docker-compose.prod.yml     # Production environment
├── Dockerfile                  # Docker image definition
├── Makefile                    # Development commands
├── pyproject.toml              # Project dependencies and config
├── poetry.toml                 # Poetry configuration
├── poetry.lock                 # Locked dependencies
├── pytest-mocked.ini           # Pytest configuration for mocked tests
├── API.postman_collection.json # Postman API collection
├── DECISION_LOG.md             # Technical decisions documentation
└── README.md                   # Project documentation
```
