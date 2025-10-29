# ✅ Setup Checklist

Use this checklist to verify your development environment is properly configured.

---

## Phase 1: VSCode Configuration ✅

- [ ] `.vscode/settings.json` exists
- [ ] `.vscode/extensions.json` exists
- [ ] `.vscode/launch.json` exists

**Status:** All files created ✅

---

## Phase 2: Install Extensions (5 min)

### Option A: VSCode Notification (Easiest)
- [ ] Open project in VSCode
- [ ] See notification "Install recommended extensions"
- [ ] Click "Install All"
- [ ] Wait for installation to complete

### Option B: Command Line
```bash
bash install-extensions.sh
```
- [ ] Script runs without errors
- [ ] All extensions installed

### Option C: Manual
```bash
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
```
- [ ] All extensions installed

**Verify:**
```bash
code --list-extensions | grep -E "python|black|isort|ruff|mypy"
```
- [ ] All 5 extensions listed

---

## Phase 3: Virtual Environment (3 min)

```bash
cd src/dotfiles-installer/cli
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

- [ ] `.venv/` directory created
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] No errors during installation

**Verify:**
```bash
which python
python --version
```
- [ ] Python path shows `.venv/bin/python`
- [ ] Version shows 3.12.x

---

## Phase 4: VSCode Reload (1 min)

- [ ] Press `Ctrl+Shift+P`
- [ ] Type "Reload Window"
- [ ] Press Enter
- [ ] VSCode reloads

---

## Phase 5: Verify Setup (5 min)

### Test 1: Format on Save
- [ ] Open `src/dotfiles-installer/cli/main.py`
- [ ] Add extra spaces: `x  =  1`
- [ ] Press `Ctrl+S`
- [ ] Spaces removed: `x = 1`
- [ ] ✅ Format on save works

### Test 2: Linting
- [ ] Open any Python file
- [ ] Add unused import: `import os`
- [ ] See red squiggle under `os`
- [ ] ✅ Linting works

### Test 3: Type Checking
- [ ] Open any Python file
- [ ] Add type error: `x: int = "string"`
- [ ] See yellow squiggle
- [ ] ✅ Type checking works

### Test 4: Makefile Commands
```bash
cd src/dotfiles-installer/cli
make format
make lint
make type-check
```
- [ ] `make format` passes
- [ ] `make lint` passes
- [ ] `make type-check` passes

---

## Phase 6: Debug Configuration (Optional)

- [ ] Press `F5` to open debug menu
- [ ] See 5 debug configurations:
  - [ ] Python: Current File
  - [ ] Python: CLI Install
  - [ ] Python: CLI Uninstall
  - [ ] Python: Tests
  - [ ] Python: Tests (Current File)

---

## Troubleshooting

### Extensions not showing?
```bash
code --list-extensions
```
- [ ] All 5 extensions listed
- [ ] If not, reinstall: `bash install-extensions.sh`

### Format on save not working?
- [ ] Check Python extension is installed
- [ ] Check `.venv` path in `.vscode/settings.json`
- [ ] Reload VSCode: `Ctrl+Shift+P` → "Reload Window"

### Type checking not working?
- [ ] Check mypy extension is installed
- [ ] Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
- [ ] Choose `.venv/bin/python`

### Linting not working?
- [ ] Check Ruff extension is installed
- [ ] Verify Ruff installed: `uv run ruff --version`
- [ ] Reload VSCode

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

- [ ] All versions shown
- [ ] No errors

---

## Ready to Code! 🚀

If all checkboxes are checked, your development environment is properly configured!

**Next:** Start coding and enjoy:
- ✅ Format on save
- ✅ Real-time linting
- ✅ Real-time type checking
- ✅ Debug configurations
- ✅ Consistent code style

---

## Quick Reference

| Action | Shortcut |
|--------|----------|
| Format code | Ctrl+S |
| Run tests | F5 → Python: Tests |
| Debug CLI | F5 → Python: CLI Install |
| Type check | Terminal: `uv run mypy .` |
| Lint | Terminal: `uv run ruff check .` |


