# Configuration Reference

This document describes all configuration options for the template_renderer module.

---

## RenderConfig

**Location:** `core/types.py`

Configuration dataclass for template rendering.

```python
@dataclass
class RenderConfig:
    """Configuration for template rendering."""

    strict_mode: bool = True
    autoescape: bool = False
    trim_blocks: bool = False
    lstrip_blocks: bool = False
    keep_trailing_newline: bool = False
    undefined_behavior: str = "strict"
    custom_filters: dict[str, Callable] = field(default_factory=dict)
    custom_tests: dict[str, Callable] = field(default_factory=dict)
    custom_globals: dict[str, Any] = field(default_factory=dict)
```

---

## Configuration Options

### strict_mode

**Type:** `bool`
**Default:** `True`

Controls whether to validate variables before rendering.

**Values:**
- `True` - Validate before rendering, raise `MissingVariableError` if variables are missing
- `False` - Skip validation, allow rendering with missing variables (template must have defaults)

**Example:**
```python
# Strict mode (default)
config = RenderConfig(strict_mode=True)
renderer = Jinja2Renderer("templates", config=config)

# Will raise MissingVariableError if variables are missing
result = renderer.render("app.j2", variables={"name": "myapp"})
```

```python
# Lenient mode
config = RenderConfig(strict_mode=False)
renderer = Jinja2Renderer("templates", config=config)

# Will render even if variables are missing (template must have defaults)
result = renderer.render("app.j2", variables={"name": "myapp"})
```

**Use Cases:**
- **Strict mode:** Production environments, critical templates, fail-fast behavior
- **Lenient mode:** Development, templates with defaults, flexible rendering

---

### autoescape

**Type:** `bool`
**Default:** `False`

Controls HTML/XML autoescaping in templates.

**Values:**
- `True` - Automatically escape HTML/XML special characters
- `False` - No autoescaping (raw output)

**Example:**
```python
# With autoescaping
config = RenderConfig(autoescape=True)
renderer = Jinja2Renderer("templates", config=config)

result = renderer.render("page.j2", variables={"content": "<script>alert('xss')</script>"})
# Output: &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;
```

```python
# Without autoescaping (default)
config = RenderConfig(autoescape=False)
renderer = Jinja2Renderer("templates", config=config)

result = renderer.render("page.j2", variables={"content": "<script>alert('xss')</script>"})
# Output: <script>alert('xss')</script>
```

**Use Cases:**
- **True:** HTML/XML templates, web pages, preventing XSS
- **False:** Plain text, Dockerfiles, configs, scripts

---

### trim_blocks

**Type:** `bool`
**Default:** `False`

Controls whether to remove the first newline after a template tag.

**Example:**
```python
# Template
"""
{% for item in items %}
{{ item }}
{% endfor %}
"""

# With trim_blocks=False (default)
# Output:
#
# item1
#
# item2
#

# With trim_blocks=True
config = RenderConfig(trim_blocks=True)
# Output:
# item1
# item2
```

**Use Cases:**
- **True:** Cleaner output, remove extra blank lines
- **False:** Preserve exact formatting

---

### lstrip_blocks

**Type:** `bool`
**Default:** `False`

Controls whether to strip leading whitespace from the start of a line to the start of a block.

**Example:**
```python
# Template
"""
    {% if condition %}
    content
    {% endif %}
"""

# With lstrip_blocks=False (default)
# Output:
#
#     content
#

# With lstrip_blocks=True
config = RenderConfig(lstrip_blocks=True)
# Output:
# content
```

**Use Cases:**
- **True:** Clean indentation, remove leading whitespace
- **False:** Preserve indentation

---

### keep_trailing_newline

**Type:** `bool`
**Default:** `False`

Controls whether to keep the trailing newline at the end of the template.

**Example:**
```python
# Template: "Hello {{ name }}\n"

# With keep_trailing_newline=False (default)
result = renderer.render("hello.j2", variables={"name": "World"})
# result = "Hello World" (no trailing newline)

# With keep_trailing_newline=True
config = RenderConfig(keep_trailing_newline=True)
result = renderer.render("hello.j2", variables={"name": "World"})
# result = "Hello World\n" (trailing newline preserved)
```

**Use Cases:**
- **True:** POSIX-compliant files, shell scripts
- **False:** Inline content, no trailing newline needed

---

### undefined_behavior

**Type:** `str`
**Default:** `"strict"`

Controls how undefined variables are handled during rendering.

**Values:**
- `"strict"` - Raise exception on undefined variables
- `"debug"` - Return debug string like `{{ undefined_var }}`
- `"chainable"` - Return empty string, allow chaining

