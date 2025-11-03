"""Exceptions for container management."""


class ContainerError(Exception):
    """Base exception for container operations."""

    def __init__(
        self,
        message: str,
        command: list[str] | None = None,
        exit_code: int | None = None,
        stderr: str | None = None,
    ):
        """
        Initialize container error.

        Args:
            message: Error message
            command: Command that failed
            exit_code: Exit code of the failed command
            stderr: Standard error output
        """
        self.message = message
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message."""
        parts = [self.message]

        if self.command:
            parts.append(f"Command: {' '.join(self.command)}")

        if self.exit_code is not None:
            parts.append(f"Exit code: {self.exit_code}")

        if self.stderr:
            parts.append(f"Error output: {self.stderr}")

        return "\n".join(parts)


class ImageError(ContainerError):
    """Raised when image operations fail."""

    pass


class ImageNotFoundError(ImageError):
    """Raised when an image cannot be found."""

    def __init__(self, image_name: str):
        """
        Initialize image not found error.

        Args:
            image_name: Name of the image that was not found
        """
        self.image_name = image_name
        super().__init__(f"Image not found: {image_name}")


class ImageBuildError(ImageError):
    """Raised when image build fails."""

    pass


class ContainerRuntimeError(ContainerError):
    """Raised when container runtime operations fail."""

    pass


class ContainerNotFoundError(ContainerRuntimeError):
    """Raised when a container cannot be found."""

    def __init__(self, container_id: str):
        """
        Initialize container not found error.

        Args:
            container_id: ID of the container that was not found
        """
        self.container_id = container_id
        super().__init__(f"Container not found: {container_id}")


class VolumeError(ContainerError):
    """Raised when volume operations fail."""

    pass


class VolumeNotFoundError(VolumeError):
    """Raised when a volume cannot be found."""

    def __init__(self, volume_name: str):
        """
        Initialize volume not found error.

        Args:
            volume_name: Name of the volume that was not found
        """
        self.volume_name = volume_name
        super().__init__(f"Volume not found: {volume_name}")


class NetworkError(ContainerError):
    """Raised when network operations fail."""

    pass


class NetworkNotFoundError(NetworkError):
    """Raised when a network cannot be found."""

    def __init__(self, network_name: str):
        """
        Initialize network not found error.

        Args:
            network_name: Name of the network that was not found
        """
        self.network_name = network_name
        super().__init__(f"Network not found: {network_name}")


class RuntimeNotAvailableError(ContainerError):
    """Raised when container runtime is not available."""

    def __init__(self, runtime: str):
        """
        Initialize runtime not available error.

        Args:
            runtime: Name of the runtime that is not available
        """
        self.runtime = runtime
        super().__init__(
            f"Container runtime '{runtime}' is not available. "
            f"Please ensure it is installed and running."
        )


class InvalidConfigError(ContainerError):
    """Raised when configuration is invalid."""

    pass
