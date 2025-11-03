# Renderers API Reference

This document describes the concrete renderer implementations.

---

## Jinja2Renderer

**Location:** `renderers/jinja2.py`

Jinja2-based implementation of the TemplateRenderer interface.

### Class Definition

```python
class Jinja2Renderer(TemplateRenderer):
    """Jinja2 template renderer implementation."""
```

### Constructor

```python
def __init__(
    self,
    template_dir: Path | str,
    config: RenderConfig | None = None
)
```

**Parameters:**
- `template_dir`: Directory containing Jinja2 templates
- `config`: Optional rendering configuration (default: RenderConfig())

**Raises:**
- `FileNotFoundError`: If template_dir doesn't exist

**Example:**
```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

# Basic usage
renderer = Jinja2Renderer("templates")

# With custom configuration
config = RenderConfig(
    strict_mode=True,
    autoescape=True,
    custom_filters={"uppercase": lambda x: x.upper()}
)
renderer = Jinja2Renderer("templates", config=config)
```

**Internal Initialization:**
- Creates Jinja2 `Environment` with `FileSystemLoader`
- Applies configuration settings to environment
- Registers custom filters, tests, and globals

---

## Public Methods

### render()

```python
def render(
    self,
    template_name: str,
    variables: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str
```

Render a Jinja2 template with the given variables.

**Parameters:**
- `template_name`: Name of the template file (relative to template_dir)
- `variables`: Dictionary of variables to use in rendering
- `**kwargs`: Additional variables (merged with variables dict)

**Returns:** Rendered template as string

**Raises:**
- `TemplateNotFoundError`: If template file doesn't exist
- `TemplateRenderError`: If rendering fails
- `MissingVariableError`: If required variables are missing (strict mode only)

**Behavior:**
1. Merges `variables` dict with `kwargs`
2. Validates variables if `strict_mode=True`
3. Gets template from Jinja2 environment
4. Renders template with merged variables
5. Returns rendered string

**Example:**
```python
# Basic rendering
result = renderer.render("app.j2", variables={"name": "myapp", "version": "1.0"})

# Using kwargs
result = renderer.render("app.j2", name="myapp", version="1.0")

# Mixing both
result = renderer.render(
    "app.j2",
    variables={"name": "myapp"},
    version="1.0",  # Additional via kwargs
    port=8080
)
```

**Error Handling:**
```python
from dotfiles_template_renderer import (
    MissingVariableError,
    TemplateNotFoundError,
    TemplateRenderError,
)

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing: {e.missing_variables}")
except TemplateNotFoundError as e:
    print(f"Template not found: {e.template_name}")
except TemplateRenderError as e:
    print(f"Rendering failed: {e}")
```

---

### validate()

```python
def validate(
    self,
    template_name: str,
    variables: dict[str, Any] | None = None,
) -> ValidationResult
```

Validate that all required variables are provided for a template.

**Parameters:**
- `template_name`: Name of the template file
- `variables`: Variables to validate against template requirements

**Returns:** `ValidationResult` with validation details

**Raises:**
- `TemplateNotFoundError`: If template doesn't exist

**Behavior:**
1. Gets template source from Jinja2 environment
2. Extracts required variables using AST parsing
3. Validates provided variables against requirements
4. Returns ValidationResult with details

**Example:**
```python
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Missing variables: {validation.missing_variables}")
    print(f"Errors: {validation.errors}")
else:
    print("Validation passed!")
    result = renderer.render("app.j2", variables={"name": "myapp"})
```

**ValidationResult Fields:**
```python
@dataclass
class ValidationResult:
    is_valid: bool                      # True if all required variables provided
    missing_variables: list[str]        # Variables required but not provided
    unused_variables: list[str]         # Variables provided but not used
    required_variables: list[str]       # All variables required by template
    errors: list[str]                   # Error messages
    warnings: list[str]                 # Warning messages
```

---

### get_template_variables()

```python
def get_template_variables(self, template_name: str) -> list[str]
```

Get list of all variables used in a template.

**Parameters:**
- `template_name`: Name of the template file

**Returns:** Sorted list of variable names

**Raises:**
- `TemplateNotFoundError`: If template doesn't exist

**Behavior:**
1. Gets template source
2. Parses template AST to find undeclared variables
3. Falls back to regex extraction if AST parsing fails
4. Returns sorted list of unique variable names

