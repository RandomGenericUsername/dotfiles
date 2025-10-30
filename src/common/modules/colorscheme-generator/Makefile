.PHONY: help install test lint format type-check clean dev-shell

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linter"
	@echo "  make format      - Format code"
	@echo "  make type-check  - Run type checker"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make dev-shell   - Activate development shell"

install:
	uv venv
	uv sync
	uv pip install -e ".[dev]"

test:
	uv run pytest -v

test-cov:
	uv run pytest --cov=colorscheme_generator --cov-report=html

lint:
	uv run ruff check src/

format:
	uv run black src/ tests/
	uv run ruff check --fix src/

type-check:
	uv run mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

dev-shell:
	@bash -c "source .venv/bin/activate && exec bash"

