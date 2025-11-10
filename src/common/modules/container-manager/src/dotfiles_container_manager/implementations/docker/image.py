"""Docker image manager implementation."""

from __future__ import annotations

import json

from ...core.exceptions import ImageBuildError, ImageError, ImageNotFoundError
from ...core.managers import ImageManager
from ...core.types import BuildContext, ImageInfo
from .utils import (
    create_build_context_tar,
    extract_image_id,
    format_build_args,
    format_labels,
    run_docker_command,
)


class DockerImageManager(ImageManager):
    """Docker implementation of ImageManager."""

    def __init__(self, command: str = "docker"):
        """
        Initialize Docker image manager.

        Args:
            command: Docker command to use
        """
        self.command = command

    def build(
        self,
        context: BuildContext,
        image_name: str,
        timeout: int = 600,
    ) -> str:
        """Build a Docker image."""
        # Create tar archive with Dockerfile and files
        tar_data = create_build_context_tar(
            context.dockerfile,
            context.files,
        )

        # Build command
        cmd = [self.command, "build", "-t", image_name]

        # Add build args
        if context.build_args:
            cmd.extend(format_build_args(context.build_args))

        # Add labels
        if context.labels:
            cmd.extend(format_labels(context.labels))

        # Add target for multi-stage builds
        if context.target:
            cmd.extend(["--target", context.target])

        # Add network mode
        if context.network:
            cmd.extend(["--network", context.network])

        # Add flags
        if context.no_cache:
            cmd.append("--no-cache")
        if context.pull:
            cmd.append("--pull")
        if not context.rm:
            cmd.append("--rm=false")

        # Read from stdin
        cmd.append("-")

        try:
            result = run_docker_command(
                cmd, timeout=timeout, input_data=tar_data
            )
            output = result.stdout.decode("utf-8")

            # Extract image ID
            image_id = extract_image_id(output)
            if not image_id:
                # Fallback: inspect the image we just built
                image_id = self._get_image_id(image_name)

            return image_id

        except Exception as e:
            raise ImageBuildError(
                message=f"Failed to build image '{image_name}': {e}",
                command=cmd,
            ) from e

    def tag(self, image: str, tag: str) -> None:
        """Tag a Docker image."""
        cmd = [self.command, "tag", image, tag]

        try:
            run_docker_command(cmd)
        except Exception as e:
            raise ImageError(
                message=f"Failed to tag image '{image}' as '{tag}': {e}",
                command=cmd,
            ) from e

    def push(self, image: str, timeout: int = 300) -> None:
        """Push a Docker image to registry."""
        cmd = [self.command, "push", image]

        try:
            run_docker_command(cmd, timeout=timeout)
        except Exception as e:
            raise ImageError(
                message=f"Failed to push image '{image}': {e}",
                command=cmd,
            ) from e

    def pull(self, image: str, timeout: int = 300) -> str:
        """Pull a Docker image from registry."""
        cmd = [self.command, "pull", image]

        try:
            run_docker_command(cmd, timeout=timeout)
            return self._get_image_id(image)
        except Exception as e:
            raise ImageError(
                message=f"Failed to pull image '{image}': {e}",
                command=cmd,
            ) from e

    def remove(self, image: str, force: bool = False) -> None:
        """Remove a Docker image."""
        cmd = [self.command, "rmi", image]
        if force:
            cmd.append("--force")

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such image" in str(e):
                raise ImageNotFoundError(image) from e
            raise ImageError(
                message=f"Failed to remove image '{image}': {e}",
                command=cmd,
            ) from e

    def exists(self, image: str) -> bool:
        """Check if a Docker image exists."""
        cmd = [self.command, "image", "inspect", image]

        try:
            run_docker_command(cmd)
            return True
        except Exception:
            return False

    def inspect(self, image: str) -> ImageInfo:
        """Get detailed information about a Docker image."""
        cmd = [self.command, "image", "inspect", image]

        try:
            result = run_docker_command(cmd)
            data = json.loads(result.stdout.decode("utf-8"))

            if not data:
                raise ImageNotFoundError(image)

            img_data = data[0]

            return ImageInfo(
                id=img_data.get("Id", "").replace("sha256:", "")[:12],
                tags=img_data.get("RepoTags", []),
                size=img_data.get("Size", 0),
                created=img_data.get("Created"),
                labels=img_data.get("Config", {}).get("Labels") or {},
            )

        except ImageNotFoundError:
            # Re-raise ImageNotFoundError without wrapping
            raise
        except json.JSONDecodeError as e:
            raise ImageError(
                message=f"Failed to parse image info for '{image}': {e}",
                command=cmd,
            ) from e
        except Exception as e:
            if "No such image" in str(e):
                raise ImageNotFoundError(image) from e
            raise ImageError(
                message=f"Failed to inspect image '{image}': {e}",
                command=cmd,
            ) from e

    def list(self, filters: dict[str, str] | None = None) -> list[ImageInfo]:
        """List Docker images."""
        cmd = [self.command, "images", "--format", "{{json .}}"]

        if filters:
            for key, value in filters.items():
                cmd.extend(["--filter", f"{key}={value}"])

        try:
            result = run_docker_command(cmd)
            output = result.stdout.decode("utf-8").strip()

            if not output:
                return []

            images = []
            for line in output.split("\n"):
                if line:
                    data = json.loads(line)
                    images.append(
                        ImageInfo(
                            id=data.get("ID", ""),
                            tags=[
                                data.get("Repository", "")
                                + ":"
                                + data.get("Tag", "")
                            ],
                            size=self._parse_size(data.get("Size", "0B")),
                            created=data.get("CreatedAt"),
                        )
                    )

            return images

        except Exception as e:
            raise ImageError(
                message=f"Failed to list images: {e}",
                command=cmd,
            ) from e

    def prune(self, all: bool = False) -> dict[str, int]:
        """Remove unused Docker images."""
        cmd = [self.command, "image", "prune", "--force"]
        if all:
            cmd.append("--all")

        try:
            result = run_docker_command(cmd)
            output = result.stdout.decode("utf-8")

            # Parse output for deleted count and space reclaimed
            # Output format: "Total reclaimed space: 1.2GB"
            deleted = 0
            space_reclaimed = 0

            if "Total reclaimed space:" in output:
                # Extract space value
                import re

                match = re.search(
                    r"Total reclaimed space:\s*([\d.]+)([KMGT]?B)", output
                )
                if match:
                    value = float(match.group(1))
                    unit = match.group(2)
                    multipliers = {
                        "B": 1,
                        "KB": 1024,
                        "MB": 1024**2,
                        "GB": 1024**3,
                        "TB": 1024**4,
                    }
                    space_reclaimed = int(value * multipliers.get(unit, 1))

            return {"deleted": deleted, "space_reclaimed": space_reclaimed}

        except Exception as e:
            raise ImageError(
                message=f"Failed to prune images: {e}",
                command=cmd,
            ) from e

    def _get_image_id(self, image: str) -> str:
        """Get image ID by name."""
        cmd = [self.command, "image", "inspect", "--format", "{{.Id}}", image]

        try:
            result = run_docker_command(cmd)
            image_id = result.stdout.decode("utf-8").strip()
            return image_id.replace("sha256:", "")[:12]
        except Exception:
            return ""

    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes."""
        import re

        match = re.match(r"([\d.]+)([KMGT]?B)", size_str)
        if not match:
            return 0

        value = float(match.group(1))
        unit = match.group(2)
        multipliers = {
            "B": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
        }
        return int(value * multipliers.get(unit, 1))
