# Best Practices

This guide documents recommended practices and anti-patterns for the template_renderer module.

---

## Best Practices

### 1. Always Use Strict Mode in Production

**✅ Good:**
```python
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))
```

**❌ Bad:**
```python
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))
```

**Rationale:**
- Strict mode catches errors early
- Prevents generating invalid output
- Makes debugging easier
- Ensures all required variables are provided

---

### 2. Validate Before Rendering Critical Templates

**✅ Good:**
```python
validation = renderer.validate(template_name, variables)
if validation.is_valid:
    result = renderer.render(template_name, variables)
else:
    handle_errors(validation.errors)
```

**❌ Bad:**
```python
result = renderer.render(template_name, variables)  # May fail
```

**Rationale:**
- Validation provides detailed error information
- Can collect all missing variables at once
- Avoids exceptions in production

---

### 3. Use Specific Exception Handlers

**✅ Good:**
```python
try:
    result = renderer.render(template_name, variables)
except MissingVariableError as e:
    handle_missing_variables(e.missing_variables)
except TemplateNotFoundError as e:
    handle_missing_template(e.template_name)
except TemplateRenderError as e:
    handle_render_error(e)
```

**❌ Bad:**
```python
try:
    result = renderer.render(template_name, variables)
except Exception as e:  # Too broad
    print(f"Error: {e}")
```

**Rationale:**
- Specific handlers allow targeted error recovery
- Better error messages
- Easier debugging

---

### 4. Provide Meaningful Variable Names

**✅ Good:**
```python
variables = {
    "base_image": "python:3.12",
    "workdir": "/app",
    "system_packages": ["git", "curl"],
}
```

**❌ Bad:**
```python
variables = {
    "img": "python:3.12",
    "dir": "/app",
    "pkgs": ["git", "curl"],
}
```

**Rationale:**
- Clear names improve template readability
- Self-documenting code
- Easier maintenance

---

### 5. Use Template Comments for Documentation

**✅ Good:**
```jinja2
{# Dockerfile template for Python applications

   Required variables:
   - base_image: Python base image (e.g., python:3.12)
   - workdir: Working directory (e.g., /app)
   - system_packages: List of system packages to install
#}
FROM {{ base_image }}
WORKDIR {{ workdir }}
```

**❌ Bad:**
```jinja2
FROM {{ base_image }}
WORKDIR {{ workdir }}
```

**Rationale:**
- Documents template purpose and requirements
- Helps other developers understand templates
- Can be extracted for documentation

---

### 6. Organize Templates by Category

**✅ Good:**
```
templates/
├── dockerfiles/
│   ├── python.j2
│   ├── node.j2
│   └── rust.j2
├── configs/
│   ├── nginx.j2
│   └── app.j2
└── scripts/
    └── deploy.j2
```

**❌ Bad:**
```
templates/
├── python.j2
├── node.j2
├── nginx.j2
├── app.j2
└── deploy.j2
```

**Rationale:**
- Better organization
- Easier to find templates
- Scales better with many templates

---

### 7. Use Default Values in Templates

**✅ Good:**
```jinja2
{{ version | default('1.0.0') }}
{{ debug | default(false) }}
{{ log_level | default('INFO') }}
```

**❌ Bad:**
```jinja2
{{ version }}
{{ debug }}
{{ log_level }}
```

**Rationale:**
- Makes variables optional
- Provides sensible defaults
- More flexible templates

---

### 8. Log Rendering Operations

**✅ Good:**
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Rendering template: {template_name}")
result = renderer.render(template_name, variables)
logger.info(f"Rendered {len(result)} bytes")
```

**❌ Bad:**
```python
result = renderer.render(template_name, variables)  # No logging
```

**Rationale:**
- Helps debugging
- Audit trail
- Performance monitoring

---

### 9. Reuse Renderer Instances

**✅ Good:**
```python
renderer = Jinja2Renderer("templates")
for template in templates:
    result = renderer.render(template, variables)
```

**❌ Bad:**
```python
for template in templates:
    renderer = Jinja2Renderer("templates")  # Wasteful
    result = renderer.render(template, variables)
```

**Rationale:**
- Better performance (template caching)
- Less memory usage
- Faster execution

---

### 10. Use Type Hints

**✅ Good:**
```python
def render_template(
    renderer: Jinja2Renderer,
    template: str,
    variables: dict[str, Any]
) -> str:
    return renderer.render(template, variables)
