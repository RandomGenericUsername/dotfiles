.PHONY: install test clean clean-venv

install:
	uv venv .venv
	uv pip install -e ".[dev]"

test:
	.venv/bin/pytest tests/ -v

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-venv:
	rm -rf .venv
	$(MAKE) install

