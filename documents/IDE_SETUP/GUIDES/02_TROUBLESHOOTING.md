# Troubleshooting Guide

Solutions for common issues.

---

## Extensions Not Showing

### Problem
VSCode doesn't show the "Install recommended extensions" notification.

### Solution

**Option 1: Check if extensions are installed**
```bash
code --list-extensions
```

**Option 2: Reinstall extensions**
```bash
bash install-extensions.sh
```

**Option 3: Manual installation**
```bash
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
```

**Option 4: Reload VSCode**
- Press `Ctrl+Shift+P`
- Type "Reload Window"
- Press Enter

---

## Format on Save Not Working

### Problem
Pressing Ctrl+S doesn't format the code.

### Checklist

- [ ] Python extension is installed
  ```bash
  code --list-extensions | grep ms-python.python
  ```

- [ ] `.venv` path is correct in `.vscode/settings.json`
  ```json
  "python.defaultInterpreterPath": "${workspaceFolder}/src/dotfiles-installer/cli/.venv/bin/python"
  ```

- [ ] Python interpreter is set to `.venv/bin/python`
  - Press `Ctrl+Shift+P`
  - Type "Python: Select Interpreter"
  - Choose `.venv/bin/python`

- [ ] VSCode is reloaded
  - Press `Ctrl+Shift+P`
  - Type "Reload Window"
  - Press Enter

### If Still Not Working

1. Check the VSCode output panel:
   - Press `Ctrl+Shift+U`
   - Look for error messages

2. Check Python extension logs:
   - Press `Ctrl+Shift+P`
   - Type "Developer: Show Logs"
   - Select "Python"

3. Verify Black is installed:
   ```bash
   cd src/dotfiles-installer/cli
   uv run black --version
   ```

---

## Type Checking Not Working

### Problem
mypy errors don't appear in the editor.

### Checklist

- [ ] mypy extension is installed
  ```bash
  code --list-extensions | grep mypy
  ```

- [ ] Python interpreter is set to `.venv/bin/python`
  - Press `Ctrl+Shift+P`
  - Type "Python: Select Interpreter"
  - Choose `.venv/bin/python`

- [ ] mypy is installed
  ```bash
  cd src/dotfiles-installer/cli
  uv run mypy --version
  ```

- [ ] VSCode is reloaded
  - Press `Ctrl+Shift+P`
  - Type "Reload Window"
  - Press Enter

### If Still Not Working

1. Check the VSCode output panel:
   - Press `Ctrl+Shift+U`
   - Look for error messages

2. Run mypy manually:
   ```bash
   cd src/dotfiles-installer/cli
   uv run mypy .
   ```

3. Check mypy extension settings:
   - Press `Ctrl+,` to open settings
   - Search for "mypy"
   - Verify settings are correct

---

## Linting Not Working

### Problem
Ruff errors don't appear in the editor.

### Checklist

- [ ] Ruff extension is installed
  ```bash
  code --list-extensions | grep ruff
  ```

- [ ] Ruff is installed
  ```bash
  cd src/dotfiles-installer/cli
  uv run ruff --version
  ```

- [ ] VSCode is reloaded
  - Press `Ctrl+Shift+P`
  - Type "Reload Window"
  - Press Enter

### If Still Not Working

1. Check the VSCode output panel:
   - Press `Ctrl+Shift+U`
   - Look for error messages

2. Run Ruff manually:
   ```bash
   cd src/dotfiles-installer/cli
   uv run ruff check .
   ```

3. Check Ruff extension settings:
   - Press `Ctrl+,` to open settings
   - Search for "ruff"
   - Verify settings are correct

---

## Virtual Environment Not Activated

### Problem
`which python` shows system Python instead of `.venv/bin/python`.

### Solution

