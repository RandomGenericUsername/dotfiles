# Validators API Reference

This document describes the validation utility functions.

**Location:** `validators.py`

---

## Overview

The validators module provides utility functions for extracting variables from templates and validating them against provided values. These functions are used internally by renderers but can also be used standalone.

---

## extract_jinja2_variables()

```python
def extract_jinja2_variables(
    template_source: str,
    env: Environment | None = None
) -> set[str]
```

Extract all variables used in a Jinja2 template using AST parsing.

**Parameters:**
- `template_source`: The template source code as a string
- `env`: Optional Jinja2 Environment (creates default if not provided)

**Returns:** Set of variable names found in the template

**Algorithm:**
1. Try AST parsing using `jinja2.meta.find_undeclared_variables()`
2. If AST parsing fails, fall back to `extract_variables_regex()`
3. Return set of unique variable names

**Example:**
```python
from dotfiles_template_renderer import extract_jinja2_variables

template_source = """
FROM {{ base_image }}
WORKDIR {{ workdir }}
LABEL name={{ name }}
LABEL version={{ version }}
"""

variables = extract_jinja2_variables(template_source)
print(variables)
# Output: {'base_image', 'workdir', 'name', 'version'}
```

**With Custom Environment:**
```python
from jinja2 import Environment

env = Environment()
variables = extract_jinja2_variables(template_source, env=env)
```

**Why AST Parsing?**
- More accurate than regex
- Handles complex expressions
- Understands Jinja2 syntax
- Ignores variables in comments

**Fallback Behavior:**
If AST parsing fails (malformed template), falls back to regex extraction:
```python
try:
    # Try AST parsing
    ast = env.parse(template_source)
    variables = meta.find_undeclared_variables(ast)
except Exception:
    # Fall back to regex
    variables = extract_variables_regex(template_source)
```

---

## extract_variables_regex()

```python
def extract_variables_regex(template_source: str) -> set[str]
```

Extract variables from a template using regex pattern matching.

**Parameters:**
- `template_source`: The template source code as a string

**Returns:** Set of variable names found in the template

**Pattern:** Matches `{{ variable_name }}` patterns

**Example:**
```python
from dotfiles_template_renderer import extract_variables_regex

template_source = """
Hello {{ name }}!
Your email is {{ email }}.
"""

variables = extract_variables_regex(template_source)
print(variables)
# Output: {'name', 'email'}
```

**Regex Pattern:**
```python
pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
```

**Limitations:**
- Only matches simple variable references
- Doesn't handle complex expressions like `{{ user.name }}`
- Doesn't understand Jinja2 control structures
- May match variables in comments

**When to Use:**
- As a fallback when AST parsing fails
- For quick, simple variable extraction
- When you don't have a Jinja2 environment

**Recommendation:** Prefer `extract_jinja2_variables()` which uses AST parsing with regex fallback.

---

## validate_variables()

```python
def validate_variables(
    template_name: str,
    required_variables: set[str],
    provided_variables: dict[str, Any],
    strict: bool = True,
) -> ValidationResult
```

Validate that provided variables match template requirements.

**Parameters:**
- `template_name`: Name of the template (for error messages)
- `required_variables`: Set of variables required by the template
- `provided_variables`: Dictionary of variables provided by user
- `strict`: If True, missing variables are errors; if False, they're warnings

**Returns:** `ValidationResult` with validation details

**Validation Logic:**
1. Calculate missing variables: `required - provided.keys()`
2. Calculate unused variables: `provided.keys() - required`
3. Generate errors (strict mode) or warnings (lenient mode)
4. Set `is_valid` based on whether there are errors

**Example:**
```python
from dotfiles_template_renderer import validate_variables

required = {"name", "version", "port"}
provided = {"name": "myapp", "version": "1.0"}

result = validate_variables(
    template_name="app.j2",
    required_variables=required,
    provided_variables=provided,
    strict=True
)

if not result.is_valid:
    print(f"Missing: {result.missing_variables}")  # ['port']
    print(f"Errors: {result.errors}")
```

**Strict Mode (default):**
```python
result = validate_variables("app.j2", required, provided, strict=True)
# Missing variables → errors
# is_valid = False if any missing
```

