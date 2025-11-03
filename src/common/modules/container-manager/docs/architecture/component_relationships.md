# Component Relationships

**Module:** `dotfiles_container_manager`
**Purpose:** Document how components interact and depend on each other

---

## Table of Contents

1. [Component Hierarchy](#component-hierarchy)
2. [Dependency Graph](#dependency-graph)
3. [Interaction Patterns](#interaction-patterns)
4. [Data Flow](#data-flow)
5. [Lifecycle Management](#lifecycle-management)

---

## Component Hierarchy

### Class Hierarchy

```
ContainerEngine (ABC)
    └── DockerEngine

ImageManager (ABC)
    └── DockerImageManager

ContainerManager (ABC)
    └── DockerContainerManager

VolumeManager (ABC)
    └── DockerVolumeManager

NetworkManager (ABC)
    └── DockerNetworkManager

ContainerError (Exception)
    ├── ImageError
    │   ├── ImageNotFoundError
    │   └── ImageBuildError
    ├── ContainerRuntimeError
    │   └── ContainerNotFoundError
    ├── VolumeError
    │   └── VolumeNotFoundError
    ├── NetworkError
    │   └── NetworkNotFoundError
    ├── RuntimeNotAvailableError
    └── InvalidConfigError
```

### Composition Hierarchy

```
ContainerEngineFactory
    └── creates → ContainerEngine
                      ├── has → ImageManager
                      ├── has → ContainerManager
                      ├── has → VolumeManager
                      └── has → NetworkManager

DockerEngine
    ├── has → DockerImageManager
    ├── has → DockerContainerManager
    ├── has → DockerVolumeManager
    └── has → DockerNetworkManager
```

---

## Dependency Graph

### Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Code                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  factory.py                                  │
│  ContainerEngineFactory                                     │
│  ├── depends on → core.base.ContainerEngine                 │
│  ├── depends on → core.enums.ContainerRuntime               │
│  ├── depends on → implementations.docker.DockerEngine       │
│  └── depends on → core.exceptions.RuntimeNotAvailableError  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              implementations/docker/engine.py                │
│  DockerEngine                                               │
│  ├── depends on → core.base.ContainerEngine                 │
│  ├── depends on → core.enums.ContainerRuntime               │
│  ├── depends on → core.managers.*                           │
│  ├── depends on → implementations.docker.*Manager           │
│  └── depends on → implementations.docker.utils              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│          implementations/docker/*_manager.py                 │
│  Docker*Manager                                             │
│  ├── depends on → core.managers.*Manager                    │
│  ├── depends on → core.types.*                              │
│  ├── depends on → core.exceptions.*                         │
│  └── depends on → implementations.docker.utils              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│          implementations/docker/utils.py                     │
│  Utility Functions                                          │
│  ├── depends on → subprocess                                │
│  ├── depends on → tarfile                                   │
│  ├── depends on → io                                        │
│  └── depends on → core.exceptions.*                         │
└─────────────────────────────────────────────────────────────┘
```

### Core Module Dependencies

```
core/
├── base.py
│   ├── depends on → enums.ContainerRuntime
│   └── depends on → managers.*Manager
│
├── enums.py
│   └── (no dependencies)
│
├── exceptions.py
│   └── (no dependencies)
│
├── types.py
│   ├── depends on → enums.*
│   └── depends on → dataclasses
│
└── managers/
    ├── image.py
    │   ├── depends on → types.BuildContext, ImageInfo
    │   └── depends on → abc.ABC
    │
    ├── container.py
    │   ├── depends on → types.RunConfig, ContainerInfo
    │   └── depends on → abc.ABC
    │
    ├── volume.py
    │   ├── depends on → types.VolumeInfo
    │   └── depends on → abc.ABC
    │
    └── network.py
        ├── depends on → types.NetworkInfo
        └── depends on → abc.ABC
```

---

## Interaction Patterns

### Pattern 1: Engine Creation

```
Client
    ↓ ContainerEngineFactory.create(runtime)
Factory
    ↓ DockerEngine(command)
DockerEngine.__init__()
    ├→ DockerImageManager(command)
    ├→ DockerContainerManager(command)
    ├→ DockerVolumeManager(command)
    └→ DockerNetworkManager(command)
    ↓
Client ← engine
```

### Pattern 2: Image Build

```
Client
    ↓ engine.images.build(context, name)
DockerImageManager
    ↓ create_build_context_tar(context)
utils.create_build_context_tar()
    ├→ tarfile.TarFile()
    ├→ add Dockerfile
    └→ add files
    ↓ tar_data (bytes)
DockerImageManager
    ↓ run_docker_command([docker, build, ...], input_data=tar_data)
utils.run_docker_command()
    ↓ subprocess.run()
    ↓ stdout/stderr
DockerImageManager
    ↓ extract_image_id(stdout)
utils.extract_image_id()
    ↓ image_id
Client ← image_id
```

### Pattern 3: Container Run

```
Client
    ↓ engine.containers.run(config)
DockerContainerManager
    ├→ format_env_vars(config.environment)
    ├→ format_volume_mounts(config.volumes)
    └→ format_port_mappings(config.ports)
    ↓ [docker, run, ...]
DockerContainerManager
    ↓ run_docker_command(cmd)
utils.run_docker_command()
    ↓ subprocess.run()
    ↓ container_id
Client ← container_id
```

### Pattern 4: Error Handling

```
Client
    ↓ engine.images.build(context, name)
DockerImageManager
    ↓ run_docker_command(cmd)
utils.run_docker_command()
    ↓ subprocess.run() → CalledProcessError
    ↓ raise ImageBuildError(...)
DockerImageManager
    ↑ (exception propagates)
Client
    ↓ except ImageBuildError as e:
    ↓ handle error
```

---

## Data Flow

### Configuration Flow

```
Client Code
    ↓ Creates configuration objects
BuildContext / RunConfig / etc.
    ↓ Passed to managers
Manager Methods
    ↓ Extract and format data
Command Formatters (utils)
    ↓ Build command arrays
subprocess
    ↓ Execute commands
Container Runtime
```

### Information Flow

```
Container Runtime
    ↓ JSON output
subprocess
    ↓ stdout
Manager Methods
    ↓ Parse JSON
Info Objects (ImageInfo, ContainerInfo, etc.)
    ↓ Return to client
Client Code
```

### Error Flow

```
Container Runtime
    ↓ Error (non-zero exit)
subprocess
    ↓ CalledProcessError
utils.run_docker_command()
    ↓ Catch and wrap
Specific Exception (ImageBuildError, etc.)
    ↓ Propagate
Manager Methods
    ↓ Propagate
Client Code
    ↓ Handle
```

---

## Lifecycle Management

### Engine Lifecycle

```
1. Creation
   ContainerEngineFactory.create()
       ↓
   DockerEngine.__init__()
       ├→ Create ImageManager
       ├→ Create ContainerManager
       ├→ Create VolumeManager
       └→ Create NetworkManager

2. Usage
   engine.images.build(...)
   engine.containers.run(...)
   engine.volumes.create(...)
   engine.networks.create(...)

3. Cleanup
   (No explicit cleanup needed - managers are stateless)
```

### Resource Lifecycle

**Image Lifecycle:**
```
build() → image exists
    ↓
tag() → additional tags
    ↓
push() → image in registry
    ↓
pull() → image on local system
    ↓
remove() → image deleted
```

**Container Lifecycle:**
```
run() → container created and started
    ↓
stop() → container stopped
    ↓
start() → container restarted
    ↓
remove() → container deleted
```

**Volume Lifecycle:**
```
create() → volume exists
    ↓
(used by containers)
    ↓
remove() → volume deleted
```

**Network Lifecycle:**
```
create() → network exists
    ↓
connect() → container connected
    ↓
disconnect() → container disconnected
    ↓
remove() → network deleted
```

---

## Component Communication

### Manager to Utility Communication

```python
# Manager calls utility functions
class DockerImageManager:
    def build(self, context: BuildContext, image_name: str) -> str:
        # Create tar archive
        tar_data = create_build_context_tar(
            context.dockerfile,
            context.files,
        )

        # Execute command
        result = run_docker_command(
            [self.command, "build", "-t", image_name, "-"],
            input_data=tar_data,
        )

        # Parse output
        return extract_image_id(result.stdout)
```

### Engine to Manager Communication

```python
# Engine provides access to managers
class DockerEngine:
    @property
    def images(self) -> ImageManager:
        return self._images_manager

    @property
    def containers(self) -> ContainerManager:
        return self._containers_manager
```

### Client to Engine Communication

```python
# Client uses engine facade
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Access managers through engine
image_id = engine.images.build(context, "my-image")
container_id = engine.containers.run(config)
```

---

## Summary

### Key Relationships

1. **Factory creates Engine** - Factory pattern for engine instantiation
2. **Engine composes Managers** - Facade pattern for unified access
3. **Managers use Utilities** - Shared utilities for common operations
4. **All depend on Core** - Core types, enums, exceptions used throughout

### Dependency Direction

```
Client Code
    ↓
Factory
    ↓
Engine
    ↓
Managers
    ↓
Utilities
    ↓
Core (types, enums, exceptions)
```

### Communication Patterns

- **Synchronous** - All operations are synchronous
- **Exception-based** - Errors communicated via exceptions
- **Immutable data** - Configuration objects are immutable
- **Stateless managers** - Managers don't maintain state

---

**Next:** [Core Abstractions](../api/core_abstractions.md) | [Managers API](../api/managers.md)
