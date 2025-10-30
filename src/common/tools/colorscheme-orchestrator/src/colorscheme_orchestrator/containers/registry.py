"""Backend registry for managing backend metadata."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class BackendMetadata:
    """Metadata for a colorscheme backend."""

    name: str
    image_name: str
    image_tag: str
    dockerfile_path: Path
    entrypoint_path: Path
    dependencies: list[str]


class BackendRegistry:
    """Registry of available colorscheme backends."""

    def __init__(self, containers_dir: Path):
        """Initialize backend registry.

        Args:
            containers_dir: Path to containers directory
        """
        self.containers_dir = containers_dir
        self._backends: dict[str, BackendMetadata] = {}
        self._initialize_backends()

    def _initialize_backends(self) -> None:
        """Initialize backend metadata."""
        self._backends = {
            "pywal": BackendMetadata(
                name="pywal",
                image_name="colorscheme-pywal",
                image_tag="latest",
                dockerfile_path=self.containers_dir / "pywal" / "Dockerfile",
                entrypoint_path=self.containers_dir / "pywal" / "entrypoint.py",
                dependencies=["pywal"],
            ),
            "wallust": BackendMetadata(
                name="wallust",
                image_name="colorscheme-wallust",
                image_tag="latest",
                dockerfile_path=self.containers_dir / "wallust" / "Dockerfile",
                entrypoint_path=self.containers_dir / "wallust" / "entrypoint.py",
                dependencies=["wallust"],
            ),
            "custom": BackendMetadata(
                name="custom",
                image_name="colorscheme-custom",
                image_tag="latest",
                dockerfile_path=self.containers_dir / "custom" / "Dockerfile",
                entrypoint_path=self.containers_dir / "custom" / "entrypoint.py",
                dependencies=["pillow", "scikit-learn", "numpy"],
            ),
        }

    def get(self, backend: str) -> BackendMetadata:
        """Get metadata for a backend.

        Args:
            backend: Backend name

        Returns:
            BackendMetadata: Backend metadata

        Raises:
            KeyError: If backend not found
        """
        if backend not in self._backends:
            raise KeyError(f"Backend '{backend}' not found in registry")
        return self._backends[backend]

    def list_backends(self) -> list[str]:
        """List all available backends.

        Returns:
            list[str]: List of backend names
        """
        return list(self._backends.keys())

    def is_valid_backend(self, backend: str) -> bool:
        """Check if backend is valid.

        Args:
            backend: Backend name

        Returns:
            bool: True if backend is valid
        """
        return backend in self._backends

