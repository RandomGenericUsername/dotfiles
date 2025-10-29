# Exceptions API Reference

This document describes the exception hierarchy and error handling.

**Location:** `core/exceptions.py`

---

## Exception Hierarchy

```
Exception (Python stdlib)
    │
    └─── TemplateError (base)
            │
            ├─── TemplateNotFoundError
            ├─── TemplateRenderError
            └─── ValidationError
                    │
                    ├─── MissingVariableError
                    └─── InvalidVariableError
```

---

## TemplateError

**Base exception for all template-related errors.**

```python
class TemplateError(Exception):
    """Base exception for all template errors."""
    
    def __init__(self, message: str, template_name: str | None = None):
        self.message = message
        self.template_name = template_name
        super().__init__(message)
```

**Attributes:**
- `message`: Error message
- `template_name`: Name of the template that caused the error (optional)

**Usage:**
```python
# Catch all template errors
try:
    result = renderer.render("app.j2", variables={...})
except TemplateError as e:
    print(f"Template error: {e.message}")
    if e.template_name:
        print(f"Template: {e.template_name}")
```

**When to Use:**
- As a base class for custom exceptions
- To catch all template-related errors
- When you don't need specific error handling

---

## TemplateNotFoundError

**Raised when a template file cannot be found.**

```python
class TemplateNotFoundError(TemplateError):
    """Template file not found."""
    
    def __init__(self, template_name: str, template_dir: Path | None = None):
        self.template_name = template_name
        self.template_dir = template_dir
        message = f"Template '{template_name}' not found"
        if template_dir:
            message += f" in '{template_dir}'"
        super().__init__(message, template_name)
```

**Attributes:**
- `template_name`: Name of the missing template
- `template_dir`: Directory where template was searched (optional)
- `message`: Formatted error message

**Example:**
```python
from dotfiles_template_renderer import TemplateNotFoundError

try:
    result = renderer.render("missing.j2", variables={...})
except TemplateNotFoundError as e:
    print(f"Template not found: {e.template_name}")
    print(f"Searched in: {e.template_dir}")
    
    # List available templates
    available = renderer.get_available_templates()
    print(f"Available templates: {available}")
    
    # Use fallback
    result = renderer.render("default.j2", variables={...})
```

**Common Causes:**
- Typo in template name
- Template file doesn't exist
- Wrong template directory
- File permissions issue

**Solutions:**
- Verify template exists: `Path(template_dir / template_name).exists()`
- List available templates: `renderer.get_available_templates()`
- Check template directory: `renderer.template_dir`
- Verify file permissions

---

## TemplateRenderError

**Raised when template rendering fails.**

```python
class TemplateRenderError(TemplateError):
    """Template rendering failed."""
    
    def __init__(
        self,
        message: str,
        template_name: str | None = None,
        original_error: Exception | None = None
    ):
        self.original_error = original_error
        super().__init__(message, template_name)
```

**Attributes:**
- `message`: Error message
- `template_name`: Name of the template that failed
- `original_error`: Original exception from Jinja2 (if any)

**Example:**
```python
from dotfiles_template_renderer import TemplateRenderError

try:
    result = renderer.render("app.j2", variables={...})
except TemplateRenderError as e:
    print(f"Rendering failed: {e.message}")
    print(f"Template: {e.template_name}")
    
    if e.original_error:
        print(f"Original error: {e.original_error}")
        import traceback
        traceback.print_exception(type(e.original_error), e.original_error, e.original_error.__traceback__)
```

**Common Causes:**
- Syntax error in template
- Invalid Jinja2 expression
- Filter/test not found
- Type error in template logic
- Division by zero or other runtime errors

**Solutions:**
- Check template syntax
- Verify all filters/tests are registered
- Validate variable types
- Test template with simple variables first

---

## ValidationError

**Base exception for validation errors.**

```python
class ValidationError(TemplateError):
    """Template validation failed."""
    
    def __init__(self, message: str, template_name: str | None = None):
        super().__init__(message, template_name)
```

**Usage:**
```python
from dotfiles_template_renderer import ValidationError

try:
    result = renderer.render("app.j2", variables={...})
except ValidationError as e:
    print(f"Validation error: {e.message}")
    # Handle validation errors (missing variables, invalid types, etc.)
```

**Subclasses:**
- `MissingVariableError` - Required variables not provided
- `InvalidVariableError` - Variable has invalid value

---

## MissingVariableError

**Raised when required variables are not provided (strict mode only).**

