# Design Patterns

This document describes the design patterns used in the template_renderer module.

---

## 1. Abstract Base Class (ABC) Pattern

### Purpose
Define a contract that all template renderers must implement.

### Implementation

**Location:** `core/base.py`

```python
from abc import ABC, abstractmethod

class TemplateRenderer(ABC):
    """Abstract base class for template renderers."""

    @abstractmethod
    def render(self, template_name: str, variables: dict[str, Any] | None = None, **kwargs: Any) -> str:
        """Render a template with variables."""
        pass

    @abstractmethod
    def validate(self, template_name: str, variables: dict[str, Any] | None = None) -> ValidationResult:
        """Validate template variables."""
        pass

    # ... other abstract methods
```

### Benefits
- **Enforces Contract:** All renderers must implement required methods
- **Polymorphism:** Can use different renderers interchangeably
- **Type Safety:** IDE can check implementations
- **Documentation:** Clear interface for implementers

### Usage
```python
# Can use any renderer that implements TemplateRenderer
def process_template(renderer: TemplateRenderer, template: str, vars: dict):
    return renderer.render(template, vars)

# Works with any implementation
jinja_renderer = Jinja2Renderer("templates")
# future: mako_renderer = MakoRenderer("templates")

result1 = process_template(jinja_renderer, "app.j2", {"name": "app1"})
# result2 = process_template(mako_renderer, "app.mako", {"name": "app2"})
```

---

## 2. Template Method Pattern

### Purpose
Define the skeleton of an algorithm, letting subclasses override specific steps.

### Implementation

**Location:** `core/base.py`

```python
class TemplateRenderer(ABC):
    def render_from_context(self, context: TemplateContext) -> str:
        """Template method - defines workflow."""
        # Save original config
        original_config = self.config

        # Temporarily override config if provided
        if context.config:
            self.config = context.config

        try:
            # Call abstract method (implemented by subclass)
            return self.render(context.template_name, context.variables)
        finally:
            # Restore original config
            self.config = original_config
```

### Benefits
- **Consistent Workflow:** Same process across all implementations
- **Reusable Logic:** Common code in base class
- **Extensible:** Subclasses customize specific steps
- **DRY:** Don't repeat workflow logic

### Usage
```python
context = TemplateContext(
    template_name="app.j2",
    variables={"name": "myapp"},
    config=RenderConfig(strict_mode=False)  # Temporary override
)

# Workflow handled by base class
result = renderer.render_from_context(context)
```

---

## 3. Adapter Pattern

### Purpose
Adapt Jinja2's API to match our TemplateRenderer interface.

### Implementation

**Location:** `renderers/jinja2.py`

```python
class Jinja2Renderer(TemplateRenderer):
    """Adapts Jinja2 to TemplateRenderer interface."""

    def __init__(self, template_dir, config=None):
        super().__init__(template_dir, config)
        # Create Jinja2 environment (adaptee)
        self._env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def render(self, template_name, variables=None, **kwargs):
        """Adapt Jinja2's render method to our interface."""
        all_variables = {**(variables or {}), **kwargs}

        # Use Jinja2's API
        template = self._env.get_template(template_name)
        return template.render(**all_variables)
```

### Benefits
- **Hides Complexity:** Users don't need to know Jinja2 API
- **Consistent Interface:** Same API for all renderers
- **Swappable:** Easy to replace Jinja2 with another engine
- **Isolation:** Changes to Jinja2 don't affect our API

### Diagram
```
┌──────────────┐         ┌──────────────────┐
│ User Code    │────────>│ TemplateRenderer │
└──────────────┘         │   (Interface)    │
                         └────────┬─────────┘
                                  │
                                  │ implements
                                  ▼
                         ┌──────────────────┐
                         │ Jinja2Renderer   │
                         │   (Adapter)      │
                         └────────┬─────────┘
                                  │
                                  │ uses
                                  ▼
                         ┌──────────────────┐
                         │ Jinja2 Library   │
                         │   (Adaptee)      │
                         └──────────────────┘
```

---

## 4. Facade Pattern

### Purpose
Provide a simplified interface to a complex subsystem.

### Implementation

**Location:** `__init__.py`

```python
# Facade: Single import point for entire module
from .core import (
    TemplateRenderer,
    RenderConfig,
    TemplateContext,
    ValidationResult,
    TemplateInfo,
)
from .core.exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateRenderError,
    ValidationError,
    MissingVariableError,
    InvalidVariableError,
)
from .renderers import Jinja2Renderer
from .validators import (
    extract_jinja2_variables,
    extract_variables_regex,
    validate_variables,
    validate_variable_types,
)

__all__ = [...]
```

### Benefits
- **Simplified Imports:** One import location
- **Hides Structure:** Users don't need to know internal organization
- **Stable API:** Can reorganize internally without breaking users
- **Discoverability:** Easy to find what's available

### Usage
```python
# ✅ Good: Simple import from facade
from dotfiles_template_renderer import (
    Jinja2Renderer,
    RenderConfig,
    MissingVariableError,
)

# ❌ Bad: Complex imports from internal structure
from dotfiles_template_renderer.renderers.jinja2 import Jinja2Renderer
from dotfiles_template_renderer.core.types import RenderConfig
from dotfiles_template_renderer.core.exceptions import MissingVariableError
```

---

## 5. Strategy Pattern

### Purpose
Define a family of algorithms (strategies) and make them interchangeable.

### Implementation

**Location:** `core/types.py`