**Example:**
```python
variables = renderer.get_template_variables("app.j2")
print(f"Required variables: {variables}")
# Output: ['base_image', 'name', 'port', 'version', 'workdir']

# Use to collect variables dynamically
user_vars = {}
for var in variables:
    user_vars[var] = input(f"Enter {var}: ")

result = renderer.render("app.j2", variables=user_vars)
```

---

### get_available_templates()

```python
def get_available_templates(self) -> list[str]
```

Get list of all available template files in the template directory.

**Returns:** Sorted list of template file names (relative paths)

**Behavior:**
1. Uses Jinja2's `list_templates()` method
2. Returns all template files found recursively
3. Paths are relative to template_dir

**Example:**
```python
templates = renderer.get_available_templates()
for template in templates:
    print(f"- {template}")

# Output:
# - app.j2
# - configs/nginx.j2
# - configs/app.yaml.j2
# - dockerfiles/python.j2
# - scripts/deploy.sh.j2
```

**Use Case - Template Selection:**
```python
def select_template(renderer, category):
    """Select template from a category."""
    all_templates = renderer.get_available_templates()
    category_templates = [t for t in all_templates if t.startswith(f"{category}/")]

    print(f"Templates in {category}:")
    for i, template in enumerate(category_templates, 1):
        print(f"{i}. {template}")

    choice = int(input("Select template: ")) - 1
    return category_templates[choice]

template = select_template(renderer, "dockerfiles")
result = renderer.render(template, variables={...})
```

---

### get_template_info()

```python
def get_template_info(self, template_name: str) -> TemplateInfo
```

Get detailed information about a template.

**Parameters:**
- `template_name`: Name of the template file

**Returns:** `TemplateInfo` with template metadata

**Raises:**
- `TemplateNotFoundError`: If template doesn't exist

**Behavior:**
1. Gets template path
2. Reads file size
3. Extracts required variables
4. Extracts description from template comments
5. Returns TemplateInfo with all metadata

**Example:**
```python
info = renderer.get_template_info("app.j2")

print(f"Template: {info.name}")
print(f"Path: {info.path}")
print(f"Size: {info.size} bytes")
print(f"Required variables: {info.required_variables}")
if info.description:
    print(f"Description: {info.description}")
```

**TemplateInfo Fields:**
```python
@dataclass
class TemplateInfo:
    name: str                           # Template name
    path: Path                          # Full path to template file
    size: int                           # File size in bytes
    required_variables: list[str]       # Variables required by template
    optional_variables: list[str]       # Variables with defaults
    description: str | None             # Description from comments
```

---

## Private Methods

### _merge_variables()

```python
def _merge_variables(
    self,
    variables: dict[str, Any] | None,
    kwargs: dict[str, Any]
) -> dict[str, Any]
```

Merge variables dict with kwargs.

**Internal use only.** Combines the `variables` parameter with `**kwargs` from render().

---

### _get_template_source()

```python
def _get_template_source(self, template_name: str) -> str
```

Get the source code of a template.

**Internal use only.** Retrieves template source for validation and introspection.

---

### _apply_config()

```python
def _apply_config(self) -> None
```

Apply configuration to Jinja2 environment.

**Internal use only.** Called during initialization to configure the Jinja2 environment with settings from RenderConfig.

---

## Configuration

The Jinja2Renderer respects all RenderConfig options:

```python
config = RenderConfig(
    strict_mode=True,              # Validate before rendering
    autoescape=False,              # HTML/XML escaping
    trim_blocks=True,              # Remove first newline after tag
    lstrip_blocks=True,            # Strip leading whitespace
    keep_trailing_newline=True,    # Keep trailing newline
    undefined_behavior="strict",   # How to handle undefined variables
    custom_filters={},             # Custom Jinja2 filters
    custom_tests={},               # Custom Jinja2 tests
    custom_globals={},             # Custom global variables/functions
)
```

See [Configuration Reference](../reference/configuration.md) for details.

---

## See Also

- [Core API](core.md) - TemplateRenderer base class
- [Validators API](validators.md) - Validation utilities
- [Exceptions API](exceptions.md) - Exception hierarchy
- [Getting Started](../guides/getting_started.md) - Usage examples