```python
class MissingVariableError(ValidationError):
    """Required variables are missing."""
    
    def __init__(
        self,
        missing_variables: list[str],
        template_name: str | None = None
    ):
        self.missing_variables = missing_variables
        message = f"Missing required variables: {', '.join(missing_variables)}"
        super().__init__(message, template_name)
```

**Attributes:**
- `missing_variables`: List of variable names that are missing
- `template_name`: Name of the template
- `message`: Formatted error message

**Example:**
```python
from dotfiles_template_renderer import MissingVariableError

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing variables: {e.missing_variables}")
    
    # Collect missing variables
    for var in e.missing_variables:
        value = input(f"Enter {var}: ")
        variables[var] = value
    
    # Retry with complete variables
    result = renderer.render("app.j2", variables=variables)
```

**When Raised:**
- Only in strict mode (`RenderConfig(strict_mode=True)`)
- When `render()` is called without all required variables
- After validation fails

**Prevention:**
```python
# Option 1: Validate before rendering
validation = renderer.validate("app.j2", variables={...})
if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    # Provide missing variables
else:
    result = renderer.render("app.j2", variables={...})

# Option 2: Use lenient mode
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))
# Template must have defaults: {{ version | default('1.0.0') }}

# Option 3: Get required variables first
required = renderer.get_template_variables("app.j2")
variables = {var: get_value(var) for var in required}
result = renderer.render("app.j2", variables=variables)
```

---

## InvalidVariableError

**Raised when a variable has an invalid value.**

```python
class InvalidVariableError(ValidationError):
    """Variable has invalid value."""
    
    def __init__(
        self,
        variable_name: str,
        reason: str,
        template_name: str | None = None
    ):
        self.variable_name = variable_name
        self.reason = reason
        message = f"Invalid variable '{variable_name}': {reason}"
        super().__init__(message, template_name)
```

**Attributes:**
- `variable_name`: Name of the invalid variable
- `reason`: Reason why the variable is invalid
- `template_name`: Name of the template
- `message`: Formatted error message

**Example:**
```python
from dotfiles_template_renderer import InvalidVariableError

try:
    result = renderer.render("app.j2", variables={"port": "invalid"})
except InvalidVariableError as e:
    print(f"Invalid variable: {e.variable_name}")
    print(f"Reason: {e.reason}")
    
    # Fix the variable
    variables[e.variable_name] = 8080
    result = renderer.render("app.j2", variables=variables)
```

**Common Reasons:**
- Wrong type (e.g., string instead of int)
- Value out of range
- Invalid format
- Null/None when not allowed

---

## Error Handling Patterns

### Pattern 1: Specific Exception Handling

```python
from dotfiles_template_renderer import (
    MissingVariableError,
    TemplateNotFoundError,
    TemplateRenderError,
)

try:
    result = renderer.render("app.j2", variables={...})
except MissingVariableError as e:
    # Handle missing variables
    print(f"Missing: {e.missing_variables}")
except TemplateNotFoundError as e:
    # Handle missing template
    print(f"Template not found: {e.template_name}")
except TemplateRenderError as e:
    # Handle rendering errors
    print(f"Rendering failed: {e.message}")
```

### Pattern 2: Catch All Template Errors

```python
from dotfiles_template_renderer import TemplateError

try:
    result = renderer.render("app.j2", variables={...})
except TemplateError as e:
    print(f"Template error: {e.message}")
    if e.template_name:
        print(f"Template: {e.template_name}")
```

### Pattern 3: Validation Before Rendering

```python
# Validate first to avoid exceptions
validation = renderer.validate("app.j2", variables={...})

if not validation.is_valid:
    # Handle validation errors without exceptions
    print(f"Errors: {validation.errors}")
else:
    # Safe to render
    result = renderer.render("app.j2", variables={...})
```

### Pattern 4: Retry with Fallback

```python
from dotfiles_template_renderer import TemplateError

try:
    result = renderer.render("app.j2", variables={...})
except TemplateError as e:
    print(f"Error: {e.message}")
    # Use fallback template
    result = renderer.render("default.j2", variables={...})
```

### Pattern 5: Logging and Re-raising

```python
import logging
from dotfiles_template_renderer import TemplateError

logger = logging.getLogger(__name__)

try:
    result = renderer.render("app.j2", variables={...})
except TemplateError as e:
    # Log detailed error
    logger.error(f"Template error: {e.message}", exc_info=True)
    # Re-raise for caller to handle
    raise
```

---

## See Also

- [Core API](core.md) - TemplateRenderer base class
- [Renderers API](renderers.md) - When exceptions are raised
- [Troubleshooting](../reference/troubleshooting.md) - Common issues and solutions

