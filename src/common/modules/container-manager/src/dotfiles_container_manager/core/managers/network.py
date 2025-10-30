"""Abstract base class for network management."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import NetworkInfo


class NetworkManager(ABC):
    """Abstract base class for managing networks."""

    @abstractmethod
    def create(
        self,
        name: str,
        driver: str = "bridge",
        labels: dict[str, str] | None = None,
    ) -> str:
        """
        Create a network.

        Args:
            name: Network name
            driver: Network driver
            labels: Network labels

        Returns:
            Network ID

        Raises:
            NetworkError: If creation fails
        """
        pass

    @abstractmethod
    def remove(self, name: str) -> None:
        """
        Remove a network.

        Args:
            name: Network name or ID

        Raises:
            NetworkNotFoundError: If network doesn't exist
            NetworkError: If removal fails
        """
        pass

    @abstractmethod
    def connect(self, network: str, container: str) -> None:
        """
        Connect a container to a network.

        Args:
            network: Network name or ID
            container: Container ID or name

        Raises:
            NetworkNotFoundError: If network doesn't exist
            ContainerNotFoundError: If container doesn't exist
            NetworkError: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(
        self, network: str, container: str, force: bool = False
    ) -> None:
        """
        Disconnect a container from a network.

        Args:
            network: Network name or ID
            container: Container ID or name
            force: Force disconnection

        Raises:
            NetworkNotFoundError: If network doesn't exist
            NetworkError: If disconnection fails
        """
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        """
        Check if a network exists.

        Args:
            name: Network name or ID

        Returns:
            True if network exists, False otherwise
        """
        pass

    @abstractmethod
    def inspect(self, name: str) -> NetworkInfo:
        """
        Get detailed information about a network.

        Args:
            name: Network name or ID

        Returns:
            NetworkInfo with network details

        Raises:
            NetworkNotFoundError: If network doesn't exist
        """
        pass

    @abstractmethod
    def list(self, filters: dict[str, str] | None = None) -> list[NetworkInfo]:
        """
        List networks.

        Args:
            filters: Optional filters (e.g., {'driver': 'bridge'})

        Returns:
            List of NetworkInfo objects
        """
        pass

    @abstractmethod
    def prune(self) -> dict[str, int]:
        """
        Remove unused networks.

        Returns:
            Dictionary with 'deleted' count
        """
        pass