```bash
cd src/dotfiles-installer/cli
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Verify

```bash
which python
python --version
```

Should show:
```
/path/to/project/src/dotfiles-installer/cli/.venv/bin/python
Python 3.12.x
```

---

## Dependencies Not Installed

### Problem
`uv run` fails with "module not found" errors.

### Solution

```bash
cd src/dotfiles-installer/cli
source .venv/bin/activate
uv sync
```

### Verify

```bash
uv run black --version
uv run isort --version
uv run ruff --version
uv run mypy --version
```

All should show version numbers.

---

## Python Version Mismatch

### Problem
`python --version` shows Python 3.11 or 3.10 instead of 3.12.

### Solution

1. Check available Python versions:
   ```bash
   python3.12 --version
   ```

2. Create virtual environment with Python 3.12:
   ```bash
   cd src/dotfiles-installer/cli
   python3.12 -m venv .venv
   source .venv/bin/activate
   uv sync
   ```

3. Update VSCode Python interpreter:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose `.venv/bin/python`

---

## Make Commands Fail

### Problem
`make format`, `make lint`, or `make type-check` fail.

### Solution

1. Activate virtual environment:
   ```bash
   cd src/dotfiles-installer/cli
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run make command:
   ```bash
   make format
   ```

### If Still Failing

1. Check the error message
2. Run the command manually:
   ```bash
   uv run black .
   uv run isort .
   uv run ruff check --fix .
   uv run mypy .
   ```

3. Check that all tools are installed:
   ```bash
   uv run black --version
   uv run isort --version
   uv run ruff --version
   uv run mypy --version
   ```

---

## VSCode Settings Not Applied

### Problem
Changes to `.vscode/settings.json` don't take effect.

### Solution

1. Reload VSCode:
   - Press `Ctrl+Shift+P`
   - Type "Reload Window"
   - Press Enter

2. Or restart VSCode completely:
   - Close VSCode
   - Open VSCode again

---

## Extensions Keep Disabling

### Problem
Extensions are disabled after VSCode restart.

### Solution

1. Check extension compatibility:
   - Open Extensions panel (Ctrl+Shift+X)
   - Look for warning icons
   - Check extension details

2. Reinstall extensions:
   ```bash
   bash install-extensions.sh
   ```

3. Check VSCode version:
   - Press `Ctrl+Shift+P`
   - Type "About"
   - Check VSCode version

---

## Still Having Issues?

### Debug Steps

1. **Check VSCode output panel**
   - Press `Ctrl+Shift+U`
   - Look for error messages

2. **Check extension logs**
   - Press `Ctrl+Shift+P`
   - Type "Developer: Show Logs"
   - Select each extension

3. **Run tools manually**
   ```bash
   cd src/dotfiles-installer/cli
   source .venv/bin/activate
   uv run black --version
   uv run isort --version
   uv run ruff --version
   uv run mypy --version
   ```

4. **Check configuration files**
   - Verify `.vscode/settings.json` exists
   - Verify `pyproject.toml` exists
   - Verify `.venv` directory exists

5. **Restart everything**
   - Close VSCode
   - Deactivate virtual environment: `deactivate`
   - Reopen VSCode
   - Activate virtual environment: `source .venv/bin/activate`

---

## UV Sync and Module Installation Issues

### Problem: Module Changes Not Reflected After `uv sync`

**Symptoms:**
- You make changes to a local module (e.g., `filesystem-path-builder`)
- Changes work when you run `make sync-all-modules`
- But after running `make dev-shell` or `uv sync`, changes disappear
- You get errors like `TypeError: __init__() got an unexpected keyword argument 'strict'`

**Root Cause:**

The module is installed in **non-editable mode**. When `uv sync` runs, it reinstalls the module by copying files instead of symlinking, overwriting your editable install.

**Diagnosis:**

Check if modules are installed in editable mode:

```bash
cd src/dotfiles-installer/cli
cat .venv/lib/python3.12/site-packages/filesystem_path_builder-*.dist-info/direct_url.json
```

Look for `"editable":true`. If you see `"editable":false`, the module is not editable.

**Solution:**

1. **Add `editable = true` to `pyproject.toml`:**

   ```toml
   [tool.uv.sources]
   filesystem-path-builder = { path = "../../common/modules/filesystem-path-builder", editable = true }
   dotfiles-logging = { path = "../../common/modules/logging", editable = true }
   # ... add for all local modules
   ```

