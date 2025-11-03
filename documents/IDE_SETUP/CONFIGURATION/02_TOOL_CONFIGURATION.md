# Tool Configuration Guide

Detailed explanation of each tool's configuration.

---

## Black Formatter

### What It Does
Automatically formats Python code to be consistent and readable.

### Configuration
```json
"python.formatting.blackArgs": [
  "--line-length=79",
  "--target-version=py312"
]
```

### Key Settings
- **Line Length**: 79 characters (PEP 8 recommendation)
- **Target Version**: Python 3.12
- **Format on Save**: Enabled (Ctrl+S)

### How It Works
1. You write code
2. Press Ctrl+S
3. Black automatically reformats to 79 characters
4. Code is consistent with project rules

### Example
```python
# Before (88 chars)
def my_function(parameter1, parameter2, parameter3, parameter4, parameter5):
    return parameter1 + parameter2 + parameter3 + parameter4 + parameter5

# After (79 chars)
def my_function(
    parameter1, parameter2, parameter3, parameter4, parameter5
):
    return (
        parameter1
        + parameter2
        + parameter3
        + parameter4
        + parameter5
    )
```

---

## isort

### What It Does
Automatically sorts and organizes Python imports.

### Configuration
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

### Key Settings
- **Profile**: black (compatible with Black formatter)
- **Line Length**: 79 characters
- **Multi-line Mode**: 3 (vertical hanging indent)
- **Trailing Comma**: Enabled
- **Parentheses**: Enabled

### How It Works
1. You write imports
2. Press Ctrl+S
3. isort automatically organizes them
4. Imports are sorted and grouped

### Example
```python
# Before
import os
from typing import Dict, List
import sys
from pathlib import Path

# After
import os
import sys
from pathlib import Path
from typing import Dict, List
```

---

## Ruff

### What It Does
Fast Python linter that checks for errors and style issues.

### Configuration
```json
"ruff.lineLength": 79,
"ruff.targetVersion": "py312",
"ruff.lint.select": [
  "E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH"
],
"ruff.lint.ignore": [
  "E501", "B008", "C901", "W191"
]
```

### Key Settings
- **Line Length**: 79 characters
- **Target Version**: Python 3.12
- **Rules Selected**: 10 rule categories
- **Auto-fix on Save**: Enabled

### Rules Explained
| Rule | Name | Purpose |
|------|------|---------|
| E | pycodestyle errors | PEP 8 compliance |
| W | pycodestyle warnings | PEP 8 warnings |
| F | pyflakes | Logical errors |
| I | isort | Import sorting |
| B | flake8-bugbear | Common bugs |
| C4 | flake8-comprehensions | List/dict comprehensions |
| UP | pyupgrade | Python syntax upgrades |
| ARG | flake8-unused-arguments | Unused function arguments |
| SIM | flake8-simplify | Code simplification |
| PTH | flake8-use-pathlib | Use pathlib instead of os.path |

### How It Works
1. You write code
2. Ruff checks in real-time
3. Errors appear as red squiggles
4. Press Ctrl+S to auto-fix
5. Many issues are fixed automatically

### Example
```python
# Before (Ruff shows errors)
import os  # F401: unused import
x = [i for i in range(10) if i % 2 == 0]  # SIM: can be simplified

# After (Ruff auto-fixes)
x = [i for i in range(10) if i % 2 == 0]  # Still shows SIM
# Ruff suggests: x = [i for i in range(0, 10, 2)]
```

---

## mypy

### What It Does
Static type checker that finds type errors before runtime.

### Configuration
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
]
```

### Key Settings
- **Python Version**: 3.12
- **Strict Mode**: Enabled
- **Check Untyped Defs**: Yes
- **Disallow Incomplete Defs**: Yes
- **Disallow Untyped Defs**: Yes

### How It Works
1. You write code with type hints
2. mypy checks in real-time
3. Type errors appear as yellow squiggles
4. You fix the type errors
5. Code is type-safe

### Example
```python
# Before (mypy shows error)
def add(x: int, y: int) -> int:
    return x + y

result = add("5", "10")  # Error: str is not int

# After (mypy is happy)
def add(x: int, y: int) -> int:
    return x + y

result = add(5, 10)  # OK: int is int
```

---

## Python Interpreter

### Configuration
```json
"python.defaultInterpreterPath": "${workspaceFolder}/src/dotfiles-installer/cli/.venv/bin/python"
```

### What It Does
Tells VSCode which Python to use for running code and tools.

### How It Works
1. VSCode uses `.venv/bin/python` (Python 3.12)
2. All tools use the same Python version
3. Dependencies are consistent
4. No version conflicts

---

## Editor Preferences

### Configuration
```json
"editor.rulers": [79],
"editor.wordWrap": "off",
"editor.insertSpaces": true,
"editor.tabSize": 4,
"files.trimTrailingWhitespace": true,
"files.insertFinalNewline": true
```

### What Each Does
- **Rulers**: Visual guide at 79 characters
- **Word Wrap**: Don't auto-wrap lines
- **Insert Spaces**: Use spaces instead of tabs
- **Tab Size**: 4 spaces per indent
- **Trim Whitespace**: Remove trailing spaces
- **Final Newline**: Add newline at end of file

---

## Format on Save

### Configuration
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

### What It Does
When you press Ctrl+S:
1. Ruff auto-fixes linting issues
2. isort organizes imports
3. Black formats code
4. Code is ready to commit

---

## Next Steps

1. Read `03_VSCODE_REFERENCE.md` for VSCode settings reference
2. Read `../GUIDES/01_SETUP_GUIDE.md` for setup instructions
3. Read `../GUIDES/02_TROUBLESHOOTING.md` for common issues
