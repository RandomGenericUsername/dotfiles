# Code Examples

Comprehensive collection of code examples for the template_renderer module.

---

## Basic Usage

### Example 1: Simple Rendering

```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer("templates")
result = renderer.render("hello.j2", variables={"name": "World"})
print(result)
```

### Example 2: Rendering with Multiple Variables

```python
variables = {
    "name": "myapp",
    "version": "1.0.0",
    "port": 8080,
    "debug": False,
}

result = renderer.render("app.j2", variables=variables)
```

### Example 3: Using Kwargs

```python
result = renderer.render("app.j2", name="myapp", version="1.0.0", port=8080)
```

---

## Validation

### Example 4: Pre-Validation

```python
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    print(f"Required: {validation.required_variables}")
else:
    result = renderer.render("app.j2", variables={"name": "myapp"})
```

### Example 5: Strict Mode

```python
from dotfiles_template_renderer import RenderConfig, MissingVariableError

renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing variables: {e.missing_variables}")
```

### Example 6: Lenient Mode

```python
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))

# Template must have defaults: {{ version | default('1.0.0') }}
result = renderer.render("app.j2", variables={"name": "myapp"})
```

---

## Template Introspection

### Example 7: Get Template Variables

```python
variables = renderer.get_template_variables("app.j2")
print(f"Required variables: {variables}")
# Output: ['base_image', 'name', 'port', 'version', 'workdir']
```

### Example 8: List Available Templates

```python
templates = renderer.get_available_templates()
for template in templates:
    print(f"- {template}")
```

### Example 9: Get Template Info

```python
info = renderer.get_template_info("app.j2")
print(f"Name: {info.name}")
print(f"Path: {info.path}")
print(f"Size: {info.size} bytes")
print(f"Variables: {info.required_variables}")
```

---

## Custom Filters

### Example 10: Simple Filter

```python
def uppercase_filter(text):
    return text.upper()

config = RenderConfig(custom_filters={"uppercase": uppercase_filter})
renderer = Jinja2Renderer("templates", config=config)

# Template: {{ name | uppercase }}
result = renderer.render("app.j2", variables={"name": "myapp"})
# Output: MYAPP
```

### Example 11: Multiple Filters

```python
def format_bytes(bytes):
    return f"{bytes / 1024:.2f} KB"

def truncate(text, length=50):
    return text[:length] + "..." if len(text) > length else text

config = RenderConfig(
    custom_filters={
        "uppercase": lambda x: x.upper(),
        "format_bytes": format_bytes,
        "truncate": truncate,
    }
)
```

---

## File Operations

### Example 12: Render to File

```python
renderer.render_to_file(
    "nginx.conf.j2",
    "/etc/nginx/sites-available/mysite",
    variables={"server_name": "example.com", "port": 80}
)
```

### Example 13: Batch Rendering to Files

```python
templates = [
    ("app.j2", "output/app.txt", {"name": "app1"}),
    ("config.j2", "output/config.yaml", {"env": "prod"}),
]

for template, output, vars in templates:
    renderer.render_to_file(template, output, vars)
```

---

## Error Handling

### Example 14: Specific Exception Handling

```python
from dotfiles_template_renderer import (
    MissingVariableError,
    TemplateNotFoundError,
    TemplateRenderError,
)

try:
    result = renderer.render("app.j2", variables={...})
except MissingVariableError as e:
    print(f"Missing: {e.missing_variables}")
except TemplateNotFoundError as e:
    print(f"Template not found: {e.template_name}")
except TemplateRenderError as e:
    print(f"Rendering failed: {e.message}")
```

### Example 15: Catch All Template Errors

```python
from dotfiles_template_renderer import TemplateError

try:
    result = renderer.render("app.j2", variables={...})
except TemplateError as e:
    print(f"Error: {e.message}")
```

---

## Advanced Templates

### Example 16: Template with Loops

```python
# Template
"""
FROM {{ base_image }}
{% for package in system_packages %}
RUN apt-get install -y {{ package }}
{% endfor %}
"""

variables = {
    "base_image": "python:3.12",
    "system_packages": ["git", "curl", "vim"],
}

result = renderer.render("dockerfile.j2", variables)
```

### Example 17: Template with Conditionals

```python
# Template
"""
FROM {{ base_image }}
{% if install_dev_tools %}
RUN apt-get update && apt-get install -y git vim
{% endif %}
"""

variables = {
    "base_image": "python:3.12",
    "install_dev_tools": True,
}

result = renderer.render("dockerfile.j2", variables)
```

### Example 18: Template Inheritance

```python
# base.j2
"""
FROM {{ base_image }}
{% block packages %}{% endblock %}
{% block app %}{% endblock %}
"""

# python.j2
"""
{% extends "base.j2" %}
{% block packages %}
RUN pip install {{ packages | join(' ') }}
{% endblock %}
{% block app %}
COPY . .
CMD ["python", "{{ entrypoint }}"]
{% endblock %}
"""

result = renderer.render("python.j2", variables={
    "base_image": "python:3.12",
    "packages": ["flask", "requests"],
    "entrypoint": "app.py"
})
```