2. **Update lockfile and sync:**

   ```bash
   cd src/dotfiles-installer/cli
   uv lock
   uv sync
   ```

3. **Verify editable install:**

   ```bash
   cat .venv/lib/python3.12/site-packages/filesystem_path_builder-*.dist-info/direct_url.json
   # Should show: "editable":true
   ```

**Prevention:**

Always use `editable = true` in `[tool.uv.sources]` for local path dependencies.

---

### Problem: `make sync-all-modules` Doesn't Create Editable Install

**Symptoms:**
- Running `make sync-all-modules` appears to work
- But changes to module source code aren't reflected
- `direct_url.json` shows `"editable":false`

**Root Cause:**

The Makefile was using `uv pip install -e ... --force-reinstall`, which creates non-editable installs in UV.

**Solution:**

The Makefile has been updated to uninstall before installing:

```makefile
sync-module:
	@cd $(CLI_DIR) && uv pip uninstall -y $(MODULE) 2>/dev/null || true
	@cd $(CLI_DIR) && uv pip install -e ../../common/modules/$(MODULE) --no-deps
	@cd $(CLI_DIR) && uv lock
```

If you have an old Makefile, update it or run manually:

```bash
cd src/dotfiles-installer/cli
uv pip uninstall -y filesystem-path-builder
uv pip install -e ../../common/modules/filesystem-path-builder --no-deps
uv lock
```

---

### Problem: Python Bytecode Cache Causing Stale Code

**Symptoms:**
- Module is installed in editable mode
- But changes still don't appear
- Restarting Python doesn't help

**Root Cause:**

Python's bytecode cache (`__pycache__` directories and `.pyc` files) contains compiled versions of old code.

**Solution:**

Clean the bytecode cache:

```bash
# From project root
make clean-cache

# Or manually
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

Then restart your Python process or VSCode.

---

### Problem: Lockfile Out of Sync with Installed Packages

**Symptoms:**
- `make dev-shell` fails with "Lock file newer than venv - sync needed"
- Or `uv sync` keeps reinstalling packages

**Root Cause:**

The lockfile (`uv.lock`) doesn't match the installed packages in `.venv`.

**Solution:**

1. **Update lockfile after syncing modules:**

   ```bash
   make sync-all-modules  # This now updates lockfile automatically
   ```

2. **Or manually sync:**

   ```bash
   cd src/dotfiles-installer/cli
   uv lock
   uv sync
   ```

3. **For persistent issues, rebuild venv:**

   ```bash
   cd src/dotfiles-installer/cli
   rm -rf .venv
   python3.12 -m venv .venv
   source .venv/bin/activate
   uv sync
   ```

---

### Problem: `--force-reinstall` Flag Breaks Editable Installs

**Symptoms:**
- Using `uv pip install -e ... --force-reinstall` creates non-editable install
- Even though `-e` flag is present

**Root Cause:**

UV's `--force-reinstall` flag causes packages to be copied instead of symlinked.

**Solution:**

Never use `--force-reinstall` with editable installs. Instead:

```bash
# Wrong
uv pip install -e . --force-reinstall --no-deps

# Correct
uv pip uninstall -y package-name
uv pip install -e . --no-deps
```

---

### Quick Reference: Editable Install Workflow

**Initial Setup:**
```bash
cd src/dotfiles-installer/cli
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

**After Modifying a Module:**
```bash
# From project root
make sync-all-modules
make dev-shell
```

**Verify Editable Install:**
```bash
cd src/dotfiles-installer/cli
cat .venv/lib/python3.12/site-packages/MODULE_NAME-*.dist-info/direct_url.json
# Should show: "editable":true
```

**Clean Everything:**
```bash
make clean-cache
cd src/dotfiles-installer/cli
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

---

## Next Steps

1. Read `03_DEVELOPMENT_WORKFLOW.md` for how to use
2. Read `../REFERENCE/03_FAQ.md` for frequently asked questions
3. Contact the team if issues persist