**Example:**
```python
# Strict (default)
config = RenderConfig(undefined_behavior="strict")
# Raises exception on undefined variables

# Debug
config = RenderConfig(undefined_behavior="debug")
result = renderer.render("app.j2", variables={})
# Output includes: {{ missing_var }}

# Chainable
config = RenderConfig(undefined_behavior="chainable")
result = renderer.render("app.j2", variables={})
# Output: empty strings for undefined variables
```

**Use Cases:**
- **strict:** Production, catch errors early
- **debug:** Development, see which variables are undefined
- **chainable:** Lenient mode, allow missing variables

---

### custom_filters

**Type:** `dict[str, Callable]`
**Default:** `{}`

Custom Jinja2 filters to register.

**Example:**
```python
def uppercase_filter(text):
    return text.upper()

def format_bytes(bytes):
    return f"{bytes / 1024:.2f} KB"

config = RenderConfig(
    custom_filters={
        "uppercase": uppercase_filter,
        "format_bytes": format_bytes,
    }
)

renderer = Jinja2Renderer("templates", config=config)

# In template: {{ name | uppercase }}, {{ size | format_bytes }}
result = renderer.render("app.j2", variables={"name": "myapp", "size": 2048})
# Output: MYAPP, 2.00 KB
```

**Use Cases:**
- Domain-specific formatting
- Reusable transformations
- Custom data processing

---

### custom_tests

**Type:** `dict[str, Callable]`
**Default:** `{}`

Custom Jinja2 tests to register.

**Example:**
```python
def is_even(n):
    return n % 2 == 0

def is_valid_email(email):
    return "@" in email and "." in email

config = RenderConfig(
    custom_tests={
        "even": is_even,
        "valid_email": is_valid_email,
    }
)

renderer = Jinja2Renderer("templates", config=config)

# In template:
# {% if port is even %}Even port{% endif %}
# {% if email is valid_email %}Valid{% endif %}
```

**Use Cases:**
- Custom validation in templates
- Domain-specific checks
- Conditional rendering

---

### custom_globals

**Type:** `dict[str, Any]`
**Default:** `{}`

Custom global variables/functions available in all templates.

**Example:**
```python
import datetime

def now():
    return datetime.datetime.now()

config = RenderConfig(
    custom_globals={
        "now": now,
        "version": "1.0.0",
        "app_name": "MyApp",
    }
)

renderer = Jinja2Renderer("templates", config=config)

# In template: {{ app_name }} v{{ version }}, Generated: {{ now() }}
result = renderer.render("app.j2", variables={})
# Output: MyApp v1.0.0, Generated: 2024-01-15 10:30:00
```

**Use Cases:**
- Common variables across all templates
- Utility functions
- Constants

---

## Configuration Strategies

### Strategy 1: Environment-Specific Configs

```python
def get_config(environment):
    if environment == "production":
        return RenderConfig(
            strict_mode=True,
            autoescape=True,
            undefined_behavior="strict",
        )
    elif environment == "development":
        return RenderConfig(
            strict_mode=False,
            autoescape=False,
            undefined_behavior="debug",
        )
    else:
        return RenderConfig()

config = get_config(os.getenv("ENV", "production"))
renderer = Jinja2Renderer("templates", config=config)
```

### Strategy 2: Template-Specific Configs

```python
# Different configs for different template types
dockerfile_config = RenderConfig(
    strict_mode=True,
    trim_blocks=True,
    lstrip_blocks=True,
)

html_config = RenderConfig(
    strict_mode=False,
    autoescape=True,
    keep_trailing_newline=False,
)

# Use appropriate config
dockerfile_renderer = Jinja2Renderer("dockerfiles", config=dockerfile_config)
html_renderer = Jinja2Renderer("html", config=html_config)
```

### Strategy 3: Builder Pattern

```python
class ConfigBuilder:
    def __init__(self):
        self.config = RenderConfig()

    def strict(self):
        self.config.strict_mode = True
        return self

    def lenient(self):
        self.config.strict_mode = False
        return self

    def with_filter(self, name, func):
        self.config.custom_filters[name] = func
        return self

    def build(self):
        return self.config

config = (ConfigBuilder()
    .strict()
    .with_filter("uppercase", lambda x: x.upper())
    .build())
```

---

## See Also

- [Core API](../api/core.md) - RenderConfig dataclass
- [Getting Started](../guides/getting_started.md) - Basic usage
- [Best Practices](../guides/best_practices.md) - Configuration recommendations
