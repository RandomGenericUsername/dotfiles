# Troubleshooting Guide

Common issues and solutions for the template_renderer module.

---

## Template Not Found Errors

### Issue: TemplateNotFoundError

**Symptom:**
```python
TemplateNotFoundError: Template 'app.j2' not found in '/path/to/templates'
```

**Causes:**
1. Template file doesn't exist
2. Wrong template directory
3. Incorrect template name
4. File permissions

**Solutions:**

**Solution 1: Verify template exists**
```python
from pathlib import Path

template_dir = Path("templates")
template_file = template_dir / "app.j2"

if not template_file.exists():
    print(f"Template not found: {template_file}")
    print(f"Directory contents: {list(template_dir.iterdir())}")
```

**Solution 2: Check template directory**
```python
renderer = Jinja2Renderer("templates")  # Relative path
# vs
renderer = Jinja2Renderer("/absolute/path/to/templates")  # Absolute path

# Verify directory
print(f"Template dir: {renderer.template_dir}")
print(f"Exists: {renderer.template_dir.exists()}")
```

**Solution 3: List available templates**
```python
templates = renderer.get_available_templates()
print(f"Available templates: {templates}")
```

**Solution 4: Check file permissions**
```bash
ls -la templates/
chmod 644 templates/*.j2
```

---

## Missing Variable Errors

### Issue: MissingVariableError

**Symptom:**
```python
MissingVariableError: Missing variables: ['version', 'port']
```

**Causes:**
1. Required variables not provided
2. Typo in variable name
3. Strict mode enabled

**Solutions:**

**Solution 1: Provide all required variables**
```python
# Get required variables first
required = renderer.get_template_variables("app.j2")
print(f"Required: {required}")

# Provide all variables
variables = {var: get_value(var) for var in required}
result = renderer.render("app.j2", variables=variables)
```

**Solution 2: Validate before rendering**
```python
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    # Collect missing variables
    for var in validation.missing_variables:
        variables[var] = input(f"Enter {var}: ")

result = renderer.render("app.j2", variables=variables)
```

**Solution 3: Use lenient mode**
```python
# Disable strict mode
renderer = Jinja2Renderer(
    "templates",
    config=RenderConfig(strict_mode=False)
)

# Template must have defaults: {{ version | default('1.0.0') }}
result = renderer.render("app.j2", variables={"name": "myapp"})
```

**Solution 4: Check for typos**
```python
# ❌ Wrong: Typo in variable name
variables = {"nmae": "myapp"}  # Should be "name"

# ✅ Correct
variables = {"name": "myapp"}
```

---

## Rendering Errors

### Issue: TemplateRenderError

**Symptom:**
```python
TemplateRenderError: Error rendering template 'app.j2': ...
```

**Causes:**
1. Syntax error in template
2. Invalid expression
3. Filter/test not found
4. Type error in template

**Solutions:**

**Solution 1: Check template syntax**
```jinja2
{# ❌ Wrong: Missing closing brace #}
{{ name }

{# ✅ Correct #}
{{ name }}

{# ❌ Wrong: Invalid expression #}
{{ name + }}

{# ✅ Correct #}
{{ name + " suffix" }}
```

**Solution 2: Verify filters exist**
```python
# ❌ Wrong: Filter doesn't exist
# {{ name | nonexistent_filter }}

# ✅ Correct: Add custom filter
config = RenderConfig(
    custom_filters={"uppercase": lambda x: x.upper()}
)
renderer = Jinja2Renderer("templates", config=config)

# In template: {{ name | uppercase }}
```

**Solution 3: Check variable types**
```python
# Template expects list: {% for item in items %}
variables = {
    "items": ["a", "b", "c"]  # ✅ Correct: list
    # "items": "abc"  # ❌ Wrong: string
}
```

**Solution 4: Enable debug mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

try:
    result = renderer.render("app.j2", variables=variables)
except TemplateRenderError as e:
    print(f"Error: {e}")
    print(f"Template: {e.template_name}")
    import traceback
    traceback.print_exc()
```

---

## Validation Issues

### Issue: Validation passes but rendering fails

**Symptom:**
```python
validation.is_valid == True
# But rendering still fails
```

**Causes:**
1. Type mismatch (validation doesn't check types)
2. Runtime error in template logic
3. Filter/test error

**Solutions:**

**Solution 1: Validate variable types**
```python
from dotfiles_template_renderer import validate_variable_types

expected_types = {
    "name": str,
    "port": int,
    "items": list,
}

type_errors = validate_variable_types(variables, expected_types)
if type_errors:
    print(f"Type errors: {type_errors}")
```

**Solution 2: Test with simple variables first**
```python
# Test with minimal variables
test_vars = {var: "test" for var in required_variables}
try:
    result = renderer.render("app.j2", variables=test_vars)
except TemplateRenderError as e:
    print(f"Template has logic errors: {e}")
```

---

## Performance Issues

### Issue: Slow rendering

**Symptom:**
Rendering takes too long

**Causes:**
1. Creating new renderer for each render
2. Large templates
3. Complex expressions
4. Validation overhead

**Solutions:**

**Solution 1: Reuse renderer**
```python
# ❌ Wrong: Create new renderer each time
for i in range(1000):
    renderer = Jinja2Renderer("templates")
    result = renderer.render("app.j2", variables)

