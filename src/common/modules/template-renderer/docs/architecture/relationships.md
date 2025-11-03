# Component Relationships

This document describes how components in the template_renderer module interact with each other.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Code                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ imports from
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Public API (__init__.py)                      │
│                                                                   │
│  Exports:                                                         │
│  - TemplateRenderer (ABC)                                        │
│  - Jinja2Renderer                                                │
│  - RenderConfig, TemplateContext, ValidationResult, TemplateInfo│
│  - Exceptions (TemplateError, MissingVariableError, etc.)       │
│  - Validators (extract_jinja2_variables, validate_variables)    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Core Layer   │    │ Renderers    │    │ Validators   │
│              │    │ Layer        │    │ Module       │
│ - base.py    │◄───│              │◄───│              │
│ - types.py   │    │ - jinja2.py  │    │-validators.py│
│ - exceptions │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## Dependency Graph

### Module-Level Dependencies

```
validators.py
    │
    ├─── depends on ───> core/types.py (ValidationResult)
    └─── depends on ───> jinja2 (external)

renderers/jinja2.py
    │
    ├─── depends on ───> core/base.py (TemplateRenderer)
    ├─── depends on ───> core/types.py (RenderConfig, ValidationResult, TemplateInfo)
    ├─── depends on ───> core/exceptions.py (all exceptions)
    ├─── depends on ───> validators.py (extract_jinja2_variables, validate_variables)
    └─── depends on ───> jinja2 (external)

core/base.py
    │
    ├─── depends on ───> core/types.py (RenderConfig, TemplateContext, ValidationResult, TemplateInfo)
    └─── depends on ───> core/exceptions.py (TemplateNotFoundError)

core/types.py
    │
    └─── depends on ───> Python stdlib only (dataclasses, typing, pathlib)

core/exceptions.py
    │
    └─── depends on ───> Python stdlib only (typing)

__init__.py
    │
    ├─── depends on ───> core/*
    ├─── depends on ───> renderers/*
    └─── depends on ───> validators.py
```

### Dependency Rules

1. **Core has no internal dependencies** - Only depends on Python stdlib
2. **Validators depend on core types** - Uses ValidationResult
3. **Renderers depend on everything** - Uses core, validators, external libs
4. **Public API depends on all layers** - Aggregates exports

---

## Class Relationships

### Inheritance Hierarchy

```
ABC (Python stdlib)
    │
    └─── TemplateRenderer (abstract)
            │
            └─── Jinja2Renderer (concrete)
                    │
                    └─── (Future: MakoRenderer, MustacheRenderer, etc.)

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

### Composition Relationships

```
Jinja2Renderer
    │
    ├─── has-a ───> RenderConfig
    ├─── has-a ───> Path (template_dir)
    └─── has-a ───> Environment (Jinja2)

TemplateContext
    │
    ├─── has-a ───> str (template_name)
    ├─── has-a ───> dict (variables)
    └─── has-a ───> RenderConfig

ValidationResult
    │
    ├─── has-a ───> bool (is_valid)
    ├─── has-a ───> list[str] (missing_variables)
    ├─── has-a ───> list[str] (unused_variables)
    ├─── has-a ───> list[str] (required_variables)
    ├─── has-a ───> list[str] (errors)
    └─── has-a ───> list[str] (warnings)

TemplateInfo
    │
    ├─── has-a ───> str (name)
    ├─── has-a ───> Path (path)
    ├─── has-a ───> int (size)
    ├─── has-a ───> list[str] (required_variables)
    ├─── has-a ───> list[str] (optional_variables)
    └─── has-a ───> str | None (description)
```

---

## Data Flow Diagrams

### Rendering Flow

```
┌──────────────┐
│  User Code   │
└──────┬───────┘
       │
       │ calls render(template_name, variables)
       ▼
┌──────────────────┐
│ Jinja2Renderer   │
└──────┬───────────┘
       │
       │ 1. Merge variables
       ▼
┌──────────────────┐
│ _merge_variables │
└──────┬───────────┘
       │
       │ 2. Validate (if strict_mode)
       ▼
┌──────────────────┐
│ validate()       │
└──────┬───────────┘
       │
       │ 3. Extract variables
       ▼
┌──────────────────────────┐
│ extract_jinja2_variables │
└──────┬───────────────────┘
       │
       │ 4. Validate variables
       ▼
┌──────────────────┐
│validate_variables│
└──────┬───────────┘
       │
       │ 5. Get template
       ▼
┌──────────────────┐
│ _env.get_template│
└──────┬───────────┘
       │
       │ 6. Render
       ▼
┌──────────────────┐
│ template.render  │
└──────┬───────────┘
       │
       │ 7. Return result
       ▼
┌──────────────┐
│  User Code   │
└──────────────┘
```

### Validation Flow

```
┌──────────────┐
│  User Code   │
└──────┬───────┘
       │
       │ calls validate(template_name, variables)
       ▼
┌──────────────────┐
│ Jinja2Renderer   │
└──────┬───────────┘
       │
       │ 1. Get template source
       ▼
┌──────────────────┐
│ _get_template_   │
│    source()      │
└──────┬───────────┘
       │
       │ 2. Extract variables
       ▼
