# Template Renderer CLI

Command-line tool for rendering Jinja2 templates with strict variable validation and flexible input methods.

## Overview

The Template Renderer CLI provides a simple, powerful interface for rendering Jinja2 templates from the command line. It wraps the `dotfiles-template-renderer` module with a user-friendly CLI built with Typer and Rich.

## Features

- **Multiple Variable Input Methods**: JSON files, inline JSON, or key=value pairs
- **Strict Validation**: Ensure all required variables are provided before rendering
- **Template Introspection**: List templates, view required variables, and get detailed info
- **Beautiful Output**: Rich terminal output with colors, tables, and panels
- **Flexible Output**: Print to stdout or save to file
- **Template Discovery**: Automatically find all templates in a directory

## Installation

```bash
# From the template-renderer directory
cd src/common/tools/template-renderer
make install
```

This will:
1. Install the `dotfiles-template-renderer` module dependency
2. Install the CLI tool in editable mode
3. Make the `template-render` command available

## Usage

### Render a Template

```bash
# Basic rendering with variables from JSON file
template-render render app.j2 -d templates/ -f vars.json

# Render with inline JSON
template-render render app.j2 -j '{"name": "myapp", "version": "1.0.0"}'

# Render with key=value pairs
template-render render app.j2 -v name=myapp -v version=1.0.0 -v port=8080

# Combine multiple sources (merged in order)
template-render render app.j2 -f base.json -v name=override -v debug=true

# Save output to file
template-render render app.j2 -f vars.json -o output.txt

# Disable strict mode (allow missing variables)
template-render render app.j2 -f vars.json --no-strict

# Show template info before rendering
template-render render app.j2 -f vars.json --show-info
```

### List Available Templates

```bash
# List templates in current directory
template-render list

# List templates in specific directory
template-render list -d templates/

# Output shows:
# - Template name
# - File size
# - Required variables
```

### Show Template Information

```bash
# Show detailed info about a template
template-render info app.j2 -d templates/

# Displays:
# - Template name and path
# - File size
# - List of required variables
# - Description (from template comments)
```

### Validate Variables

```bash
# Validate that all required variables are provided
template-render validate app.j2 -f vars.json

# Validate with inline JSON
template-render validate app.j2 -j '{"name": "myapp"}'

# Validate with key=value pairs
template-render validate app.j2 -v name=myapp -v version=1.0

# Shows:
# - Validation status (pass/fail)
# - Missing variables (if any)
# - Unused variables (warnings)
# - Validation errors
```

## Commands

### `render`

Render a Jinja2 template with provided variables.

**Arguments:**
- `template` - Template name (relative to template directory)

**Options:**
- `-d, --template-dir PATH` - Directory containing templates (default: current directory)
- `-f, --vars-file PATH` - JSON or YAML file containing variables
- `-j, --vars-json TEXT` - JSON string containing variables
- `-v, --var TEXT` - Variable in key=value format (repeatable)
- `-o, --output PATH` - Output file path (default: stdout)
- `--strict/--no-strict` - Enable/disable strict mode (default: strict)
- `--show-info` - Show template info before rendering

### `list`

List all available templates in the template directory.

**Options:**
- `-d, --template-dir PATH` - Directory containing templates (default: current directory)

### `info`

Show detailed information about a template.

**Arguments:**
- `template` - Template name

**Options:**
- `-d, --template-dir PATH` - Directory containing templates (default: current directory)

### `validate`

Validate that all required variables are provided for a template.

**Arguments:**
- `template` - Template name

**Options:**
- `-d, --template-dir PATH` - Directory containing templates (default: current directory)
- `-f, --vars-file PATH` - JSON or YAML file containing variables
- `-j, --vars-json TEXT` - JSON string containing variables
- `-v, --var TEXT` - Variable in key=value format (repeatable)

## Variable Input Methods

### JSON File

Create a JSON file with your variables:

```json
{
  "name": "myapp",
  "version": "1.0.0",
  "port": 8080,
  "debug": false,
  "features": ["auth", "api", "ui"]
}
```

Use with `-f` or `--vars-file`:

```bash
template-render render app.j2 -f vars.json
```

