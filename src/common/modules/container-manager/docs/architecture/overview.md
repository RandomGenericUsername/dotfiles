# Architecture Overview

**Module:** `dotfiles_container_manager`
**Design:** Runtime-agnostic container management

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Module Structure](#module-structure)
3. [Design Principles](#design-principles)
4. [Component Layers](#component-layers)
5. [Data Flow](#data-flow)
6. [Extension Points](#extension-points)

---

## High-Level Architecture

The Container Manager follows a **layered architecture** with clear separation between abstractions and implementations:

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Code                              │
│  (CLI, Scripts, Other Modules)                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  Factory Layer                               │
│  ContainerEngineFactory                                     │
│  - Runtime selection                                        │
│  - Engine creation                                          │
│  - Availability checking                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 Abstraction Layer                            │
│  ContainerEngine (ABC)                                      │
│  ├── ImageManager (ABC)                                     │
│  ├── ContainerManager (ABC)                                 │
│  ├── VolumeManager (ABC)                                    │
│  └── NetworkManager (ABC)                                   │
│                                                              │
│  Types: BuildContext, RunConfig, VolumeMount, PortMapping   │
│  Enums: ContainerRuntime, ContainerState, RestartPolicy     │
│  Exceptions: ContainerError hierarchy                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Implementation Layer                            │
│  DockerEngine                                               │
│  ├── DockerImageManager                                     │
│  ├── DockerContainerManager                                 │
│  ├── DockerVolumeManager                                    │
│  └── DockerNetworkManager                                   │
│                                                              │
│  Utilities: Command execution, tar creation, parsing        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                Container Runtime                             │
│  Docker / Podman / Other                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### Directory Organization

```
src/dotfiles_container_manager/
├── __init__.py              # Public API exports
├── factory.py               # ContainerEngineFactory
│
├── core/                    # Core abstractions (runtime-agnostic)
│   ├── __init__.py
│   ├── base.py             # ContainerEngine ABC
│   ├── enums.py            # Enumerations
│   ├── exceptions.py       # Exception hierarchy
│   ├── types.py            # Data models (dataclasses)
│   └── managers/           # Manager interfaces
│       ├── __init__.py
│       ├── image.py        # ImageManager ABC
│       ├── container.py    # ContainerManager ABC
│       ├── volume.py       # VolumeManager ABC
│       └── network.py      # NetworkManager ABC
│
└── implementations/         # Runtime-specific implementations
    ├── __init__.py
    └── docker/             # Docker implementation
        ├── __init__.py
        ├── engine.py       # DockerEngine
        ├── image.py        # DockerImageManager
        ├── container.py    # DockerContainerManager
        ├── volume.py       # DockerVolumeManager
        ├── network.py      # DockerNetworkManager
        └── utils.py        # Docker utilities
```

### Separation of Concerns

**Core (`core/`):**
- Defines contracts (abstract base classes)
- Provides type definitions (dataclasses, enums)
- Defines exception hierarchy
- **No runtime-specific code**

**Implementations (`implementations/`):**
- Concrete implementations of core contracts
- Runtime-specific logic
- Command construction and execution
- Output parsing

**Factory (`factory.py`):**
- Engine creation logic
- Runtime selection
- Availability verification

---

## Design Principles

### 1. Runtime Agnostic

The module is designed to work with any container runtime:

```python
# Same code works with Docker or Podman
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)
# or
engine = ContainerEngineFactory.create(ContainerRuntime.PODMAN)

# Client code doesn't change
image_id = engine.images.build(context, "my-image")
```

**Benefits:**
- Easy to switch runtimes
- Easy to add new runtimes
- Client code is portable

### 2. Separation of Abstractions and Implementations

**Abstractions define WHAT:**
```python
class ImageManager(ABC):
    @abstractmethod
    def build(self, context: BuildContext, image_name: str) -> str:
        """Build a container image."""
        pass
```

**Implementations define HOW:**
```python
class DockerImageManager(ImageManager):
    def build(self, context: BuildContext, image_name: str) -> str:
        # Docker-specific implementation
        tar_data = create_build_context_tar(...)
        cmd = [self.command, "build", "-t", image_name, "-"]
        result = run_docker_command(cmd, input_data=tar_data)
        return extract_image_id(result.stdout)
```

### 3. Type Safety

All operations use strongly-typed configurations:

```python
# Type-safe configuration
config = RunConfig(
    image="alpine:latest",
    name="my-container",
    environment={"KEY": "value"},
    volumes=[VolumeMount(source="/host", target="/container")],
    ports=[PortMapping(container_port=8080, host_port=80)],
    restart_policy=RestartPolicy.ALWAYS,
)

# Type checking catches errors at development time
container_id = engine.containers.run(config)
```

### 4. In-Memory Operations

Dockerfile builds don't require filesystem operations:

```python
# Build from string - no temp files needed
context = BuildContext(
    dockerfile="""
    FROM alpine:latest
    COPY app.py /app/
    CMD ["python3", "/app/app.py"]
    """,
    files={
        "app.py": b"print('Hello, World!')"
    }
)

# Tar archive created in memory
image_id = engine.images.build(context, "my-app")
```

**Benefits:**
- No filesystem pollution
- Thread-safe (no temp file conflicts)
- Cleaner, more testable code

### 5. Comprehensive Error Handling

Hierarchical exceptions with rich context:

```python
try:
    engine.images.build(context, "my-image")
except ImageBuildError as e:
    print(f"Build failed: {e.message}")
    print(f"Command: {' '.join(e.command)}")
    print(f"Exit code: {e.exit_code}")
    print(f"Error output: {e.stderr}")
except RuntimeNotAvailableError as e:
    print(f"Runtime not available: {e.runtime}")
```

---

## Component Layers

### Layer 1: Factory

**Purpose:** Create and configure container engines

**Components:**
- `ContainerEngineFactory`

**Responsibilities:**
- Runtime selection
- Engine instantiation
- Availability verification

**Example:**
```python
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)
```

### Layer 2: Engine

**Purpose:** Provide unified access to all managers

**Components:**
- `ContainerEngine` (abstract)
- `DockerEngine` (concrete)

**Responsibilities:**
- Manager composition
- Runtime detection
- Version/info queries

**Example:**
```python
print(f"Runtime: {engine.runtime}")
print(f"Version: {engine.version()}")
print(f"Available: {engine.is_available()}")
```

### Layer 3: Managers

**Purpose:** Specialized operations for different resource types

**Components:**
- `ImageManager` - Image operations
- `ContainerManager` - Container operations
- `VolumeManager` - Volume operations
- `NetworkManager` - Network operations

**Responsibilities:**
- Resource lifecycle management
- CRUD operations
- Resource inspection

**Example:**
```python
# Each manager handles its domain
engine.images.build(...)
engine.containers.run(...)
engine.volumes.create(...)
engine.networks.create(...)
```

### Layer 4: Types and Enums

**Purpose:** Type-safe configuration and data

**Components:**
- Configuration types: `BuildContext`, `RunConfig`
- Mount/Port types: `VolumeMount`, `PortMapping`
- Info types: `ImageInfo`, `ContainerInfo`, `VolumeInfo`, `NetworkInfo`
- Enums: `ContainerRuntime`, `ContainerState`, `RestartPolicy`, etc.

**Responsibilities:**
- Type safety
- Default values
- Data validation

### Layer 5: Exceptions

**Purpose:** Structured error handling

**Components:**
- Base: `ContainerError`
- Domain-specific: `ImageError`, `VolumeError`, `NetworkError`
- Specific: `ImageNotFoundError`, `ImageBuildError`, etc.

**Responsibilities:**
- Error categorization
- Rich error context
- Error recovery guidance

---

## Data Flow

### Image Build Flow

```
Client Code
    ↓ BuildContext(dockerfile="...", files={...})
ContainerEngine.images
    ↓
DockerImageManager.build()
    ↓ create_build_context_tar()
Tar Archive (in memory)
    ↓ run_docker_command([docker, build, -t, name, -], input_data=tar)
Docker Runtime
    ↓ stdout/stderr
DockerImageManager
    ↓ extract_image_id()
Client Code ← image_id
```

### Container Run Flow

```
Client Code
    ↓ RunConfig(image="...", name="...", ...)
ContainerEngine.containers
    ↓
DockerContainerManager.run()
    ↓ format_env_vars(), format_volume_mounts(), format_port_mappings()
Docker Command
    ↓ run_docker_command([docker, run, ...])
Docker Runtime
    ↓ container_id
Client Code ← container_id
```

---

## Extension Points

### Adding a New Runtime

1. **Create implementation directory:**
   ```
   implementations/podman/
   ```

2. **Implement engine:**
   ```python
   class PodmanEngine(ContainerEngine):
       def __init__(self, command: str = "podman"):
           super().__init__(command)
           # Initialize managers
   ```

3. **Implement managers:**
   ```python
   class PodmanImageManager(ImageManager):
       # Implement all abstract methods
   ```

4. **Update factory:**
   ```python
   if runtime == ContainerRuntime.PODMAN:
       engine = PodmanEngine(command)
   ```

### Adding Custom Functionality

Extend managers with additional methods:

```python
class CustomDockerImageManager(DockerImageManager):
    def build_with_cache_from(self, context: BuildContext,
                               image_name: str,
                               cache_from: list[str]) -> str:
        # Custom build with cache-from support
        pass
```

---

## Summary

The Container Manager architecture provides:

✅ **Clean separation** between abstractions and implementations
✅ **Runtime agnostic** design for portability
✅ **Type safety** through comprehensive dataclasses
✅ **In-memory operations** for cleaner code
✅ **Extensibility** through well-defined interfaces
✅ **Robust error handling** with rich context

This architecture makes it easy to:
- Switch between container runtimes
- Add new runtime implementations
- Test code without real containers
- Build complex container workflows
- Handle errors gracefully

---

**Next:** [Design Patterns](design_patterns.md) | [Component Relationships](component_relationships.md)
