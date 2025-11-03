"""Container builder for wallpaper-processor images."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from dotfiles_container_manager import BuildContext, ImageManager
from wallpaper_orchestrator.config import ContainerConfig


class ContainerBuilder:
    """Builds wallpaper-processor container images."""

    def __init__(self, image_manager: ImageManager, config: ContainerConfig):
        """Initialize builder.

        Args:
            image_manager: Image manager instance
            config: Container configuration
        """
        self.image_manager = image_manager
        self.config = config

    def build(
        self,
        dockerfile_content: str,
        files: dict[str, bytes],
        _progress_callback: Callable | None = None,
    ) -> str:
        """Build container image.

        Args:
            dockerfile_content: Dockerfile content as string
            files: Additional files to include in build context
            _progress_callback: Optional callback for build progress
                (reserved for future use)

        Returns:
            Image ID

        Raises:
            ImageBuildError: If build fails
        """
        # Create build context
        build_context = BuildContext(
            dockerfile=dockerfile_content,
            files=files,
            no_cache=self.config.build_no_cache,
            pull=self.config.build_pull,
        )

        # Build image
        image_name = f"{self.config.image_name}:{self.config.image_tag}"
        image_id = self.image_manager.build(build_context, image_name)

        return image_id

    def _add_directory_to_context(
        self, files: dict[str, bytes], directory: Path, prefix: str = ""
    ) -> None:
        """Recursively add directory contents to build context.

        Args:
            files: Files dictionary to add to
            directory: Directory to add
            prefix: Prefix for file paths in context
        """
        for item in directory.rglob("*"):
            if item.is_file():
                # Skip __pycache__ and .pyc files
                if "__pycache__" in item.parts or item.suffix == ".pyc":
                    continue

                # Get relative path from directory
                rel_path = item.relative_to(directory)

                # Create path in context
                if prefix:
                    context_path = f"{prefix}/{rel_path}"
                else:
                    context_path = str(rel_path)

                # Read file content
                with item.open("rb") as f:
                    files[context_path] = f.read()

    def prepare_build_context(
        self, dockerfile_path: Path, entrypoint_path: Path
    ) -> tuple[str, dict[str, bytes]]:
        """Prepare build context with all necessary files.

        Args:
            dockerfile_path: Path to Dockerfile
            entrypoint_path: Path to entrypoint script

        Returns:
            Tuple of (dockerfile_content, files_dict)
        """
        # Read Dockerfile
        with dockerfile_path.open() as f:
            dockerfile_content = f.read()

        # Create files dict
        files = {}

        # Add entrypoint script
        if entrypoint_path.exists():
            with entrypoint_path.open("rb") as f:
                files["entrypoint.py"] = f.read()

        # Get module paths
        # __file__ is in:
        # src/common/tools/wallpaper-orchestrator/src/
        # wallpaper_orchestrator/containers/builder.py
        # 7 parents up gets us to workspace_root/src, so we need 8 parents
        workspace_root = Path(
            __file__
        ).parent.parent.parent.parent.parent.parent.parent.parent
        modules_dir = workspace_root / "src" / "common" / "modules"

        # Add wallpaper-processor module
        processor_src = (
            modules_dir / "wallpaper-processor" / "src" / "wallpaper_processor"
        )
        if processor_src.exists():
            self._add_directory_to_context(
                files, processor_src, "wallpaper_processor"
            )

        # Add logging module
        logging_src = modules_dir / "logging" / "src" / "dotfiles_logging"
        if logging_src.exists():
            self._add_directory_to_context(
                files, logging_src, "dotfiles_logging"
            )

        return dockerfile_content, files
