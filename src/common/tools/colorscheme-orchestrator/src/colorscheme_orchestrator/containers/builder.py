"""Container image builder for colorscheme backends."""

from pathlib import Path

from dotfiles_container_manager import BuildContext, ContainerEngine

from colorscheme_orchestrator.containers.registry import BackendRegistry
from colorscheme_orchestrator.exceptions import ImageBuildError


class ContainerBuilder:
    """Builds container images for colorscheme backends."""

    def __init__(
        self,
        engine: ContainerEngine,
        registry: BackendRegistry,
        colorscheme_generator_path: Path,
    ):
        """Initialize container builder.

        Args:
            engine: Container engine instance
            registry: Backend registry
            colorscheme_generator_path: Path to colorscheme-generator module
        """
        self.engine = engine
        self.registry = registry
        self.colorscheme_generator_path = colorscheme_generator_path

    def _add_directory_to_context(
        self,
        files: dict[str, bytes],
        directory: Path,
        prefix: str = "",
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
                with open(item, "rb") as f:
                    files[context_path] = f.read()

    def image_exists(self, image_name: str, image_tag: str = "latest") -> bool:
        """Check if container image exists.

        Args:
            image_name: Image name
            image_tag: Image tag

        Returns:
            bool: True if image exists
        """
        try:
            images = self.engine.images.list()
            full_name = f"{image_name}:{image_tag}"
            for image in images:
                if full_name in image.tags:
                    return True
            return False
        except Exception:
            return False

    def build_backend_image(
        self,
        backend: str,
        rebuild: bool = False,
        no_cache: bool = False,
    ) -> str:
        """Build container image for a backend.

        Args:
            backend: Backend name
            rebuild: Force rebuild even if image exists
            no_cache: Build without using cache

        Returns:
            str: Image ID

        Raises:
            ImageBuildError: If build fails
        """
        # Get backend metadata
        metadata = self.registry.get(backend)

        # Check if image exists (unless rebuild requested)
        if not rebuild and self.image_exists(
            metadata.image_name, metadata.image_tag
        ):
            print(
                f"✓ Image {metadata.image_name}:{metadata.image_tag} already exists"
            )
            return f"{metadata.image_name}:{metadata.image_tag}"

        print(f"→ Building image for backend '{backend}'...")
        print(f"  Dockerfile: {metadata.dockerfile_path}")
        print(f"  Dependencies: {', '.join(metadata.dependencies)}")

        try:
            # Read Dockerfile
            if not metadata.dockerfile_path.exists():
                raise ImageBuildError(
                    backend=backend,
                    message=f"Dockerfile not found: {metadata.dockerfile_path}",
                )

            with open(metadata.dockerfile_path) as f:
                dockerfile_content = f.read()

            # Create build context with files
            files = {}

            # Add entrypoint script
            if metadata.entrypoint_path.exists():
                with open(metadata.entrypoint_path, "rb") as f:
                    files["entrypoint.py"] = f.read()

            # Add colorscheme-generator module files
            # We need to recursively add all files from the module
            if self.colorscheme_generator_path.exists():
                print("  Adding colorscheme-generator module...")
                self._add_directory_to_context(
                    files,
                    self.colorscheme_generator_path,
                    "colorscheme-generator",
                )
            else:
                raise ImageBuildError(
                    backend=backend,
                    message=f"colorscheme-generator module not found: {self.colorscheme_generator_path}",
                )

            # Create BuildContext
            context = BuildContext(
                dockerfile=dockerfile_content,
                files=files,
                no_cache=no_cache,
            )

            # Build image
            print("  Building container image...")
            image_name = f"{metadata.image_name}:{metadata.image_tag}"
            image_id = self.engine.images.build(context, image_name)

            print(
                f"✓ Image built successfully: {metadata.image_name}:{metadata.image_tag}"
            )
            print(f"  Image ID: {image_id[:12]}")

            return image_id

        except Exception as e:
            raise ImageBuildError(
                backend=backend,
                message=f"Failed to build image: {e}",
            ) from e

    def build_all_images(
        self,
        rebuild: bool = False,
        no_cache: bool = False,
    ) -> dict[str, str]:
        """Build images for all backends.

        Args:
            rebuild: Force rebuild even if images exist
            no_cache: Build without using cache

        Returns:
            dict[str, str]: Mapping of backend name to image ID

        Raises:
            ImageBuildError: If any build fails
        """
        results = {}
        for backend in self.registry.list_backends():
            try:
                image_id = self.build_backend_image(backend, rebuild, no_cache)
                results[backend] = image_id
            except Exception as e:
                raise ImageBuildError(
                    backend=backend,
                    message=str(e),
                ) from e

        return results
