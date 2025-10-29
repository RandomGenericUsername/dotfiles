"""Enums for container management."""

from enum import Enum


class ContainerRuntime(Enum):
    """Supported container runtimes."""

    DOCKER = "docker"
    PODMAN = "podman"


class ContainerState(Enum):
    """Container states."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"


class RestartPolicy(Enum):
    """Container restart policies."""

    NO = "no"
    ON_FAILURE = "on-failure"
    ALWAYS = "always"
    UNLESS_STOPPED = "unless-stopped"


class NetworkMode(Enum):
    """Container network modes."""

    BRIDGE = "bridge"
    HOST = "host"
    NONE = "none"
    CONTAINER = "container"


class VolumeDriver(Enum):
    """Volume drivers."""

    LOCAL = "local"
    NFS = "nfs"
    TMPFS = "tmpfs"


class LogDriver(Enum):
    """Container log drivers."""

    JSON_FILE = "json-file"
    SYSLOG = "syslog"
    JOURNALD = "journald"
    NONE = "none"

