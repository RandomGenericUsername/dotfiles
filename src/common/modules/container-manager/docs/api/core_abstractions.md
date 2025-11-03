# Core Abstractions API

**Module:** `dotfiles_container_manager.core`
**Purpose:** Abstract base classes defining the container management interface

---

## Table of Contents

1. [ContainerEngine](#containerengine)
2. [ContainerEngineFactory](#containerenginefactory)
3. [Usage Examples](#usage-examples)

---

## ContainerEngine

**Location:** `core/base.py`
**Type:** Abstract Base Class

### Description

The `ContainerEngine` is the main entry point for all container operations. It provides access to four specialized managers and defines the contract that all runtime implementations must follow.

### Class Definition

```python
class ContainerEngine(ABC):
    """Abstract base class for container engines."""

    def __init__(self, command: str):
        """Initialize the container engine.

        Args:
            command: The command to use for container operations (e.g., 'docker', 'podman')
        """
        self.command = command
        self._runtime = self._detect_runtime()

    @property
    def runtime(self) -> ContainerRuntime:
        """Get the detected container runtime."""
        return self._runtime

    @abstractmethod
    def _detect_runtime(self) -> ContainerRuntime:
        """Detect the container runtime.

        Returns:
            The detected container runtime
        """
        pass

    @property
    @abstractmethod
    def images(self) -> ImageManager:
        """Get the image manager.

        Returns:
            Manager for image operations
        """
        pass

    @property
    @abstractmethod
    def containers(self) -> ContainerManager:
        """Get the container manager.

        Returns:
            Manager for container operations
        """
        pass

    @property
    @abstractmethod
    def volumes(self) -> VolumeManager:
        """Get the volume manager.

        Returns:
            Manager for volume operations
        """
        pass

    @property
    @abstractmethod
    def networks(self) -> NetworkManager:
        """Get the network manager.

        Returns:
            Manager for network operations
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the container runtime is available.

        Returns:
            True if the runtime is available, False otherwise
        """
        pass

    @abstractmethod
    def version(self) -> str:
        """Get the container runtime version.

        Returns:
            Version string

        Raises:
            RuntimeNotAvailableError: If runtime is not available
        """
        pass

    @abstractmethod
    def info(self) -> dict[str, Any]:
        """Get container runtime information.

        Returns:
            Dictionary containing runtime information

        Raises:
            RuntimeNotAvailableError: If runtime is not available
        """
        pass
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `runtime` | `ContainerRuntime` | The detected container runtime (DOCKER or PODMAN) |
| `command` | `str` | The command used for container operations |
| `images` | `ImageManager` | Manager for image operations |
| `containers` | `ContainerManager` | Manager for container operations |
| `volumes` | `VolumeManager` | Manager for volume operations |
| `networks` | `NetworkManager` | Manager for network operations |

### Methods

#### `is_available() -> bool`

Check if the container runtime is available on the system.

**Returns:**
- `bool`: True if runtime is available, False otherwise

**Example:**
```python
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)
if engine.is_available():
    print("Docker is available")
else:
    print("Docker is not available")
```

#### `version() -> str`

Get the version string of the container runtime.

**Returns:**
- `str`: Version string (e.g., "Docker version 24.0.5, build ced0996")

**Raises:**
- `RuntimeNotAvailableError`: If the runtime is not available

**Example:**
```python
try:
    version = engine.version()
    print(f"Runtime version: {version}")
except RuntimeNotAvailableError:
    print("Runtime not available")
```

#### `info() -> dict[str, Any]`

Get detailed information about the container runtime.

**Returns:**
- `dict[str, Any]`: Dictionary containing runtime information (varies by runtime)

**Raises:**
- `RuntimeNotAvailableError`: If the runtime is not available

**Example:**
```python
info = engine.info()
print(f"Containers: {info.get('Containers')}")
print(f"Images: {info.get('Images')}")
print(f"Server Version: {info.get('ServerVersion')}")
```

---

## ContainerEngineFactory

**Location:** `factory.py`
**Type:** Static Factory Class

### Description

The `ContainerEngineFactory` provides static methods for creating container engine instances. It handles runtime selection, command configuration, and availability verification.

### Class Definition

```python
class ContainerEngineFactory:
    """Factory for creating container engine instances."""

    @staticmethod
    def create(runtime: ContainerRuntime, command: str | None = None) -> ContainerEngine:
        """Create a container engine for the specified runtime.

        Args:
            runtime: The container runtime to use
            command: Optional custom command (defaults based on runtime)

        Returns:
            Configured container engine instance

        Raises:
            ValueError: If runtime is not supported
            RuntimeNotAvailableError: If runtime is not available on the system
        """
        if runtime == ContainerRuntime.DOCKER:
            engine = DockerEngine(command or "docker")
        elif runtime == ContainerRuntime.PODMAN:
            engine = DockerEngine(command or "podman")
        else:
            raise ValueError(f"Unsupported runtime: {runtime}")

        if not engine.is_available():
            raise RuntimeNotAvailableError(command or runtime.value)

        return engine

    @staticmethod
    def create_docker(command: str = "docker") -> ContainerEngine:
        """Create a Docker engine.

        Args:
            command: Docker command to use (default: 'docker')

        Returns:
            Docker engine instance

        Raises:
            RuntimeNotAvailableError: If Docker is not available
        """
        return ContainerEngineFactory.create(ContainerRuntime.DOCKER, command)

    @staticmethod
    def create_podman(command: str = "podman") -> ContainerEngine:
        """Create a Podman engine.

        Args:
            command: Podman command to use (default: 'podman')

        Returns:
            Podman engine instance

        Raises:
            RuntimeNotAvailableError: If Podman is not available
        """
        return ContainerEngineFactory.create(ContainerRuntime.PODMAN, command)
```

### Methods

#### `create(runtime, command=None) -> ContainerEngine`

Create a container engine for the specified runtime.

**Parameters:**
- `runtime` (`ContainerRuntime`): The runtime to use (DOCKER or PODMAN)
- `command` (`str | None`): Optional custom command (defaults: "docker" or "podman")

**Returns:**
- `ContainerEngine`: Configured engine instance

**Raises:**
- `ValueError`: If runtime is not supported
- `RuntimeNotAvailableError`: If runtime is not available

**Example:**
```python
# Create Docker engine
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Create Podman engine
engine = ContainerEngineFactory.create(ContainerRuntime.PODMAN)

# Create with custom command
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER, command="/usr/local/bin/docker")
```

#### `create_docker(command="docker") -> ContainerEngine`

Convenience method to create a Docker engine.

**Parameters:**
- `command` (`str`): Docker command (default: "docker")

**Returns:**
- `ContainerEngine`: Docker engine instance

**Example:**
```python
engine = ContainerEngineFactory.create_docker()
```

#### `create_podman(command="podman") -> ContainerEngine`

Convenience method to create a Podman engine.

**Parameters:**
- `command` (`str`): Podman command (default: "podman")

**Returns:**
- `ContainerEngine`: Podman engine instance

**Example:**
```python
engine = ContainerEngineFactory.create_podman()
```

---

## Usage Examples

### Basic Engine Creation

```python
from dotfiles_container_manager import ContainerEngineFactory, ContainerRuntime

# Method 1: Using runtime enum
engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

# Method 2: Using convenience method
engine = ContainerEngineFactory.create_docker()

# Method 3: With custom command
engine = ContainerEngineFactory.create(
    ContainerRuntime.DOCKER,
    command="/usr/local/bin/docker"
)
```

### Checking Runtime Availability

```python
from dotfiles_container_manager import ContainerEngineFactory, ContainerRuntime
from dotfiles_container_manager import RuntimeNotAvailableError

try:
    engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)
    print(f"Docker is available: {engine.version()}")
except RuntimeNotAvailableError as e:
    print(f"Docker is not available: {e}")
```

### Accessing Managers

```python
engine = ContainerEngineFactory.create_docker()

# Access specialized managers
image_manager = engine.images
container_manager = engine.containers
volume_manager = engine.volumes
network_manager = engine.networks

# Use managers
image_id = image_manager.build(context, "my-image")
container_id = container_manager.run(config)
volume_name = volume_manager.create("my-volume")
network_id = network_manager.create("my-network")
```

### Runtime Information

```python
engine = ContainerEngineFactory.create_docker()

# Get runtime type
print(f"Runtime: {engine.runtime}")  # ContainerRuntime.DOCKER

# Get version
print(f"Version: {engine.version()}")

# Get detailed info
info = engine.info()
print(f"Containers: {info.get('Containers')}")
print(f"Images: {info.get('Images')}")
print(f"Storage Driver: {info.get('Driver')}")
```

---

**Next:** [Managers API](managers.md) | [Types and Enums](types_and_enums.md)