┌──────────────────────────┐
│ extract_jinja2_variables │
└──────┬───────────────────┘
       │
       │ 3. Validate
       ▼
┌──────────────────┐
│validate_variables│
└──────┬───────────┘
       │
       │ 4. Return ValidationResult
       ▼
┌──────────────┐
│  User Code   │
└──────────────┘
```

### Template Discovery Flow

```
┌──────────────┐
│  User Code   │
└──────┬───────┘
       │
       │ calls get_available_templates()
       ▼
┌──────────────────┐
│ Jinja2Renderer   │
└──────┬───────────┘
       │
       │ 1. List template files
       ▼
┌──────────────────┐
│ _env.list_       │
│   templates()    │
└──────┬───────────┘
       │
       │ 2. Sort templates
       ▼
┌──────────────────┐
│ sorted()         │
└──────┬───────────┘
       │
       │ 3. Return list
       ▼
┌──────────────┐
│  User Code   │
└──────────────┘
```

---

## Interaction Patterns

### Pattern 1: Basic Rendering

```
User → Jinja2Renderer.render()
         │
         ├─→ _merge_variables()
         ├─→ validate() (if strict)
         │     └─→ extract_jinja2_variables()
         │     └─→ validate_variables()
         ├─→ _env.get_template()
         └─→ template.render()
```

### Pattern 2: Validation Before Rendering

```
User → Jinja2Renderer.validate()
         │
         ├─→ _get_template_source()
         ├─→ extract_jinja2_variables()
         └─→ validate_variables()
              └─→ return ValidationResult

User → check ValidationResult.is_valid

User → Jinja2Renderer.render() (if valid)
```

### Pattern 3: Template Introspection

```
User → Jinja2Renderer.get_template_variables()
         │
         ├─→ _get_template_source()
         └─→ extract_jinja2_variables()
              └─→ return list[str]

User → Jinja2Renderer.get_template_info()
         │
         ├─→ get_template_variables()
         ├─→ Path.stat()
         └─→ return TemplateInfo
```

### Pattern 4: Context-Based Rendering

```
User → create TemplateContext
         │
         └─→ TemplateContext(template_name, variables, config)

User → Jinja2Renderer.render_from_context()
         │
         ├─→ save original config
         ├─→ override with context.config
         ├─→ render(context.template_name, context.variables)
         └─→ restore original config
```

---

## External Dependencies

### Jinja2 Library

```
Jinja2Renderer
    │
    ├─→ jinja2.Environment
    │     └─→ Used for template compilation and rendering
    │
    ├─→ jinja2.FileSystemLoader
    │     └─→ Used for loading templates from filesystem
    │
    ├─→ jinja2.meta.find_undeclared_variables
    │     └─→ Used for extracting variables from templates
    │
    ├─→ jinja2.TemplateNotFound
    │     └─→ Caught and wrapped in TemplateNotFoundError
    │
    └─→ jinja2.TemplateError
          └─→ Caught and wrapped in TemplateRenderError

validators.py
    │
    └─→ jinja2.Environment
          └─→ Used for AST parsing in extract_jinja2_variables()
```

### Python Standard Library

```
All modules
    │
    ├─→ typing (Type hints)
    ├─→ pathlib.Path (File paths)
    └─→ dataclasses (Data models)

core/base.py
    │
    └─→ abc.ABC, abc.abstractmethod (Abstract base class)

validators.py
    │
    └─→ re (Regex for fallback variable extraction)
```

---

## Integration Points

### Pipeline Integration

```
Pipeline Step (external)
    │
    └─→ Jinja2Renderer.render()
          │
          └─→ Returns rendered string
                │
                └─→ Passed to next pipeline step
```

### Container Manager Integration

```
Container Manager (external)
    │
    └─→ Jinja2Renderer.render()
          │
          └─→ Returns rendered Dockerfile
                │
                └─→ Passed to DockerManager.build_image()
```

---

## Communication Protocols

### Method Call Protocol

1. **User calls public method** (render, validate, etc.)
2. **Renderer validates inputs** (template exists, variables provided)
3. **Renderer delegates to helpers** (_merge_variables, extract_jinja2_variables, etc.)
4. **Helpers return results** (merged variables, extracted variables, etc.)
5. **Renderer processes results** (validate, render, etc.)
6. **Renderer returns to user** (string, ValidationResult, etc.)

### Exception Protocol

1. **Error occurs** (template not found, rendering fails, etc.)
2. **Renderer catches low-level exception** (Jinja2 exception)
3. **Renderer wraps in custom exception** (TemplateNotFoundError, etc.)
4. **Renderer adds context** (template_name, missing_variables, etc.)
5. **Renderer raises custom exception** (propagates to user)
6. **User catches and handles** (specific or base exception)

---

## State Management

### Renderer State

```
Jinja2Renderer
    │
    ├─→ template_dir (immutable after init)
    ├─→ config (mutable, can be changed)
    └─→ _env (internal, recreated when config changes)
```

### Stateless Components

- **validators.py** - Pure functions, no state
- **core/types.py** - Dataclasses, immutable data
- **core/exceptions.py** - Exception classes, no state

---

## See Also

- [Architecture Overview](overview.md) - Module structure
- [Design Patterns](design_patterns.md) - Patterns used
