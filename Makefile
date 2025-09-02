# EpochCore RAS Development Makefile

.PHONY: help setup test lint format clean demo status validate

help: ## Show this help message
	@echo "EpochCore RAS Development Commands"
	@echo "================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up development environment
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "✓ Development environment setup complete"

test: ## Run all tests with coverage
	pytest --cov=. --cov-report=html --cov-report=term-missing

test-fast: ## Run tests without coverage (faster)
	pytest -x -v

lint: ## Run linting checks
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format: ## Format code with Black
	black .

format-check: ## Check if code needs formatting
	black --check --diff .

clean: ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

demo: ## Run demo workflow
	python integration.py setup-demo
	python integration.py run-workflow

status: ## Show system status
	python integration.py status

validate: ## Validate system integrity
	python integration.py validate

install: ## Install dependencies
	pip install -r requirements.txt

all-checks: format lint test ## Run all quality checks