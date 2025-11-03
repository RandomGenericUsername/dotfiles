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

## Next Steps

1. Read `03_DEVELOPMENT_WORKFLOW.md` for how to use
2. Read `../REFERENCE/03_FAQ.md` for frequently asked questions
3. Contact the team if issues persist
