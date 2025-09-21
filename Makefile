.PHONY: test test-unit test-api test-integration test-coverage install dev-install clean lint format

# Default Python and pip commands
PYTHON := python
PIP := pip

# Test commands
test:
	@echo "Running all tests..."
	pytest

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v

test-api:
	@echo "Running API tests..."
	pytest tests/api/ -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v

test-coverage:
	@echo "Running tests with coverage..."
	pytest --cov=api --cov-report=html --cov-report=term-missing

test-watch:
	@echo "Running tests in watch mode..."
	pytest-watch

# Installation commands
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

dev-install: install
	@echo "Installing development dependencies..."
	$(PIP) install pytest-cov pytest-watch

# Development commands
dev:
	@echo "Starting development server..."
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

dev-bg:
	@echo "Starting development server in background..."
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &

# Database commands
db-init:
	@echo "Initializing database..."
	$(PYTHON) scripts/init_database.py

# Linting and formatting
lint:
	@echo "Linting code..."
	flake8 api/ tests/ --max-line-length=100 --ignore=E203,W503

format:
	@echo "Formatting code..."
	black api/ tests/ --line-length=100
	isort api/ tests/

# Cleanup
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

# Health check
health:
	@echo "Checking API health..."
	curl -s http://localhost:8000/api/health | python -m json.tool

# Quick test specific components
test-goals:
	@echo "Testing Goals API..."
	pytest tests/api/goals/ -v

test-tasks:
	@echo "Testing Tasks API..."
	pytest tests/api/tasks/ -v

test-validation:
	@echo "Testing validation utilities..."
	pytest tests/unit/test_validation.py -v

# Help
help:
	@echo "Available commands:"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-api      - Run API tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-goals    - Test Goals API specifically"
	@echo "  test-tasks    - Test Tasks API specifically"
	@echo "  install       - Install dependencies"
	@echo "  dev           - Start development server"
	@echo "  db-init       - Initialize database"
	@echo "  lint          - Lint code"
	@echo "  format        - Format code"
	@echo "  clean         - Clean up generated files"
	@echo "  health        - Check API health"
	@echo "  help          - Show this help message"
