# Settings Alignment Reference

This document shows how VSCode settings map to your `pyproject.toml` configuration.

---

## Black Formatter Alignment

### pyproject.toml
```toml
[tool.black]
line-length = 79
target-version = ['py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''
```

### .vscode/settings.json
```json
"python.formatting.blackArgs": [
  "--line-length=79",
  "--target-version=py312"
],
"[python]": {
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.formatOnSave": true
}
```

✅ **Status**: Perfectly aligned

---

## isort Alignment

### pyproject.toml
```toml
[tool.isort]
profile = "black"
line_length = 79
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### .vscode/settings.json
```json
"isort.args": [
  "--profile=black",
  "--line-length=79",
  "--multi-line-mode=3",
  "--trailing-comma",
  "--use-parentheses",
  "--ensure-newline-before-comments"
]
```

✅ **Status**: Perfectly aligned

---

## Ruff Alignment

### pyproject.toml
```toml
[tool.ruff]
line-length = 79
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "ARG", # flake8-unused-arguments
    "SIM", # flake8-simplify
    "PTH", # flake8-use-pathlib
]
ignore = [
    "E501", # line too long, handled by black
    "B008", # do not perform function calls in argument defaults
    "C901", # too complex
    "W191", # indentation contains tabs
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
```

### .vscode/settings.json
```json
"ruff.lineLength": 79,
"ruff.targetVersion": "py312",
"ruff.lint.select": [
  "E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH"
],
"ruff.lint.ignore": [
  "E501", "B008", "C901", "W191"
],
"[python]": {
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  }
}
```

✅ **Status**: Perfectly aligned (per-file ignores handled by Ruff automatically)

---

## mypy Alignment

### pyproject.toml
```toml
[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_equality = true
show_error_codes = true

[[tool.mypy.overrides]]
module = ["dynaconf.*", "shellingham.*"]
ignore_missing_imports = true
```

### .vscode/settings.json
```json
"mypy-type-checker.args": [
  "--python-version=3.12",
  "--check-untyped-defs",
  "--disallow-any-generics",
  "--disallow-incomplete-defs",
  "--disallow-untyped-defs",
  "--no-implicit-optional",
  "--warn-redundant-casts",
  "--warn-unused-ignores",
  "--warn-return-any",
  "--strict-equality",
  "--show-error-codes"
],
"mypy-type-checker.runUsingActiveInterpreter": true
```

✅ **Status**: Perfectly aligned (module overrides handled by mypy.ini or pyproject.toml)

---

## Python Version Alignment

### pyproject.toml
```toml
requires-python = ">=3.12"
```

### .vscode/settings.json
```json
"python.defaultInterpreterPath": "${workspaceFolder}/src/dotfiles-installer/cli/.venv/bin/python"
```

✅ **Status**: Aligned (VSCode will use Python 3.12 from .venv)

---

## Editor Preferences Alignment

### .vscode/settings.json
```json
"editor.rulers": [79],           // Visual guide at 79 chars
"editor.wordWrap": "off",        // Don't auto-wrap
"editor.insertSpaces": true,     // Use spaces, not tabs
"editor.tabSize": 4,             // 4 spaces per indent
"files.trimTrailingWhitespace": true,
"files.insertFinalNewline": true
```

These match Python conventions and your tool configurations.

---

## Format on Save Configuration

### .vscode/settings.json
```json
"[python]": {
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  }
}
```

This ensures:
- ✅ Code is formatted on save
- ✅ Imports are organized on save
- ✅ Linting issues are auto-fixed on save

---

## Makefile Commands Alignment

Your Makefile commands now have IDE equivalents:

| Makefile | VSCode | Trigger |
|----------|--------|---------|
| `make format` | Format on save | Ctrl+S |
| `make lint` | Ruff linting | Real-time |
| `make type-check` | mypy checking | Real-time |
| `make test` | Debug config | F5 |

---

## Verification Checklist

After setup, verify each tool works:

- [ ] Black formats code on save (Ctrl+S)
- [ ] isort organizes imports on save
- [ ] Ruff shows linting errors in real-time
- [ ] mypy shows type errors in real-time
- [ ] `make format` passes without changes
- [ ] `make lint` passes without changes
- [ ] `make type-check` passes without changes
- [ ] Debug configurations work (F5)

---

## Updating Settings

If you change `pyproject.toml`, update the corresponding VSCode settings:

1. Update `pyproject.toml`
2. Update `.vscode/settings.json` to match
3. Restart VSCode or reload window (Ctrl+Shift+P → "Reload Window")
4. Verify with `make format lint type-check`

---

## Next Steps

1. Read `02_TOOL_CONFIGURATION.md` for detailed tool explanations
2. Read `03_VSCODE_REFERENCE.md` for VSCode settings reference
3. Read `../GUIDES/01_SETUP_GUIDE.md` for setup instructions
