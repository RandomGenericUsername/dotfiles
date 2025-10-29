"""Abstract base class for image management."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import BuildContext, ImageInfo


class ImageManager(ABC):
    """Abstract base class for managing container images."""

    @abstractmethod
    def build(
        self,
        context: BuildContext,
        image_name: str,
        timeout: int = 600,
    ) -> str:
        """
        Build a container image.

        Args:
            context: Build context with Dockerfile and files
            image_name: Name/tag for the built image
            timeout: Build timeout in seconds

        Returns:
            Image ID of the built image

        Raises:
            ImageBuildError: If build fails
        """
        pass

    @abstractmethod
    def tag(self, image: str, tag: str) -> None:
        """
        Tag an image.

        Args:
            image: Image ID or name
            tag: New tag to apply

        Raises:
            ImageNotFoundError: If image doesn't exist
            ImageError: If tagging fails
        """
        pass

    @abstractmethod
    def push(self, image: str, timeout: int = 300) -> None:
        """
        Push an image to a registry.

        Args:
            image: Image name with tag
            timeout: Push timeout in seconds

        Raises:
            ImageNotFoundError: If image doesn't exist
            ImageError: If push fails
        """
        pass

    @abstractmethod
    def pull(self, image: str, timeout: int = 300) -> str:
        """
        Pull an image from a registry.

        Args:
            image: Image name with tag
            timeout: Pull timeout in seconds

        Returns:
            Image ID of the pulled image

        Raises:
            ImageError: If pull fails
        """
        pass

    @abstractmethod
    def remove(self, image: str, force: bool = False) -> None:
        """
        Remove an image.

        Args:
            image: Image ID or name
            force: Force removal even if in use

        Raises:
            ImageNotFoundError: If image doesn't exist
            ImageError: If removal fails
        """
        pass

    @abstractmethod
    def exists(self, image: str) -> bool:
        """
        Check if an image exists.

        Args:
            image: Image ID or name

        Returns:
            True if image exists, False otherwise
        """
        pass

    @abstractmethod
    def inspect(self, image: str) -> ImageInfo:
        """
        Get detailed information about an image.

        Args:
            image: Image ID or name

        Returns:
            ImageInfo with image details

        Raises:
            ImageNotFoundError: If image doesn't exist
        """
        pass

    @abstractmethod
    def list(self, filters: dict[str, str] | None = None) -> list[ImageInfo]:
        """
        List images.

        Args:
            filters: Optional filters (e.g., {'label': 'app=myapp'})

        Returns:
            List of ImageInfo objects
        """
        pass

    @abstractmethod
    def prune(self, all: bool = False) -> dict[str, int]:
        """
        Remove unused images.

        Args:
            all: Remove all unused images, not just dangling ones

        Returns:
            Dictionary with 'deleted' count and 'space_reclaimed' in bytes
        """
        pass
