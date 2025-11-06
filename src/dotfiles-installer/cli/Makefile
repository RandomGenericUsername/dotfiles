MAKEFLAGS += --no-print-directory

# Development tools
.PHONY: format lint type-check test security-check safety-check clean clean-venv dev-shell sync-check ensure-sync

sync-check: ## Check if sync is needed
	@if ! uv run python -c "import main" 2>/dev/null; then \
		echo "❌ Package not installed - sync needed"; \
		exit 1; \
	elif [ uv.lock -nt .venv/pyvenv.cfg ] 2>/dev/null; then \
		echo "❌ Lock file newer than venv - sync needed"; \
		exit 1; \
	elif [ pyproject.toml -nt .venv/pyvenv.cfg ] 2>/dev/null; then \
		echo "❌ pyproject.toml newer than venv - sync needed"; \
		exit 1; \
	else \
		echo "✅ Environment is up to date"; \
	fi

ensure-sync: ## Ensure environment is synced
	@$(MAKE) sync-check || uv sync

dev-shell: ensure-sync
	@echo "Activating virtual environment..."
	@echo "You can leave the dev shell by typing 'exit'"
	@bash -c "source .venv/bin/activate && exec bash"

format: ensure-sync ## Format code with black and isort
	uv run black .
	uv run isort .

lint: ensure-sync ## Lint code with ruff
	uv run ruff check --fix .

type-check: ensure-sync ## Type check with mypy
	uv run mypy .

test: ensure-sync ## Run tests
	uv run python -m pytest -v

security-check: ## Run security checks with bandit
	uv run bandit -r src/

safety-check: ## Check dependencies for vulnerabilities
	uv run safety check

clean: ## Clean cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-venv: ## Remove virtual environment
	@echo "Removing virtual environment..."
	@rm -rf .venv
	@echo "✅ Virtual environment removed"
	@echo "Run 'uv sync' to recreate"

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install-extensions: ## Install VS Code extensions
	@echo "Installing VS Code extensions..."
	@echo "You can leave the dev shell by typing 'exit'"
	@bash -c "source install-extensions.sh"
