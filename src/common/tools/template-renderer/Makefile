# Makefile for template-renderer CLI tool
# Handles installation and dependency management

.PHONY: help install install-deps install-local clean build test lint format

# Default target
help:
	@echo "Template Renderer CLI - Makefile Commands"
	@echo "=========================================="
	@echo ""
	@echo "Installation:"
	@echo "  make install          - Install CLI tool and all dependencies"
	@echo "  make install-deps     - Install common module dependencies"
	@echo "  make install-local    - Install CLI tool in editable mode"
	@echo ""
	@echo "Development:"
	@echo "  make build            - Build the package"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linters (ruff, mypy)"
	@echo "  make format           - Format code (black, isort)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove build artifacts and cache"
	@echo ""

# Install everything (dependencies + CLI tool)
install: install-deps install-local
	@echo "✓ Installation complete"
	@echo ""
	@echo "Usage: template-render --help"

# Install common module dependencies
install-deps:
	@echo "Installing common module dependencies..."
	@echo ""
	@echo "→ Installing dotfiles-template-renderer..."
	@cd ../../modules/template-renderer && uv pip install -e .
	@echo ""
	@echo "✓ Common module dependencies installed"

# Install CLI tool in editable mode
install-local:
	@echo "Installing template-renderer CLI..."
	@uv pip install -e .
	@echo "✓ CLI tool installed"

# Build the package
build:
	@echo "Building package..."
	@uv build
	@echo "✓ Build complete"

# Run tests
test:
	@echo "Running tests..."
	@uv run pytest
	@echo "✓ Tests complete"

# Run linters
lint:
	@echo "Running linters..."
	@echo "→ Ruff..."
	@uv run ruff check src/
	@echo "→ Mypy..."
	@uv run mypy src/
	@echo "✓ Linting complete"

# Format code
format:
	@echo "Formatting code..."
	@echo "→ Black..."
	@uv run black src/
	@echo "→ Isort..."
	@uv run isort src/
	@echo "✓ Formatting complete"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"

