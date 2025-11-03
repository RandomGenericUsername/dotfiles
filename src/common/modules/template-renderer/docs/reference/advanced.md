# Advanced Topics

This document covers advanced topics for the template_renderer module.

---

## Security Considerations

### 1. Template Injection Attacks

**Risk:** Malicious users could inject Jinja2 code into templates.

**Attack Vector:**
```python
# DANGEROUS: User-controlled template content
user_template = request.form.get("template")  # Could be: {{ config.__class__.__init__.__globals__['os'].system('rm -rf /') }}
renderer.render_string(user_template, variables={})
```

**Mitigation:**
```python
# SAFE: Only allow rendering from pre-defined templates
allowed_templates = ["app.j2", "config.j2"]
template_name = request.form.get("template")

if template_name not in allowed_templates:
    raise ValueError("Invalid template")

result = renderer.render(template_name, variables={})
```

**Best Practices:**
- Never render user-provided template strings
- Only allow selection from pre-defined templates
- Validate template names against whitelist
- Use strict file permissions on template directory

---

### 2. Variable Injection

**Risk:** Malicious variable values could exploit template logic.

**Attack Vector:**
```python
# DANGEROUS: User-controlled variables without validation
variables = {
    "command": request.form.get("command"),  # Could be: "rm -rf /"
}
# Template: RUN {{ command }}
```

**Mitigation:**
```python
# SAFE: Validate and sanitize variables
import re

def validate_command(cmd):
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', cmd):
        raise ValueError("Invalid command")
    return cmd

variables = {
    "command": validate_command(request.form.get("command")),
}
```

**Best Practices:**
- Validate all user-provided variables
- Use type checking
- Sanitize inputs
- Use whitelists for allowed values

---

### 3. Path Traversal

**Risk:** Malicious template names could access files outside template directory.

**Attack Vector:**
```python
# DANGEROUS: User-controlled template name
template_name = request.form.get("template")  # Could be: "../../etc/passwd"
result = renderer.render(template_name, variables={})
```

**Mitigation:**
```python
# SAFE: Validate template name
from pathlib import Path

def validate_template_name(name):
    # Ensure no path traversal
    if ".." in name or name.startswith("/"):
        raise ValueError("Invalid template name")

    # Ensure template exists in allowed directory
    template_path = Path(renderer.template_dir) / name
    if not template_path.resolve().is_relative_to(Path(renderer.template_dir).resolve()):
        raise ValueError("Template outside allowed directory")

    return name

template_name = validate_template_name(request.form.get("template"))
```

**Best Practices:**
- Validate template names
- Check for path traversal attempts
- Use `Path.resolve()` to check actual paths
- Restrict template directory permissions

---

### 4. Information Disclosure

**Risk:** Templates could expose sensitive information.

**Mitigation:**
```python
# Don't pass sensitive data to templates
variables = {
    "api_key": "***REDACTED***",  # Don't pass actual key
    "password": "***REDACTED***",
}

# Use environment variables in deployment instead
# Template: ENV API_KEY=${API_KEY}
```

**Best Practices:**
- Don't hardcode secrets in templates
- Use environment variables for sensitive data
- Audit templates for information disclosure
- Use separate templates for different environments

---

### 5. Denial of Service

**Risk:** Complex templates could consume excessive resources.

**Mitigation:**
```python
# Set timeouts and limits
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Template rendering timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)  # 5 second timeout

try:
    result = renderer.render(template_name, variables)
finally:
    signal.alarm(0)  # Cancel alarm
```

**Best Practices:**
- Set rendering timeouts
- Limit template complexity
- Monitor resource usage
- Rate limit rendering requests

---

## Performance Optimization

### 1. Template Caching

**Problem:** Re-compiling templates on every render is slow.

**Solution:** Reuse renderer instances (templates are cached automatically).

