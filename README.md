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

## 🚀 Development Phases

### Phase 1: Foundation ✅
- [x] Project setup with Poetry
- [x] Code quality tools configuration
- [x] Documentation structure
- [x] Project planning
- [x] Initial API design
- [x] FastAPI project setup

### Phase 2: Core Domain
- [ ] Domain models (Task, TaskList, User)
- [ ] Custom exceptions and validations
- [ ] Repository interfaces

### Phase 3: Infrastructure
- [ ] Database setup (SQLAlchemy + PostgreSQL)
- [ ] Repository implementations

### Phase 4: API Layer
- [ ] FastAPI routes and schemas
- [ ] Error handling middleware

### Phase 5: Testing & Quality
- [ ] Unit and integration tests
- [ ] Coverage report (75%+ target)

### Phase 6: Deployment
- [ ] Docker configuration
- [ ] Environment setup

## 🏃‍♂️ Quick Start

### Initial Setup
```bash
# Install dependencies and pre-commit hooks
make install

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Development
```bash
# Run development server
make dev

# Update dependencies
make update-deps
```

### Code Quality
```bash
# Format code (DOESN'T fix imports/unused)
make format

# Check code quality issues (doesn't modify)
make lint

# Fix ALL issues (format + unused imports)
make fix

# Verify everything is correct (CI-friendly)
make check
```

### Development Workflow
```bash
# 1. Write code
# 2. Fix all issues before committing
make fix

# 3. Verify everything is good
make check

# 4. Run tests
make test
```

### Testing
```bash
# Run tests
make test

# Run tests with coverage report
make test-cov
```

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

The project includes a Makefile with the following commands:

| Command | Description                                     |
|---------|-------------------------------------------------|
| `make help` | Display help information                        |
| `make install` | Install dependencies and setup hooks           |
| `make dev` | Run development server                          |
| `make test` | Run tests                                       |
| `make test-cov` | Run tests with coverage report                  |
| `make format` | Format code                                     |
| `make lint` | Check code quality issues                       |
| `make check` | Check code (CI-friendly, no changes)            |
| `make docker-dev` | Start development environment (PostgreSQL only) |
| `make docker-prod` | Start production environment (PostgreSQL + API) |
| `make docker-down` | Stop all Docker containers                      |
| `make clean` | Clean up temporary files and caches             |
| `make update` | Update dependencies                             |

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
│   │   ├── exceptions.py       # Domain-specific exceptions
│   │   └── repositories/       # Repository interfaces
│   │       ├── __init__.py
│   │       ├── task_repository.py
│   │       ├── task_list_repository.py
│   │       └── user_repository.py
│   ├── application/            # Use cases and services
│   │   ├── __init__.py
│   │   ├── dtos/               # Data Transfer Objects
│   │   │   ├── __init__.py
│   │   │   ├── task_dto.py
│   │   │   ├── task_list_dto.py
│   │   │   └── user_dto.py
│   │   └── services/           # Application services
│   │       ├── __init__.py
│   │       ├── task_service.py
│   │       ├── task_list_service.py
│   │       └── user_service.py
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
│       ├── middlewares.py      # API middlewares
│       └── routes/             # API endpoints
│           ├── __init__.py
│           ├── auth.py         # Authentication routes
│           ├── tasks.py        # Task routes
│           ├── task_lists.py   # TaskList routes
│           └── users.py        # User routes
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── __init__.py
│   │   ├── domain/             # Domain layer tests
│   │   ├── application/        # Application layer tests
│   │   ├── infrastructure/     # Infrastructure layer tests
│   │   └── api/                # API layer tests
│   └── integration/            # Integration tests
│       ├── __init__.py
│       ├── test_api.py         # API integration tests
│       └── test_repositories.py # Repository integration tests
├── docker/                     # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── .flake8                     # Flake8 configuration
├── .gitignore                  # Git ignore file
├── Makefile                    # Development commands
├── pyproject.toml              # Project dependencies
├── poetry.toml                 # Poetry configuration
├── poetry.lock                 # Locked dependencies
├── DECISION_LOG.md             # Technical decisions documentation
└── README.md                   # Project documentation
```