**Lenient Mode:**
```python
result = validate_variables("app.j2", required, provided, strict=False)
# Missing variables → warnings
# is_valid = True even if missing (template should have defaults)
```

**ValidationResult Structure:**
```python
@dataclass
class ValidationResult:
    is_valid: bool                  # True if validation passed
    missing_variables: list[str]    # Variables required but not provided
    unused_variables: list[str]     # Variables provided but not used
    required_variables: list[str]   # All variables required by template
    errors: list[str]               # Error messages
    warnings: list[str]             # Warning messages
```

**Error Messages:**
```python
# Strict mode
errors = [
    "Missing required variable: port",
    "Template 'app.j2' requires variables: name, version, port"
]

# Lenient mode
warnings = [
    "Variable 'port' not provided (template should have default)",
    "Unused variable provided: 'debug'"
]
```

---

## validate_variable_types()

```python
def validate_variable_types(
    variables: dict[str, Any],
    expected_types: dict[str, type],
) -> list[str]
```

Validate that variables have the expected types.

**Parameters:**
- `variables`: Dictionary of variables to validate
- `expected_types`: Dictionary mapping variable names to expected types

**Returns:** List of error messages (empty if all types are correct)

**Example:**
```python
from dotfiles_template_renderer import validate_variable_types

variables = {
    "name": "myapp",
    "port": "8080",  # Wrong type - should be int
    "debug": True,
}

expected_types = {
    "name": str,
    "port": int,
    "debug": bool,
}

errors = validate_variable_types(variables, expected_types)
print(errors)
# Output: ["Variable 'port' has type str, expected int"]
```

**Type Checking:**
```python
for var_name, expected_type in expected_types.items():
    if var_name in variables:
        actual_type = type(variables[var_name])
        if actual_type != expected_type:
            errors.append(
                f"Variable '{var_name}' has type {actual_type.__name__}, "
                f"expected {expected_type.__name__}"
            )
```

**Use Case - Pre-Validation:**
```python
# Define expected types
expected_types = {
    "name": str,
    "version": str,
    "port": int,
    "debug": bool,
    "packages": list,
}

# Validate types before rendering
type_errors = validate_variable_types(variables, expected_types)
if type_errors:
    for error in type_errors:
        print(f"Type error: {error}")
    # Fix types or abort
else:
    # Types are correct, proceed with rendering
    result = renderer.render("app.j2", variables=variables)
```

**Supported Types:**
- Any Python type can be used: `str`, `int`, `float`, `bool`, `list`, `dict`, etc.
- Custom classes and types are supported
- Uses `isinstance()` for type checking

---

## Usage Patterns

### Pattern 1: Manual Validation

```python
from dotfiles_template_renderer import (
    extract_jinja2_variables,
    validate_variables,
)

# Read template
with open("templates/app.j2") as f:
    template_source = f.read()

# Extract required variables
required = extract_jinja2_variables(template_source)

# Get variables from user
provided = {
    "name": input("Enter name: "),
    "version": input("Enter version: "),
}

# Validate
result = validate_variables("app.j2", required, provided, strict=True)

if result.is_valid:
    print("Validation passed!")
else:
    print(f"Errors: {result.errors}")
```

### Pattern 2: Type-Safe Validation

```python
from dotfiles_template_renderer import (
    validate_variables,
    validate_variable_types,
)

# Define schema
required_vars = {"name", "port", "debug"}
expected_types = {"name": str, "port": int, "debug": bool}

# Validate presence
result = validate_variables("app.j2", required_vars, variables, strict=True)

# Validate types
type_errors = validate_variable_types(variables, expected_types)

# Check both
if result.is_valid and not type_errors:
    print("All validations passed!")
else:
    print(f"Errors: {result.errors + type_errors}")
```

### Pattern 3: Standalone Variable Extraction

```python
from dotfiles_template_renderer import extract_jinja2_variables
from pathlib import Path

# Extract variables from all templates
template_dir = Path("templates")
for template_file in template_dir.glob("**/*.j2"):
    source = template_file.read_text()
    variables = extract_jinja2_variables(source)
    print(f"{template_file.name}: {variables}")
```

---

## See Also

- [Core API](core.md) - ValidationResult dataclass
- [Renderers API](renderers.md) - How renderers use validators
- [Getting Started](../guides/getting_started.md) - Validation examples
