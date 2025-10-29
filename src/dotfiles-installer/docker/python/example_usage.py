#!/usr/bin/env python3
"""
Example usage of the Docker templating functionality.

This script demonstrates how to use the Docker utilities to render
Dockerfile templates and build Docker images without writing files to disk.
"""

from pathlib import Path
from typing import Dict, Any

from src.utils.docker_manager import (
    DockerTemplateRenderer,
    DockerImageBuilder,
    render_and_build_docker_image,
    DockerError,
)


def example_basic_rendering():
    """Example: Basic Dockerfile template rendering."""
    print("=== Basic Template Rendering ===")
    
    # Get the template directory
    template_dir = Path(__file__).parent
    
    # Create renderer
    renderer = DockerTemplateRenderer(template_dir)
    
    # Basic template variables
    template_vars = {
        "base_image": "python:3.12-slim",
        "maintainer": "dotfiles-installer",
        "version": "1.0.0",
        "description": "My Python application",
        "create_user": True,
        "app_user": "myapp",
        "workdir": "/app",
        "use_uv": True,
        "port": 8000,
    }
    
    try:
        # Render the template
        dockerfile_content = renderer.render_dockerfile(
            "Dockerfile.j2", **template_vars
        )
        
        print("Rendered Dockerfile:")
        print("-" * 50)
        print(dockerfile_content)
        print("-" * 50)
        
    except DockerError as e:
        print(f"Error rendering template: {e}")


def example_advanced_rendering():
    """Example: Advanced Dockerfile template rendering with system packages."""
    print("\n=== Advanced Template Rendering ===")
    
    template_dir = Path(__file__).parent
    renderer = DockerTemplateRenderer(template_dir)
    
    # Advanced template variables
    template_vars = {
        "base_image": "python:3.12-slim",
        "maintainer": "dotfiles-installer",
        "version": "2.0.0",
        "description": "Advanced Python application with system dependencies",
        "system_packages": [
            "git",
            "curl",
            "build-essential",
            "libpq-dev",
        ],
        "env_vars": {
            "APP_ENV": "production",
            "DATABASE_URL": "postgresql://localhost/myapp",
            "REDIS_URL": "redis://localhost:6379",
        },
        "create_user": True,
        "app_user": "webapp",
        "workdir": "/opt/app",
        "use_uv": True,
        "port": 8080,
        "healthcheck": {
            "command": "curl -f http://localhost:8080/health || exit 1",
            "interval": "30s",
            "timeout": "10s",
            "start_period": "5s",
            "retries": 3,
        },
        "copy_patterns": [
            {"src": "requirements.pip", "dest": "./requirements.pip"},
            {"src": "src/", "dest": "./src/"},
            {"src": "config/", "dest": "./config/"},
        ],
        "entrypoint": ["python", "-m", "uvicorn"],
        "cmd": ["src.main:app", "--host", "0.0.0.0", "--port", "8080"],
    }
    
    try:
        dockerfile_content = renderer.render_dockerfile(
            "Dockerfile.j2", **template_vars
        )
        
        print("Advanced Dockerfile:")
        print("-" * 50)
        print(dockerfile_content)
        print("-" * 50)
        
    except DockerError as e:
        print(f"Error rendering advanced template: {e}")


def example_build_image():
    """Example: Build Docker image from template (requires Docker)."""
    print("\n=== Building Docker Image ===")
    
    template_dir = Path(__file__).parent
    
    # Template variables for a simple Python app
    template_vars = {
        "base_image": "python:3.12-slim",
        "maintainer": "dotfiles-installer-example",
        "version": "1.0.0",
        "description": "Example Python application",
        "create_user": True,
        "app_user": "exampleapp",
        "workdir": "/app",
        "use_uv": False,  # Use regular pip for simplicity
        "main_script": "app.py",
    }
    
    # Create a simple Python app file to include in build context
    app_content = '''#!/usr/bin/env python3
print("Hello from Docker container!")
print("This is an example Python application.")
'''
    
    # Additional files for build context
    context_files = {
        "app.py": app_content.encode("utf-8"),
        "requirements.pip": b"# No additional requirements for this example\n",
    }
    
    try:
        # Build the image
        image_id = render_and_build_docker_image(
            template_dir=template_dir,
            image_name="dotfiles-installer-example:latest",
            template_name="Dockerfile.j2",
            template_vars=template_vars,
            context_files=context_files,
            timeout=300,  # 5 minutes timeout
        )
        
        print(f"Successfully built Docker image: {image_id}")
        print("You can run it with:")
        print("docker run --rm dotfiles-installer-example:latest")
        
    except DockerError as e:
        print(f"Error building Docker image: {e}")
        if "docker" in str(e).lower():
            print("Make sure Docker is installed and running.")


def example_list_templates():
    """Example: List available templates."""
    print("\n=== Available Templates ===")
    
    template_dir = Path(__file__).parent
    renderer = DockerTemplateRenderer(template_dir)
    
    templates = renderer.get_available_templates()
    
    if templates:
        print("Available Dockerfile templates:")
        for template in templates:
            print(f"  - {template}")
    else:
        print("No templates found in the directory.")


def example_with_configuration():
    """Example: Using Docker utilities with application configuration."""
    print("\n=== Using with App Configuration ===")
    
    # This would typically come from your app's configuration system
    docker_config = {
        "command": "docker",
        "build_timeout": 600,
        "template_directory": Path(__file__).parent,
        "default_template": "Dockerfile.j2",
        "default_base_image": "python:3.12-slim",
        "create_user": True,
        "app_user": "appuser",
        "workdir": "/app",
        "use_uv": True,
    }
    
    # Use configuration values
    renderer = DockerTemplateRenderer(docker_config["template_directory"])
    builder = DockerImageBuilder(docker_config["command"])
    
    # Check if Docker is available
    try:
        if builder.image_exists("hello-world"):
            print("Docker is available and working.")
        else:
            print("Docker is available but hello-world image not found.")
    except DockerError:
        print("Docker is not available or not working.")
    
    print(f"Template directory: {docker_config['template_directory']}")
    print(f"Available templates: {renderer.get_available_templates()}")


if __name__ == "__main__":
    """Run all examples."""
    print("Docker Template and Build Examples")
    print("=" * 50)
    
    # Run examples
    example_list_templates()
    example_basic_rendering()
    example_advanced_rendering()
    example_with_configuration()
    
    # Only try to build if user confirms (requires Docker)
    try:
        response = input("\nDo you want to try building a Docker image? (y/N): ")
        if response.lower().startswith('y'):
            example_build_image()
        else:
            print("Skipping Docker image build example.")
    except KeyboardInterrupt:
        print("\nExamples completed.")
