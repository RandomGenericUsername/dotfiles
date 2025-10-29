"""Docker volume manager implementation."""

from __future__ import annotations

import json

from ...core.exceptions import VolumeError, VolumeNotFoundError
from ...core.managers import VolumeManager
from ...core.types import VolumeInfo
from .utils import format_labels, run_docker_command


class DockerVolumeManager(VolumeManager):
    """Docker implementation of VolumeManager."""

    def __init__(self, command: str = "docker"):
        """
        Initialize Docker volume manager.

        Args:
            command: Docker command to use
        """
        self.command = command

    def create(
        self,
        name: str,
        driver: str = "local",
        labels: dict[str, str] | None = None,
    ) -> str:
        """Create a Docker volume."""
        cmd = [self.command, "volume", "create", "--driver", driver]

        if labels:
            cmd.extend(format_labels(labels))

        cmd.append(name)

        try:
            result = run_docker_command(cmd)
            return result.stdout.decode("utf-8").strip()
        except Exception as e:
            raise VolumeError(
                message=f"Failed to create volume '{name}': {e}",
                command=cmd,
            ) from e

    def remove(self, name: str, force: bool = False) -> None:
        """Remove a Docker volume."""
        cmd = [self.command, "volume", "rm", name]
        if force:
            cmd.append("--force")

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such volume" in str(e):
                raise VolumeNotFoundError(name) from e
            raise VolumeError(
                message=f"Failed to remove volume '{name}': {e}",
                command=cmd,
            ) from e

    def exists(self, name: str) -> bool:
        """Check if a Docker volume exists."""
        cmd = [self.command, "volume", "inspect", name]

        try:
            run_docker_command(cmd)
            return True
        except Exception:
            return False

    def inspect(self, name: str) -> VolumeInfo:
        """Get detailed information about a Docker volume."""
        cmd = [self.command, "volume", "inspect", name]

        try:
            result = run_docker_command(cmd)
            data = json.loads(result.stdout.decode("utf-8"))

            if not data:
                raise VolumeNotFoundError(name)

            vol_data = data[0]

            return VolumeInfo(
                name=vol_data.get("Name", ""),
                driver=vol_data.get("Driver", ""),
                mountpoint=vol_data.get("Mountpoint"),
                labels=vol_data.get("Labels") or {},
            )

        except json.JSONDecodeError as e:
            raise VolumeError(
                message=f"Failed to parse volume info for '{name}': {e}",
                command=cmd,
            ) from e
        except Exception as e:
            if "No such volume" in str(e):
                raise VolumeNotFoundError(name) from e
            raise VolumeError(
                message=f"Failed to inspect volume '{name}': {e}",
                command=cmd,
            ) from e

    def list(self, filters: dict[str, str] | None = None) -> list[VolumeInfo]:
        """List Docker volumes."""
        cmd = [self.command, "volume", "ls", "--format", "{{json .}}"]

        if filters:
            for key, value in filters.items():
                cmd.extend(["--filter", f"{key}={value}"])

        try:
            result = run_docker_command(cmd)
            output = result.stdout.decode("utf-8").strip()

            if not output:
                return []

            volumes = []
            for line in output.split("\n"):
                if line:
                    data = json.loads(line)
                    volumes.append(
                        VolumeInfo(
                            name=data.get("Name", ""),
                            driver=data.get("Driver", ""),
                            mountpoint=data.get("Mountpoint"),
                            labels=data.get("Labels") or {},
                        )
                    )

            return volumes

        except Exception as e:
            raise VolumeError(
                message=f"Failed to list volumes: {e}",
                command=cmd,
            ) from e

    def prune(self) -> dict[str, int]:
        """Remove unused Docker volumes."""
        cmd = [self.command, "volume", "prune", "--force"]

        try:
            result = run_docker_command(cmd)
            output = result.stdout.decode("utf-8")

            # Parse output for deleted count and space reclaimed
            deleted = 0
            space_reclaimed = 0

            if "Total reclaimed space:" in output:
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
            raise VolumeError(
                message=f"Failed to prune volumes: {e}",
                command=cmd,
            ) from e