```python
# SLOW: Creates new renderer each time
for i in range(1000):
    renderer = Jinja2Renderer("templates")
    result = renderer.render("app.j2", variables)

# FAST: Reuses renderer and cached templates
renderer = Jinja2Renderer("templates")
for i in range(1000):
    result = renderer.render("app.j2", variables)
```

**Performance Gain:** ~100x faster for repeated renders.

---

### 2. Batch Rendering

**Problem:** Rendering templates one-by-one is inefficient.

**Solution:** Batch render multiple templates.

```python
# Batch rendering
renderer = Jinja2Renderer("templates")

templates_to_render = [
    ("app.j2", {"name": "app1"}),
    ("config.j2", {"env": "prod"}),
    ("script.j2", {"cmd": "start"}),
]

results = {}
for template, vars in templates_to_render:
    results[template] = renderer.render(template, vars)
```

---

### 3. Lazy Variable Evaluation

**Problem:** Computing all variables upfront is wasteful.

**Solution:** Use lazy evaluation for expensive variables.

```python
class LazyVariable:
    def __init__(self, func):
        self._func = func
        self._value = None

    def __str__(self):
        if self._value is None:
            self._value = self._func()
        return str(self._value)

# Only computed if used in template
variables = {
    "expensive_data": LazyVariable(lambda: compute_expensive_data()),
}
```

---

### 4. Parallel Rendering

**Problem:** Rendering many templates sequentially is slow.

**Solution:** Use multiprocessing for parallel rendering.

```python
from multiprocessing import Pool

def render_template(args):
    template, variables = args
    renderer = Jinja2Renderer("templates")
    return renderer.render(template, variables)

templates = [
    ("app1.j2", {"name": "app1"}),
    ("app2.j2", {"name": "app2"}),
    ("app3.j2", {"name": "app3"}),
]

with Pool(4) as pool:
    results = pool.map(render_template, templates)
```

---

### 5. Minimize Template Complexity

**Problem:** Complex templates are slow to render.

**Solution:** Move logic to Python, keep templates simple.

```python
# SLOW: Complex logic in template
"""
{% for user in users %}
  {% if user.age > 18 and user.country == 'US' and user.verified %}
    {{ user.name }}
  {% endif %}
{% endfor %}
"""

# FAST: Logic in Python
eligible_users = [
    u for u in users
    if u.age > 18 and u.country == 'US' and u.verified
]

variables = {"users": eligible_users}

# Template: {% for user in users %}{{ user.name }}{% endfor %}
```

---

## Extensibility

### 1. Custom Renderer Implementation

Extend `TemplateRenderer` for custom rendering engines.

```python
from dotfiles_template_renderer import TemplateRenderer

class MustacheRenderer(TemplateRenderer):
    """Mustache template renderer."""

    def __init__(self, template_dir, config=None):
        super().__init__(template_dir, config)
        import pystache
        self.renderer = pystache.Renderer(search_dirs=[template_dir])

    def render(self, template_name, variables=None, **kwargs):
        merged_vars = self._merge_variables(variables, kwargs)
        return self.renderer.render_path(template_name, merged_vars)

    # Implement other abstract methods...
```

---

### 2. Custom Filters

Add domain-specific filters.

```python
def docker_escape(text):
    """Escape text for Dockerfile."""
    return text.replace('"', '\\"').replace('$', '\\$')

def yaml_multiline(text):
    """Format text as YAML multiline."""
    lines = text.split('\n')
    return '|\n  ' + '\n  '.join(lines)

config = RenderConfig(
    custom_filters={
        "docker_escape": docker_escape,
        "yaml_multiline": yaml_multiline,
    }
)
```

---

### 3. Custom Validators

Add custom validation logic.

```python
from dotfiles_template_renderer import ValidationResult

def validate_dockerfile_variables(variables):
    """Validate Dockerfile-specific variables."""
    errors = []

    if "base_image" in variables:
        if ":" not in variables["base_image"]:
            errors.append("base_image must include tag (e.g., python:3.12)")

    if "port" in variables:
        port = variables["port"]
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("port must be between 1 and 65535")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        # ... other fields
    )
```