---

## Integration Examples

### Example 19: Pipeline Integration

```python
from src.modules.pipeline import Pipeline
from src.pipeline_steps.container_steps import RenderTemplateStep

step = RenderTemplateStep(
    template_name="Dockerfile.j2",
    template_dir="templates",
    variables={"base_image": "python:3.12"},
    output_key="dockerfile",
)

pipeline = Pipeline.create([step])
context = pipeline.run(context)
```

### Example 20: Container Manager Integration

```python
from dotfiles_container_manager import DockerManager, BuildContext

# Render Dockerfile
dockerfile = renderer.render("python.j2", variables={...})

# Build image
manager = DockerManager()
build_context = BuildContext(
    dockerfile_content=dockerfile,
    context_dir=Path("."),
    tag="myapp:latest",
)
manager.build_image(build_context)
```

### Example 21: CLI Integration

```python
import click

@click.command()
@click.argument("template")
@click.option("--vars", help="Variables as JSON")
def render(template, vars):
    renderer = Jinja2Renderer("templates")
    variables = json.loads(vars) if vars else {}
    result = renderer.render(template, variables=variables)
    click.echo(result)
```

---

## Configuration Examples

### Example 22: Production Config

```python
config = RenderConfig(
    strict_mode=True,
    autoescape=True,
    undefined_behavior="strict",
)
renderer = Jinja2Renderer("templates", config=config)
```

### Example 23: Development Config

```python
config = RenderConfig(
    strict_mode=False,
    autoescape=False,
    undefined_behavior="debug",
)
renderer = Jinja2Renderer("templates", config=config)
```

### Example 24: Custom Globals

```python
import datetime

config = RenderConfig(
    custom_globals={
        "now": datetime.datetime.now,
        "version": "1.0.0",
    }
)

# Template: Generated at {{ now() }}, Version {{ version }}
```

---

## Testing Examples

### Example 25: Unit Test

```python
import pytest

def test_render_basic():
    renderer = Jinja2Renderer("tests/fixtures/templates")
    result = renderer.render("simple.j2", variables={"name": "test"})
    assert "test" in result

def test_missing_variables():
    renderer = Jinja2Renderer("tests/fixtures/templates")
    with pytest.raises(MissingVariableError):
        renderer.render("app.j2", variables={"name": "test"})
```

### Example 26: Validation Test

```python
def test_validate():
    renderer = Jinja2Renderer("tests/fixtures/templates")
    validation = renderer.validate("app.j2", variables={"name": "test"})
    assert not validation.is_valid
    assert "version" in validation.missing_variables
```

---

## Real-World Examples

### Example 27: Dockerfile Generation

```python
renderer = Jinja2Renderer("dockerfiles")

dockerfile = renderer.render("python.j2", variables={
    "base_image": "python:3.12-slim",
    "workdir": "/app",
    "system_packages": ["git", "curl"],
    "python_packages": ["flask", "requests", "pytest"],
    "entrypoint": "app.py",
})

with open("Dockerfile", "w") as f:
    f.write(dockerfile)
```

### Example 28: Nginx Config Generation

```python
renderer = Jinja2Renderer("configs")

nginx_config = renderer.render("nginx.j2", variables={
    "server_name": "example.com",
    "port": 80,
    "ssl_enabled": True,
    "ssl_cert": "/etc/ssl/certs/example.com.crt",
    "ssl_key": "/etc/ssl/private/example.com.key",
    "proxy_pass": "http://localhost:8080",
})

renderer.render_to_file("nginx.j2", "/etc/nginx/sites-available/example", variables)
```

### Example 29: Multi-Environment Deployment

```python
environments = {
    "dev": {"debug": True, "db_host": "localhost"},
    "staging": {"debug": False, "db_host": "staging-db"},
    "prod": {"debug": False, "db_host": "prod-db"},
}

for env, vars in environments.items():
    output = f"config/{env}.yaml"
    renderer.render_to_file("app.yaml.j2", output, vars)
```

### Example 30: Interactive Template Wizard

```python
def template_wizard():
    renderer = Jinja2Renderer("templates")

    # List templates
    templates = renderer.get_available_templates()
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template}")

    # Select template
    choice = int(input("Select template: ")) - 1
    template_name = templates[choice]

    # Get required variables
    required = renderer.get_template_variables(template_name)

    # Collect variables
    variables = {}
    for var in required:
        variables[var] = input(f"Enter {var}: ")

    # Render
    result = renderer.render(template_name, variables=variables)

    # Save
    output = input("Output file: ")
    with open(output, "w") as f:
        f.write(result)

    print(f"Rendered to {output}")

template_wizard()
```

---

## See Also

- [Usage Patterns](../guides/usage_patterns.md) - Common patterns
- [Integration Guide](../guides/integration.md) - Integration examples
- [API Reference](../api/core.md) - Detailed API docs
