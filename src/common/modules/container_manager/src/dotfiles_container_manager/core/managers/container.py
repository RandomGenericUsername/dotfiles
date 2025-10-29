"""Abstract base class for container management."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import ContainerInfo, RunConfig


class ContainerManager(ABC):
    """Abstract base class for managing containers."""

    @abstractmethod
    def run(self, config: RunConfig) -> str:
        """
        Run a container.

        Args:
            config: Container run configuration

        Returns:
            Container ID

        Raises:
            ImageNotFoundError: If image doesn't exist
            ContainerRuntimeError: If container fails to start
        """
        pass

    @abstractmethod
    def start(self, container: str) -> None:
        """
        Start a stopped container.

        Args:
            container: Container ID or name

        Raises:
            ContainerNotFoundError: If container doesn't exist
            ContainerRuntimeError: If start fails
        """
        pass

    @abstractmethod
    def stop(self, container: str, timeout: int = 10) -> None:
        """
        Stop a running container.

        Args:
            container: Container ID or name
            timeout: Seconds to wait before killing

        Raises:
            ContainerNotFoundError: If container doesn't exist
            ContainerRuntimeError: If stop fails
        """
        pass

    @abstractmethod
    def restart(self, container: str, timeout: int = 10) -> None:
        """
        Restart a container.

        Args:
            container: Container ID or name
            timeout: Seconds to wait before killing

        Raises:
            ContainerNotFoundError: If container doesn't exist
            ContainerRuntimeError: If restart fails
        """
        pass

    @abstractmethod
    def remove(
        self, container: str, force: bool = False, volumes: bool = False
    ) -> None:
        """
        Remove a container.

        Args:
            container: Container ID or name
            force: Force removal of running container
            volumes: Remove associated volumes

        Raises:
            ContainerNotFoundError: If container doesn't exist
            ContainerRuntimeError: If removal fails
        """
        pass

    @abstractmethod
    def exists(self, container: str) -> bool:
        """
        Check if a container exists.

        Args:
            container: Container ID or name

        Returns:
            True if container exists, False otherwise
        """
        pass

    @abstractmethod
    def inspect(self, container: str) -> ContainerInfo:
        """
        Get detailed information about a container.

        Args:
            container: Container ID or name

        Returns:
            ContainerInfo with container details

        Raises:
            ContainerNotFoundError: If container doesn't exist
        """
        pass

    @abstractmethod
    def list(
        self,
        all: bool = False,
        filters: dict[str, str] | None = None,
    ) -> list[ContainerInfo]:
        """
        List containers.

        Args:
            all: Show all containers (default shows just running)
            filters: Optional filters (e.g., {'status': 'running'})

        Returns:
            List of ContainerInfo objects
        """
        pass

    @abstractmethod
    def logs(
        self,
        container: str,
        follow: bool = False,
        tail: int | None = None,
    ) -> str:
        """
        Get container logs.

        Args:
            container: Container ID or name
            follow: Follow log output
            tail: Number of lines from end of logs

        Returns:
            Log output as string

        Raises:
            ContainerNotFoundError: If container doesn't exist
        """
        pass

    @abstractmethod
    def exec(
        self,
        container: str,
        command: list[str],
        detach: bool = False,
        user: str | None = None,
    ) -> tuple[int, str]:
        """
        Execute a command in a running container.

        Args:
            container: Container ID or name
            command: Command to execute
            detach: Run in detached mode
            user: User to run as

        Returns:
            Tuple of (exit_code, output)

        Raises:
            ContainerNotFoundError: If container doesn't exist
            ContainerRuntimeError: If exec fails
        """
        pass

    @abstractmethod
    def prune(self) -> dict[str, int]:
        """
        Remove stopped containers.

        Returns:
            Dictionary with 'deleted' count and 'space_reclaimed' in bytes
        """
        pass
