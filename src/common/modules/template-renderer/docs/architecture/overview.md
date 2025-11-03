# Architecture Overview

**Module:** template_renderer
**Purpose:** Generic, agnostic template rendering with Jinja2
**Design:** Layered architecture with abstract base and concrete implementations

---

## Module Structure

```
template_renderer/
├── __init__.py              # Public API exports
├── README.md                # User-facing documentation
├── validators.py            # Validation utilities
├── core/                    # Core abstractions
│   ├── __init__.py         # Core exports
│   ├── base.py             # TemplateRenderer ABC
│   ├── exceptions.py       # Exception hierarchy
│   └── types.py            # Data models
└── renderers/               # Implementations
    ├── __init__.py         # Renderer exports
    └── jinja2.py           # Jinja2 implementation
```

---

## Layered Architecture

The module follows a **layered architecture** with clear separation of concerns:

### Layer 1: Core Abstractions (`core/`)

**Purpose:** Define contracts and interfaces

**Components:**
- `base.py` - TemplateRenderer abstract base class
- `types.py` - Data models (RenderConfig, TemplateContext, ValidationResult, TemplateInfo)
- `exceptions.py` - Exception hierarchy

**Responsibilities:**
- Define renderer contract (abstract methods)
- Provide type definitions
- Define exception hierarchy
- Provide concrete helper methods

**Dependencies:** None (only Python stdlib and typing)

### Layer 2: Implementations (`renderers/`)

**Purpose:** Concrete template engine implementations

**Components:**
- `jinja2.py` - Jinja2Renderer implementation

**Responsibilities:**
- Implement TemplateRenderer contract
- Integrate with Jinja2 library
- Handle Jinja2-specific logic
- Wrap Jinja2 exceptions

**Dependencies:**
- Core layer (base, types, exceptions)
- Jinja2 library
- Validators module

### Layer 3: Utilities (root level)

**Purpose:** Shared utilities across implementations

**Components:**
- `validators.py` - Variable extraction and validation

**Responsibilities:**
- Extract variables from templates
- Validate variables against requirements
- Type checking utilities

**Dependencies:**
- Core types (ValidationResult)
- Jinja2 library (for AST parsing)

### Layer 4: Public API (`__init__.py`)

**Purpose:** Clean, organized public interface

**Components:**
- Exports from core, renderers, and validators
- Organized by category

**Responsibilities:**
- Expose public API
- Hide internal implementation details
- Provide single import point

**Dependencies:** All other layers

---

## Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    Public API (__init__.py)              │
│  Exports: TemplateRenderer, Jinja2Renderer, RenderConfig│
│           ValidationResult, Exceptions, Validators       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Core Layer   │ │Renderers │ │ Validators   │
│              │ │Layer     │ │ Module       │
│ - base.py    │ │          │ │              │
│ - types.py   │ │-jinja2.py│ │-validators.py│
│ - exceptions │ │          │ │              │
└──────────────┘ └─────┬────┘ └──────────────┘
                       │
                       │ implements
                       ▼
              ┌─────────────────┐
              │TemplateRenderer │
              │      (ABC)      │
              └─────────────────┘
```

---

## Data Flow

### Rendering Flow

```
User Code
    │
    ├─── RenderConfig ───┐
    ├─── template_name   │
    └─── variables       │
                         ▼
              ┌──────────────────┐
              │ Jinja2Renderer   │
              └────────┬─────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
  ┌──────────────┐          ┌──────────────┐
  │  validate()  │          │   render()   │
  │              │          │              │
  │ 1. Extract   │          │ 1. Merge     │
  │    variables │          │    variables │
  │ 2. Validate  │          │ 2. Validate  │
  │ 3. Return    │          │    (strict)  │
  │    result    │          │ 3. Get       │
  │              │          │    template  │
  │              │          │ 4. Render    │
  └──────┬───────┘          └──────┬───────┘
         │                         │
         ▼                         ▼
  ┌──────────────────┐      ┌─────────┐
  │ ValidationResult │      │  string │
  └──────────────────┘      └─────────┘
```

### Validation Flow

```
Template Source
    │
    ▼
extract_jinja2_variables()
    │
    ├─── Try AST parsing
    │    └─── jinja2.meta.find_undeclared_variables()
    │
    └─── Fallback to regex
         └─── extract_variables_regex()
    │
    ▼
set of required variables
    │
    ▼
validate_variables()
    │
    ├─── Calculate missing = required - provided
    ├─── Calculate unused = provided - required
    ├─── Generate errors (strict mode)
    └─── Generate warnings
    │
    ▼
