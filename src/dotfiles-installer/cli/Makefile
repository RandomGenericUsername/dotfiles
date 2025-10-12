
# Development tools
.PHONY: format lint type-check test security-check safety-check clean dev-shell

dev-shell:
	@echo "Activating virtual environment..."
	@echo "You can leave the dev shell by typing 'exit'"
	@bash -c "source .venv/bin/activate && exec bash"

format: ## Format code with black and isort
	uv run black .
	uv run isort .

lint: ## Lint code with ruff
	uv run ruff check --fix .

type-check: ## Type check with mypy
	uv run mypy .

test: ## Run tests
	uv run python -m pytest -v

security-check: ## Run security checks with bandit
	uv run bandit -r src/

safety-check: ## Check dependencies for vulnerabilities
	uv run safety check

clean: ## Clean cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
