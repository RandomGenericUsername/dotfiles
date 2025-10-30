# Getting Started with Template Renderer

This guide will help you get started with the template_renderer module.

---

## Installation

The template_renderer module is part of the dotfiles project. No separate installation is required.

---

## Basic Concepts

### What is Template Rendering?

Template rendering is the process of taking a template file with placeholders and replacing those placeholders with actual values to produce final output.

**Example Template (app.j2):**
```jinja2
FROM {{ base_image }}
WORKDIR {{ workdir }}
LABEL name={{ name }}
LABEL version={{ version }}
```

**Variables:**
```python
{
    "base_image": "python:3.12",
    "workdir": "/app",
    "name": "myapp",
    "version": "1.0.0"
}
```

**Rendered Output:**
```dockerfile
FROM python:3.12
WORKDIR /app
LABEL name=myapp
LABEL version=1.0.0
```

### Why Use Template Renderer?

- **Separation of Concerns:** Keep templates separate from code
- **Reusability:** Use the same template with different variables
- **Validation:** Catch missing variables before rendering
- **Type Safety:** Full type hints for better IDE support
- **Flexibility:** Easy to change templates without code changes

---

## Quick Start

### Step 1: Create a Template

Create a directory for your templates and add a template file:

```bash
mkdir templates
cat > templates/hello.j2 << 'EOF'
Hello, {{ name }}!
Welcome to {{ project }}.
EOF
```

### Step 2: Create a Renderer

```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer(template_dir="templates")
```

### Step 3: Render the Template

```python
result = renderer.render(
    template_name="hello.j2",
    variables={
        "name": "Alice",
        "project": "Template Renderer"
    }
)

print(result)
# Output:
# Hello, Alice!
# Welcome to Template Renderer.
```

---

## Common Use Cases

### Use Case 1: Rendering Dockerfiles

**Template (templates/python.j2):**
```jinja2
FROM {{ base_image }}
WORKDIR {{ workdir }}

# Install system packages
RUN apt-get update && apt-get install -y \
{% for package in system_packages %}
    {{ package }}{% if not loop.last %} \{% endif %}
{% endfor %}
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
{% for key, value in env_vars.items() %}
ENV {{ key }}={{ value }}
{% endfor %}

ENTRYPOINT {{ entrypoint }}
CMD {{ cmd }}
```

**Python Code:**
```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer("templates")

dockerfile = renderer.render(
    "python.j2",
    variables={
        "base_image": "python:3.12-slim",
        "workdir": "/app",
        "system_packages": ["git", "curl", "build-essential"],
        "env_vars": {
            "PYTHONUNBUFFERED": "1",
            "ENV": "production"
        },
        "entrypoint": ["python"],
        "cmd": ["app.py"]
    }
)

# Save to file
with open("Dockerfile", "w") as f:
    f.write(dockerfile)
```

### Use Case 2: Configuration Files

**Template (templates/app.yaml.j2):**
```jinja2
app:
  name: {{ app_name }}
  version: {{ version }}
  debug: {{ debug }}

database:
  host: {{ db_host }}
  port: {{ db_port }}
  name: {{ db_name }}

logging:
  level: {{ log_level }}
  format: {{ log_format }}
```

**Python Code:**
```python
renderer = Jinja2Renderer("templates")

config = renderer.render(
    "app.yaml.j2",
    variables={
        "app_name": "myapp",
        "version": "1.0.0",
        "debug": False,
        "db_host": "localhost",
        "db_port": 5432,
        "db_name": "myapp_db",
        "log_level": "INFO",
        "log_format": "json"
    }
)

with open("config/production.yaml", "w") as f:
    f.write(config)
```

### Use Case 3: Script Generation

**Template (templates/deploy.sh.j2):**
```jinja2
#!/bin/bash
set -e

echo "Deploying {{ app_name }} version {{ version }}"

# Build Docker image
docker build -t {{ image_name }}:{{ version }} .

# Tag as latest
docker tag {{ image_name }}:{{ version }} {{ image_name }}:latest

# Push to registry
docker push {{ image_name }}:{{ version }}
docker push {{ image_name }}:latest

# Deploy to {{ environment }}
kubectl set image deployment/{{ app_name }} \
    {{ app_name }}={{ image_name }}:{{ version }}

echo "Deployment complete!"
```

**Python Code:**
```python
renderer = Jinja2Renderer("templates")

script = renderer.render(
    "deploy.sh.j2",
    variables={
        "app_name": "myapp",
        "version": "1.2.3",
        "image_name": "myregistry/myapp",
        "environment": "production"
    }
)

with open("deploy.sh", "w") as f:
    f.write(script)

# Make executable
import os
os.chmod("deploy.sh", 0o755)
```