```python
@dataclass
class RenderConfig:
    """Configuration strategies for rendering."""

    # Validation strategy
    strict_mode: bool = True

    # Escaping strategy
    autoescape: bool = False

    # Whitespace strategy
    trim_blocks: bool = True
    lstrip_blocks: bool = True

    # Custom behavior strategies
    custom_filters: dict[str, Any] = field(default_factory=dict)
    custom_tests: dict[str, Any] = field(default_factory=dict)
    custom_globals: dict[str, Any] = field(default_factory=dict)
```

### Benefits
- **Flexible Configuration:** Change behavior without subclassing
- **Runtime Changes:** Can change strategies at runtime
- **Composition:** Combine multiple strategies
- **Testability:** Easy to test different configurations

### Usage
```python
# Strategy 1: Strict validation, no escaping
config1 = RenderConfig(strict_mode=True, autoescape=False)

# Strategy 2: Lenient validation, HTML escaping
config2 = RenderConfig(strict_mode=False, autoescape=True)

# Strategy 3: Custom filters
config3 = RenderConfig(
    custom_filters={"uppercase": lambda x: x.upper()}
)

# Use different strategies
renderer1 = Jinja2Renderer("templates", config=config1)
renderer2 = Jinja2Renderer("templates", config=config2)
renderer3 = Jinja2Renderer("templates", config=config3)
```

---

## 6. Dataclass Pattern

### Purpose
Use dataclasses for immutable, type-safe data structures.

### Implementation

**Location:** `core/types.py`

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ValidationResult:
    """Immutable validation result."""
    is_valid: bool
    missing_variables: list[str] = field(default_factory=list)
    unused_variables: list[str] = field(default_factory=list)
    required_variables: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
```

### Benefits
- **Type Safety:** Full type hints
- **Immutability:** Encourages immutable data
- **Auto-generated Methods:** `__init__`, `__repr__`, `__eq__` for free
- **IDE Support:** Better autocomplete and type checking
- **Default Values:** Easy to specify defaults

### Usage
```python
# Create with defaults
result = ValidationResult(is_valid=True)

# Create with specific values
result = ValidationResult(
    is_valid=False,
    missing_variables=["name", "version"],
    errors=["Missing required variable: name"]
)

# Access fields with type safety
if not result.is_valid:
    print(result.errors)  # IDE knows this is list[str]
```

---

## 7. Exception Hierarchy Pattern

### Purpose
Create a hierarchy of exceptions for fine-grained error handling.

### Implementation

**Location:** `core/exceptions.py`

```python
class TemplateError(Exception):
    """Base exception for all template errors."""
    pass

class TemplateNotFoundError(TemplateError):
    """Template file not found."""
    pass

class TemplateRenderError(TemplateError):
    """Template rendering failed."""
    pass

class ValidationError(TemplateError):
    """Template validation failed."""
    pass

class MissingVariableError(ValidationError):
    """Required variables are missing."""
    def __init__(self, missing_variables, template_name=None):
        self.missing_variables = missing_variables
        super().__init__(f"Missing variables: {missing_variables}")
```

### Benefits
- **Fine-Grained Handling:** Catch specific errors
- **Fallback Handling:** Can catch base exception
- **Context:** Exceptions carry relevant data
- **Documentation:** Clear error types

### Usage
```python
try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    # Handle missing variables specifically
    print(f"Missing: {e.missing_variables}")
except TemplateNotFoundError as e:
    # Handle missing template
    print(f"Template not found: {e.template_name}")
except TemplateError as e:
    # Catch all template errors
    print(f"Template error: {e}")
```

---

## 8. Dependency Injection Pattern

### Purpose
Inject dependencies rather than creating them internally.

### Implementation

**Location:** `core/base.py`

```python
class TemplateRenderer(ABC):
    def __init__(self, template_dir: Path | str, config: RenderConfig | None = None):
        self.template_dir = Path(template_dir)
        # Inject config or use default
        self.config = config or RenderConfig()
```

### Benefits
- **Testability:** Easy to inject mock config
- **Flexibility:** Can provide custom config
- **Decoupling:** Doesn't depend on specific config implementation
- **Explicit:** Dependencies are clear

### Usage
```python
# Inject custom config
custom_config = RenderConfig(strict_mode=False, autoescape=True)
renderer = Jinja2Renderer("templates", config=custom_config)

# Use default config
renderer = Jinja2Renderer("templates")  # Uses RenderConfig()
```

---

## Pattern Interactions

### How Patterns Work Together

```
User Code
    │
    ▼
┌─────────────────┐
│ Facade Pattern  │  Simplified imports
│ (__init__.py)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ABC Pattern     │  Contract definition
│ (base.py)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Adapter Pattern │  Jinja2 integration
│ (jinja2.py)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│Strategy │ │ Dataclass    │
│Pattern  │ │ Pattern      │
│(Config) │ │ (Types)      │
└─────────┘ └──────────────┘
```

---

## Anti-Patterns Avoided

### 1. God Object
**Avoided:** Separated concerns into multiple classes (renderer, config, validators)

### 2. Tight Coupling
**Avoided:** Used ABC and dependency injection

### 3. Magic Strings
**Avoided:** Used type-safe dataclasses and enums

### 4. Implicit Dependencies
**Avoided:** Explicit dependency injection via constructor

### 5. Mutable State
**Avoided:** Dataclasses encourage immutability

---

## See Also

- [Architecture Overview](overview.md) - Module structure
- [Component Relationships](relationships.md) - How components interact
