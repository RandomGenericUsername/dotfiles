# Development Scripts

This directory contains utility scripts for development workflows across all UV Python projects in the repository.

## 🎯 Development Workflow

This monorepo uses a **decentralized approach** with **centralized enforcement**:

- **Configuration**: Each project's `pyproject.toml` is the single source of truth for tool settings
- **Local Development**: Use `make` commands in each project for manual checks
- **Automatic Enforcement**: Root `.pre-commit-config.yaml` runs project-specific `make` targets on commit
- **Bulk Operations**: Scripts in this directory for running checks across all projects

### Quick Start

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Work on a project
cd src/common/modules/logging
# Edit files...

# Run checks manually (optional - pre-commit will run them automatically)
make format      # Format code
make lint        # Lint code
make type-check  # Type check
make all-checks  # Run all checks

# Commit from anywhere (root or subdirectory)
git add .
git commit -m "Update logging"
# Pre-commit automatically runs format + lint for changed projects only!
```

---

## Available Scripts

### `format-all.sh`
Formats and lints all UV Python projects in the repository.

**What it does:**
- Runs `make format` in each project (black + isort)
- Runs `make lint` in each project (ruff)
- Reports success/failure for each project

**Usage:**
```bash
./dev/scripts/format-all.sh
```

**When to use:**
- Before committing large changes across multiple projects
- To fix formatting issues in bulk
- After updating tool configurations

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
./dev/scripts/lint-all.sh
```

**Note:** This is more aggressive than `format-all.sh` as it applies unsafe fixes.

**When to use:**
- When you want aggressive auto-fixing
- After major refactoring
- To clean up code before a release

---

### `install-hooks.sh`
**DEPRECATED**: This script is no longer needed with the new setup.

The root `.pre-commit-config.yaml` now uses local hooks that call `make` targets.
Simply run `pre-commit install` from the repository root.

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
│   │   └── wallpaper-effects-processor/
│   └── tools/                       # Standalone CLI tools
│       ├── colorscheme-orchestrator/
│       ├── template-renderer/
│       └── wallpaper-effects-orchestrator/
```

## Standard Configuration

All projects use:
- **Line length:** 79 characters
- **Python version:** 3.12+
- **Package manager:** uv
- **Formatters:** black, isort
- **Linter:** ruff (comprehensive rules: E, W, F, I, B, C4, UP, ARG, SIM, PTH, N)
- **Type checker:** mypy (strict mode)

**Configuration location:** Each project's `pyproject.toml` contains all tool settings.

## How Pre-Commit Works

The root `.pre-commit-config.yaml` uses **local hooks** that call `make` targets:

```yaml
- repo: local
  hooks:
    - id: format-logging
      name: Format logging (black + isort)
      entry: bash -c 'cd src/common/modules/logging && make format'
      language: system
      files: ^src/common/modules/logging/
      pass_filenames: false
```

**What this means:**
1. You commit from anywhere (root or subdirectory)
2. Pre-commit detects which files changed
3. For each changed project, it runs that project's `make format` and `make lint`
4. Only the projects you actually modified get checked (fast!)
5. All configuration comes from `pyproject.toml` (single source of truth)

## Adding New Projects

To add a new project:

1. **Create the project** with standard structure:
   - `pyproject.toml` with tool configurations (black, isort, ruff, mypy)
   - `Makefile` with standard targets (format, lint, type-check, test, all-checks)
   - `src/` directory with code
   - `tests/` directory with tests

2. **Add to root `.pre-commit-config.yaml`**:
   ```yaml
   - id: format-my-new-project
     name: Format my-new-project (black + isort)
     entry: bash -c 'cd src/path/to/my-new-project && make format'
     language: system
     files: ^src/path/to/my-new-project/
     pass_filenames: false

   - id: lint-my-new-project
     name: Lint my-new-project (ruff)
     entry: bash -c 'cd src/path/to/my-new-project && make lint'
     language: system
     files: ^src/path/to/my-new-project/
     pass_filenames: false
   ```

3. **Add to bulk scripts** (`format-all.sh`, `lint-all.sh`):
   - Add project path to the `PROJECTS` array

4. **Test it**:
   ```bash
   # Make a change in the new project
   echo "# test" >> src/path/to/my-new-project/README.md

   # Try to commit
   git add .
   git commit -m "Test pre-commit"

   # Should see your project's format + lint hooks run!
   ```

## Notes

- All scripts must be run from the repository root
- Scripts use colored output for better readability
- Each script exits on first error (`set -e`)
- Virtual environment warnings are expected and can be ignored
- Pre-commit hooks only run on **staged files** (files you `git add`)
- To run pre-commit manually: `pre-commit run --all-files`
