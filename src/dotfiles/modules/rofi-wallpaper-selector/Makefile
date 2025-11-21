.PHONY: help install clean clean-venv test lint format check build sync ensure-sync

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

ensure-sync: ## Ensure dependencies are synced
	@if [ ! -d ".venv" ]; then \
		echo "Virtual environment not found. Running 'uv sync'..."; \
		uv sync; \
	fi

sync: ## Sync dependencies with uv
	@echo "Syncing dependencies..."
	@uv sync
	@echo "✅ Dependencies synced"

clean-venv: ## Remove virtual environment
	@echo "Removing virtual environment..."
	@rm -rf .venv
	@echo "✅ Virtual environment removed"
	@echo "Run 'make install' or 'uv sync' to recreate"

install: ## Install project in editable mode
	@echo "Installing project..."
	@uv sync
	@echo "✅ Installation complete"

build: ensure-sync ## Build the package
	@echo "Building package..."
	@uv build
	@echo "✅ Build complete"

test: ensure-sync ## Run tests
	@echo "Running tests..."
	@uv run pytest
	@echo "✅ Tests complete"

lint: ensure-sync ## Run linter
	@echo "Running linter..."
	@uv run ruff check src/
	@echo "✅ Linting complete"

format: ensure-sync ## Format code
	@echo "Formatting code..."
	@uv run ruff format src/
	@echo "✅ Formatting complete"

check: ensure-sync ## Run linter and tests
	@echo "Running checks..."
	@uv run ruff check src/
	@uv run pytest
	@echo "✅ All checks passed"

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"
