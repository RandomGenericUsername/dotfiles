"""Container registry for managing wallpaper-effects-processor images."""

import contextlib

from dotfiles_container_manager import (
    ContainerEngineFactory,
    ContainerRuntime,
    ImageInfo,
    ImageManager,
    ImageNotFoundError,
)

from wallpaper_orchestrator.config import ContainerConfig


class ContainerRegistry:
    """Manages wallpaper-effects-processor container images."""

    def __init__(self, config: ContainerConfig):
        """Initialize registry.

        Args:
            config: Container configuration
        """
        self.config = config
        self.runtime = ContainerRuntime(config.runtime)
        self.engine = ContainerEngineFactory.create(self.runtime)
        self.image_manager: ImageManager = self.engine.images

    def get_image_name(self) -> str:
        """Get full image name with tag.

        Returns:
            Image name with tag (e.g., "wallpaper-effects-processor:latest")
        """
        return f"{self.config.image_name}:{self.config.image_tag}"

    def image_exists(self) -> bool:
        """Check if image exists.

        Returns:
            True if image exists, False otherwise
        """
        try:
            self.image_manager.inspect(self.get_image_name())
            return True
        except ImageNotFoundError:
            return False

    def get_image_info(self) -> ImageInfo | None:
        """Get image information.

        Returns:
            ImageInfo if image exists, None otherwise
        """
        try:
            return self.image_manager.inspect(self.get_image_name())
        except ImageNotFoundError:
            return None

    def remove_image(self, force: bool = False) -> None:
        """Remove image.

        Args:
            force: Force removal even if containers are using it
        """
        with contextlib.suppress(ImageNotFoundError):
            self.image_manager.remove(self.get_image_name(), force=force)

    def list_images(self) -> list[ImageInfo]:
        """List all wallpaper-effects-processor images.

        Returns:
            List of ImageInfo objects
        """
        all_images = self.image_manager.list()
        return [
            img
            for img in all_images
            if any(
                tag.startswith(f"{self.config.image_name}:")
                for tag in (img.tags or [])
            )
        ]

    def prune_images(self) -> None:
        """Remove unused wallpaper-effects-processor images."""
        images = self.list_images()
        current_image = self.get_image_name()

        for img in images:
            # Skip current image
            if img.tags and current_image in img.tags:
                continue

            # Remove old images
            if img.id:
                # Ignore errors (image might be in use)
                with contextlib.suppress(Exception):
                    self.image_manager.remove(img.id, force=False)
