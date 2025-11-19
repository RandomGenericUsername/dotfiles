.PHONY: install test clean clean-venv

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
PYTEST = $(VENV_DIR)/bin/pytest

install:
	uv venv $(VENV_DIR)
	uv pip install -e ".[dev]"

test:
	$(PYTEST) tests/ -v

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-venv:
	rm -rf $(VENV_DIR)

