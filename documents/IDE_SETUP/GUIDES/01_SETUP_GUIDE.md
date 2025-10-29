# Detailed Setup Guide

Complete step-by-step setup instructions.

---

## Prerequisites

- VSCode installed
- Python 3.12 installed
- Git installed
- Project cloned

---

## Step 1: Install VSCode Extensions (5 minutes)

### Option A: Automatic Installation (Recommended)

1. Open the project in VSCode
2. You'll see a notification: "Install recommended extensions"
3. Click "Install All"
4. Wait for installation to complete

### Option B: Manual Installation via Script

```bash
bash install-extensions.sh
```

This script installs all required extensions automatically.

### Option C: Manual Installation via Command Line

```bash
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
```

### Verify Installation

```bash
code --list-extensions | grep -E "python|black|isort|ruff|mypy"
```

You should see:
```
charliermarsh.ruff
ms-python.black-formatter
ms-python.isort
ms-python.mypy-type-checker
ms-python.python
```

---

## Step 2: Create Virtual Environment (5 minutes)

### Navigate to Project Directory

```bash
cd src/dotfiles-installer/cli
```

### Create Virtual Environment

```bash
python3.12 -m venv .venv
```

This creates a `.venv` directory with Python 3.12.

### Activate Virtual Environment

```bash
# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Install Dependencies

```bash
uv sync
```

This installs all project dependencies using `uv`.

### Verify Installation

```bash
which python
python --version
```

You should see:
```
/path/to/project/src/dotfiles-installer/cli/.venv/bin/python
Python 3.12.x
```

---

## Step 3: Configure VSCode (2 minutes)

### Verify Settings Files Exist

Check that these files exist in `.vscode/`:
- `settings.json` ✅
- `extensions.json` ✅
- `launch.json` ✅

### Reload VSCode

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type "Reload Window"
3. Press Enter

VSCode will reload and apply the settings.

---

## Step 4: Verify Setup (5 minutes)

### Test 1: Format on Save

1. Open `src/dotfiles-installer/cli/main.py`
2. Add extra spaces: `x  =  1`
3. Press `Ctrl+S` to save
4. Spaces should be removed: `x = 1`

✅ **Format on save works!**

### Test 2: Linting

1. Open any Python file
2. Add unused import: `import os`
3. You should see a red squiggle under `os`
4. Hover over it to see the error

✅ **Linting works!**

### Test 3: Type Checking

1. Open any Python file
2. Add type error: `x: int = "string"`
3. You should see a yellow squiggle
4. Hover over it to see the error

✅ **Type checking works!**

### Test 4: Makefile Commands

```bash
cd src/dotfiles-installer/cli
make format
make lint
make type-check
```

All commands should pass without errors.

✅ **All checks pass!**

---

## Step 5: Configure Python Interpreter (Optional)

If VSCode doesn't automatically detect the Python interpreter:

1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose `.venv/bin/python`

---

## Step 6: Test Debug Configuration (Optional)

1. Press `F5` to open the debug menu
2. You should see 5 debug configurations:
   - Python: Current File
   - Python: CLI Install
   - Python: CLI Uninstall
   - Python: Tests
   - Python: Tests (Current File)

3. Select "Python: Tests"
4. Press Enter to run tests

✅ **Debug configuration works!**

---

## Troubleshooting

### Extensions Not Showing?

```bash
code --list-extensions
```

If extensions are missing, reinstall:
```bash
bash install-extensions.sh
```

### Format on Save Not Working?

1. Check Python extension is installed
2. Verify `.venv` path in `.vscode/settings.json`
3. Reload VSCode: `Ctrl+Shift+P` → "Reload Window"
4. Check that Python interpreter is set to `.venv/bin/python`

### Type Checking Not Working?

1. Check mypy extension is installed
2. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose `.venv/bin/python`
4. Reload VSCode

### Linting Not Working?

1. Check Ruff extension is installed
2. Verify Ruff is installed: `uv run ruff --version`
3. Reload VSCode

---

## Final Verification

Run this command to verify everything:

```bash
cd src/dotfiles-installer/cli
echo "=== Python Version ===" && python --version
echo "=== Black ===" && uv run black --version
echo "=== isort ===" && uv run isort --version
echo "=== Ruff ===" && uv run ruff --version
echo "=== mypy ===" && uv run mypy --version
echo "=== All tools ready! ===" 
```

Expected output:
```
=== Python Version ===
Python 3.12.x

=== Black ===
black, 24.x.x

=== isort ===
isort 5.x.x

=== Ruff ===
ruff 0.x.x

=== mypy ===
mypy 1.x.x

=== All tools ready! ===
```

---

## You're All Set! 🎉

Your development environment is now properly configured!

**Next Steps:**
1. Read `02_TROUBLESHOOTING.md` for common issues
2. Read `03_DEVELOPMENT_WORKFLOW.md` for how to use
3. Start coding!


