# Integration Guide

This guide shows how to integrate the template_renderer module with other components.

---

## Pipeline Integration

### RenderTemplateStep

The template_renderer integrates with the pipeline system via `RenderTemplateStep`.

**Location:** `src/dotfiles-installer/cli/src/pipeline_steps/container_steps.py`

**Implementation:**
```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig
from src.modules.pipeline.core.types import PipelineContext, PipelineStep

class RenderTemplateStep(PipelineStep):
    """Pipeline step to render a Jinja2 template."""
    
    def __init__(self, template_name, template_dir, variables, output_key, strict_mode=True):
        self.template_name = template_name
        self.template_dir = template_dir
        self.variables = variables
        self.output_key = output_key
        self.strict_mode = strict_mode
    
    def run(self, context: PipelineContext) -> PipelineContext:
        # Create renderer
        renderer = Jinja2Renderer(
            self.template_dir,
            config=RenderConfig(strict_mode=self.strict_mode),
        )
        
        # Render template
        rendered = renderer.render(self.template_name, self.variables)
        
        # Store in context
        context.results[self.output_key] = rendered
        
        return context
```

**Usage:**
```python
from src.modules.pipeline import Pipeline
from src.pipeline_steps.container_steps import RenderTemplateStep

step = RenderTemplateStep(
    template_name="Dockerfile.j2",
    template_dir="templates",
    variables={"base_image": "python:3.12", "workdir": "/app"},
    output_key="dockerfile",
)

pipeline = Pipeline.create([step])
context = pipeline.run(context)

dockerfile = context.results["dockerfile"]
```

---

## Container Manager Integration

### Dockerfile Rendering

The template_renderer renders Dockerfiles before passing them to the container manager.

**Pattern:**
```python
from dotfiles_template_renderer import Jinja2Renderer
from dotfiles_container_manager import DockerManager, BuildContext
from pathlib import Path

# Step 1: Render Dockerfile
renderer = Jinja2Renderer("templates")
dockerfile = renderer.render("python.j2", variables={
    "base_image": "python:3.12-slim",
    "workdir": "/app",
    "system_packages": ["git", "curl"],
})

# Step 2: Pass to container manager
manager = DockerManager()
build_context = BuildContext(
    dockerfile_content=dockerfile,  # Rendered content
    context_dir=Path("."),
    tag="myapp:latest",
)

# Step 3: Build image
manager.build_image(build_context)
```

**Benefits:**
- Separation of concerns: template rendering vs. container management
- Template reusability across different projects
- Easy to test templates independently

---

## Configuration File Generation

### Multi-File Configuration

Generate multiple configuration files from templates.

**Example:**
```python
from dotfiles_template_renderer import Jinja2Renderer
from pathlib import Path

renderer = Jinja2Renderer("config_templates")

# Define configurations
configs = {
    "nginx.conf": {"server_name": "example.com", "port": 80},
    "app.yaml": {"env": "production", "debug": False},
    "database.ini": {"host": "localhost", "port": 5432},
}

# Render all configs
config_dir = Path("/etc/myapp")
config_dir.mkdir(exist_ok=True)

for template_name, variables in configs.items():
    output_path = config_dir / template_name
    renderer.render_to_file(f"{template_name}.j2", output_path, variables)
    print(f"Created {output_path}")
```

---

## Dynamic Template Selection

### Platform-Specific Templates

Select templates based on platform or environment.

**Implementation:**
```python
from dotfiles_template_renderer import Jinja2Renderer
import platform

class TemplateManager:
    def __init__(self, template_dir):
        self.renderer = Jinja2Renderer(template_dir)
    
    def render_for_platform(self, base_name, variables):
        """Render template based on current platform."""
        system = platform.system().lower()
        template_map = {
            "linux": f"{base_name}_linux.j2",
            "darwin": f"{base_name}_macos.j2",
            "windows": f"{base_name}_windows.j2",
        }
        template_name = template_map.get(system, f"{base_name}_default.j2")
        return self.renderer.render(template_name, variables)
    
    def list_templates_for_category(self, category):
        """List templates in a category."""
        all_templates = self.renderer.get_available_templates()
        return [t for t in all_templates if t.startswith(f"{category}/")]

# Usage
manager = TemplateManager("templates")
config = manager.render_for_platform("install_script", variables={
    "app_name": "myapp",
    "version": "1.0.0"
})
```

---

## Web Framework Integration

### Flask Integration

Use template_renderer in Flask applications.

