# VSCode Settings Reference

Complete reference for all VSCode settings used in this project.

---

## Python Interpreter

```json
"python.defaultInterpreterPath": "${workspaceFolder}/src/dotfiles-installer/cli/.venv/bin/python"
```

Sets the Python interpreter to use for the project.

---

## Black Formatter

```json
"python.formatting.provider": "black",
"python.formatting.blackArgs": [
  "--line-length=79",
  "--target-version=py312"
]
```

Configures Black formatter with 79-character line length and Python 3.12 target.

---

## isort Configuration

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

Configures isort to be compatible with Black and use 79-character line length.

---

## Ruff Configuration

```json
"ruff.lineLength": 79,
"ruff.targetVersion": "py312",
"ruff.lint.select": [
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
],
"ruff.lint.ignore": [
  "E501", # line too long, handled by black
  "B008", # do not perform function calls in argument defaults
  "C901", # too complex
  "W191", # indentation contains tabs
]
```

Configures Ruff linter with 10 rule categories and specific ignores.

---

## mypy Configuration

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

Configures mypy with strict type checking and Python 3.12.

---

## Python Language Settings

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

Configures Python-specific editor settings:
- Default formatter: Ruff
- Format on save: Enabled
- Auto-fix on save: Enabled
- Organize imports on save: Enabled

---

## Editor Preferences

```json
"editor.rulers": [79],
"editor.wordWrap": "off",
"editor.insertSpaces": true,
"editor.tabSize": 4,
"files.trimTrailingWhitespace": true,
"files.insertFinalNewline": true
```

General editor preferences:
- **Rulers**: Visual guide at 79 characters
- **Word Wrap**: Off (don't auto-wrap)
- **Insert Spaces**: Use spaces instead of tabs
- **Tab Size**: 4 spaces per indent
- **Trim Whitespace**: Remove trailing spaces
- **Final Newline**: Add newline at end of file

---

## File Exclusions

```json
"files.exclude": {
  "**/__pycache__": true,
  "**/*.pyc": true,
  "**/.pytest_cache": true,
  "**/.mypy_cache": true,
  "**/.ruff_cache": true,
  "**/.venv": true,
  "**/node_modules": true
}
```

Hides cache and virtual environment directories from file explorer.

---

## Search Exclusions

```json
"search.exclude": {
  "**/__pycache__": true,
  "**/.pytest_cache": true,
  "**/.mypy_cache": true,
  "**/.ruff_cache": true,
  "**/.venv": true,
  "**/node_modules": true
}
```

Excludes cache and virtual environment directories from search.

---

## Linting Configuration

```json
"python.linting.enabled": true,
"python.linting.pylintEnabled": false
```

Enables linting but disables pylint (we use Ruff instead).

---

## Complete settings.json

Here's the complete `.vscode/settings.json` file:

```json
{
  // Python Configuration
  "python.defaultInterpreterPath": "${workspaceFolder}/src/dotfiles-installer/cli/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,

  // Black Formatter Configuration
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": [
    "--line-length=79",
    "--target-version=py312"
  ],

  // isort Configuration
  "isort.args": [
    "--profile=black",
    "--line-length=79",
    "--multi-line-mode=3",
    "--trailing-comma",
    "--use-parentheses",
    "--ensure-newline-before-comments"
  ],

  // Ruff Configuration
  "ruff.lineLength": 79,
  "ruff.targetVersion": "py312",
  "ruff.lint.select": [
    "E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH"
  ],
  "ruff.lint.ignore": [
    "E501", "B008", "C901", "W191"
  ],

  // mypy Configuration
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
  "mypy-type-checker.runUsingActiveInterpreter": true,

  // Python Language Settings
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },

  // Editor Configuration
  "editor.rulers": [79],
  "editor.wordWrap": "off",
  "editor.insertSpaces": true,
  "editor.tabSize": 4,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,

  // File Exclusions
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true,
    "**/.venv": true,
    "**/node_modules": true
  },

  // Search Exclusions
  "search.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true,
    "**/.venv": true,
    "**/node_modules": true
  }
}
```

---

## Next Steps

1. Read `../GUIDES/01_SETUP_GUIDE.md` for setup instructions
2. Read `../GUIDES/02_TROUBLESHOOTING.md` for common issues
3. Read `../GUIDES/03_DEVELOPMENT_WORKFLOW.md` for how to use


