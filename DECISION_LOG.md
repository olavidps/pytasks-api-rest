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

**Additional Features:**

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

### Repository Pattern and Rich Domain Models

**Decision**: Implement repository pattern with rich domain models containing business logic

- Models contain business logic with clear method names like `mark_as_completed()`
- Repository interfaces abstract data access from business logic
- Properties represent computed states like `is_completed` and `is_overdue`
- Custom exceptions provide meaningful error handling

**Why**: Prevents anemic domain models and scattered business logic. Repository pattern enables easy testing with mocks. Domain methods like `mark_as_completed()` keep business rules in one place.

## 5. Testing Infrastructure

### Database Isolation Strategy

**Problem**: Integration tests were failing due to data persistence between tests, causing `UserAlreadyExistsError` and other conflicts.

**Solution**: Implemented comprehensive test isolation using:

- `isolated_db_session` fixture with transaction rollback
- Proper async session management with SQLAlchemy
- Automatic cleanup without data persistence

**Why**: Prevents flaky tests and "works on my machine" issues. Transaction rollback is faster than recreating DB. Each test gets clean state regardless of execution order.

### Pre-commit Integration

**Decision**: Integrate full database lifecycle into pre-commit hooks

- Automatic test database startup via docker-compose
- Database migrations before test execution
- Complete test suite execution on every commit
- Automatic cleanup of test containers

**Why**: Catches issues before they reach CI/CD where they're expensive to fix. Automatic DB lifecycle removes friction - no excuses to skip tests.

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

**Why**: Eliminates manual validation and boilerplate. Auto-generates docs. Modular structure prevents monolithic schema files. Dependency injection makes testing easy with mocks.

## 8. Domain Services and Database Refinements

### Task and TaskList Domain Services

**Decision**: Implement dedicated domain services for complex business operations

- Created `TaskDomainService` for task-specific business logic
- Created `TaskListDomainService` for task list operations and ownership management
- Encapsulated complex domain rules and validations

**Why**: Needed a place for complex business logic that doesn't fit in repositories or entities. Solves the "where does this logic go?" problem. Keeps business rules centralized and testable.

### Database Schema Evolution

**Decision**: Make TaskList owner_id nullable to support shared/public task lists

- Added migration `cde2f8866870_make_owner_id_nullable_in_tasklist.py`
- Updated repository implementations to handle nullable owner scenarios
- Enhanced filtering capabilities for ownership-based queries

**Why**: Original design assumed all lists need owners, but real-world needs shared/public lists. Making it nullable now avoids major refactoring later. Better to be flexible from the start.

### Test Infrastructure Enhancement

**Decision**: Implement comprehensive mocked endpoint testing alongside integration tests

- Added `test_users_endpoints.py` for real database integration tests
- Enhanced `test_users_endpoints_mocked.py` for fast unit-style API tests
- Improved test configuration and fixtures for better isolation

**Why**: Integration tests are slow but thorough, mocked tests are fast but limited. Need both for the testing pyramid - fast feedback during development, confidence in real scenarios.
