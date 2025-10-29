# Quick Start Guide

Get your development environment running in 5 minutes.

## Step 1: Install Extensions (1 min)

When you open this project in VSCode, you'll see a notification:
- Click **"Install All"** to install recommended extensions
- Or run: `bash install-extensions.sh`

## Step 2: Create Virtual Environment (2 min)

```bash
cd src/dotfiles-installer/cli
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

## Step 3: Reload VSCode (1 min)

- Press `Ctrl+Shift+P`
- Type "Reload Window"
- Press Enter

## Step 4: Verify Setup (1 min)

Open any Python file and check:
- ✅ Format on save works (Ctrl+S)
- ✅ Linting errors appear in red squiggles
- ✅ Type errors appear in yellow squiggles

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
2. Verify `.venv` path in settings.json
3. Reload VSCode

### Type checking not working?
1. Ensure mypy extension is installed
2. Check Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
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

1. Read `.vscode/README.md` for detailed setup
2. Read `SETTINGS_ALIGNMENT_REFERENCE.md` to understand configuration
3. Start coding! 🚀


