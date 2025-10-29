# Core API Reference

This document describes the core abstractions and types in the template_renderer module.

---

## TemplateRenderer (Abstract Base Class)

**Location:** `core/base.py`

Abstract base class defining the contract for all template renderers.

### Constructor

```python
def __init__(self, template_dir: Path | str, config: RenderConfig | None = None)
```

**Parameters:**
- `template_dir`: Directory containing templates (Path or string)
- `config`: Optional rendering configuration (default: RenderConfig())

**Raises:**
- `FileNotFoundError`: If template_dir doesn't exist

**Example:**
```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

renderer = Jinja2Renderer(
    template_dir="templates",
    config=RenderConfig(strict_mode=True)
)
```

### Abstract Methods

#### render()

```python
@abstractmethod
def render(
    self,
    template_name: str,
    variables: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str
```

Render a template with the given variables.

**Parameters:**
- `template_name`: Name of the template file
- `variables`: Variables to use in rendering (optional)
- `**kwargs`: Additional variables (merged with variables dict)

**Returns:** Rendered template as string

**Raises:**
- `TemplateNotFoundError`: If template doesn't exist
- `TemplateRenderError`: If rendering fails
- `MissingVariableError`: If required variables are missing (strict mode)

**Example:**
```python
result = renderer.render(
    "app.j2",
    variables={"name": "myapp", "version": "1.0"},
    port=8080  # Additional variable via kwargs
)
```

#### validate()

```python
@abstractmethod
def validate(
    self,
    template_name: str,
    variables: dict[str, Any] | None = None,
) -> ValidationResult
```

Validate that all required variables are provided.

**Parameters:**
- `template_name`: Name of the template file
- `variables`: Variables to validate against template (optional)

**Returns:** ValidationResult with details about missing/unused variables

**Example:**
```python
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    print(f"Errors: {validation.errors}")
```

#### get_template_variables()

```python
@abstractmethod
def get_template_variables(self, template_name: str) -> list[str]
```

Get list of all variables used in a template.

**Parameters:**
- `template_name`: Name of the template file

**Returns:** Sorted list of variable names

**Raises:**
- `TemplateNotFoundError`: If template doesn't exist

**Example:**
```python
variables = renderer.get_template_variables("app.j2")
print(f"Required: {variables}")  # ['name', 'port', 'version']
```

#### get_available_templates()

```python
@abstractmethod
def get_available_templates(self) -> list[str]
```

Get list of all available template files.

**Returns:** Sorted list of template file names (relative paths)

**Example:**
```python
templates = renderer.get_available_templates()
for template in templates:
    print(f"- {template}")
# Output:
# - app.j2
# - configs/nginx.j2
# - scripts/deploy.j2
```

#### get_template_info()

```python
@abstractmethod
def get_template_info(self, template_name: str) -> TemplateInfo
```

Get detailed information about a template.

**Parameters:**
- `template_name`: Name of the template file

**Returns:** TemplateInfo with metadata

**Raises:**
- `TemplateNotFoundError`: If template doesn't exist

**Example:**
```python
info = renderer.get_template_info("app.j2")
print(f"Size: {info.size} bytes")
print(f"Variables: {info.required_variables}")
print(f"Description: {info.description}")
```

### Concrete Methods

#### render_from_context()

```python
def render_from_context(self, context: TemplateContext) -> str
```

Render a template using a TemplateContext object.

**Parameters:**
- `context`: TemplateContext with name, variables, and optional config

**Returns:** Rendered template as string

**Example:**
```python
from dotfiles_template_renderer import TemplateContext, RenderConfig

context = TemplateContext(
    template_name="app.j2",
    variables={"name": "myapp"},
    config=RenderConfig(strict_mode=False)  # Override config
)

result = renderer.render_from_context(context)
```

#### render_to_file()

```python
def render_to_file(
    self,
    template_name: str,
    output_path: Path | str,
    variables: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None
```

Render a template and write to a file.

**Parameters:**
- `template_name`: Name of the template file
- `output_path`: Path where rendered content should be written
- `variables`: Variables to use in rendering (optional)
- `**kwargs`: Additional variables