### YAML File (Optional)

If PyYAML is installed, you can use YAML files:

```yaml
name: myapp
version: 1.0.0
port: 8080
debug: false
features:
  - auth
  - api
  - ui
```

```bash
template-render render app.j2 -f vars.yaml
```

### Inline JSON

Pass variables as a JSON string:

```bash
template-render render app.j2 -j '{"name": "myapp", "version": "1.0.0"}'
```

### Key=Value Pairs

Pass individual variables:

```bash
template-render render app.j2 -v name=myapp -v version=1.0.0 -v port=8080
```

For complex types, use JSON syntax:

```bash
template-render render app.j2 \
  -v name=myapp \
  -v 'features=["auth","api"]' \
  -v 'config={"debug":true}'
```

### Combining Methods

All methods can be combined. Variables are merged in order:

```bash
template-render render app.j2 \
  -f base.json \              # Base variables
  -j '{"env": "prod"}' \      # Override environment
  -v debug=false              # Override debug flag
```

## Template Format

Templates use standard Jinja2 syntax. Add a description comment at the top:

```jinja2
{# Application configuration template #}
app_name: {{ name }}
version: {{ version }}
port: {{ port }}

{% if debug %}
debug: true
log_level: DEBUG
{% else %}
debug: false
log_level: INFO
{% endif %}

{% if features %}
features:
{% for feature in features %}
  - {{ feature }}
{% endfor %}
{% endif %}
```

## Examples

### Example 1: Render Dockerfile

**Template** (`docker/python.j2`):
```jinja2
FROM {{ base_image }}

WORKDIR {{ workdir }}

{% if system_packages %}
RUN apt-get update && apt-get install -y \
{% for pkg in system_packages %}
    {{ pkg }}{% if not loop.last %} \{% endif %}
{% endfor %}
{% endif %}

COPY . .

CMD {{ cmd | tojson }}
```

**Variables** (`vars.json`):
```json
{
  "base_image": "python:3.12-slim",
  "workdir": "/app",
  "system_packages": ["git", "curl"],
  "cmd": ["python", "app.py"]
}
```

**Render**:
```bash
template-render render python.j2 -d docker/ -f vars.json -o Dockerfile
```

### Example 2: Configuration File

```bash
# Render nginx config
template-render render nginx.conf.j2 \
  -v server_name=example.com \
  -v port=80 \
  -v root=/var/www/html \
  -o /etc/nginx/sites-available/mysite
```

### Example 3: Batch Processing

```bash
# Validate all templates in a directory
for template in templates/*.j2; do
  echo "Validating $(basename $template)..."
  template-render validate $(basename $template) -d templates/ -f vars.json
done
```

## Development

```bash
# Install in development mode
make install

# Run linters
make lint

# Format code
make format

# Run tests
make test

# Clean build artifacts
make clean
```

## Troubleshooting

### Template Not Found

```bash
# List available templates to check the name
template-render list -d templates/

# Check template directory exists
ls -la templates/
```

### Missing Variables

```bash
# Use info command to see required variables
template-render info app.j2 -d templates/

# Use validate command to check your variables
template-render validate app.j2 -f vars.json

# Use --show-info flag when rendering
template-render render app.j2 -f vars.json --show-info
```

### Strict Mode Errors

```bash
# Disable strict mode to allow missing variables
template-render render app.j2 -f vars.json --no-strict
```

## Integration with Other Tools

### With Make

```makefile
render-config:
	template-render render app.j2 -f vars.json -o config/app.conf

deploy: render-config
	# Deploy with rendered config
```

### With Shell Scripts

```bash
#!/bin/bash
# Generate multiple configs
for env in dev staging prod; do
  template-render render app.j2 \
    -f "vars/${env}.json" \
    -o "config/${env}.conf"
done
```

### Piping Output

```bash
# Pipe to other commands
template-render render app.j2 -f vars.json | kubectl apply -f -

# Use with Docker
template-render render Dockerfile.j2 -f vars.json | docker build -t myapp -
```

## See Also

- [dotfiles-template-renderer](../../modules/template-renderer/) - The underlying template rendering module
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Template syntax reference

