"""Docker engine implementation."""

import json
from typing import Any

from ...core.base import ContainerEngine
from ...core.enums import ContainerRuntime
from ...core.exceptions import ContainerError, RuntimeNotAvailableError
from .container import DockerContainerManager
from .image import DockerImageManager
from .network import DockerNetworkManager
from .utils import run_docker_command
from .volume import DockerVolumeManager


class DockerEngine(ContainerEngine):
    """Docker implementation of ContainerEngine."""

    def __init__(self, command: str = "docker"):
        """
        Initialize Docker engine.

        Args:
            command: Docker command to use
        """
        super().__init__(command)

        # Initialize managers
        self._images_manager = DockerImageManager(command)
        self._containers_manager = DockerContainerManager(command)
        self._volumes_manager = DockerVolumeManager(command)
        self._networks_manager = DockerNetworkManager(command)

    @property
    def images(self) -> DockerImageManager:
        """Get the image manager."""
        return self._images_manager

    @property
    def containers(self) -> DockerContainerManager:
        """Get the container manager."""
        return self._containers_manager

    @property
    def volumes(self) -> DockerVolumeManager:
        """Get the volume manager."""
        return self._volumes_manager

    @property
    def networks(self) -> DockerNetworkManager:
        """Get the network manager."""
        return self._networks_manager

    def _detect_runtime(self) -> ContainerRuntime:
        """Detect the container runtime type."""
        # For Docker, always return DOCKER
        # This could be enhanced to detect if it's actually Podman
        # masquerading as Docker
        return ContainerRuntime.DOCKER

    def is_available(self) -> bool:
        """Check if Docker is available."""
        try:
            cmd = [self.command, "--version"]
            run_docker_command(cmd)
            return True
        except Exception:
            return False

    def version(self) -> str:
        """Get Docker version."""
        try:
            cmd = [self.command, "--version"]
            result = run_docker_command(cmd)
            return result.stdout.decode("utf-8").strip()
        except Exception as e:
            raise ContainerError(
                message=f"Failed to get Docker version: {e}",
                command=[self.command, "--version"],
            ) from e

    def info(self) -> dict[str, Any]:
        """Get Docker system information."""
        try:
            cmd = [self.command, "info", "--format", "{{json .}}"]
            result = run_docker_command(cmd)
            return json.loads(result.stdout.decode("utf-8"))
        except Exception as e:
            raise ContainerError(
                message=f"Failed to get Docker info: {e}",
                command=[self.command, "info"],
            ) from e

    def ping(self) -> bool:
        """
        Ping Docker daemon to check if it's responsive.

        Returns:
            True if daemon is responsive, False otherwise
        """
        try:
            cmd = [self.command, "info"]
            run_docker_command(cmd)
            return True
        except Exception:
            return False

    def ensure_available(self) -> None:
        """
        Ensure Docker is available and raise error if not.

        Raises:
            RuntimeNotAvailableError: If Docker is not available
        """
        if not self.is_available():
            raise RuntimeNotAvailableError(self.command)
