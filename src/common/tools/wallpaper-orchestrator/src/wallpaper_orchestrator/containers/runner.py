"""Container runner for executing wallpaper processing."""

import contextlib
import json
import time
from pathlib import Path

from dotfiles_container_manager import (
    ContainerManager,
    RunConfig,
    VolumeMount,
)

from wallpaper_orchestrator.config import ContainerConfig, ProcessingConfig


class ContainerRunner:
    """Runs wallpaper processing in containers."""

    def __init__(
        self,
        container_manager: ContainerManager,
        config: ContainerConfig,
        processing_config: ProcessingConfig,
    ):
        """Initialize runner.

        Args:
            container_manager: Container manager instance
            config: Container configuration
            processing_config: Processing configuration
        """
        self.container_manager = container_manager
        self.config = config
        self.processing_config = processing_config

    def run_effects(
        self,
        input_path: Path,
        output_path: Path,
        effects: list[dict],
        effect_params: dict,
    ) -> tuple[int, str, str]:
        """Run effects in container.

        Args:
            input_path: Input image path
            output_path: Output image path
            effects: List of effect names
            effect_params: Effect parameters dict

        Returns:
            Tuple of (exit_code, stdout, stderr)

        Raises:
            ContainerRuntimeError: If container execution fails
        """
        # Prepare volume mounts
        volumes = [
            VolumeMount(
                source=str(input_path.absolute()),
                target="/input/image",
                read_only=True,
            ),
            VolumeMount(
                source=str(output_path.parent.absolute()),
                target="/output",
                read_only=False,
            ),
        ]

        # Prepare environment variables
        environment = {
            "IMAGE_PATH": "/input/image",
            "OUTPUT_PATH": f"/output/{output_path.name}",
            "EFFECTS": ",".join(effects),
            "EFFECT_PARAMS": json.dumps(effect_params),
            "PROCESSING_MODE": self.processing_config.mode,
            "OUTPUT_FORMAT": self.processing_config.output_format,
            "QUALITY": str(self.processing_config.quality),
            "WRITE_METADATA": str(
                self.processing_config.write_metadata
            ).lower(),
        }

        # Create run config
        run_config = RunConfig(
            image=f"{self.config.image_name}:{self.config.image_tag}",
            volumes=volumes,
            environment=environment,
            detach=True,  # Run in background
            remove=False,  # Don't auto-remove so we can get logs
        )

        # Run container
        container_id = self.container_manager.run(run_config)

        try:
            # Wait for container to finish
            while True:
                info = self.container_manager.inspect(container_id)
                # Check if container is no longer running
                if info.state in ("exited", "dead", "stopped"):
                    break
                time.sleep(0.5)

            # Get final exit code
            exit_code = info.exit_code if info.exit_code is not None else 0

            # Get logs
            logs = self.container_manager.logs(container_id)
        finally:
            # Clean up container (ignore cleanup errors)
            with contextlib.suppress(Exception):
                self.container_manager.remove(container_id, force=True)

        # Parse logs (stdout/stderr combined in logs)
        return exit_code, logs, ""

    def run_preset(
        self,
        input_path: Path,
        output_path: Path,
        preset_name: str,
    ) -> tuple[int, str, str]:
        """Run preset in container.

        Args:
            input_path: Input image path
            output_path: Output image path
            preset_name: Preset name

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        # Prepare volume mounts
        volumes = [
            VolumeMount(
                source=str(input_path.absolute()),
                target="/input/image",
                read_only=True,
            ),
            VolumeMount(
                source=str(output_path.parent.absolute()),
                target="/output",
                read_only=False,
            ),
        ]

        # Prepare environment variables
        environment = {
            "IMAGE_PATH": "/input/image",
            "OUTPUT_PATH": f"/output/{output_path.name}",
            "PRESET": preset_name,
            "PROCESSING_MODE": self.processing_config.mode,
            "OUTPUT_FORMAT": self.processing_config.output_format,
            "QUALITY": str(self.processing_config.quality),
            "WRITE_METADATA": str(
                self.processing_config.write_metadata
            ).lower(),
        }

        # Create run config
        run_config = RunConfig(
            image=f"{self.config.image_name}:{self.config.image_tag}",
            volumes=volumes,
            environment=environment,
            detach=True,  # Run in background
            remove=False,  # Don't auto-remove so we can get logs
        )

        # Run container
        container_id = self.container_manager.run(run_config)

        try:
            # Wait for container to finish
            while True:
                info = self.container_manager.inspect(container_id)
                # Check if container is no longer running
                if info.state in ("exited", "dead", "stopped"):
                    break
                time.sleep(0.5)

            # Get final exit code
            exit_code = info.exit_code if info.exit_code is not None else 0

            # Get logs
            logs = self.container_manager.logs(container_id)
        finally:
            # Clean up container (ignore cleanup errors)
            with contextlib.suppress(Exception):
                self.container_manager.remove(container_id, force=True)

        return exit_code, logs, ""