**Side Effects:**
- Creates parent directories if they don't exist
- Writes rendered content to file

**Example:**
```python
renderer.render_to_file(
    "nginx.conf.j2",
    "/etc/nginx/sites-available/mysite",
    variables={"server_name": "example.com", "port": 80}
)
```

---

## Data Types

### RenderConfig

**Location:** `core/types.py`

Configuration for template rendering behavior.

```python
@dataclass
class RenderConfig:
    strict_mode: bool = True
    autoescape: bool = False
    trim_blocks: bool = True
    lstrip_blocks: bool = True
    keep_trailing_newline: bool = True
    undefined_behavior: str = "strict"
    custom_filters: dict[str, Any] = field(default_factory=dict)
    custom_tests: dict[str, Any] = field(default_factory=dict)
    custom_globals: dict[str, Any] = field(default_factory=dict)
```

**Fields:**
- `strict_mode`: Fail if required variables are missing (default: True)
- `autoescape`: Enable autoescaping for HTML/XML (default: False)
- `trim_blocks`: Remove first newline after template tag (default: True)
- `lstrip_blocks`: Strip leading spaces/tabs (default: True)
- `keep_trailing_newline`: Keep trailing newline (default: True)
- `undefined_behavior`: How to handle undefined variables (default: "strict")
- `custom_filters`: Custom Jinja2 filters (default: {})
- `custom_tests`: Custom Jinja2 tests (default: {})
- `custom_globals`: Custom global variables/functions (default: {})

**Example:**
```python
config = RenderConfig(
    strict_mode=True,
    autoescape=True,  # For HTML templates
    custom_filters={"uppercase": lambda x: x.upper()},
)
```

### TemplateContext

**Location:** `core/types.py`

Context for template rendering operations.

```python
@dataclass
class TemplateContext:
    template_name: str
    variables: dict[str, Any]
    config: RenderConfig = field(default_factory=RenderConfig)
```

**Fields:**
- `template_name`: Name of the template file
- `variables`: Variables to use in rendering
- `config`: Rendering configuration (default: new RenderConfig())

**Example:**
```python
context = TemplateContext(
    template_name="app.j2",
    variables={"name": "myapp", "version": "1.0"},
    config=RenderConfig(strict_mode=False)
)
```

### ValidationResult

**Location:** `core/types.py`

Result of template validation.

```python
@dataclass
class ValidationResult:
    is_valid: bool
    missing_variables: list[str] = field(default_factory=list)
    unused_variables: list[str] = field(default_factory=list)
    required_variables: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
```

**Fields:**
- `is_valid`: Whether the template is valid
- `missing_variables`: Variables required but not provided
- `unused_variables`: Variables provided but not used
- `required_variables`: All variables required by template
- `errors`: Validation error messages
- `warnings`: Validation warning messages

**Example:**
```python
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    for error in validation.errors:
        print(f"Error: {error}")
    for warning in validation.warnings:
        print(f"Warning: {warning}")
```

### TemplateInfo

**Location:** `core/types.py`

Information about a template.

```python
@dataclass
class TemplateInfo:
    name: str
    path: Path
    size: int
    required_variables: list[str] = field(default_factory=list)
    optional_variables: list[str] = field(default_factory=list)
    description: str | None = None
```

**Fields:**
- `name`: Template name
- `path`: Full path to template file
- `size`: File size in bytes
- `required_variables`: Variables required by template
- `optional_variables`: Variables with default values
- `description`: Template description (from comments)

**Example:**
```python
info = renderer.get_template_info("app.j2")
print(f"Template: {info.name}")
print(f"Path: {info.path}")
print(f"Size: {info.size} bytes")
print(f"Variables: {info.required_variables}")
if info.description:
    print(f"Description: {info.description}")
```

---

## Type Aliases

```python
from typing import Any
from pathlib import Path

# Common type aliases used throughout the module
VariablesDict = dict[str, Any]
TemplateName = str
TemplatePath = Path | str
```

---

## See Also

- [Renderers API](renderers.md) - Jinja2Renderer implementation
- [Exceptions API](exceptions.md) - Exception hierarchy
- [Validators API](validators.md) - Validation utilities

