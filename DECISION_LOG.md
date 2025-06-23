# Technical Decision Log

This file tracks key decisions made during development.

## 1. Requirements Analysis

**Functional Requirements:**

- CRUD operations for task lists and tasks
- Task state management and filtering
- Completion percentage calculation

**Technical Requirements:**

- FastAPI + PostgreSQL + Docker
- Clean architecture (Domain/Application/Infrastructure)
- pytest testing (75% coverage target)
- Code quality: black, flake8, isort

**Bonus Features:**

- JWT authentication
- Task assignment to users
- Email notifications (simulated)

## 2. Project Setup

**Framework Choice: FastAPI**

- Reason: Modern, fast, built-in validation and docs
- Fits API requirements perfectly

**Package Management: Poetry**

- Reason: Better dependency resolution, avoids conflicts
- Commands used:
  - `poetry add fastapi uvicorn sqlalchemy pydantic pydantic-settings`
  - `poetry add --group dev black flake8 isort pytest pytest-cov httpx`
  - `poetry add --group dev pre-commit`

**Database**

- Reason: PostgreSQL for its robustness and scalability
- Used for both development and production environments for consistency
- Commands used: -

**Docker Configuration**

- Implemented separate Docker Compose configurations for different environments:
  - `docker-compose.dev.yml`: Development environment with only PostgreSQL
    - Allows running the API locally for easier debugging
    - Ideal for development with IDE features (breakpoints, variable inspection)
  - `docker-compose.prod.yml`: Production-like environment with complete stack
    - Runs both PostgreSQL and the API in containers
    - Mimics the production deployment pattern
  - `docker-compose.yml`: Simple alias to development configuration
- Added IDE debug configurations for VS Code and PyCharm

## 3. FastAPI Setup

**API Structure**

- Created a clean architecture setup with separation of concerns
- Used a factory pattern for the FastAPI app creation to facilitate testing
- Implemented CORS middleware for frontend integration
- Set up error handling with custom exception classes

**Configuration**

- Used pydantic-settings for type-safe configuration management
- Environment variables with .env file support
- Different configurations for development/production environments

**Initial Endpoints**

- Health check endpoint for API status monitoring
- Added API versioning with /api/v1 prefix
- Set up OpenAPI documentation (Swagger UI and ReDoc)

## 4. Domain Layer Implementation

### Repository Pattern

Models, exceptions, and repositories were added. Basic CRUD methods were implemented to handle data operations. Filtering and pagination were included to support project needs.

Business logic was placed inside the models. Clear method names like `mark_as_completed()` were used to make the code easy to understand. Properties were added to represent states such as `is_completed` and `is_overdue`.

These choices helped keep the code clean and maintainable.

## 5. Testing Infrastructure

### Database Isolation Strategy

**Problem**: Integration tests were failing due to data persistence between tests, causing `UserAlreadyExistsError` and other conflicts.

**Solution**: Implemented comprehensive test isolation using:

- `isolated_db_session` fixture with transaction rollback
- Proper async session management with SQLAlchemy
- Automatic cleanup without data persistence

### Pre-commit Integration

**Decision**: Integrate full database lifecycle into pre-commit hooks

- Automatic test database startup via docker-compose
- Database migrations before test execution
- Complete test suite execution on every commit
- Automatic cleanup of test containers

**Reason**: Ensures all commits are tested against a real database, preventing integration issues in CI/CD.

## 6. Development Workflow

### Makefile Commands

**Decision**: Centralize all development commands in Makefile

- Consistent command interface across team
- Simplified database management
- Integrated testing workflows
- Docker container lifecycle management

**Commands implemented**: install, dev, format, lint, check, test variants, database management

## 7. API Layer Implementation

### Phase 4: Base Schemas and Dependencies

**Decision**: Implement comprehensive Pydantic schemas and FastAPI dependencies

- Created modular schema structure: `common_schemas.py`, `user_schemas.py`, `task_list_schemas.py`, `task_schemas.py`
- Implemented pagination, filtering, and validation patterns
- Added dependency injection for database sessions and repositories
- Established consistent API response formats

**Reason**: Provides type-safe API contracts, automatic validation, and clean separation between domain models and API DTOs. Enables rapid CRUD endpoint development.
