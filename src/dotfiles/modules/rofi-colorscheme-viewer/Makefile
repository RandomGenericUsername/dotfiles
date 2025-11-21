.PHONY: help install install-dev test lint format clean clean-venv

help:
	@echo "Available targets:"
	@echo "  install      - Install package in editable mode"
	@echo "  install-dev  - Install package with dev dependencies"
	@echo "  test         - Run tests with pytest"
	@echo "  lint         - Run ruff linter"
	@echo "  format       - Format code with ruff"
	@echo "  clean        - Remove build artifacts and cache"
	@echo "  clean-venv   - Remove and recreate virtual environment"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

clean-venv:
	rm -rf .venv
	uv venv
	uv pip install -e ".[dev]"
