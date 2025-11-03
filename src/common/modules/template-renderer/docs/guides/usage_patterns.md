# Usage Patterns

This guide documents common usage patterns for the template_renderer module.

---

## Pattern 1: Basic Template Rendering

**Use Case:** Simple template rendering with variables

```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer(template_dir="templates")
result = renderer.render("app.j2", variables={"name": "myapp", "version": "1.0"})
print(result)
```

**When to Use:**
- Simple templates with few variables
- One-off rendering tasks
- Quick prototyping

---

## Pattern 2: Strict Validation

**Use Case:** Ensure all required variables are provided before rendering

```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig, MissingVariableError

renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing: {e.missing_variables}")
    # Provide missing variables and retry
    variables = {"name": "myapp", "version": "1.0", "port": 8080}
    result = renderer.render("app.j2", variables=variables)
```

**When to Use:**
- Production environments
- Critical templates (Dockerfiles, configs)
- When you want to fail fast on errors

---

## Pattern 3: Pre-Validation

**Use Case:** Validate variables before rendering to avoid exceptions

```python
renderer = Jinja2Renderer("templates")

# Validate before rendering
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    print(f"Required: {validation.required_variables}")
    # Collect missing variables
    for var in validation.missing_variables:
        variables[var] = input(f"Enter {var}: ")

# Now safe to render
result = renderer.render("app.j2", variables=variables)
```

**When to Use:**
- Interactive applications
- When you want to collect all missing variables at once
- When you need detailed validation information

---

## Pattern 4: Template Discovery

**Use Case:** List and select from available templates

```python
renderer = Jinja2Renderer("templates")

# List all templates
templates = renderer.get_available_templates()
for i, template in enumerate(templates, 1):
    print(f"{i}. {template}")

# Get template info
choice = int(input("Select template: ")) - 1
template_name = templates[choice]

info = renderer.get_template_info(template_name)
print(f"Variables: {info.required_variables}")
print(f"Size: {info.size} bytes")

# Render selected template
result = renderer.render(template_name, variables={...})
```

**When to Use:**
- Interactive template selection
- Template management tools
- Documentation generation

---

## Pattern 5: Variable Introspection

**Use Case:** Discover required variables dynamically

```python
renderer = Jinja2Renderer("templates")

# Discover required variables
variables = renderer.get_template_variables("app.j2")
print(f"Required: {variables}")

# Prepare variables dynamically
user_vars = {}
for var in variables:
    user_vars[var] = input(f"Enter {var}: ")

result = renderer.render("app.j2", variables=user_vars)
```

**When to Use:**
- Interactive applications
- Template wizards
- Dynamic form generation

---

## Pattern 6: Custom Filters

**Use Case:** Add custom Jinja2 filters for template processing

```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

def uppercase_filter(text):
    return text.upper()

def format_size_filter(bytes):
    return f"{bytes / 1024:.2f} KB"

config = RenderConfig(
    custom_filters={
        "uppercase": uppercase_filter,
        "format_size": format_size_filter,
    }
)

renderer = Jinja2Renderer("templates", config=config)

# In template: {{ name | uppercase }}, {{ size | format_size }}
result = renderer.render("app.j2", variables={"name": "myapp", "size": 2048})
```

**When to Use:**
- Domain-specific formatting
- Reusable transformations
- Complex data processing in templates

---

## Pattern 7: Render to File

**Use Case:** Render template and save directly to file

```python
renderer = Jinja2Renderer("templates")

# Render and save to file
renderer.render_to_file(
    "nginx.conf.j2",
    "/etc/nginx/sites-available/mysite",
    variables={"server_name": "example.com", "port": 80}
)
```

**When to Use:**
- Configuration file generation
- Build scripts
- Deployment automation

---

## Pattern 8: Context-Based Rendering

**Use Case:** Render with temporary configuration override

```python
from dotfiles_template_renderer import Jinja2Renderer, TemplateContext, RenderConfig

renderer = Jinja2Renderer("templates")

# Create context with custom config
context = TemplateContext(
    template_name="app.j2",
    variables={"name": "myapp"},
    config=RenderConfig(strict_mode=False)  # Override for this render
)

result = renderer.render_from_context(context)
```

**When to Use:**
- Different validation modes for different templates
- Temporary configuration changes
- Template-specific settings

---

## Pattern 9: Batch Rendering

**Use Case:** Render multiple templates with different variables

