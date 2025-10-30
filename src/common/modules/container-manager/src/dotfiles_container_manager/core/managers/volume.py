"""Abstract base class for volume management."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import VolumeInfo


class VolumeManager(ABC):
    """Abstract base class for managing volumes."""

    @abstractmethod
    def create(
        self,
        name: str,
        driver: str = "local",
        labels: dict[str, str] | None = None,
    ) -> str:
        """
        Create a volume.

        Args:
            name: Volume name
            driver: Volume driver
            labels: Volume labels

        Returns:
            Volume name

        Raises:
            VolumeError: If creation fails
        """
        pass

    @abstractmethod
    def remove(self, name: str, force: bool = False) -> None:
        """
        Remove a volume.

        Args:
            name: Volume name
            force: Force removal even if in use

        Raises:
            VolumeNotFoundError: If volume doesn't exist
            VolumeError: If removal fails
        """
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        """
        Check if a volume exists.

        Args:
            name: Volume name

        Returns:
            True if volume exists, False otherwise
        """
        pass

    @abstractmethod
    def inspect(self, name: str) -> VolumeInfo:
        """
        Get detailed information about a volume.

        Args:
            name: Volume name

        Returns:
            VolumeInfo with volume details

        Raises:
            VolumeNotFoundError: If volume doesn't exist
        """
        pass

    @abstractmethod
    def list(self, filters: dict[str, str] | None = None) -> list[VolumeInfo]:
        """
        List volumes.

        Args:
            filters: Optional filters (e.g., {'label': 'app=myapp'})

        Returns:
            List of VolumeInfo objects
        """
        pass

    @abstractmethod
    def prune(self) -> dict[str, int]:
        """
        Remove unused volumes.

        Returns:
            Dictionary with 'deleted' count and 'space_reclaimed' in bytes
        """
        pass