**Example:**
```python
from flask import Flask, request, jsonify
from dotfiles_template_renderer import Jinja2Renderer, MissingVariableError

app = Flask(__name__)
renderer = Jinja2Renderer("templates")

@app.route("/render", methods=["POST"])
def render_template():
    data = request.json
    template_name = data.get("template")
    variables = data.get("variables", {})
    
    try:
        result = renderer.render(template_name, variables=variables)
        return jsonify({"success": True, "result": result})
    except MissingVariableError as e:
        return jsonify({
            "success": False,
            "error": "Missing variables",
            "missing": e.missing_variables
        }), 400

@app.route("/templates", methods=["GET"])
def list_templates():
    templates = renderer.get_available_templates()
    return jsonify({"templates": templates})

@app.route("/templates/<path:template_name>/info", methods=["GET"])
def template_info(template_name):
    info = renderer.get_template_info(template_name)
    return jsonify({
        "name": info.name,
        "size": info.size,
        "required_variables": info.required_variables
    })
```

---

## CLI Integration

### Command-Line Tool

Create a CLI tool for template rendering.

**Example:**
```python
import click
from dotfiles_template_renderer import Jinja2Renderer
from pathlib import Path
import json

@click.group()
def cli():
    """Template rendering CLI."""
    pass

@cli.command()
@click.argument("template")
@click.option("--template-dir", default="templates", help="Template directory")
@click.option("--vars", help="Variables as JSON string")
@click.option("--vars-file", type=click.Path(exists=True), help="Variables from JSON file")
@click.option("--output", type=click.Path(), help="Output file")
def render(template, template_dir, vars, vars_file, output):
    """Render a template."""
    renderer = Jinja2Renderer(template_dir)
    
    # Load variables
    variables = {}
    if vars:
        variables = json.loads(vars)
    elif vars_file:
        with open(vars_file) as f:
            variables = json.load(f)
    
    # Render
    result = renderer.render(template, variables=variables)
    
    # Output
    if output:
        Path(output).write_text(result)
        click.echo(f"Rendered to {output}")
    else:
        click.echo(result)

@cli.command()
@click.option("--template-dir", default="templates", help="Template directory")
def list_templates(template_dir):
    """List available templates."""
    renderer = Jinja2Renderer(template_dir)
    templates = renderer.get_available_templates()
    for template in templates:
        click.echo(template)

@cli.command()
@click.argument("template")
@click.option("--template-dir", default="templates", help="Template directory")
def info(template, template_dir):
    """Show template information."""
    renderer = Jinja2Renderer(template_dir)
    info = renderer.get_template_info(template)
    click.echo(f"Name: {info.name}")
    click.echo(f"Size: {info.size} bytes")
    click.echo(f"Variables: {', '.join(info.required_variables)}")

if __name__ == "__main__":
    cli()
```

**Usage:**
```bash
# Render template
python cli.py render app.j2 --vars '{"name":"myapp","version":"1.0"}'

# Render with vars file
python cli.py render app.j2 --vars-file vars.json --output output.txt

# List templates
python cli.py list-templates

# Show template info
python cli.py info app.j2
```

---

## Testing Integration

### Unit Testing Templates

Test templates using pytest.

**Example:**
```python
import pytest
from dotfiles_template_renderer import Jinja2Renderer, MissingVariableError

@pytest.fixture
def renderer():
    return Jinja2Renderer("tests/fixtures/templates")

def test_render_basic(renderer):
    result = renderer.render("simple.j2", variables={"name": "test"})
    assert "test" in result

def test_render_missing_variables(renderer):
    with pytest.raises(MissingVariableError) as exc_info:
        renderer.render("app.j2", variables={"name": "test"})
    assert "version" in exc_info.value.missing_variables

def test_validate(renderer):
    validation = renderer.validate("app.j2", variables={"name": "test"})
    assert not validation.is_valid
    assert "version" in validation.missing_variables

def test_get_template_variables(renderer):
    variables = renderer.get_template_variables("app.j2")
    assert "name" in variables
    assert "version" in variables

def test_get_available_templates(renderer):
    templates = renderer.get_available_templates()
    assert "simple.j2" in templates
    assert "app.j2" in templates
```

---

## CI/CD Integration

### GitHub Actions

Use template_renderer in CI/CD pipelines.

**Example:**
```yaml
name: Generate Configs

on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install jinja2
      
      - name: Generate configurations
        run: |
          python scripts/generate_configs.py
      
      - name: Commit generated files
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add generated/
          git commit -m "Auto-generate configs" || echo "No changes"
          git push
```

**generate_configs.py:**
```python
from dotfiles_template_renderer import Jinja2Renderer
from pathlib import Path
import os

renderer = Jinja2Renderer("templates")

# Get environment-specific variables
env = os.getenv("ENVIRONMENT", "production")
variables = {
    "environment": env,
    "version": os.getenv("VERSION", "1.0.0"),
    "debug": env == "development",
}

# Generate configs
output_dir = Path("generated")
output_dir.mkdir(exist_ok=True)

for template in renderer.get_available_templates():
    output_file = output_dir / template.replace(".j2", "")
    renderer.render_to_file(template, output_file, variables)
    print(f"Generated {output_file}")
```

---

## See Also

- [Usage Patterns](usage_patterns.md) - Common patterns
- [Best Practices](best_practices.md) - Recommended practices
- [API Reference](../api/core.md) - Detailed API docs

