# Template Renderer Module

A generic, agnostic template rendering module using Jinja2. This module is completely independent of what it's rendering - it can render Dockerfiles, configuration files, scripts, or any text-based template.

## Features

- **Template Agnostic**: Renders any text-based template, not just Dockerfiles
- **Jinja2 Powered**: Full Jinja2 template engine support
- **Strict Validation**: Ensures all template variables are provided
- **Variable Introspection**: Discover what variables a template requires
- **Flexible Configuration**: Customizable rendering behavior
- **Type Safe**: Full type hints and Pydantic validation

## Installation

This module is a standalone UV project. Install it as a path dependency:

```toml
[project]
dependencies = [
    "dotfiles-template-renderer",
]

[tool.uv.sources]
dotfiles-template-renderer = { path = "../common/modules/template_renderer" }
```

Or install directly with uv:

```bash
cd src/common/modules/template_renderer
uv sync
```

## Quick Start

### Basic Usage

```python
from pathlib import Path
from dotfiles_template_renderer import Jinja2Renderer

# Create renderer
renderer = Jinja2Renderer(template_dir=Path("templates"))

# Render a template
result = renderer.render(
    template_name="app.j2",
    variables={
        "app_name": "myapp",
        "version": "1.0.0",
        "port": 8080,
    }
)

print(result)
```

### With Strict Validation

```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

# Enable strict mode (fail on missing variables)
renderer = Jinja2Renderer(
    template_dir="templates",
    config=RenderConfig(strict_mode=True)
)

try:
    result = renderer.render("app.j2", variables={"app_name": "myapp"})
except MissingVariableError as e:
    print(f"Missing variables: {e.missing_variables}")
```

### Template Introspection

```python
# Discover what variables a template needs
variables = renderer.get_template_variables("app.j2")
print(f"Required variables: {variables}")

# Validate before rendering
validation = renderer.validate("app.j2", variables={"app_name": "myapp"})
if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    print(f"Unused: {validation.unused_variables}")
```

### List Available Templates

```python
# Get all templates in directory
templates = renderer.get_available_templates()
for template in templates:
    print(f"- {template}")

# Get detailed info about a template
info = renderer.get_template_info("app.j2")
print(f"Template: {info.name}")
print(f"Size: {info.size} bytes")
print(f"Required variables: {info.required_variables}")
```

## Configuration

### RenderConfig Options

```python
from dotfiles_template_renderer import RenderConfig

config = RenderConfig(
    strict_mode=True,              # Fail on missing variables
    autoescape=False,              # Enable HTML/XML autoescaping
    trim_blocks=True,              # Remove first newline after tag
    lstrip_blocks=True,            # Strip leading spaces
    keep_trailing_newline=True,    # Keep trailing newline
    custom_filters={},             # Custom Jinja2 filters
    custom_tests={},               # Custom Jinja2 tests
    custom_globals={},             # Custom global functions
)
```

### Settings (settings.toml)

```toml
[template_renderer]
template_directory = "src/dotfiles-installer/docker/templates"
default_template = "python.j2"
strict_mode = true
```

## Template Format

Templates use standard Jinja2 syntax:

```jinja2
{# This is a comment - can be used for template description #}
FROM {{ base_image | default('python:3.12') }}

LABEL maintainer="{{ maintainer }}"
LABEL version="{{ version }}"

{% if system_packages %}
RUN apt-get update && apt-get install -y \
{% for package in system_packages %}
    {{ package }}{% if not loop.last %} \{% endif %}
{% endfor %}
{% endif %}

WORKDIR {{ workdir | default('/app') }}

{% if env_vars %}
{% for key, value in env_vars.items() %}
ENV {{ key }}="{{ value }}"
{% endfor %}
{% endif %}

COPY . .

{% if entrypoint %}
ENTRYPOINT {{ entrypoint | tojson }}
{% endif %}

{% if cmd %}
CMD {{ cmd | tojson }}
{% endif %}
```

## API Reference

