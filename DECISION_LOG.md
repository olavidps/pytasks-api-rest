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