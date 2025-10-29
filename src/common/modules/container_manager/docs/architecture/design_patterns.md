# Design Patterns

**Module:** `dotfiles_container_manager`  
**Purpose:** Document design patterns used in the module

---

## Table of Contents

1. [Abstract Factory Pattern](#abstract-factory-pattern)
2. [Strategy Pattern](#strategy-pattern)
3. [Facade Pattern](#facade-pattern)
4. [Builder Pattern](#builder-pattern)
5. [Template Method Pattern](#template-method-pattern)
6. [Dependency Injection](#dependency-injection)

---

## Abstract Factory Pattern

### Purpose

Create families of related objects (managers) without specifying their concrete classes.

### Implementation

**Factory:**
```python
class ContainerEngineFactory:
    @staticmethod
    def create(runtime: ContainerRuntime, command: str | None = None) -> ContainerEngine:
        if runtime == ContainerRuntime.DOCKER:
            engine = DockerEngine(command or "docker")
        elif runtime == ContainerRuntime.PODMAN:
            engine = DockerEngine(command or "podman")
        else:
            raise ValueError(f"Unsupported runtime: {runtime}")
        
        if not engine.is_available():
            raise RuntimeNotAvailableError(command)
        
        return engine
```

**Usage:**
```python
# Factory creates the entire family of managers
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# All managers are Docker-specific
engine.images      # DockerImageManager
engine.containers  # DockerContainerManager
engine.volumes     # DockerVolumeManager
engine.networks    # DockerNetworkManager
```

### Benefits

- Client code doesn't know about concrete classes
- Easy to switch between runtime families
- Ensures all managers are compatible

---

## Strategy Pattern

### Purpose

Define a family of algorithms (runtime implementations), encapsulate each one, and make them interchangeable.

### Implementation

**Strategy Interface:**
```python
class ImageManager(ABC):
    @abstractmethod
    def build(self, context: BuildContext, image_name: str) -> str:
        pass
```

**Concrete Strategies:**
```python
class DockerImageManager(ImageManager):
    def build(self, context: BuildContext, image_name: str) -> str:
        # Docker-specific build implementation
        tar_data = create_build_context_tar(...)
        cmd = [self.command, "build", "-t", image_name, "-"]
        return run_docker_command(cmd, input_data=tar_data)

class PodmanImageManager(ImageManager):
    def build(self, context: BuildContext, image_name: str) -> str:
        # Podman-specific build implementation
        # (could be different from Docker)
        pass
```

**Context:**
```python
class ContainerEngine(ABC):
    @property
    @abstractmethod
    def images(self) -> ImageManager:
        """Get the image manager (strategy)."""
        pass
```

**Usage:**
```python
# Strategy is selected at runtime
engine = ContainerEngineFactory.create(runtime)

# Same interface, different implementation
image_id = engine.images.build(context, "my-image")
```

### Benefits

- Runtime selection of algorithms
- Easy to add new implementations
- Client code is decoupled from implementation details

---

## Facade Pattern

### Purpose

Provide a unified interface to a set of interfaces in a subsystem.

### Implementation

**Subsystems (Managers):**
```python
class ImageManager:
    def build(...): pass
    def pull(...): pass
    def push(...): pass

class ContainerManager:
    def run(...): pass
    def stop(...): pass
    def remove(...): pass

class VolumeManager:
    def create(...): pass
    def remove(...): pass

class NetworkManager:
    def create(...): pass
    def connect(...): pass
```

**Facade:**
```python
class ContainerEngine(ABC):
    """Unified facade for all container operations."""
    
    @property
    def images(self) -> ImageManager:
        """Access image operations."""
        pass
    
    @property
    def containers(self) -> ContainerManager:
        """Access container operations."""
        pass
    
    @property
    def volumes(self) -> VolumeManager:
        """Access volume operations."""
        pass
    
    @property
    def networks(self) -> NetworkManager:
        """Access network operations."""
        pass
```

**Usage:**
```python
# Single entry point for all operations
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Facade provides organized access to subsystems
engine.images.build(...)
engine.containers.run(...)
engine.volumes.create(...)
engine.networks.create(...)
```

### Benefits

- Simplified interface to complex subsystem
- Reduces coupling between client and subsystems
- Organized access to related functionality

---

## Builder Pattern

### Purpose

Separate the construction of complex objects from their representation.

### Implementation

**Product:**
```python
@dataclass
class RunConfig:
    """Configuration for running containers."""
    image: str
    name: str | None = None
    command: list[str] | None = None
    environment: dict[str, str] = field(default_factory=dict)
    volumes: list[VolumeMount] = field(default_factory=list)
    ports: list[PortMapping] = field(default_factory=list)
    # ... many more fields
```

**Usage (Incremental Construction):**
```python
# Start with minimal configuration
config = RunConfig(image="alpine:latest")

# Build up configuration incrementally
config.name = "my-container"
config.environment = {"KEY": "value"}
config.volumes = [VolumeMount(source="/host", target="/container")]
config.ports = [PortMapping(container_port=8080, host_port=80)]

# Use the built configuration
container_id = engine.containers.run(config)
```

**Alternative (All at Once):**
```python
config = RunConfig(
    image="alpine:latest",
    name="my-container",
    environment={"KEY": "value"},
    volumes=[VolumeMount(source="/host", target="/container")],
    ports=[PortMapping(container_port=8080, host_port=80)],
    restart_policy=RestartPolicy.ALWAYS,
    detach=True,
)
```

### Benefits

- Complex objects built step-by-step
- Default values for optional parameters
- Type-safe construction
- Immutable after creation (dataclass frozen option)

---

## Template Method Pattern

### Purpose

Define the skeleton of an algorithm, letting subclasses override specific steps.

### Implementation

**Template (Abstract Base):**
```python
class ContainerEngine(ABC):
    def __init__(self, command: str):
        """Template method - defines initialization sequence."""
        self.command = command
        self._runtime = self._detect_runtime()  # Hook method
    
    @abstractmethod
    def _detect_runtime(self) -> ContainerRuntime:
        """Hook method - subclasses provide implementation."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Hook method - subclasses provide implementation."""
        pass
```

**Concrete Implementation:**
```python
class DockerEngine(ContainerEngine):
    def _detect_runtime(self) -> ContainerRuntime:
        """Implement hook method."""
        # Could check if it's actually Podman masquerading as Docker
        return ContainerRuntime.DOCKER
    
    def is_available(self) -> bool:
        """Implement hook method."""
        try:
            run_docker_command([self.command, "--version"])
            return True
        except Exception:
            return False
```

### Benefits

- Common initialization logic in base class
- Subclasses customize specific steps
- Ensures consistent initialization sequence

---

## Dependency Injection

### Purpose

Inject dependencies rather than creating them internally.

### Implementation

**Manager Composition:**
```python
class DockerEngine(ContainerEngine):
    def __init__(self, command: str = "docker"):
        super().__init__(command)
        
        # Inject command into all managers
        self._images_manager = DockerImageManager(command)
        self._containers_manager = DockerContainerManager(command)
        self._volumes_manager = DockerVolumeManager(command)
        self._networks_manager = DockerNetworkManager(command)
```

**Manager Implementation:**
```python
class DockerImageManager(ImageManager):
    def __init__(self, command: str = "docker"):
        """Dependency injected via constructor."""
        self.command = command
    
    def build(self, context: BuildContext, image_name: str) -> str:
        # Use injected command
        cmd = [self.command, "build", "-t", image_name, "-"]
        # ...
```

**Usage:**
```python
# Custom command injection
engine = DockerEngine(command="podman")  # Use Podman instead of Docker

# All managers use the injected command
engine.images.build(...)  # Uses "podman build"
```

### Benefits

- Flexible configuration
- Easy testing (inject mocks)
- Loose coupling
- Runtime customization

---

## Pattern Combinations

### Factory + Strategy

```python
# Factory creates strategy family
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Strategy pattern allows runtime selection
if use_docker:
    engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)
else:
    engine = ContainerEngineFactory.create(ContainerRuntime.PODMAN)

# Same interface, different implementation
engine.images.build(...)
```

### Facade + Builder

```python
# Builder creates complex configuration
config = RunConfig(
    image="alpine:latest",
    volumes=[VolumeMount(...)],
    ports=[PortMapping(...)],
)

# Facade provides simple access
engine.containers.run(config)
```

### Template Method + Dependency Injection

```python
# Template method defines initialization
class ContainerEngine(ABC):
    def __init__(self, command: str):
        self.command = command  # Injected dependency
        self._runtime = self._detect_runtime()  # Template hook

# Concrete implementation uses injected dependency
class DockerEngine(ContainerEngine):
    def _detect_runtime(self) -> ContainerRuntime:
        # Use injected command
        result = run_command([self.command, "--version"])
        # Detect runtime from output
```

---

## Summary

The Container Manager uses multiple design patterns to achieve:

| Pattern | Purpose | Benefit |
|---------|---------|---------|
| **Abstract Factory** | Create runtime families | Easy runtime switching |
| **Strategy** | Interchangeable algorithms | Runtime flexibility |
| **Facade** | Unified interface | Simplified access |
| **Builder** | Complex object construction | Type-safe configuration |
| **Template Method** | Algorithm skeleton | Consistent initialization |
| **Dependency Injection** | External dependencies | Flexibility and testability |

These patterns work together to create a:
- ✅ Flexible and extensible architecture
- ✅ Clean and maintainable codebase
- ✅ Type-safe and testable system
- ✅ Runtime-agnostic design

---

**Next:** [Component Relationships](component_relationships.md) | [API Reference](../api/core_abstractions.md)

