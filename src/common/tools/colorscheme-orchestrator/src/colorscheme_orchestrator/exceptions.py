"""Custom exceptions for colorscheme orchestrator."""


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""

    pass


class ConfigurationError(OrchestratorError):
    """Configuration-related errors."""

    pass


class BackendError(OrchestratorError):
    """Backend-related errors."""

    def __init__(self, backend: str, message: str):
        self.backend = backend
        self.message = message
        super().__init__(f"Backend '{backend}': {message}")


class ImageBuildError(OrchestratorError):
    """Container image build errors."""

    def __init__(self, backend: str, message: str, build_logs: str = ""):
        self.backend = backend
        self.message = message
        self.build_logs = build_logs
        super().__init__(f"Failed to build image for '{backend}': {message}")


class ContainerRuntimeError(OrchestratorError):
    """Container runtime errors."""

    def __init__(self, message: str, container_logs: str = ""):
        self.message = message
        self.container_logs = container_logs
        super().__init__(message)


class ImageNotFoundError(OrchestratorError):
    """Image not found error."""

    def __init__(self, image_path: str):
        self.image_path = image_path
        super().__init__(f"Image file not found: {image_path}")


class InvalidBackendError(OrchestratorError):
    """Invalid backend error."""

    def __init__(self, backend: str, valid_backends: list[str]):
        self.backend = backend
        self.valid_backends = valid_backends
        valid_str = ", ".join(valid_backends)
        super().__init__(
            f"Invalid backend '{backend}'. Valid options: {valid_str}"
        )
