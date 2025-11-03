# Development Scripts

This directory contains utility scripts for development workflows across all UV Python projects in the repository.

## Available Scripts

### `format-all.sh`
Formats and lints all UV Python projects in the repository.

**What it does:**
- Runs `black` for code formatting
- Runs `isort` for import sorting
- Runs `ruff check --fix` for auto-fixable linting issues
- Runs final `ruff check` to report remaining issues

**Usage:**
```bash
./scripts/dev/format-all.sh
```

**Projects processed:**
- `src/dotfiles-installer/cli`
- All modules in `src/common/modules/`
- All tools in `src/common/tools/`

---

### `lint-all.sh`
Comprehensive linting with auto-fixes across all projects.

**What it does:**
- Runs `black` for formatting
- Runs `isort` for imports
- Runs `ruff check --fix` (safe fixes)
- Runs `ruff check --fix --unsafe-fixes` (unsafe fixes)
- Reports final status for each project

**Usage:**
```bash
./scripts/dev/lint-all.sh
```

**Note:** This is more aggressive than `format-all.sh` as it applies unsafe fixes.

---

### `install-hooks.sh`
Installs pre-commit hooks in all UV Python projects.

**What it does:**
- Runs `make pre-commit-install` in each project
- Sets up git hooks for automatic formatting/linting on commit

**Usage:**
```bash
./scripts/dev/install-hooks.sh
```

**Prerequisites:**
- Each project must have a `.pre-commit-config.yaml` file
- Each project must have a Makefile with `pre-commit-install` target

---

## Project Structure

All scripts operate on these projects:
```
src/
├── dotfiles-installer/cli/          # Main CLI application
├── common/
│   ├── modules/                     # Shared Python modules
│   │   ├── colorscheme-generator/
│   │   ├── container-manager/
│   │   ├── filesystem-path-builder/
│   │   ├── logging/
│   │   ├── package-manager/
│   │   ├── pipeline/
│   │   ├── template-renderer/
│   │   └── wallpaper-processor/
│   └── tools/                       # Standalone CLI tools
│       ├── colorscheme-orchestrator/
│       ├── template-renderer/
│       └── wallpaper-orchestrator/
```

## Standard Configuration

All projects use:
- **Line length:** 79 characters
- **Python version:** 3.12+
- **Package manager:** uv
- **Formatters:** black, isort
- **Linter:** ruff (comprehensive rules: E, W, F, I, B, C4, UP, ARG, SIM, PTH, N)
- **Type checker:** mypy (strict mode)

## Adding New Projects

To add a new project to these scripts:

1. Edit the `PROJECTS` array in each script
2. Add the project path relative to repository root
3. Ensure the project has:
   - `pyproject.toml` with standard configuration
   - `Makefile` with standard targets
   - `.pre-commit-config.yaml` (for pre-commit hooks)

## Notes

- All scripts must be run from the repository root
- Scripts use colored output for better readability
- Each script exits on first error (`set -e`)
- Virtual environment warnings are expected and can be ignored
