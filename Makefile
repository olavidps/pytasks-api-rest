.PHONY: help install dev test test-cov lint format check clean docker-dev docker-prod docker-down update

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# === Development Setup ===
install: ## Install dependencies and setup hooks
	poetry install
	@if [ -f .pre-commit-config.yaml ]; then poetry run pre-commit install; fi

dev: ## Run development server
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# === Code Quality ===
format: ## Format code
	@echo "🎨 Formatting code..."
	poetry run black app tests
	poetry run isort app tests
	poetry run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app tests
	poetry run flake8 app tests
	@echo "✅ Code formatted!"

lint: ## Check code quality issues
	@echo "🔍 Linting code..."
	poetry run flake8 app tests
	@echo "✅ Linting passed!"

check: ## Check code (CI-friendly, no changes)
	@echo "🔍 Checking code..."
	poetry run black --check app tests
	poetry run isort --check-only app tests
	poetry run flake8 app tests
	@echo "✅ All checks passed!"

# === Testing ===
test: ## Run all tests (unit + integration) with database lifecycle
	@echo "Running all tests (unit + integration)..."
	@echo "First running unit tests (no database)..."
	poetry run pytest tests/unit/ -v --no-cov
	@echo "Now running integration tests (with database)..."
	@echo "🧹 Cleaning up any existing test containers..."
	docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
	@echo "🐳 Starting test database..."
	docker-compose -f docker-compose.test.yml up -d --wait
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5
	@echo "🔄 Running database migrations..."
	ENVIRONMENT=test poetry run alembic upgrade head
	@echo "🧪 Running all tests with test database..."
	ENVIRONMENT=test poetry run pytest tests/ -v
	@echo "🧹 Cleaning up test containers..."
	docker-compose -f docker-compose.test.yml down -v

test-unit: ## Run unit tests only (no database required)
	@echo "Running unit tests (no database)..."
	poetry run pytest tests/unit/ -v --no-cov

test-integration: ## Run integration tests with database lifecycle
	@echo "Running integration tests (with database)..."
	@echo "🧹 Cleaning up any existing test containers..."
	docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
	@echo "🐳 Starting test database..."
	docker-compose -f docker-compose.test.yml up -d --wait
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5
	@echo "🔄 Running database migrations..."
	ENVIRONMENT=test poetry run alembic upgrade head
	@echo "🧪 Running integration tests..."
	ENVIRONMENT=test poetry run pytest tests/integration/ -v
	@echo "🧹 Cleaning up test containers..."
	docker-compose -f docker-compose.test.yml down -v

test-cov: ## Run tests with coverage report
	@echo "🧹 Cleaning up any existing test containers..."
	docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
	@echo "🐳 Starting test database..."
	docker-compose -f docker-compose.test.yml up -d --wait
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5
	@echo "🔄 Running database migrations..."
	ENVIRONMENT=test poetry run alembic upgrade head
	@echo "🧪 Running tests with coverage..."
	ENVIRONMENT=test poetry run pytest --cov=app --cov-report=html --cov-report=term-missing
	@echo "🧹 Cleaning up test containers..."
	docker-compose -f docker-compose.test.yml down -v

test-watch: ## Run tests in watch mode
	docker-compose -f docker-compose.test.yml up -d
	poetry run pytest-watch -- tests/ -v

test-db:
	@echo "Starting test database..."
	docker-compose -f docker-compose.test.yml up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "Running database migrations..."
	DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pytasks_test poetry run alembic upgrade head
	@echo "Test database ready at localhost:5432"

test-db-stop: ## Stop test database
	@echo "Stopping test database..."
	docker-compose -f docker-compose.test.yml down

# Database migrations
migrate:
	@echo "Running database migrations..."
	poetry run alembic upgrade head

migration:
	@echo "Creating new migration..."
	@read -p "Migration name: " name; \
	poetry run alembic revision --autogenerate -m "$$name"

migration-history:
	@echo "Migration history:"
	poetry run alembic history

migration-current:
	@echo "Current migration:"
	poetry run alembic current

# === Docker ===
docker-dev: ## Start PostgreSQL for development
	docker-compose up -d

docker-test: ## Start PostgreSQL for testing
	@echo "🐳 Starting test database..."
	docker-compose -f docker-compose.test.yml up -d
	@echo "⏳ Waiting for test database to be ready..."
	@sleep 5

docker-test-down: ## Stop test containers
	@echo "🐳 Stopping test database..."
	docker-compose -f docker-compose.test.yml down -v

docker-prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up --build

docker-down: ## Stop all containers
	docker-compose down -v

docker-down-all: ## Stop all containers (dev, test, prod)
	docker-compose down -v
	docker-compose -f docker-compose.test.yml down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker-compose -f docker-compose.prod.yml down -v

# === Utilities ===
clean: ## Clean temporary files
	rm -rf .pytest_cache .coverage htmlcov __pycache__
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete

update: ## Update dependencies
	poetry update
	@if [ -f .pre-commit-config.yaml ]; then poetry run pre-commit autoupdate; fi
