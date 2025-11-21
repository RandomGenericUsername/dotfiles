.PHONY: install clean test

install:
	uv venv
	uv pip install -e .

clean:
	rm -rf .venv
	rm -rf src/*.egg-info
	rm -rf /tmp/rofi-colorscheme-swatches-minimal

clean-venv:
	rm -rf .venv
	uv venv
	uv pip install -e .

test:
	.venv/bin/rofi-colorscheme-viewer-minimal
