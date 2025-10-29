# Docker Python Templates

This directory contains Jinja2 templates and utilities for building Docker images for Python applications without writing intermediate files to disk.

## Features

- **Jinja2 Templates**: Flexible Dockerfile templates with variable substitution
- **In-Memory Building**: Build Docker images without writing Dockerfile to disk
- **Configuration Integration**: Seamlessly integrates with the application's settings system
- **Error Handling**: Comprehensive error handling for Docker operations
- **Type Safety**: Full type hints and validation

## Files

- `Dockerfile.j2` - Main Dockerfile template with Jinja2 syntax
- `requirements.pip` - Base Python dependencies for containers
- `example_usage.py` - Complete usage examples
- `README.md` - This documentation

## Quick Start

### Basic Usage

```python
from pathlib import Path
from src.utils.docker_manager import render_and_build_docker_image

# Build a Docker image from template
template_dir = Path("src/dotfiles-installer/docker/python")
image_id = render_and_build_docker_image(
    template_dir=template_dir,
    image_name="my-python-app:latest",
    template_vars={
        "base_image": "python:3.12-slim",
        "maintainer": "your-name",
        "app_user": "myapp",
        "use_uv": True,
        "port": 8000,
    }
)
print(f"Built image: {image_id}")
```

### Advanced Usage

```python
from src.utils.docker_manager import DockerTemplateRenderer, DockerImageBuilder

# Render template only
renderer = DockerTemplateRenderer(template_dir)
dockerfile_content = renderer.render_dockerfile(
    "Dockerfile.j2",
    base_image="python:3.12-slim",
    system_packages=["git", "curl", "build-essential"],
    env_vars={
        "APP_ENV": "production",
        "DATABASE_URL": "postgresql://localhost/myapp"
    },
    healthcheck={
        "command": "curl -f http://localhost:8000/health || exit 1",
        "interval": "30s",
        "timeout": "10s",
        "retries": 3
    }
)

# Build image with additional context files
builder = DockerImageBuilder()
context_files = {
    "app.py": open("src/main.py", "rb").read(),
    "config.json": '{"debug": false}'.encode()
}

image_id = builder.build_image(
    dockerfile_content=dockerfile_content,
    image_name="advanced-app:latest",
    context_files=context_files,
    build_args={"BUILD_ENV": "production"}
)
```

## Template Variables

The `Dockerfile.j2` template supports the following variables:

### Basic Configuration
- `base_image` (default: "python:3.12-slim") - Base Docker image
- `maintainer` (default: "dotfiles-installer") - Image maintainer
- `version` (default: "1.0.0") - Image version
- `description` (default: "Python application container") - Image description

### Environment & Dependencies
- `env_vars` (dict) - Environment variables to set
- `system_packages` (list) - System packages to install via apt
- `requirements_file` (default: "requirements.pip") - Python requirements file
- `use_uv` (default: false) - Use uv for faster dependency installation

### User & Security
- `create_user` (default: true) - Create non-root user
- `app_user` (default: "appuser") - Application user name
- `workdir` (default: "/app") - Working directory

### Application
- `copy_patterns` (list) - Custom copy patterns for files
- `port` (int) - Port to expose
- `main_script` (default: "main.py") - Main Python script
- `entrypoint` (list) - Custom entrypoint
- `cmd` (list) - Custom command

### Health Check
- `healthcheck` (dict) - Health check configuration
  - `command` - Health check command
  - `interval` (default: "30s") - Check interval
  - `timeout` (default: "10s") - Check timeout
  - `start_period` (default: "5s") - Start period
  - `retries` (default: 3) - Number of retries

## Configuration

Add Docker settings to your `settings.toml`:

```toml
[docker]
command = "docker"  # or "podman"
build_timeout = 600
template_directory = "src/dotfiles-installer/docker/python"
default_template = "Dockerfile.j2"
default_base_image = "python:3.12-slim"
create_user = true
app_user = "appuser"
workdir = "/app"
use_uv = true
```

## Examples

### Simple Web Application

```python
template_vars = {
    "base_image": "python:3.12-slim",
    "maintainer": "web-team",
    "description": "Flask web application",
    "system_packages": ["curl"],
    "env_vars": {
        "FLASK_ENV": "production",
        "PORT": "5000"
    },
    "port": 5000,
    "healthcheck": {
        "command": "curl -f http://localhost:5000/health || exit 1"
    },
    "main_script": "app.py"
}
```

### Data Processing Application

```python
template_vars = {
    "base_image": "python:3.12",
    "description": "Data processing application",
    "system_packages": ["git", "build-essential", "libpq-dev"],
    "env_vars": {
        "PYTHONPATH": "/app/src",
        "DATA_DIR": "/data"
    },
    "use_uv": True,
    "copy_patterns": [
        {"src": "src/", "dest": "./src/"},
        {"src": "data/", "dest": "./data/"},
        {"src": "requirements.pip", "dest": "./requirements.pip"}
    ],
    "cmd": ["python", "-m", "src.processor"]
}
```

## Testing

Run the tests:

```bash
# Unit tests (no Docker required)
uv run python -m pytest tests/test_docker_manager.py -v

# Integration tests (requires Docker)
uv run python -m pytest tests/test_docker_manager.py::TestDockerIntegration -v -m integration

# All tests including slow ones
uv run python -m pytest tests/test_docker_manager.py -v -m "not slow"
```

## Error Handling

The Docker utilities provide comprehensive error handling:

```python
from src.utils.docker_manager import DockerError

try:
    image_id = render_and_build_docker_image(...)
except DockerError as e:
    print(f"Docker operation failed: {e}")
    if e.command:
        print(f"Failed command: {e.command}")
    if e.exit_code:
        print(f"Exit code: {e.exit_code}")
```

## Requirements

- Python 3.12+
- Jinja2 (automatically installed)
- Docker or Podman (for building images)

## Integration with Pipeline System

The Docker utilities can be integrated with the existing pipeline system:

```python
from src.modules.pipeline import PipelineStep, PipelineContext

class BuildDockerImageStep(PipelineStep):
    def __init__(self, image_name: str, template_vars: dict):
        self.image_name = image_name
        self.template_vars = template_vars
    
    @property
    def step_id(self) -> str:
        return "build_docker_image"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        try:
            template_dir = context.app_config.docker.template_directory
            image_id = render_and_build_docker_image(
                template_dir=template_dir,
                image_name=self.image_name,
                template_vars=self.template_vars
            )
            context.results["docker_image_id"] = image_id
            context.logger_instance.info(f"Built Docker image: {image_id}")
        except DockerError as e:
            context.errors.append(e)
            context.logger_instance.error(f"Docker build failed: {e}")
        
        return context
```
