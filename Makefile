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
test: ## Run tests
	poetry run pytest -v

test-cov: ## Run tests with coverage
	poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

# === Docker ===
docker-dev: ## Start PostgreSQL for development
	docker-compose up -d

docker-prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up --build

docker-down: ## Stop all containers
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v

# === Utilities ===
clean: ## Clean temporary files
	rm -rf .pytest_cache .coverage htmlcov __pycache__
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete

update: ## Update dependencies
	poetry update
	@if [ -f .pre-commit-config.yaml ]; then poetry run pre-commit autoupdate; fi
