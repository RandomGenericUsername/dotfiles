# Managers API Reference

**Module:** `colorscheme_generator.core.managers`  
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [OutputManager](#outputmanager)
2. [Template System](#template-system)

---

## OutputManager

**Location:** `colorscheme_generator.core.managers.output_manager`

Manages writing ColorScheme objects to files in various formats.

### Class Definition

```python
class OutputManager:
    """Manages output file generation from ColorScheme objects.
    
    Responsibilities:
    - Load and render Jinja2 templates
    - Write rendered content to files
    - Manage output directory structure
    
    Does NOT:
    - Extract colors from images (that's backends' job)
    - Modify ColorScheme objects
    """
```

### Constructor

```python
def __init__(self, settings: AppConfig):
    """Initialize OutputManager.
    
    Args:
        settings: Application configuration
        
    Sets up:
    - Jinja2 environment with template directory
    - Template loader
    - Auto-escaping disabled (for shell scripts, etc.)
    """
```

**Example:**
```python
from colorscheme_generator.core.managers.output_manager import OutputManager
from colorscheme_generator.config.settings import Settings

settings = Settings.get()
manager = OutputManager(settings)
```

### Methods

#### write_outputs()

```python
def write_outputs(
    self,
    scheme: ColorScheme,
    output_dir: Path,
    formats: list[ColorFormat]
) -> dict[str, Path]:
    """Write ColorScheme to files in specified formats.
    
    Process:
    1. Create output directory if it doesn't exist
    2. For each format:
       a. Render template with ColorScheme data
       b. Write to file (colors.<format>)
       c. Add to output_files dict
    3. Update scheme.output_files
    4. Return output_files dict
    
    Args:
        scheme: ColorScheme to write
        output_dir: Directory to write files to
        formats: List of output formats
        
    Returns:
        Dictionary mapping format name to output file path
        
    Raises:
        TemplateRenderError: If template rendering fails
        OutputWriteError: If file writing fails
    """
```

**Example:**
```python
from pathlib import Path
from colorscheme_generator.config.enums import ColorFormat

# Write to multiple formats
output_files = manager.write_outputs(
    scheme,
    Path("~/.cache/colorscheme"),
    [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.SHELL]
)

print(output_files)
# {
#   'json': PosixPath('/home/user/.cache/colorscheme/colors.json'),
#   'css': PosixPath('/home/user/.cache/colorscheme/colors.css'),
#   'sh': PosixPath('/home/user/.cache/colorscheme/colors.sh')
# }
```

#### _render_template()

```python
def _render_template(self, scheme: ColorScheme, fmt: ColorFormat) -> str:
    """Render template for specific format.
    
    Args:
        scheme: ColorScheme to render
        fmt: Output format
        
    Returns:
        Rendered template content
        
    Raises:
        TemplateRenderError: If template rendering fails
    """
```

**Template Context:**
```python
context = {
    "background": scheme.background,
    "foreground": scheme.foreground,
    "cursor": scheme.cursor,
    "colors": scheme.colors,
    "source_image": scheme.source_image,
    "backend": scheme.backend,
    "generated_at": scheme.generated_at,
}
```

**Example:**
```python
# Render JSON template
content = manager._render_template(scheme, ColorFormat.JSON)
print(content)
# {
#   "special": {
#     "background": "#1a1a1a",
#     ...
#   }
# }
```

#### _write_file()

```python
def _write_file(self, path: Path, content: str) -> None:
    """Write content to file.
    
    Args:
        path: File path to write to
        content: Content to write
        
    Raises:
        OutputWriteError: If file writing fails
    """
```

**Example:**
```python
manager._write_file(
    Path("~/.cache/colorscheme/colors.json"),
    '{"background": "#1a1a1a"}'
)
```

### Configuration

**Settings (settings.toml):**
```toml
[templates]
directory = "templates"  # Relative to module root

[output]
directory = "$HOME/.cache/colorscheme"
formats = ["json", "css", "sh"]
```

### Usage Examples

#### Basic Usage

```python
from colorscheme_generator.core.managers.output_manager import OutputManager
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.config.enums import ColorFormat

# Setup
settings = Settings.get()
manager = OutputManager(settings)

# Write single format
output_files = manager.write_outputs(
    scheme,
    Path("~/.config/colors"),
    [ColorFormat.JSON]
)

# Write multiple formats
output_files = manager.write_outputs(
    scheme,
    Path("~/.config/colors"),
    [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.SHELL, ColorFormat.YAML]
)
```

#### Custom Output Directory

```python
# Write to custom directory
output_files = manager.write_outputs(
    scheme,
    Path("/tmp/my-colors"),
    [ColorFormat.JSON, ColorFormat.CSS]
)
```

#### Integration with Backends

```python
from colorscheme_generator.factory import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend

# Generate colors
generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
scheme = generator.generate(Path("~/wallpapers/mountain.png"), config)

# Write to files
manager = OutputManager(settings)
output_files = manager.write_outputs(
    scheme,
    config.output_dir,
    config.formats
)

print(f"Generated {len(output_files)} files")
```

---

## Template System

### Overview

OutputManager uses Jinja2 templates to render ColorScheme objects to various formats.

### Template Location

```
colorscheme_generator/
└── templates/
    ├── colors.json.j2
    ├── colors.css.j2
    ├── colors.sh.j2
    └── colors.yaml.j2
```

### Template Context

All templates receive the same context:

```python
{
    "background": Color,      # Background color
    "foreground": Color,      # Foreground color
    "cursor": Color,          # Cursor color
    "colors": list[Color],    # 16 terminal colors
    "source_image": Path,     # Source image path
    "backend": str,           # Backend name
    "generated_at": datetime, # Generation timestamp
}
```

### Template Examples

#### JSON Template (colors.json.j2)

```jinja2
{
  "special": {
    "background": "{{ background.hex }}",
    "foreground": "{{ foreground.hex }}",
    "cursor": "{{ cursor.hex }}"
  },
  "colors": {
    {% for i in range(16) %}
    "color{{ i }}": "{{ colors[i].hex }}"{% if not loop.last %},{% endif %}
    {% endfor %}
  }
}
```

**Output:**
```json
{
  "special": {
    "background": "#1a1a1a",
    "foreground": "#ffffff",
    "cursor": "#ff0000"
  },
  "colors": {
    "color0": "#000000",
    "color1": "#ff0000",
    ...
  }
}
```

#### CSS Template (colors.css.j2)

```jinja2
:root {
  --background: {{ background.hex }};
  --foreground: {{ foreground.hex }};
  --cursor: {{ cursor.hex }};
  
  {% for i in range(16) %}
  --color{{ i }}: {{ colors[i].hex }};
  {% endfor %}
}
```

**Output:**
```css
:root {
  --background: #1a1a1a;
  --foreground: #ffffff;
  --cursor: #ff0000;
  
  --color0: #000000;
  --color1: #ff0000;
  ...
}
```

#### Shell Template (colors.sh.j2)

```jinja2
#!/bin/sh
# Generated by colorscheme_generator
# Source: {{ source_image }}
# Backend: {{ backend }}
# Generated: {{ generated_at }}

background="{{ background.hex }}"
foreground="{{ foreground.hex }}"
cursor="{{ cursor.hex }}"

{% for i in range(16) %}
color{{ i }}="{{ colors[i].hex }}"
{% endfor %}
```

**Output:**
```bash
#!/bin/sh
# Generated by colorscheme_generator
# Source: /home/user/wallpapers/mountain.png
# Backend: pywal
# Generated: 2025-10-18 10:30:00

background="#1a1a1a"
foreground="#ffffff"
cursor="#ff0000"

color0="#000000"
color1="#ff0000"
...
```

#### YAML Template (colors.yaml.j2)

```jinja2
special:
  background: "{{ background.hex }}"
  foreground: "{{ foreground.hex }}"
  cursor: "{{ cursor.hex }}"

colors:
  {% for i in range(16) %}
  color{{ i }}: "{{ colors[i].hex }}"
  {% endfor %}
```

**Output:**
```yaml
special:
  background: "#1a1a1a"
  foreground: "#ffffff"
  cursor: "#ff0000"

colors:
  color0: "#000000"
  color1: "#ff0000"
  ...
```

### Adding Custom Templates

1. **Create template file:**
```bash
cd colorscheme_generator/templates
touch colors.toml.j2
```

2. **Write template:**
```jinja2
# colors.toml.j2
[special]
background = "{{ background.hex }}"
foreground = "{{ foreground.hex }}"
cursor = "{{ cursor.hex }}"

[colors]
{% for i in range(16) %}
color{{ i }} = "{{ colors[i].hex }}"
{% endfor %}
```

3. **Add format to enum:**
```python
# config/enums.py
class ColorFormat(str, Enum):
    JSON = "json"
    CSS = "css"
    SHELL = "sh"
    YAML = "yaml"
    TOML = "toml"  # Add this
```

4. **Use it:**
```python
output_files = manager.write_outputs(
    scheme,
    output_dir,
    [ColorFormat.TOML]
)
```

---

## Next Steps

- **[Configuration API](configuration.md)** - Configuration system
- **[Templates Guide](../guides/templates.md)** - Working with templates
- **[Examples](../reference/examples.md)** - Comprehensive examples

