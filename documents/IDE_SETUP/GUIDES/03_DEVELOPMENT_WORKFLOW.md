# Development Workflow

How to use the IDE setup in your daily development.

---

## Daily Workflow

### 1. Start Your Day

```bash
cd src/dotfiles-installer/cli
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### 2. Open VSCode

```bash
code .
```

Or open VSCode and navigate to the project.

### 3. Write Code

Open a Python file and start coding.

### 4. Format on Save

Press `Ctrl+S` to save and format:
- Black formats code to 79 characters
- isort organizes imports
- Ruff auto-fixes linting issues

### 5. Check for Errors

As you type, you'll see:
- Red squiggles for linting errors (Ruff)
- Yellow squiggles for type errors (mypy)

### 6. Run Tests

Press `F5` and select "Python: Tests" to run tests.

### 7. Commit Code

```bash
git add .
git commit -m "Your commit message"
```

Code is already formatted and passes checks!

---

## Common Tasks

### Format Code

**Option 1: Format on Save (Recommended)**
- Press `Ctrl+S`
- Code is formatted automatically

**Option 2: Format All Files**
```bash
make format
```

**Option 3: Format Specific File**
```bash
uv run black src/your_file.py
```

---

### Check for Linting Errors

**Option 1: Real-time in Editor**
- Open a Python file
- See red squiggles for errors
- Hover to see error details

**Option 2: Check All Files**
```bash
make lint
```

**Option 3: Auto-fix Errors**
```bash
make lint
# or
uv run ruff check --fix .
```

---

### Check Types

**Option 1: Real-time in Editor**
- Open a Python file
- See yellow squiggles for type errors
- Hover to see error details

**Option 2: Check All Files**
```bash
make type-check
```

**Option 3: Check Specific File**
```bash
uv run mypy src/your_file.py
```

---

### Run Tests

**Option 1: Debug Configuration (Recommended)**
- Press `F5`
- Select "Python: Tests"
- Tests run in debug mode

**Option 2: Command Line**
```bash
make test
```

**Option 3: Run Specific Test**
```bash
uv run pytest tests/test_specific.py -v
```

---

### Debug Code

**Option 1: Debug Current File**
- Press `F5`
- Select "Python: Current File"
- Code runs in debug mode

**Option 2: Debug CLI Command**
- Press `F5`
- Select "Python: CLI Install"
- CLI runs in debug mode

**Option 3: Set Breakpoints**
- Click on line number to set breakpoint
- Press `F5` to run
- Execution stops at breakpoint

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Format code | Ctrl+S |
| Run/Debug | F5 |
| Open command palette | Ctrl+Shift+P |
| Open terminal | Ctrl+` |
| Select Python interpreter | Ctrl+Shift+P → "Python: Select Interpreter" |
| Reload window | Ctrl+Shift+P → "Reload Window" |
| Show problems | Ctrl+Shift+M |
| Go to definition | F12 |
| Find references | Shift+F12 |
| Rename symbol | F2 |

---

## Before Committing

### Checklist

- [ ] Code is formatted (Ctrl+S)
- [ ] No linting errors (red squiggles gone)
- [ ] No type errors (yellow squiggles gone)
- [ ] Tests pass (F5 → Python: Tests)
- [ ] `make format` passes
- [ ] `make lint` passes
- [ ] `make type-check` passes

### Run All Checks

```bash
cd src/dotfiles-installer/cli
make format
make lint
make type-check
make test
```

All should pass without errors.

---

## Debugging Tips

### Add Print Statements

```python
def my_function(x):
    print(f"x = {x}")  # Debug print
    return x * 2
```

### Use Breakpoints

1. Click on line number to set breakpoint
2. Press `F5` to run
3. Execution stops at breakpoint
4. Use debug panel to inspect variables

### Use Python Debugger

```python
import pdb; pdb.set_trace()  # Breakpoint
```

### Use Type Hints

```python
def add(x: int, y: int) -> int:
    return x + y
```

mypy will catch type errors.

---

## Performance Tips

### Format on Save is Slow

If format on save is slow:

1. Check if `.venv` is on a slow disk
2. Move project to faster disk
3. Or disable format on save and use `make format` instead

### Linting is Slow

If linting is slow:

1. Check if `.venv` is on a slow disk
2. Move project to faster disk
3. Or run `make lint` manually instead of real-time

### Type Checking is Slow

If type checking is slow:

1. Check if `.venv` is on a slow disk
2. Move project to faster disk
3. Or run `make type-check` manually instead of real-time

---

## Customization

### Change Line Length

To change from 79 to 88 characters:

1. Update `pyproject.toml`:
   ```toml
   [tool.black]
   line-length = 88
   ```

2. Update `.vscode/settings.json`:
   ```json
   "python.formatting.blackArgs": [
     "--line-length=88"
   ]
   ```

3. Reload VSCode

### Add New Linting Rules

To add new Ruff rules:

1. Update `pyproject.toml`:
   ```toml
   [tool.ruff.lint]
   select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH", "NEW_RULE"]
   ```

2. Update `.vscode/settings.json`:
   ```json
   "ruff.lint.select": ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH", "NEW_RULE"]
   ```

3. Reload VSCode

### Disable Format on Save

If you want to disable format on save:

1. Open `.vscode/settings.json`
2. Change:
   ```json
   "editor.formatOnSave": false
   ```
3. Reload VSCode

---

## Team Collaboration

### Sharing Settings

All settings are in `.vscode/` and `pyproject.toml`:
- Commit these files to git
- All team members get same settings
- No configuration drift

### Onboarding New Developers

1. Clone project
2. Run `bash install-extensions.sh`
3. Create virtual environment
4. Reload VSCode
5. Done! ✅

### Code Review

When reviewing code:
- Check that code is formatted (79 chars)
- Check that linting passes
- Check that types are correct
- Use debug configuration to test

---

## Next Steps

1. Read `../REFERENCE/03_FAQ.md` for frequently asked questions
2. Read `../REFERENCE/01_DELIVERABLES.md` for complete reference
3. Start coding!
