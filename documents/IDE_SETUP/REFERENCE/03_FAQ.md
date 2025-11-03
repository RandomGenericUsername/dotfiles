# Frequently Asked Questions (FAQ)

Common questions and answers about the IDE setup.

---

## General Questions

### Q: Do I really need VSCode settings?

**A:** Yes! Without VSCode settings:
- IDE uses default settings (88 chars instead of 79)
- Code looks good in editor but fails CI checks
- Manual fixes required
- Frustration and inconsistency

With VSCode settings:
- IDE matches project rules exactly
- Format on save works correctly
- Code passes checks immediately
- Smooth, productive workflow

---

### Q: Can I use a different IDE?

**A:** Yes, but you'll need to configure it yourself:
- **PyCharm**: Configure Black, isort, Ruff, mypy in settings
- **Vim/Neovim**: Configure with plugins
- **Emacs**: Configure with packages
- **Sublime**: Configure with packages

The configuration rules are in `pyproject.toml` and can be applied to any IDE.

---

### Q: Can I change the line length from 79 to 88?

**A:** Yes, but you need to update both files:

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

---

### Q: Can I disable format on save?

**A:** Yes, edit `.vscode/settings.json`:

```json
"[python]": {
  "editor.formatOnSave": false
}
```

Then reload VSCode.

---

## Setup Questions

### Q: How long does setup take?

**A:** About 7 minutes:
- Install extensions: 2 minutes
- Create virtual environment: 3 minutes
- Reload VSCode: 1 minute
- Test setup: 1 minute

---

### Q: What if I already have a virtual environment?

**A:** You can reuse it:

```bash
cd src/dotfiles-installer/cli
source .venv/bin/activate
uv sync
```

Or create a new one:

```bash
cd src/dotfiles-installer/cli
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

---

### Q: What if I don't have Python 3.12?

**A:** Install it first:

```bash
# On Ubuntu/Debian
sudo apt install python3.12

# On macOS
brew install python@3.12

# On Arch
sudo pacman -S python
```

Then create virtual environment:

```bash
python3.12 -m venv .venv
```

---

### Q: Can I use a different Python version?

**A:** Not recommended. The project requires Python 3.12+.

If you must use a different version:

1. Update `pyproject.toml`:
   ```toml
   requires-python = ">=3.11"
   ```

2. Update `.vscode/settings.json`:
   ```json
   "mypy-type-checker.args": [
     "--python-version=3.11"
   ]
   ```

3. Update `pyproject.toml` mypy config:
   ```toml
   [tool.mypy]
   python_version = "3.11"
   ```

---

## Configuration Questions

### Q: What do the linting rules mean?

**A:** See `CONFIGURATION/02_TOOL_CONFIGURATION.md` for detailed explanations.

Quick summary:
- **E**: PEP 8 errors
- **W**: PEP 8 warnings
- **F**: Logical errors
- **I**: Import sorting
- **B**: Common bugs
- **C4**: Comprehensions
- **UP**: Python upgrades
- **ARG**: Unused arguments
- **SIM**: Code simplification
- **PTH**: Use pathlib

---

### Q: Can I add more linting rules?

**A:** Yes, update both files:

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

---

### Q: Can I disable specific linting rules?

**A:** Yes, add to ignore list:

1. Update `pyproject.toml`:
   ```toml
   [tool.ruff.lint]
   ignore = ["E501", "B008", "C901", "W191", "RULE_TO_IGNORE"]
   ```

2. Update `.vscode/settings.json`:
   ```json
   "ruff.lint.ignore": ["E501", "B008", "C901", "W191", "RULE_TO_IGNORE"]
   ```

3. Reload VSCode

---

## Development Questions

### Q: How do I format code?

**A:** Press `Ctrl+S` to save and format automatically.

Or run:
```bash
make format
```

---

### Q: How do I check for errors?

**A:** Errors appear as squiggles in the editor:
- Red squiggles: Linting errors (Ruff)
- Yellow squiggles: Type errors (mypy)

Or run:
```bash
make lint
make type-check
```

---

### Q: How do I run tests?

**A:** Press `F5` and select "Python: Tests".

Or run:
```bash
make test
```

---

### Q: How do I debug code?

**A:** Press `F5` and select a debug configuration:
- Python: Current File
- Python: CLI Install
- Python: CLI Uninstall
- Python: Tests
- Python: Tests (Current File)

---

### Q: How do I set breakpoints?

**A:** Click on the line number to set a breakpoint, then press `F5` to run.

---

## Troubleshooting Questions

### Q: Format on save doesn't work. What do I do?

**A:** See `GUIDES/02_TROUBLESHOOTING.md` → "Format on Save Not Working"

Quick checklist:
- [ ] Python extension installed
- [ ] `.venv` path correct in settings.json
- [ ] Python interpreter set to `.venv/bin/python`
- [ ] VSCode reloaded

---

### Q: Type checking doesn't work. What do I do?

**A:** See `GUIDES/02_TROUBLESHOOTING.md` → "Type Checking Not Working"

Quick checklist:
- [ ] mypy extension installed
- [ ] Python interpreter set to `.venv/bin/python`
- [ ] mypy installed: `uv run mypy --version`
- [ ] VSCode reloaded

---

### Q: Linting doesn't work. What do I do?

**A:** See `GUIDES/02_TROUBLESHOOTING.md` → "Linting Not Working"

Quick checklist:
- [ ] Ruff extension installed
- [ ] Ruff installed: `uv run ruff --version`
- [ ] VSCode reloaded

---

### Q: Extensions keep disabling. What do I do?

**A:** See `GUIDES/02_TROUBLESHOOTING.md` → "Extensions Keep Disabling"

Quick fix:
```bash
bash install-extensions.sh
```

---

## Team Questions

### Q: How do I share settings with my team?

**A:** All settings are in version control:
- `.vscode/settings.json`
- `.vscode/extensions.json`
- `.vscode/launch.json`
- `pyproject.toml`

Commit these files to git. All team members get same settings.

---

### Q: How do I onboard new developers?

**A:** They just need to:

1. Clone project
2. Run `bash install-extensions.sh`
3. Create virtual environment
4. Reload VSCode
5. Done! ✅

---

### Q: What if a developer uses a different IDE?

**A:** They can configure their IDE using `pyproject.toml`:
- Black: 79 chars, py312
- isort: black profile, 79 chars
- Ruff: 79 chars, 10 rules
- mypy: strict mode, py312

---

## Performance Questions

### Q: Format on save is slow. What do I do?

**A:** Options:
1. Check if `.venv` is on a slow disk
2. Move project to faster disk
3. Disable format on save and use `make format` instead

---

### Q: Linting is slow. What do I do?

**A:** Options:
1. Check if `.venv` is on a slow disk
2. Move project to faster disk
3. Run `make lint` manually instead of real-time

---

### Q: Type checking is slow. What do I do?

**A:** Options:
1. Check if `.venv` is on a slow disk
2. Move project to faster disk
3. Run `make type-check` manually instead of real-time

---

## Still Have Questions?

### Resources

1. **Setup Guide**: `GUIDES/01_SETUP_GUIDE.md`
2. **Troubleshooting**: `GUIDES/02_TROUBLESHOOTING.md`
3. **Configuration**: `CONFIGURATION/01_SETTINGS_ALIGNMENT.md`
4. **Workflow**: `GUIDES/03_DEVELOPMENT_WORKFLOW.md`

### Contact

If you still have questions, contact the team or create an issue.

---

## Next Steps

1. Read `01_DELIVERABLES.md` for complete reference
2. Read `02_FILE_STRUCTURE.md` for file organization
3. Start coding!
