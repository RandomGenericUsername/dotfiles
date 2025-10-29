# ⚡ Quick Start (5 minutes)

Get your development environment running in 5 minutes.

---

## Step 1: Install Extensions (1 min)

When you open this project in VSCode, you'll see a notification:
- Click **"Install All"** to install recommended extensions
- Or run: `bash install-extensions.sh`

**Extensions installed:**
- Python (ms-python.python)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)
- Ruff (charliermarsh.ruff)
- mypy Type Checker (ms-python.mypy-type-checker)

---

## Step 2: Create Virtual Environment (2 min)

```bash
cd src/dotfiles-installer/cli
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

**Verify:**
```bash
which python
python --version
```

Should show: `.venv/bin/python` and `Python 3.12.x`

---

## Step 3: Reload VSCode (1 min)

- Press `Ctrl+Shift+P`
- Type "Reload Window"
- Press Enter

---

## Step 4: Verify Setup (1 min)

### Test Format on Save
1. Open any Python file
2. Add extra spaces: `x  =  1`
3. Press `Ctrl+S`
4. Spaces removed: `x = 1` ✅

### Test Linting
1. Add unused import: `import os`
2. See red squiggle under `os` ✅

### Test Type Checking
1. Add type error: `x: int = "string"`
2. See yellow squiggle ✅

---

## Common Commands

| Action | Shortcut | Command |
|--------|----------|---------|
| Format code | Ctrl+S | Format on save |
| Run tests | F5 | Debug → Python: Tests |
| Debug CLI | F5 | Debug → Python: CLI Install |
| Type check | Terminal | `uv run mypy .` |
| Lint | Terminal | `uv run ruff check .` |

---

## Troubleshooting

### Extensions not showing?
```bash
code --list-extensions
```

### Format on save not working?
1. Check Python extension is installed
2. Verify `.venv` path in `.vscode/settings.json`
3. Reload VSCode

### Type checking not working?
1. Check mypy extension is installed
2. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose `.venv/bin/python`

---

## What's Configured

✅ **Black** - 79 char lines, format on save
✅ **isort** - Import sorting on save
✅ **Ruff** - Real-time linting
✅ **mypy** - Real-time type checking
✅ **Python** - 3.12 from .venv

---

## Next Steps

1. ✅ Complete steps 1-4 above
2. 📋 Use `02_SETUP_CHECKLIST.md` to verify everything
3. 📖 Read `../GUIDES/01_SETUP_GUIDE.md` for detailed setup
4. 🚀 Start coding!

---

**All set? Continue to `02_SETUP_CHECKLIST.md`** ✅


