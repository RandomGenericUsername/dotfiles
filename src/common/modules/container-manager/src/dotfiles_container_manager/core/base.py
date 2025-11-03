"""Abstract base class for container engines."""

from abc import ABC, abstractmethod

from .enums import ContainerRuntime
from .managers import (
    ContainerManager,
    ImageManager,
    NetworkManager,
    VolumeManager,
)


class ContainerEngine(ABC):
    """Abstract base class for container runtime engines."""

    def __init__(self, command: str):
        """
        Initialize the container engine.

        Args:
            command: Command to use for container operations
                (e.g., 'docker', 'podman')
        """
        self.command = command
        self._runtime = self._detect_runtime()

    @property
    @abstractmethod
    def images(self) -> ImageManager:
        """Get the image manager."""
        pass

    @property
    @abstractmethod
    def containers(self) -> ContainerManager:
        """Get the container manager."""
        pass

    @property
    @abstractmethod
    def volumes(self) -> VolumeManager:
        """Get the volume manager."""
        pass

    @property
    @abstractmethod
    def networks(self) -> NetworkManager:
        """Get the network manager."""
        pass

    @property
    def runtime(self) -> ContainerRuntime:
        """Get the container runtime type."""
        return self._runtime

    @abstractmethod
    def _detect_runtime(self) -> ContainerRuntime:
        """Detect the container runtime type."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the container runtime is available.

        Returns:
            True if runtime is available and working, False otherwise
        """
        pass

    @abstractmethod
    def version(self) -> str:
        """
        Get the container runtime version.

        Returns:
            Version string

        Raises:
            ContainerError: If version check fails
        """
        pass

    @abstractmethod
    def info(self) -> dict[str, any]:
        """
        Get container runtime information.

        Returns:
            Dictionary with runtime information

        Raises:
            ContainerError: If info retrieval fails
        """
        pass
