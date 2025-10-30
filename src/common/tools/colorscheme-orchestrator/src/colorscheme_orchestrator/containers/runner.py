"""Container runner for executing colorscheme backends."""

import time
from pathlib import Path
from typing import Any

from dotfiles_container_manager import ContainerEngine, RunConfig, VolumeMount

from colorscheme_orchestrator.containers.registry import BackendRegistry
from colorscheme_orchestrator.exceptions import ContainerRuntimeError


class ContainerRunner:
    """Runs colorscheme backend containers."""

    def __init__(
        self,
        engine: ContainerEngine,
        registry: BackendRegistry,
        container_prefix: str = "colorscheme",
        auto_cleanup: bool = True,
    ):
        """Initialize container runner.

        Args:
            engine: Container engine instance
            registry: Backend registry
            container_prefix: Prefix for container names
            auto_cleanup: Automatically cleanup containers after execution
        """
        self.engine = engine
        self.registry = registry
        self.container_prefix = container_prefix
        self.auto_cleanup = auto_cleanup

    def run_backend(
        self,
        backend: str,
        image_path: Path,
        output_dir: Path,
        formats: list[str],
        color_count: int = 16,
        backend_options: dict[str, Any] | None = None,
        keep_container: bool = False,
    ) -> dict[str, Path]:
        """Run backend container and generate colorscheme.

        Args:
            backend: Backend name
            image_path: Path to source image
            output_dir: Output directory for generated files
            formats: Output formats to generate
            color_count: Number of colors to extract
            backend_options: Backend-specific options
            keep_container: Don't remove container after completion

        Returns:
            dict[str, Path]: Mapping of format to output file path

        Raises:
            ContainerRuntimeError: If container execution fails
        """
        # Get backend metadata
        metadata = self.registry.get(backend)

        # Validate inputs
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prepare backend options
        if backend_options is None:
            backend_options = {}

        # Generate container name
        container_name = (
            f"{self.container_prefix}-{backend}-{int(time.time())}"
        )

        print(f"→ Running backend '{backend}' container...")
        print(f"  Container: {container_name}")
        print(f"  Image: {image_path}")
        print(f"  Output: {output_dir}")
        print(f"  Formats: {', '.join(formats)}")
        print(f"  Colors: {color_count}")

        try:
            # Prepare volume mounts
            volumes = [
                VolumeMount(
                    source=str(image_path.absolute()),
                    target="/input/image",
                    read_only=True,
                ),
                VolumeMount(
                    source=str(output_dir.absolute()),
                    target="/output",
                    read_only=False,
                ),
            ]

            # Prepare environment variables
            environment = {
                "IMAGE_PATH": "/input/image",
                "OUTPUT_DIR": "/output",
                "FORMATS": ",".join(formats),
                "COLOR_COUNT": str(color_count),
            }

            # Add backend-specific environment variables
            if backend == "pywal":
                environment["USE_LIBRARY"] = str(
                    backend_options.get("use_library", True)
                ).lower()
            elif backend == "wallust":
                environment["BACKEND_TYPE"] = backend_options.get(
                    "backend_type", "resized"
                )
                environment["OUTPUT_FORMAT"] = backend_options.get(
                    "output_format", "json"
                )
            elif backend == "custom":
                environment["ALGORITHM"] = backend_options.get(
                    "algorithm", "kmeans"
                )

            # Create RunConfig
            # Don't use remove=True because we need to get logs after exit
            config = RunConfig(
                image=f"{metadata.image_name}:{metadata.image_tag}",
                name=container_name,
                volumes=volumes,
                environment=environment,
                detach=True,  # Run in background
                remove=False,  # Don't auto-remove so we can get logs
            )

            # Run container
            print("  Starting container...")
            try:
                container_id = self.engine.containers.run(config)
                print(f"  Container ID: {container_id[:12]}")

                # Wait for container to finish
                print("  Waiting for completion...")
                while True:
                    info = self.engine.containers.inspect(container_id)
                    # Check if container is no longer running
                    if info.state in ("exited", "dead", "stopped"):
                        break
                    time.sleep(0.5)

                print("  Container completed")

                # Get final exit code
                exit_code = info.exit_code if info.exit_code is not None else 0

                # Get logs
                logs = self.engine.containers.logs(container_id)
            finally:
                # Clean up container if auto_cleanup is enabled
                if self.auto_cleanup and not keep_container:
                    try:
                        self.engine.containers.remove(container_id, force=True)
                        print("  Container removed")
                    except Exception:
                        pass  # Ignore cleanup errors
            print("\n  Container output:")
            print("  " + "-" * 58)
            for line in logs.split("\n"):
                if line.strip():
                    print(f"  {line}")
            print("  " + "-" * 58)

            # Check exit code
            if exit_code != 0:
                raise ContainerRuntimeError(
                    f"Container exited with code {exit_code}"
                )

            # Clean up container if needed
            if not keep_container and not self.auto_cleanup:
                print("  Removing container...")
                self.engine.containers.remove(container_id)

            # Collect output files
            output_files = {}
            for fmt in formats:
                file_path = output_dir / f"colors.{fmt}"
                if file_path.exists():
                    output_files[fmt] = file_path

            # Check for metadata file
            metadata_path = output_dir / "metadata.json"
            if metadata_path.exists():
                output_files["metadata"] = metadata_path

            print("\n✓ Container execution completed successfully")
            print(f"  Generated {len(output_files)} files")

            return output_files

        except Exception as e:
            # Try to clean up container on error
            try:
                if not keep_container:
                    self.engine.containers.remove(container_name, force=True)
            except Exception:
                pass

            raise ContainerRuntimeError(
                f"Failed to run {backend} container: {e}"
            ) from e
