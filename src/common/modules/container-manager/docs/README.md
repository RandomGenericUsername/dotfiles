# Container Manager Documentation

**Version:** 1.0
**Module:** `dotfiles_container_manager`
**Purpose:** Runtime-agnostic container management with Docker implementation

---

## 📚 Overview

The Container Manager module provides a clean, runtime-agnostic interface for managing container operations. It supports Docker and Podman, with a focus on in-memory Dockerfile builds and type-safe operations.

### Key Features

- ✅ **Runtime-Agnostic Design** - Abstract interfaces work with Docker, Podman, or custom runtimes
- ✅ **In-Memory Dockerfile Builds** - Build images from strings without filesystem operations
- ✅ **Type-Safe Configuration** - Comprehensive dataclasses for all operations
- ✅ **Robust Error Handling** - Hierarchical exceptions with rich context
- ✅ **Clean Separation** - Core abstractions separate from implementations
- ✅ **Factory Pattern** - Easy engine creation and runtime selection

---

## 🚀 Quick Start

```python
from dotfiles_container_manager import (
    ContainerEngineFactory,
    ContainerRuntime,
    BuildContext,
    RunConfig,
)

# Create a Docker engine
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Build an image from in-memory Dockerfile
context = BuildContext(
    dockerfile="""
    FROM alpine:latest
    RUN apk add --no-cache python3
    CMD ["python3", "--version"]
    """
)
image_id = engine.images.build(context, "my-python-image")

# Run a container
config = RunConfig(
    image="my-python-image",
    name="my-container",
    detach=True,
)
container_id = engine.containers.run(config)

# Get container logs
logs = engine.containers.logs(container_id)
print(logs)

# Cleanup
engine.containers.stop(container_id)
engine.containers.remove(container_id)
engine.images.remove("my-python-image")
```

---

## 📖 Documentation Structure

### Architecture

- **[Overview](architecture/overview.md)** - Module architecture and design
- **[Design Patterns](architecture/design_patterns.md)** - Patterns used in the module
- **[Component Relationships](architecture/component_relationships.md)** - How components interact

### API Reference

- **[Core Abstractions](api/core_abstractions.md)** - ContainerEngine base class
- **[Managers](api/managers.md)** - ImageManager, ContainerManager, VolumeManager, NetworkManager
- **[Types and Enums](api/types_and_enums.md)** - Data models and enumerations
- **[Exceptions](api/exceptions.md)** - Exception hierarchy and error handling

### Guides

- **[Getting Started](guides/getting_started.md)** - Installation and basic usage
- **[Usage Patterns](guides/usage_patterns.md)** - Common patterns and workflows
- **[Integration](guides/integration.md)** - Integrating with other modules
- **[Best Practices](guides/best_practices.md)** - Recommendations and anti-patterns

### Reference

- **[Examples](reference/examples.md)** - Complete code examples
- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions

---

## 🎯 Core Concepts

### ContainerEngine

The main entry point for all container operations. Provides access to four specialized managers:

```python
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Access managers
engine.images      # ImageManager - build, pull, push, tag images
engine.containers  # ContainerManager - run, stop, remove containers
engine.volumes     # VolumeManager - create, remove volumes
engine.networks    # NetworkManager - create, connect networks
```

### Managers

Four specialized managers handle different aspects of container operations:

1. **ImageManager** - Image lifecycle (build, pull, push, tag, remove)
2. **ContainerManager** - Container lifecycle (run, start, stop, remove, exec)
3. **VolumeManager** - Volume management (create, remove, inspect)
4. **NetworkManager** - Network management (create, connect, disconnect)

### Configuration Types

Type-safe configuration using dataclasses:

- **BuildContext** - Image build configuration
- **RunConfig** - Container run configuration
- **VolumeMount** - Volume mount specification
- **PortMapping** - Port mapping specification

### Info Types

Structured information about resources:

- **ImageInfo** - Image metadata
- **ContainerInfo** - Container metadata
- **VolumeInfo** - Volume metadata
- **NetworkInfo** - Network metadata

---

## 🔧 Installation

This module is a standalone uv project. Install it as a dependency:

```bash
# Using uv
uv add dotfiles-container-manager

# Or add to pyproject.toml
[dependencies]
dotfiles-container-manager = { path = "src/common/modules/container_manager" }
```

---

## 📦 Public API

### Factory

```python
from dotfiles_container_manager import ContainerEngineFactory

# Create engine by runtime
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Convenience methods
docker_engine = ContainerEngineFactory.create_docker()
podman_engine = ContainerEngineFactory.create_podman()
```

### Core Classes

```python
from dotfiles_container_manager import (
    ContainerEngine,      # Base class
    ImageManager,         # Image operations interface
    ContainerManager,     # Container operations interface
    VolumeManager,        # Volume operations interface
    NetworkManager,       # Network operations interface
)
```

### Enums

```python
from dotfiles_container_manager import (
    ContainerRuntime,     # DOCKER, PODMAN
    ContainerState,       # CREATED, RUNNING, EXITED, etc.
    RestartPolicy,        # NO, ON_FAILURE, ALWAYS, UNLESS_STOPPED
    NetworkMode,          # BRIDGE, HOST, NONE, CONTAINER
    VolumeDriver,         # LOCAL, NFS, TMPFS
    LogDriver,            # JSON_FILE, SYSLOG, JOURNALD, NONE
)
```

### Types

```python
from dotfiles_container_manager import (
    BuildContext,         # Image build configuration
    RunConfig,            # Container run configuration
    VolumeMount,          # Volume mount specification
    PortMapping,          # Port mapping specification
    ImageInfo,            # Image metadata
    ContainerInfo,        # Container metadata
    VolumeInfo,           # Volume metadata
    NetworkInfo,          # Network metadata
)
```

### Exceptions

```python
from dotfiles_container_manager import (
    ContainerError,              # Base exception
    ImageError,                  # Image operation errors
    ImageNotFoundError,          # Image not found
    ImageBuildError,             # Build failures
    ContainerRuntimeError,       # Container operation errors
    ContainerNotFoundError,      # Container not found
    VolumeError,                 # Volume operation errors
    VolumeNotFoundError,         # Volume not found
    NetworkError,                # Network operation errors
    NetworkNotFoundError,        # Network not found
    RuntimeNotAvailableError,    # Runtime not available
    InvalidConfigError,          # Invalid configuration
)
```

### Implementations

```python
from dotfiles_container_manager import (
    DockerEngine,                # Docker engine implementation
    DockerImageManager,          # Docker image manager
    DockerContainerManager,      # Docker container manager
    DockerVolumeManager,         # Docker volume manager
    DockerNetworkManager,        # Docker network manager
)
```

---

## 🔗 Related Documentation

- **[Investigation Helpers](helpers/README.md)** - Investigation methodology and progress
- **[Architecture Deep Dive](architecture/overview.md)** - Detailed architecture documentation
- **[Complete Examples](reference/examples.md)** - Real-world usage examples

---

## 📝 License

Part of the dotfiles project.

---

**Ready to get started? Check out the [Getting Started Guide](guides/getting_started.md)!**
