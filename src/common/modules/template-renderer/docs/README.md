# Template Renderer Module Documentation

**Version:** 1.0
**Last Updated:** 2025-10-18
**Module Location:** `src/dotfiles/modules/template_renderer`

---

## Overview

The Template Renderer module is a generic, agnostic template rendering system built on Jinja2. It provides a clean, type-safe interface for rendering any text-based templates (Dockerfiles, configuration files, scripts, etc.) with comprehensive validation, introspection, and error handling.

### Key Features

- **Template Agnostic** - Works with any text-based content
- **Strict Validation** - Validates variables before rendering
- **Template Introspection** - Discover template requirements
- **Extensible Design** - Easy to add new template engines
- **Type Safe** - Full type hints throughout
- **Comprehensive Error Handling** - Detailed exception hierarchy

---

## Documentation Structure

This documentation is organized into the following sections:

### 📐 Architecture

- **[Overview](architecture/overview.md)** - Module structure and organization
- **[Design Patterns](architecture/design_patterns.md)** - Patterns and principles used
- **[Component Relationships](architecture/relationships.md)** - How components interact

### 📚 API Reference

- **[Core API](api/core.md)** - TemplateRenderer base class and types
- **[Renderers](api/renderers.md)** - Jinja2Renderer implementation
- **[Validators](api/validators.md)** - Validation utilities
- **[Exceptions](api/exceptions.md)** - Exception hierarchy

### 📖 Guides

- **[Getting Started](guides/getting_started.md)** - Quick start guide
- **[Usage Patterns](guides/usage_patterns.md)** - Common usage patterns
- **[Integration](guides/integration.md)** - Integration with other modules
- **[Best Practices](guides/best_practices.md)** - Recommended practices

### 🔧 Reference

- **[Configuration](reference/configuration.md)** - RenderConfig options
- **[Examples](reference/examples.md)** - Comprehensive code examples
- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions
- **[Advanced Topics](reference/advanced.md)** - Security, performance, extensibility

---

## Quick Start

### Installation

This is a standalone UV project. Install as a path dependency:

```toml
[tool.uv.sources]
dotfiles-template-renderer = { path = "../common/modules/template_renderer" }
```

### Basic Usage

```python
from dotfiles_template_renderer import Jinja2Renderer

# Create renderer
renderer = Jinja2Renderer(template_dir="templates")

# Render a template
result = renderer.render(
    template_name="app.j2",
    variables={
        "name": "myapp",
        "version": "1.0.0",
        "port": 8080,
    }
)

print(result)
```

### With Validation

```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

# Enable strict mode (default)
renderer = Jinja2Renderer(
    template_dir="templates",
    config=RenderConfig(strict_mode=True)
)

# Validate before rendering
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
else:
    result = renderer.render("app.j2", variables={"name": "myapp"})
```

---

## Module Structure

```
template_renderer/
├── __init__.py              # Public API exports
├── README.md                # User-facing documentation
├── validators.py            # Validation utilities
├── core/                    # Core abstractions
│   ├── __init__.py
│   ├── base.py             # TemplateRenderer ABC
│   ├── exceptions.py       # Exception hierarchy
│   └── types.py            # Data models
├── renderers/               # Implementations
│   ├── __init__.py
│   └── jinja2.py           # Jinja2 implementation
└── docs/                    # Documentation
    ├── README.md           # This file
    ├── architecture/       # Architecture docs
    ├── api/                # API reference
    ├── guides/             # User guides
    └── reference/          # Reference materials
```

---

## Public API

### Classes

- **`TemplateRenderer`** - Abstract base class for all renderers
- **`Jinja2Renderer`** - Jinja2 implementation
- **`RenderConfig`** - Configuration dataclass
- **`TemplateContext`** - Context dataclass for rendering
- **`TemplateInfo`** - Template metadata dataclass
- **`ValidationResult`** - Validation result dataclass

### Exceptions

- **`TemplateError`** - Base exception
- **`TemplateNotFoundError`** - Template file not found
- **`TemplateRenderError`** - Rendering failed
- **`ValidationError`** - Validation failed
- **`MissingVariableError`** - Required variables missing
- **`InvalidVariableError`** - Invalid variable value

### Functions

- **`extract_jinja2_variables(template_source, env)`** - Extract variables from template
- **`validate_variables(template_name, required_vars, provided_vars, strict)`** - Validate variables
- **`validate_variable_types(variables, expected_types)`** - Validate variable types

---

## Core Concepts

### Template Agnosticism

The module doesn't care what it's rendering. It can render:
- Dockerfiles
- Configuration files (YAML, JSON, INI, etc.)
- Scripts (Bash, Python, etc.)
- HTML/XML documents
- Any text-based content

### Strict vs. Lenient Modes

**Strict Mode (default):**
- Validates all variables before rendering
- Fails fast on missing variables
- Prevents generating invalid output

**Lenient Mode:**
- Allows missing variables
- Uses template defaults
- More flexible but less safe

### Validation-First Approach

The module emphasizes validation before rendering:
1. Extract required variables from template
2. Validate provided variables
3. Render only if validation passes (strict mode)

---

## Integration Points

### Pipeline Integration

Used by `RenderTemplateStep` in pipeline_steps.container_steps:

```python
from src.pipeline_steps.container_steps import RenderTemplateStep

step = RenderTemplateStep(
    template_name="Dockerfile.j2",
    template_dir="templates",
    variables={"base_image": "python:3.12"},
    output_key="dockerfile",
)
```

### Container Manager Integration

Renders Dockerfiles before passing to container_manager:

```python
from dotfiles_template_renderer import Jinja2Renderer
from dotfiles_container_manager import DockerManager

renderer = Jinja2Renderer("templates")
dockerfile = renderer.render("python.j2", variables={...})

manager = DockerManager()
manager.build_image(BuildContext(dockerfile_content=dockerfile, ...))
```

---

## Design Philosophy

1. **Separation of Concerns** - Template rendering separate from content semantics
2. **Fail Fast** - Catch errors early through validation
3. **Type Safety** - Full type hints for better IDE support
4. **Extensibility** - Easy to add new template engines
5. **Explicit Over Implicit** - Clear, explicit configuration

---

## Next Steps

- **New Users:** Start with [Getting Started](guides/getting_started.md)
- **API Reference:** See [Core API](api/core.md) and [Renderers](api/renderers.md)
- **Integration:** Read [Integration Guide](guides/integration.md)
- **Advanced Usage:** Check [Advanced Topics](reference/advanced.md)

---

## Contributing

When extending the module:
1. Subclass `TemplateRenderer` for new engines
2. Implement all abstract methods
3. Use existing type definitions
4. Add comprehensive tests
5. Update documentation

---

## License

Part of the dotfiles project. See project LICENSE for details.