```

**❌ Bad:**
```python
def render_template(renderer, template, vars):
    return renderer.render(template, vars)
```

**Rationale:**
- Better IDE support
- Type checking
- Self-documenting code

---

## Anti-Patterns

### Anti-Pattern 1: Hardcoding Template Directory

**❌ Bad:**
```python
renderer = Jinja2Renderer("/absolute/path/to/templates")
```

**✅ Good:**
```python
from pathlib import Path

template_dir = Path(__file__).parent / "templates"
renderer = Jinja2Renderer(template_dir)
```

**Why It's Bad:**
- Not portable
- Breaks on different systems
- Hard to test

---

### Anti-Pattern 2: Ignoring Validation Results

**❌ Bad:**
```python
validation = renderer.validate(template_name, variables)
result = renderer.render(template_name, variables)  # Render anyway
```

**✅ Good:**
```python
validation = renderer.validate(template_name, variables)
if validation.is_valid:
    result = renderer.render(template_name, variables)
else:
    handle_validation_errors(validation)
```

**Why It's Bad:**
- Wastes validation effort
- May still fail during rendering
- Misses opportunity to provide better errors

---

### Anti-Pattern 3: Catching and Swallowing Exceptions

**❌ Bad:**
```python
try:
    result = renderer.render(template_name, variables)
except Exception:
    pass  # Silent failure
```

**✅ Good:**
```python
try:
    result = renderer.render(template_name, variables)
except TemplateError as e:
    logger.error(f"Rendering failed: {e}")
    raise  # Or handle appropriately
```

**Why It's Bad:**
- Hides errors
- Makes debugging impossible
- Leads to silent failures

---

### Anti-Pattern 4: Not Handling Missing Templates

**❌ Bad:**
```python
result = renderer.render("missing.j2", variables)  # May crash
```

**✅ Good:**
```python
templates = renderer.get_available_templates()
if "missing.j2" in templates:
    result = renderer.render("missing.j2", variables)
else:
    result = renderer.render("default.j2", variables)
```

**Why It's Bad:**
- Crashes on missing templates
- No fallback mechanism
- Poor user experience

---

### Anti-Pattern 5: Mixing Template Logic with Business Logic

**❌ Bad:**
```jinja2
{% if user.age > 18 and user.country == 'US' and user.verified %}
  Access granted
{% endif %}
```

**✅ Good:**
```python
# In Python
variables = {
    "can_access": user.age > 18 and user.country == 'US' and user.verified
}

# In template
{% if can_access %}
  Access granted
{% endif %}
```

**Why It's Bad:**
- Complex logic in templates
- Hard to test
- Difficult to maintain

---

### Anti-Pattern 6: Not Using Configuration

**❌ Bad:**
```python
# Hardcoded behavior
renderer = Jinja2Renderer("templates")
# Can't change strict mode, filters, etc.
```

**✅ Good:**
```python
config = RenderConfig(
    strict_mode=True,
    custom_filters={"uppercase": lambda x: x.upper()},
)
renderer = Jinja2Renderer("templates", config=config)
```

**Why It's Bad:**
- Inflexible
- Can't customize behavior
- Hard to adapt to different use cases

---

### Anti-Pattern 7: Creating Renderer Per Render

**❌ Bad:**
```python
for i in range(1000):
    renderer = Jinja2Renderer("templates")
    result = renderer.render("app.j2", variables)
```

**✅ Good:**
```python
renderer = Jinja2Renderer("templates")
for i in range(1000):
    result = renderer.render("app.j2", variables)
```

**Why It's Bad:**
- Slow (recompiles templates)
- Wastes memory
- No template caching

---

## Recommendations

### For Development

1. **Use strict mode** - Catch errors early
2. **Enable logging** - Debug issues faster
3. **Write tests** - Validate templates work correctly
4. **Document templates** - Help other developers

### For Production

1. **Use strict mode** - Prevent invalid output
2. **Validate before rendering** - Better error handling
3. **Log all operations** - Audit trail
4. **Monitor performance** - Track rendering times
5. **Handle all exceptions** - Graceful error recovery

### For Testing

1. **Test with minimal variables** - Find required variables
2. **Test with extra variables** - Check unused variable warnings
3. **Test error cases** - Verify error handling
4. **Test edge cases** - Empty strings, None values, etc.

---

## See Also

- [Usage Patterns](usage_patterns.md) - Common patterns
- [Integration Guide](integration.md) - Integration examples
- [Troubleshooting](../reference/troubleshooting.md) - Common issues
