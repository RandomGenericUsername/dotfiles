# VSCode Workspace Configuration

This directory contains VSCode workspace settings that align with the project's formatting, linting, and type-checking rules.

## Files

- **`settings.json`** - Workspace settings that configure Python tools to match `pyproject.toml`
- **`extensions.json`** - Recommended extensions for development
- **`launch.json`** - Debug configurations for running and testing the CLI

## Setup Instructions

### 1. Install Recommended Extensions

When you open this project in VSCode, you'll see a notification to install recommended extensions. Click "Install All" or:

```bash
# Or install manually via the command line
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
```

Alternatively, run the provided script:
```bash
bash install-extensions.sh
```

### 2. Create Virtual Environment

```bash
cd src/dotfiles-installer/cli
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

### 3. Verify Setup

Open a Python file and verify:
- ✅ Black formatter is active (format on save works)
- ✅ isort organizes imports
- ✅ Ruff shows linting errors
- ✅ mypy shows type errors

## Configuration Details

### Black Formatter
- **Line length**: 79 characters
- **Target version**: Python 3.12
- **Format on save**: Enabled

### isort
- **Profile**: black (compatible with Black)
- **Line length**: 79 characters
- **Trailing comma**: Enabled
- **Multi-line mode**: 3 (vertical hanging indent)

### Ruff
- **Line length**: 79 characters
- **Target version**: Python 3.12
- **Rules enabled**: E, W, F, I, B, C4, UP, ARG, SIM, PTH
- **Auto-fix on save**: Enabled

### mypy
- **Python version**: 3.12
- **Strict mode**: Enabled
- **Check untyped defs**: Yes
- **Disallow incomplete defs**: Yes
- **Disallow untyped defs**: Yes

## Debugging

Use the debug configurations in `launch.json`:

1. **Python: Current File** - Run the current file
2. **Python: CLI Install** - Debug the install command
3. **Python: CLI Uninstall** - Debug the uninstall command
4. **Python: Tests** - Run all tests
5. **Python: Tests (Current File)** - Run tests in current file

Press `F5` or go to Run → Start Debugging to launch.

## Troubleshooting

### Extensions not showing?
- Reload VSCode: `Ctrl+Shift+P` → "Developer: Reload Window"
- Check that extensions are installed: `code --list-extensions`

### Format on save not working?
- Verify Python extension is installed
- Check that `.venv` path is correct in `settings.json`
- Restart VSCode

### Type checking not showing errors?
- Ensure mypy extension is installed
- Check Python interpreter is set to `.venv/bin/python`
- Run `mypy .` in terminal to verify

### Linting not working?
- Ensure Ruff extension is installed
- Check that Ruff is installed: `uv run ruff --version`
- Restart VSCode

## Syncing with Project Settings

These VSCode settings are derived from `pyproject.toml`. If you update tool configurations in `pyproject.toml`, update the corresponding settings here to keep them in sync.

Key mappings:
- `pyproject.toml` `[tool.black]` → `settings.json` `python.formatting.blackArgs`
- `pyproject.toml` `[tool.isort]` → `settings.json` `isort.args`
- `pyproject.toml` `[tool.ruff]` → `settings.json` `ruff.*`
- `pyproject.toml` `[tool.mypy]` → `settings.json` `mypy-type-checker.args`
