# EPOCH5 Template Development Makefile

.PHONY: help setup test lint format security clean demo

help: ## Show this help message
	@echo "EPOCH5 Template Development Commands"
	@echo "==================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up development environment
	@bash dev-setup.sh

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

security: ## Run security scans
	@echo "Running security checks..."
	@bandit -r . --skip B101 -f txt || true

clean: ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

demo: ## Run demo workflow
	python3 integration.py setup-demo
	python3 integration.py status
	python3 integration.py run-workflow

status: ## Show system status
	python3 integration.py status

validate: ## Validate system integrity
	python3 integration.py validate

dashboard: ## Launch web dashboard
	bash ceiling_launcher.sh

install: ## Install dependencies
	pip install -r requirements.txt

dev-install: ## Install dependencies including development tools
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

all-checks: format lint security test ## Run all quality checks

ci: ## Run CI-like checks
	@echo "Running CI checks..."
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) security
	@$(MAKE) test-fast

# Development shortcuts
t: test
l: lint  
f: format
s: security
c: clean
d: demo