### Jinja2Renderer

Main renderer class for Jinja2 templates.

#### Methods

- `render(template_name, variables, **kwargs)` - Render a template
- `validate(template_name, variables)` - Validate variables against template
- `get_template_variables(template_name)` - Get list of variables in template
- `get_available_templates()` - List all available templates
- `get_template_info(template_name)` - Get detailed template information
- `render_to_file(template_name, output_path, variables)` - Render and save to file

### Exceptions

- `TemplateError` - Base exception for template errors
- `TemplateNotFoundError` - Template file not found
- `TemplateRenderError` - Template rendering failed
- `ValidationError` - Template validation failed
- `MissingVariableError` - Required variables missing
- `InvalidVariableError` - Variable has invalid value

## Examples

### Render Dockerfile Template

```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer("templates")

dockerfile = renderer.render(
    "python.j2",
    variables={
        "base_image": "python:3.12-slim",
        "workdir": "/app",
        "system_packages": ["git", "curl"],
        "env_vars": {"PYTHONUNBUFFERED": "1"},
        "entrypoint": ["python"],
        "cmd": ["app.py"],
    }
)

print(dockerfile)
```

### Render Configuration File

```python
config_content = renderer.render(
    "nginx.conf.j2",
    variables={
        "server_name": "example.com",
        "port": 80,
        "root_dir": "/var/www/html",
        "ssl_enabled": True,
    }
)

# Save to file
renderer.render_to_file(
    "nginx.conf.j2",
    "/etc/nginx/sites-available/mysite",
    variables={...}
)
```

### Custom Filters

```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

def uppercase_filter(text):
    return text.upper()

config = RenderConfig(
    custom_filters={"uppercase": uppercase_filter}
)

renderer = Jinja2Renderer("templates", config=config)

# In template: {{ name | uppercase }}
result = renderer.render("greeting.j2", variables={"name": "world"})
```

## Integration with Pipeline

```python
from src.pipeline_steps.container_steps import RenderTemplateStep
from src.modules.pipeline import Pipeline, PipelineContext

# Create pipeline step
step = RenderTemplateStep(
    template_name="app.j2",
    template_dir="templates",
    variables={"app_name": "myapp"},
    output_key="app_config",
)

# Run in pipeline
pipeline = Pipeline.create([step])
context = pipeline.run(context)

# Access rendered content
rendered = context.results["app_config"]
```

## Best Practices

1. **Use Strict Mode**: Enable `strict_mode=True` to catch missing variables early
2. **Validate First**: Use `validate()` before rendering in production
3. **Template Comments**: Add description comments at the top of templates
4. **Default Values**: Use Jinja2 filters like `| default('value')` for optional variables
5. **Organize Templates**: Group related templates in subdirectories
6. **Version Templates**: Include version info in template comments

## Testing

```python
import pytest
from dotfiles_template_renderer import Jinja2Renderer, MissingVariableError

def test_render_template():
    renderer = Jinja2Renderer("tests/fixtures/templates")

    result = renderer.render(
        "test.j2",
        variables={"name": "test"}
    )

    assert "test" in result

def test_missing_variable():
    renderer = Jinja2Renderer("tests/fixtures/templates")

    with pytest.raises(MissingVariableError):
        renderer.render("test.j2", variables={})
```

## Troubleshooting

### Template Not Found

```python
# Check available templates
templates = renderer.get_available_templates()
print(f"Available: {templates}")

# Check template directory
print(f"Template dir: {renderer.template_dir}")
print(f"Exists: {renderer.template_dir.exists()}")
```

### Missing Variables

```python
# Validate before rendering
validation = renderer.validate("app.j2", variables={...})
if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    print(f"Required: {validation.required_variables}")
```

### Rendering Errors

```python
try:
    result = renderer.render("app.j2", variables={...})
except TemplateRenderError as e:
    print(f"Error: {e.message}")
    print(f"Template: {e.template_name}")
    if e.original_error:
        print(f"Original: {e.original_error}")
```