# ✅ Correct: Reuse renderer
renderer = Jinja2Renderer("templates")
for i in range(1000):
    result = renderer.render("app.j2", variables)
```

**Solution 2: Split large templates**
```jinja2
{# ❌ Wrong: Single large template #}
{# 10,000 lines in one file #}

{# ✅ Correct: Split into includes #}
{% include 'header.j2' %}
{% include 'body.j2' %}
{% include 'footer.j2' %}
```

**Solution 3: Prepare data in Python**
```python
# ❌ Wrong: Complex logic in template
# {{ (user.first_name + " " + user.last_name).upper() }}

# ✅ Correct: Prepare in Python
variables = {
    "user_display_name": f"{user.first_name} {user.last_name}".upper()
}
# {{ user_display_name }}
```

**Solution 4: Disable strict mode for performance**
```python
# Strict mode validates before rendering (2x parse)
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))
# Lenient mode skips validation (1x parse)
```

---

## Import Errors

### Issue: Cannot import from module

**Symptom:**
```python
ImportError: cannot import name 'Jinja2Renderer' from 'dotfiles.modules.template_renderer'
```

**Causes:**
1. Module not in Python path
2. Circular import
3. Missing __init__.py

**Solutions:**

**Solution 1: Check Python path**
```python
import sys
print(sys.path)

# Add to path if needed
sys.path.insert(0, '/path/to/dotfiles')
```

**Solution 2: Use correct import**
```python
# ✅ Correct: Import from public API
from dotfiles_template_renderer import Jinja2Renderer

# ❌ Wrong: Import from internal module
from dotfiles_template_renderer.renderers.jinja2 import Jinja2Renderer
```

---

## Configuration Issues

### Issue: Configuration not applied

**Symptom:**
Custom filters/tests not working

**Causes:**
1. Config not passed to renderer
2. Config created after renderer
3. Typo in config field

**Solutions:**

**Solution 1: Pass config to renderer**
```python
# ❌ Wrong: Config not passed
config = RenderConfig(custom_filters={"uppercase": lambda x: x.upper()})
renderer = Jinja2Renderer("templates")  # Uses default config

# ✅ Correct: Pass config
renderer = Jinja2Renderer("templates", config=config)
```

**Solution 2: Verify config**
```python
print(f"Strict mode: {renderer.config.strict_mode}")
print(f"Custom filters: {renderer.config.custom_filters}")
```

---

## Path Issues

### Issue: Template directory not found

**Symptom:**
```python
FileNotFoundError: Template directory '/path/to/templates' does not exist
```

**Causes:**
1. Relative path from wrong location
2. Directory doesn't exist
3. Typo in path

**Solutions:**

**Solution 1: Use absolute paths**
```python
from pathlib import Path

# Get absolute path
template_dir = Path(__file__).parent / "templates"
renderer = Jinja2Renderer(template_dir)
```

**Solution 2: Create directory if needed**
```python
template_dir = Path("templates")
template_dir.mkdir(exist_ok=True)
renderer = Jinja2Renderer(template_dir)
```

**Solution 3: Verify path**
```python
template_dir = Path("templates")
print(f"Absolute path: {template_dir.absolute()}")
print(f"Exists: {template_dir.exists()}")
print(f"Is directory: {template_dir.is_dir()}")
```

---

## Common Mistakes

### Mistake 1: Not handling exceptions

```python
# ❌ Wrong: No error handling
result = renderer.render("app.j2", variables)

# ✅ Correct: Handle exceptions
try:
    result = renderer.render("app.j2", variables)
except MissingVariableError as e:
    print(f"Missing: {e.missing_variables}")
except TemplateNotFoundError as e:
    print(f"Template not found: {e.template_name}")
except TemplateError as e:
    print(f"Error: {e}")
```

### Mistake 2: Ignoring validation

```python
# ❌ Wrong: Ignore validation
validation = renderer.validate("app.j2", variables)
result = renderer.render("app.j2", variables)  # Render anyway

# ✅ Correct: Check validation
validation = renderer.validate("app.j2", variables)
if validation.is_valid:
    result = renderer.render("app.j2", variables)
```

### Mistake 3: Hardcoding paths

```python
# ❌ Wrong: Hardcoded absolute path
renderer = Jinja2Renderer("/home/user/templates")

# ✅ Correct: Relative or configurable path
from pathlib import Path
template_dir = Path(__file__).parent / "templates"
renderer = Jinja2Renderer(template_dir)
```

---

## Getting Help

If you're still having issues:

1. **Check the logs** - Enable debug logging
2. **Read the error message** - It usually tells you what's wrong
3. **Verify your inputs** - Check template exists, variables are correct
4. **Test with simple case** - Minimal template and variables
5. **Check the documentation** - API reference, guides, examples

---

## See Also

- [Getting Started](../guides/getting_started.md) - Basic usage
- [API Reference](../api/core.md) - Detailed API docs
- [Examples](examples.md) - Code examples

