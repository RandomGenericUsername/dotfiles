# Getting Started

**Module:** `dotfiles_container_manager`  
**Purpose:** Quick start guide for using the container manager

---

## Table of Contents

1. [Installation](#installation)
2. [Prerequisites](#prerequisites)
3. [Basic Usage](#basic-usage)
4. [Common Workflows](#common-workflows)
5. [Next Steps](#next-steps)

---

## Installation

The Container Manager is a standalone uv project. Install it as a dependency in your project:

### Using uv

```bash
# Add as a dependency
uv add dotfiles-container-manager

# Or add to pyproject.toml
[dependencies]
dotfiles-container-manager = { path = "src/common/modules/container_manager" }
```

### Verify Installation

```python
from dotfiles_container_manager import ContainerEngineFactory, ContainerRuntime

# Create an engine
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)
print(f"Container Manager installed successfully!")
print(f"Runtime: {engine.runtime}")
print(f"Version: {engine.version()}")
```

---

## Prerequisites

### System Requirements

- **Docker** or **Podman** installed and running
- **Python 3.10+**
- Appropriate permissions to run container commands

### Check Docker Availability

```bash
# Check if Docker is installed
docker --version

# Check if Docker daemon is running
docker ps
```

### Check Podman Availability

```bash
# Check if Podman is installed
podman --version

# Check if Podman is working
podman ps
```

---

## Basic Usage

### 1. Create a Container Engine

```python
from dotfiles_container_manager import ContainerEngineFactory, ContainerRuntime

# Create a Docker engine
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Or use the convenience method
engine = ContainerEngineFactory.create_docker()
```

### 2. Build an Image

```python
from dotfiles_container_manager import BuildContext

# Create a build context with an in-memory Dockerfile
context = BuildContext(
    dockerfile="""
    FROM alpine:latest
    RUN apk add --no-cache python3
    CMD ["python3", "--version"]
    """
)

# Build the image
image_id = engine.images.build(context, "my-python-image")
print(f"Built image: {image_id}")
```

### 3. Run a Container

```python
from dotfiles_container_manager import RunConfig

# Create a run configuration
config = RunConfig(
    image="my-python-image",
    name="my-container",
    detach=True,  # Run in background
)

# Run the container
container_id = engine.containers.run(config)
print(f"Started container: {container_id}")
```

### 4. View Container Logs

```python
# Get container logs
logs = engine.containers.logs(container_id)
print(f"Container output:\n{logs}")
```

### 5. Cleanup

```python
# Stop and remove the container
engine.containers.stop(container_id)
engine.containers.remove(container_id)

# Remove the image
engine.images.remove("my-python-image")

print("Cleanup complete!")
```

---

## Common Workflows

### Workflow 1: Build and Run a Simple Application

```python
from dotfiles_container_manager import (
    ContainerEngineFactory,
    ContainerRuntime,
    BuildContext,
    RunConfig,
)

# 1. Create engine
engine = ContainerEngineFactory.create_docker()

# 2. Build image with application code
context = BuildContext(
    dockerfile="""
    FROM python:3.11-slim
    WORKDIR /app
    COPY app.py /app/
    CMD ["python", "app.py"]
    """,
    files={
        "app.py": b"print('Hello from container!')"
    }
)

image_id = engine.images.build(context, "hello-app")

# 3. Run container
config = RunConfig(
    image="hello-app",
    name="hello-container",
    detach=False,  # Wait for completion
)

container_id = engine.containers.run(config)

# 4. View output
logs = engine.containers.logs(container_id)
print(logs)  # Output: Hello from container!

# 5. Cleanup
engine.containers.remove(container_id)
engine.images.remove("hello-app")
```

### Workflow 2: Run with Environment Variables

```python
from dotfiles_container_manager import RunConfig

config = RunConfig(
    image="alpine:latest",
    name="env-test",
    command=["sh", "-c", "echo $MESSAGE"],
    environment={
        "MESSAGE": "Hello from environment!",
        "DEBUG": "true",
    },
    detach=False,
)

container_id = engine.containers.run(config)
logs = engine.containers.logs(container_id)
print(logs)  # Output: Hello from environment!

engine.containers.remove(container_id)
```

### Workflow 3: Run with Volume Mounts

```python
from dotfiles_container_manager import RunConfig, VolumeMount

# Create a volume
volume_name = engine.volumes.create("my-data")

# Run container with volume
config = RunConfig(
    image="alpine:latest",
    name="volume-test",
    command=["sh", "-c", "echo 'data' > /data/file.txt && cat /data/file.txt"],
    volumes=[
        VolumeMount(
            source=volume_name,
            target="/data",
            read_only=False,
        )
    ],
    detach=False,
)

container_id = engine.containers.run(config)
logs = engine.containers.logs(container_id)
print(logs)  # Output: data

# Cleanup
engine.containers.remove(container_id)
engine.volumes.remove(volume_name)
```

### Workflow 4: Run with Port Mapping

```python
from dotfiles_container_manager import RunConfig, PortMapping

config = RunConfig(
    image="nginx:alpine",
    name="web-server",
    ports=[
        PortMapping(
            container_port=80,
            host_port=8080,
            protocol="tcp",
        )
    ],
    detach=True,
)

container_id = engine.containers.run(config)
print(f"Web server running at http://localhost:8080")

# Later: stop and remove
engine.containers.stop(container_id)
engine.containers.remove(container_id)
```

### Workflow 5: Execute Commands in Running Container

```python
from dotfiles_container_manager import RunConfig

# Start a long-running container
config = RunConfig(
    image="alpine:latest",
    name="exec-test",
    command=["sleep", "3600"],
    detach=True,
)

container_id = engine.containers.run(config)

# Execute a command in the running container
output = engine.containers.exec(
    container_id,
    ["echo", "Hello from exec!"]
)
print(output)  # Output: Hello from exec!

# Cleanup
engine.containers.stop(container_id)
engine.containers.remove(container_id)
```

### Workflow 6: List and Inspect Resources

```python
# List all images
images = engine.images.list()
for image in images:
    print(f"Image: {image.id} - Tags: {image.tags}")

# List all containers
containers = engine.containers.list(all=True)
for container in containers:
    print(f"Container: {container.id} - Name: {container.name} - State: {container.state}")

# Inspect specific image
image_info = engine.images.inspect("alpine:latest")
print(f"Image size: {image_info.size}")
print(f"Created: {image_info.created}")

# Inspect specific container
container_info = engine.containers.inspect(container_id)
print(f"Container state: {container_info.state}")
print(f"Container IP: {container_info.network_settings.get('IPAddress')}")
```

### Workflow 7: Pull and Push Images

```python
# Pull an image from a registry
engine.images.pull("alpine:latest")

# Tag an image
engine.images.tag("my-app:latest", "registry.example.com/my-app:v1.0")

# Push to registry (requires authentication)
engine.images.push("registry.example.com/my-app:v1.0")
```

### Workflow 8: Network Management

```python
# Create a custom network
network_id = engine.networks.create(
    name="my-network",
    driver="bridge",
)

# Run containers on the network
config1 = RunConfig(
    image="alpine:latest",
    name="container1",
    command=["sleep", "3600"],
    network="my-network",
    detach=True,
)

config2 = RunConfig(
    image="alpine:latest",
    name="container2",
    command=["sleep", "3600"],
    network="my-network",
    detach=True,
)

container1_id = engine.containers.run(config1)
container2_id = engine.containers.run(config2)

# Containers can now communicate using their names
output = engine.containers.exec(
    container1_id,
    ["ping", "-c", "1", "container2"]
)
print(output)

# Cleanup
engine.containers.stop(container1_id)
engine.containers.stop(container2_id)
engine.containers.remove(container1_id)
engine.containers.remove(container2_id)
engine.networks.remove(network_id)
```

---

## Next Steps

### Learn More

- **[Usage Patterns](usage_patterns.md)** - Advanced patterns and best practices
- **[API Reference](../api/managers.md)** - Complete API documentation
- **[Examples](../reference/examples.md)** - More comprehensive examples

### Common Tasks

- **Building multi-stage images** - See [Usage Patterns](usage_patterns.md#multi-stage-builds)
- **Managing container lifecycle** - See [Usage Patterns](usage_patterns.md#container-lifecycle)
- **Error handling** - See [API Reference](../api/exceptions.md)
- **Testing** - See [Best Practices](best_practices.md#testing)

### Troubleshooting

If you encounter issues:

1. **Check runtime availability:**
   ```python
   if not engine.is_available():
       print("Runtime not available!")
   ```

2. **Check runtime version:**
   ```python
   print(engine.version())
   ```

3. **Handle exceptions:**
   ```python
   from dotfiles_container_manager import ImageBuildError
   
   try:
       engine.images.build(context, "my-image")
   except ImageBuildError as e:
       print(f"Build failed: {e.message}")
       print(f"Error: {e.stderr}")
   ```

4. **See [Troubleshooting Guide](../reference/troubleshooting.md)** for common issues

---

**Ready to dive deeper? Check out [Usage Patterns](usage_patterns.md) for advanced workflows!**