```python
renderer = Jinja2Renderer("templates")

templates_to_render = [
    ("app.j2", {"name": "app1", "version": "1.0"}),
    ("config.j2", {"env": "production", "debug": False}),
    ("script.j2", {"command": "start", "args": ["--verbose"]}),
]

results = {}
for template_name, variables in templates_to_render:
    results[template_name] = renderer.render(template_name, variables)

# Save all results
for template_name, content in results.items():
    output_file = template_name.replace(".j2", "")
    with open(output_file, "w") as f:
        f.write(content)
```

**When to Use:**
- Project generation
- Multi-file configuration
- Batch processing

---

## Pattern 10: Template Selection

**Use Case:** Select template based on criteria

```python
renderer = Jinja2Renderer("templates")

def select_template(app_type):
    templates = {
        "python": "python.j2",
        "node": "node.j2",
        "rust": "rust.j2",
    }
    return templates.get(app_type, "default.j2")

template_name = select_template("python")
result = renderer.render(template_name, variables={"name": "myapp"})
```

**When to Use:**
- Multi-platform support
- Template variants
- Conditional rendering

---

## Pattern 11: Lenient Mode with Defaults

**Use Case:** Allow missing variables with template defaults

```python
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))

# Template can use defaults: {{ version | default('1.0.0') }}
result = renderer.render("app.j2", variables={"name": "myapp"})
# Works even if 'version' not provided
```

**When to Use:**
- Optional variables
- Backward compatibility
- Flexible templates

---

## Pattern 12: Error Handling with Fallback

**Use Case:** Handle errors gracefully with fallback template

```python
from dotfiles_template_renderer import Jinja2Renderer, TemplateError

renderer = Jinja2Renderer("templates")

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except TemplateError as e:
    print(f"Error: {e}")
    # Use fallback template
    result = renderer.render("default.j2", variables={"name": "myapp"})
```

**When to Use:**
- Robust applications
- Graceful degradation
- Default configurations

---

## Advanced Patterns

### Pattern 13: Multi-Environment Configuration

```python
renderer = Jinja2Renderer("config_templates")

environments = {
    "development": {
        "debug": True,
        "log_level": "DEBUG",
        "database_host": "localhost",
    },
    "staging": {
        "debug": False,
        "log_level": "INFO",
        "database_host": "staging-db.example.com",
    },
    "production": {
        "debug": False,
        "log_level": "WARNING",
        "database_host": "prod-db.example.com",
    },
}

for env_name, env_vars in environments.items():
    output_path = f"config/{env_name}.yaml"
    renderer.render_to_file("app.yaml.j2", output_path, env_vars)
```

### Pattern 14: Template Inheritance

```python
# base.j2
"""
FROM {{ base_image }}
WORKDIR {{ workdir }}
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

renderer = Jinja2Renderer("templates")
result = renderer.render("python.j2", variables={
    "base_image": "python:3.12",
    "workdir": "/app",
    "packages": ["flask", "requests"],
    "entrypoint": "app.py"
})
```

### Pattern 15: Template Composition

```python
# header.j2
"""
FROM {{ base_image }}
LABEL maintainer="{{ maintainer }}"
"""

# main.j2
"""
{% include 'header.j2' %}
WORKDIR {{ workdir }}
COPY . .
"""

renderer = Jinja2Renderer("templates")
result = renderer.render("main.j2", variables={
    "base_image": "python:3.12",
    "maintainer": "user@example.com",
    "workdir": "/app"
})
```

### Pattern 16: Conditional Rendering

```python
# Template with conditionals
"""
FROM {{ base_image }}
{% if install_dev_tools %}
RUN apt-get update && apt-get install -y git vim curl
{% endif %}
{% if use_cache %}
RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt
{% else %}
RUN pip install --no-cache-dir -r requirements.txt
{% endif %}
"""

renderer = Jinja2Renderer("templates")
result = renderer.render("dockerfile.j2", variables={
    "base_image": "python:3.12",
    "install_dev_tools": True,
    "use_cache": False
})
```

### Pattern 17: Loop-Based Generation

```python
# Template with loops
"""
FROM {{ base_image }}
{% for package in system_packages %}
RUN apt-get install -y {{ package }}
{% endfor %}
{% for key, value in env_vars.items() %}
ENV {{ key }}={{ value }}
{% endfor %}
"""

renderer = Jinja2Renderer("templates")
result = renderer.render("dockerfile.j2", variables={
    "base_image": "python:3.12",
    "system_packages": ["git", "curl", "vim"],
    "env_vars": {"PYTHONUNBUFFERED": "1", "ENV": "production"}
})
```

---

## See Also

- [Getting Started](getting_started.md) - Basic usage
- [Integration Guide](integration.md) - Integration patterns
- [Best Practices](best_practices.md) - Recommended practices
- [API Reference](../api/core.md) - Detailed API docs