---

## Validation

### Why Validate?

Validation helps catch errors early by checking that all required variables are provided before rendering.

### Basic Validation

```python
renderer = Jinja2Renderer("templates")

# Validate before rendering
validation = renderer.validate(
    "app.j2",
    variables={"name": "myapp"}
)

if not validation.is_valid:
    print("Validation failed!")
    print(f"Missing variables: {validation.missing_variables}")
    print(f"Errors: {validation.errors}")
else:
    # Safe to render
    result = renderer.render("app.j2", variables={"name": "myapp"})
```

### Strict Mode (Default)

In strict mode, rendering fails if required variables are missing:

```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig, MissingVariableError

renderer = Jinja2Renderer(
    "templates",
    config=RenderConfig(strict_mode=True)  # Default
)

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing: {e.missing_variables}")
    # Provide missing variables and retry
```

### Lenient Mode

In lenient mode, missing variables use template defaults:

```python
renderer = Jinja2Renderer(
    "templates",
    config=RenderConfig(strict_mode=False)
)

# Template can use defaults: {{ version | default('1.0.0') }}
result = renderer.render("app.j2", variables={"name": "myapp"})
# Works even if 'version' not provided
```

---

## Template Introspection

### Discover Required Variables

```python
renderer = Jinja2Renderer("templates")

# Get list of variables used in template
variables = renderer.get_template_variables("app.j2")
print(f"Required variables: {variables}")
# Output: ['base_image', 'name', 'version', 'workdir']
```

### List Available Templates

```python
templates = renderer.get_available_templates()
for template in templates:
    print(f"- {template}")
# Output:
# - app.j2
# - configs/nginx.j2
# - scripts/deploy.j2
```

### Get Template Information

```python
info = renderer.get_template_info("app.j2")
print(f"Name: {info.name}")
print(f"Path: {info.path}")
print(f"Size: {info.size} bytes")
print(f"Variables: {info.required_variables}")
```

---

## Error Handling

### Handling Missing Templates

```python
from dotfiles_template_renderer import TemplateNotFoundError

try:
    result = renderer.render("missing.j2", variables={})
except TemplateNotFoundError as e:
    print(f"Template not found: {e.template_name}")
    # Use fallback template
    result = renderer.render("default.j2", variables={})
```

### Handling Rendering Errors

```python
from dotfiles_template_renderer import TemplateRenderError

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except TemplateRenderError as e:
    print(f"Rendering failed: {e}")
    # Log error and handle gracefully
```

### Handling Validation Errors

```python
from dotfiles_template_renderer import MissingVariableError

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing variables: {e.missing_variables}")
    # Collect missing variables from user
    for var in e.missing_variables:
        value = input(f"Enter {var}: ")
        variables[var] = value
    # Retry with complete variables
    result = renderer.render("app.j2", variables=variables)
```

---

## Best Practices

### 1. Use Strict Mode in Production

```python
# ✅ Good: Catch errors early
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))
```

### 2. Validate Before Rendering

```python
# ✅ Good: Validate first
validation = renderer.validate(template_name, variables)
if validation.is_valid:
    result = renderer.render(template_name, variables)
```

### 3. Organize Templates by Category

```
templates/
├── dockerfiles/
│   ├── python.j2
│   └── node.j2
├── configs/
│   ├── nginx.j2
│   └── app.j2
└── scripts/
    └── deploy.j2
```

### 4. Use Meaningful Variable Names

```python
# ✅ Good: Clear names
variables = {
    "base_image": "python:3.12",
    "workdir": "/app",
}

# ❌ Bad: Unclear names
variables = {
    "img": "python:3.12",
    "dir": "/app",
}
```

### 5. Document Templates

```jinja2
{# Dockerfile template for Python applications
   
   Required variables:
   - base_image: Python base image (e.g., python:3.12)
   - workdir: Working directory (e.g., /app)
   - system_packages: List of system packages to install
#}
FROM {{ base_image }}
WORKDIR {{ workdir }}
...
```

---

## Next Steps

- **Learn More:** Read [Usage Patterns](usage_patterns.md) for advanced patterns
- **API Reference:** See [Core API](../api/core.md) for detailed API docs
- **Integration:** Check [Integration Guide](integration.md) for module integration
- **Advanced Topics:** Explore [Advanced Topics](../reference/advanced.md) for security, performance, etc.