---

### 4. Template Preprocessors

Preprocess templates before rendering.

```python
class PreprocessingRenderer(Jinja2Renderer):
    def render(self, template_name, variables=None, **kwargs):
        # Get template source
        source = self._get_template_source(template_name)

        # Preprocess
        source = self._preprocess(source)

        # Render preprocessed template
        template = self.env.from_string(source)
        merged_vars = self._merge_variables(variables, kwargs)
        return template.render(**merged_vars)

    def _preprocess(self, source):
        # Example: Replace custom syntax
        source = source.replace("@@", "{{")
        source = source.replace("@@", "}}")
        return source
```

---

### 5. Template Hooks

Add hooks for template lifecycle events.

```python
class HookableRenderer(Jinja2Renderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hooks = {
            "before_render": [],
            "after_render": [],
        }

    def add_hook(self, event, func):
        self.hooks[event].append(func)

    def render(self, template_name, variables=None, **kwargs):
        # Before render hooks
        for hook in self.hooks["before_render"]:
            hook(template_name, variables)

        # Render
        result = super().render(template_name, variables, **kwargs)

        # After render hooks
        for hook in self.hooks["after_render"]:
            hook(template_name, result)

        return result

# Usage
renderer = HookableRenderer("templates")
renderer.add_hook("before_render", lambda t, v: print(f"Rendering {t}"))
renderer.add_hook("after_render", lambda t, r: print(f"Rendered {len(r)} bytes"))
```

---

## Future Enhancements

### 1. Template Versioning

Track template versions and changes.

```python
# Proposed API
info = renderer.get_template_info("app.j2")
print(f"Version: {info.version}")
print(f"Last modified: {info.last_modified}")
print(f"Changelog: {info.changelog}")
```

### 2. Template Linting

Validate template syntax and best practices.

```python
# Proposed API
lint_results = renderer.lint_template("app.j2")
for issue in lint_results:
    print(f"{issue.severity}: {issue.message} at line {issue.line}")
```

### 3. Template Metrics

Collect rendering metrics.

```python
# Proposed API
metrics = renderer.get_metrics()
print(f"Total renders: {metrics.total_renders}")
print(f"Average time: {metrics.avg_render_time}ms")
print(f"Cache hit rate: {metrics.cache_hit_rate}%")
```

### 4. Template Diffing

Compare template versions.

```python
# Proposed API
diff = renderer.diff_templates("app.j2", "app_v2.j2")
print(diff.unified_diff())
```

### 5. Template Composition

Compose templates from reusable components.

```python
# Proposed API
renderer.register_component("header", "components/header.j2")
renderer.register_component("footer", "components/footer.j2")

# Template: {% component 'header' %}...{% component 'footer' %}
```

---

## Migration Guides

### Migrating from String Templates

```python
# Old: String templates
template = "Hello {name}!"
result = template.format(name="World")

# New: Jinja2 templates
renderer = Jinja2Renderer("templates")
# Template: Hello {{ name }}!
result = renderer.render("hello.j2", variables={"name": "World"})
```

### Migrating from Jinja2 Directly

```python
# Old: Direct Jinja2 usage
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("app.j2")
result = template.render(name="myapp")

# New: template_renderer
renderer = Jinja2Renderer("templates")
result = renderer.render("app.j2", variables={"name": "myapp"})
```

### Migrating to Strict Mode

```python
# Step 1: Discover required variables
variables = renderer.get_template_variables("app.j2")
print(f"Required: {variables}")

# Step 2: Add defaults to template
# {{ version | default('1.0.0') }}

# Step 3: Enable strict mode
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))
```

---

## See Also

- [Security Best Practices](../guides/best_practices.md) - Security recommendations
- [Performance Guide](../guides/best_practices.md) - Performance tips
- [API Reference](../api/core.md) - Detailed API docs
