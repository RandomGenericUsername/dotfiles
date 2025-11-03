"""Factory for creating container engines."""

from .core import ContainerEngine, ContainerRuntime, RuntimeNotAvailableError
from .implementations import DockerEngine


class ContainerEngineFactory:
    """Factory for creating container engine instances."""

    @staticmethod
    def create(
        runtime: ContainerRuntime,
        command: str | None = None,
    ) -> ContainerEngine:
        """
        Create a container engine instance.

        Args:
            runtime: Container runtime to use
            command: Optional custom command (defaults to runtime value)

        Returns:
            ContainerEngine instance

        Raises:
            ValueError: If runtime is not supported
            RuntimeNotAvailableError: If runtime is not available

        Examples:
            >>> engine = ContainerEngineFactory.create(
            ...     ContainerRuntime.DOCKER
            ... )
            >>> engine = ContainerEngineFactory.create(
            ...     ContainerRuntime.DOCKER, command="podman"
            ... )
        """
        # Determine command
        if command is None:
            command = runtime.value

        # Create engine based on runtime
        if runtime == ContainerRuntime.DOCKER:
            engine = DockerEngine(command)
        elif runtime == ContainerRuntime.PODMAN:
            # For now, use DockerEngine with podman command
            # In the future, we can create a dedicated PodmanEngine
            engine = DockerEngine(command)
        else:
            raise ValueError(f"Unsupported container runtime: {runtime}")

        # Verify engine is available
        if not engine.is_available():
            raise RuntimeNotAvailableError(command)

        return engine

    @staticmethod
    def create_docker(command: str = "docker") -> DockerEngine:
        """
        Create a Docker engine instance.

        Args:
            command: Docker command to use

        Returns:
            DockerEngine instance

        Raises:
            RuntimeNotAvailableError: If Docker is not available

        Examples:
            >>> engine = ContainerEngineFactory.create_docker()
        """
        engine = DockerEngine(command)
        engine.ensure_available()
        return engine

    @staticmethod
    def create_podman(command: str = "podman") -> DockerEngine:
        """
        Create a Podman engine instance.

        Note: Currently uses DockerEngine with podman command.
        In the future, this will use a dedicated PodmanEngine.

        Args:
            command: Podman command to use

        Returns:
            DockerEngine instance (with podman command)

        Raises:
            RuntimeNotAvailableError: If Podman is not available

        Examples:
            >>> engine = ContainerEngineFactory.create_podman()
        """
        engine = DockerEngine(command)
        engine.ensure_available()
        return engine
