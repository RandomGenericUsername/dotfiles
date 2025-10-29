"""Core types for container management."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .enums import LogDriver, NetworkMode, RestartPolicy


@dataclass
class VolumeMount:
    """Volume mount configuration."""

    source: str | Path
    """Source path (host) or volume name"""

    target: str | Path
    """Target path in container"""

    read_only: bool = False
    """Whether the mount is read-only"""

    type: str = "bind"
    """Mount type: 'bind', 'volume', 'tmpfs'"""


@dataclass
class PortMapping:
    """Port mapping configuration."""

    container_port: int
    """Port inside the container"""

    host_port: int | None = None
    """Port on the host (None for random)"""

    protocol: str = "tcp"
    """Protocol: 'tcp' or 'udp'"""

    host_ip: str = "0.0.0.0"
    """Host IP to bind to"""


@dataclass
class BuildContext:
    """Context for building container images."""

    dockerfile: str
    """Rendered Dockerfile content"""

    files: dict[str, bytes] = field(default_factory=dict)
    """Additional files to include in build context (path -> content)"""

    build_args: dict[str, str] = field(default_factory=dict)
    """Build arguments"""

    labels: dict[str, str] = field(default_factory=dict)
    """Image labels"""

    target: str | None = None
    """Build target for multi-stage builds"""

    network: str | None = None
    """Network mode during build"""

    no_cache: bool = False
    """Disable build cache"""

    pull: bool = False
    """Always pull base images"""

    rm: bool = True
    """Remove intermediate containers"""


@dataclass
class RunConfig:
    """Configuration for running containers."""

    image: str
    """Image name or ID to run"""

    name: str | None = None
    """Container name"""

    command: list[str] | None = None
    """Command to run"""

    entrypoint: list[str] | None = None
    """Override entrypoint"""

    environment: dict[str, str] = field(default_factory=dict)
    """Environment variables"""

    volumes: list[VolumeMount] = field(default_factory=list)
    """Volume mounts"""

    ports: list[PortMapping] = field(default_factory=list)
    """Port mappings"""

    network: str | NetworkMode = NetworkMode.BRIDGE
    """Network to connect to"""

    restart_policy: RestartPolicy = RestartPolicy.NO
    """Restart policy"""

    detach: bool = True
    """Run in detached mode"""

    remove: bool = False
    """Remove container when it exits"""

    user: str | None = None
    """User to run as"""

    working_dir: str | None = None
    """Working directory"""

    hostname: str | None = None
    """Container hostname"""

    labels: dict[str, str] = field(default_factory=dict)
    """Container labels"""

    log_driver: LogDriver = LogDriver.JSON_FILE
    """Logging driver"""

    privileged: bool = False
    """Run in privileged mode"""

    read_only: bool = False
    """Mount root filesystem as read-only"""

    memory_limit: str | None = None
    """Memory limit (e.g., '512m', '2g')"""

    cpu_limit: str | None = None
    """CPU limit (e.g., '0.5', '2')"""


@dataclass
class ImageInfo:
    """Information about a container image."""

    id: str
    """Image ID"""

    tags: list[str] = field(default_factory=list)
    """Image tags"""

    size: int = 0
    """Image size in bytes"""

    created: str | None = None
    """Creation timestamp"""

    labels: dict[str, str] = field(default_factory=dict)
    """Image labels"""


@dataclass
class ContainerInfo:
    """Information about a container."""

    id: str
    """Container ID"""

    name: str
    """Container name"""

    image: str
    """Image name"""

    state: str
    """Container state"""

    status: str
    """Container status"""

    created: str | None = None
    """Creation timestamp"""

    ports: list[PortMapping] = field(default_factory=list)
    """Port mappings"""

    labels: dict[str, str] = field(default_factory=dict)
    """Container labels"""


@dataclass
class VolumeInfo:
    """Information about a volume."""

    name: str
    """Volume name"""

    driver: str
    """Volume driver"""

    mountpoint: str | None = None
    """Mount point on host"""

    labels: dict[str, str] = field(default_factory=dict)
    """Volume labels"""


@dataclass
class NetworkInfo:
    """Information about a network."""

    id: str
    """Network ID"""

    name: str
    """Network name"""

    driver: str
    """Network driver"""

    scope: str
    """Network scope"""

    labels: dict[str, str] = field(default_factory=dict)
    """Network labels"""

