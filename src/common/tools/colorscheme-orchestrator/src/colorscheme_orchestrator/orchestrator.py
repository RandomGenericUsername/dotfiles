"""Main orchestrator for colorscheme generation."""

from pathlib import Path
from typing import Any

from dotfiles_container_manager import (
    ContainerEngine,
    ContainerEngineFactory,
    ContainerRuntime,
)

from colorscheme_orchestrator.config import OrchestratorConfig, load_settings
from colorscheme_orchestrator.containers import (
    BackendRegistry,
    ContainerBuilder,
    ContainerRunner,
)
from colorscheme_orchestrator.exceptions import (
    ImageNotFoundError,
    InvalidBackendError,
)


class ColorSchemeOrchestrator:
    """Orchestrates containerized colorscheme generation."""

    def __init__(
        self,
        config: OrchestratorConfig | None = None,
        engine: ContainerEngine | None = None,
    ):
        """Initialize orchestrator.

        Args:
            config: Orchestrator configuration (loads from settings.toml
                if None)
            engine: Container engine instance (creates one if None)
        """
        # Load configuration
        self.config = config or load_settings()

        # Initialize container engine
        if engine is None:
            # Create engine based on config.orchestrator.container_runtime
            runtime_str = self.config.orchestrator.container_runtime.lower()
            if runtime_str == "docker":
                runtime = ContainerRuntime.DOCKER
            elif runtime_str == "podman":
                runtime = ContainerRuntime.PODMAN
            else:
                raise ValueError(
                    f"Unsupported container runtime: {runtime_str}"
                )

            print(f"→ Initializing {runtime_str} container engine...")
            self.engine = ContainerEngineFactory.create(runtime)
            print("✓ Container engine initialized")
        else:
            self.engine = engine

        # Get paths
        # __file__ is: .../src/colorscheme_orchestrator/orchestrator.py
        # .parent = .../src/colorscheme_orchestrator/
        # .parent.parent = .../src/
        # .parent.parent.parent = .../(colorscheme-orchestrator root)
        orchestrator_root = Path(__file__).parent.parent.parent
        self.containers_dir = orchestrator_root / "containers"

        # Get colorscheme-generator module path
        # Get colorscheme-generator module path from configuration
        # This is set by the installer or defaults to
        # src/common/modules/colorscheme-generator for dev
        colorscheme_generator_path = (
            self.config.paths.colorscheme_generator_module
        )

        # If relative path, resolve it relative to the tool root or
        # workspace root
        if not colorscheme_generator_path.is_absolute():
            # __file__ is in:
            # .../colorscheme-orchestrator/src/colorscheme_orchestrator/
            # orchestrator.py
            # 3 parents up gets us to the tool root
            tool_root = Path(__file__).parent.parent.parent
            colorscheme_generator_path = (
                tool_root / colorscheme_generator_path
            ).resolve()

        self.colorscheme_generator_path = colorscheme_generator_path

        # Initialize components
        self.registry = BackendRegistry(self.containers_dir)
        self.builder = ContainerBuilder(
            self.engine,
            self.registry,
            self.colorscheme_generator_path,
        )
        self.runner = ContainerRunner(
            self.engine,
            self.registry,
            container_prefix=self.config.orchestrator.container_prefix,
            auto_cleanup=self.config.orchestrator.auto_cleanup,
        )

    def generate(
        self,
        backend: str,
        image_path: Path,
        output_dir: Path | None = None,
        formats: list[str] | None = None,
        color_count: int | None = None,
        rebuild: bool = False,
        keep_container: bool = False,
        **backend_options,
    ) -> dict[str, Path]:
        """Generate colorscheme using specified backend.

        Args:
            backend: Backend name (pywal, wallust, custom)
            image_path: Path to source image
            output_dir: Output directory (uses default if None)
            formats: Output formats (uses default if None)
            color_count: Number of colors (uses default if None)
            rebuild: Force rebuild container image
            keep_container: Don't remove container after completion
            **backend_options: Backend-specific options

        Returns:
            dict[str, Path]: Mapping of format to output file path

        Raises:
            InvalidBackendError: If backend is invalid
            ImageNotFoundError: If image file not found
        """
        # Validate backend
        if not self.registry.is_valid_backend(backend):
            raise InvalidBackendError(
                backend=backend,
                valid_backends=self.registry.list_backends(),
            )

        # Validate image exists
        image_path = image_path.expanduser().resolve()
        if not image_path.exists():
            raise ImageNotFoundError(str(image_path))

        # Use defaults from config if not provided
        output_dir = output_dir or self.config.orchestrator.default_output_dir
        formats = formats or self.config.orchestrator.default_formats
        color_count = (
            color_count or self.config.orchestrator.default_color_count
        )

        # Ensure output directory is resolved
        output_dir = output_dir.expanduser().resolve()

        print(f"\n{'=' * 60}")
        print("Colorscheme Generation")
        print(f"{'=' * 60}")
        print(f"Backend:      {backend}")
        print(f"Image:        {image_path}")
        print(f"Output:       {output_dir}")
        print(f"Formats:      {', '.join(formats)}")
        print(f"Colors:       {color_count}")
        print(f"{'=' * 60}\n")

        # Step 1: Ensure backend image exists
        metadata = self.registry.get(backend)
        if rebuild or not self.builder.image_exists(
            metadata.image_name, metadata.image_tag
        ):
            print(f"\n→ Building container image for '{backend}'...")
            self.builder.build_backend_image(backend, rebuild=rebuild)

        # Step 2: Run backend container
        print(f"\n→ Running '{backend}' backend...")
        output_files = self.runner.run_backend(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
            formats=formats,
            color_count=color_count,
            backend_options=backend_options,
            keep_container=keep_container,
        )

        print(f"\n{'=' * 60}")
        print("✓ Colorscheme Generation Complete")
        print(f"{'=' * 60}\n")

        return output_files

    def list_backends(self) -> list[str]:
        """List available backends.

        Returns:
            list[str]: List of backend names
        """
        return self.registry.list_backends()

    def get_backend_info(self, backend: str) -> dict[str, Any]:
        """Get information about a backend.

        Args:
            backend: Backend name

        Returns:
            dict[str, Any]: Backend information
        """
        metadata = self.registry.get(backend)
        return {
            "name": metadata.name,
            "image": f"{metadata.image_name}:{metadata.image_tag}",
            "dependencies": metadata.dependencies,
            "dockerfile": str(metadata.dockerfile_path),
            "entrypoint": str(metadata.entrypoint_path),
        }