ValidationResult
```

---

## Design Patterns

### 1. Abstract Base Class (ABC) Pattern

**Used In:** TemplateRenderer

**Purpose:** Define contract for all renderers

**Benefits:**
- Enforces consistent interface
- Allows multiple implementations
- Enables polymorphism

**Implementation:**
```python
class TemplateRenderer(ABC):
    @abstractmethod
    def render(self, template_name, variables, **kwargs) -> str:
        pass

    @abstractmethod
    def validate(self, template_name, variables) -> ValidationResult:
        pass

    # ... other abstract methods
```

### 2. Template Method Pattern

**Used In:** TemplateRenderer base class

**Purpose:** Define workflow, let subclasses implement details

**Benefits:**
- Consistent workflow across implementations
- Reusable concrete methods
- Extensible design

**Implementation:**
```python
class TemplateRenderer(ABC):
    def render_from_context(self, context: TemplateContext) -> str:
        # Template method - defines workflow
        original_config = self.config
        if context.config:
            self.config = context.config
        try:
            return self.render(context.template_name, context.variables)
        finally:
            self.config = original_config
```

### 3. Adapter Pattern

**Used In:** Jinja2Renderer

**Purpose:** Adapt Jinja2 API to TemplateRenderer interface

**Benefits:**
- Hides Jinja2 complexity
- Provides consistent interface
- Easy to swap implementations

**Implementation:**
```python
class Jinja2Renderer(TemplateRenderer):
    def render(self, template_name, variables, **kwargs):
        # Adapts Jinja2's API to our interface
        template = self._env.get_template(template_name)
        return template.render(**variables)
```

### 4. Facade Pattern

**Used In:** Public API (__init__.py)

**Purpose:** Simplify complex subsystem

**Benefits:**
- Single import point
- Hides internal structure
- Clean public API

**Implementation:**
```python
# __init__.py
from .core import TemplateRenderer, RenderConfig, ...
from .renderers import Jinja2Renderer
from .validators import extract_jinja2_variables, ...

__all__ = [...]
```

### 5. Strategy Pattern

**Used In:** RenderConfig

**Purpose:** Configure behavior without subclassing

**Benefits:**
- Flexible configuration
- Runtime behavior changes
- No subclassing needed

**Implementation:**
```python
config = RenderConfig(
    strict_mode=True,  # Strategy for validation
    autoescape=False,  # Strategy for escaping
    custom_filters={...},  # Strategy for filtering
)
```

---

## Dependency Graph

```
┌─────────────────┐
│  User Code      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  __init__.py    │
│  (Public API)   │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    │         │            │          │
    ▼         ▼            ▼          ▼
┌────────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
│ base.py│ │types │ │exceptions│ │validators│
└────────┘ └──────┘ └──────────┘ └──────────┘
    ▲         ▲            ▲          ▲
    │         │            │          │
    └─────────┴────────────┴──────────┘
                   │
                   ▼
            ┌──────────────┐
            │  jinja2.py   │
            │ (Renderer)   │
            └──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │ Jinja2 Lib   │
            │ (External)   │
            └──────────────┘
```

---

## Key Design Decisions

### 1. Separation of Core and Implementations

**Decision:** Keep abstract base separate from concrete implementations

**Rationale:**
- Easy to add new template engines
- Clear contracts and interfaces
- Testable in isolation

**Trade-off:** More files and indirection, but better maintainability

### 2. Validators as Separate Module

**Decision:** Keep validators separate from renderers

**Rationale:**
- Reusable across different renderers
- Can be used standalone
- Single responsibility

**Trade-off:** Extra module, but better separation of concerns

### 3. Dataclasses for Configuration

**Decision:** Use dataclasses instead of dicts or classes

**Rationale:**
- Type safety
- Default values
- Immutability (by convention)
- IDE support

**Trade-off:** Requires Python 3.7+, but worth it for type safety

### 4. Strict Mode by Default

**Decision:** Enable strict_mode=True by default

**Rationale:**
- Fail fast
- Catch errors early
- Prevent invalid output

**Trade-off:** Less flexible, but safer

### 5. AST Parsing with Regex Fallback

**Decision:** Use Jinja2 AST parser with regex fallback

**Rationale:**
- AST parsing is more accurate
- Regex fallback ensures robustness
- Best of both worlds

**Trade-off:** More complex, but more reliable

---

## Extension Points

The architecture provides several extension points:

1. **New Template Engines:** Subclass TemplateRenderer
2. **Custom Validators:** Add functions to validators.py
3. **Custom Exceptions:** Subclass existing exceptions
4. **Custom Configuration:** Extend RenderConfig
5. **Custom Filters/Tests:** Use RenderConfig.custom_filters/tests

---

## Future Considerations

Potential architectural improvements:

1. **Plugin System:** Dynamic renderer discovery
2. **Caching Layer:** Cache compiled templates and results
3. **Async Support:** Async rendering methods
4. **Streaming:** Stream large template outputs
5. **Template Registry:** Central template management
