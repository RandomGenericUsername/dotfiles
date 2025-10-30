"""Docker network manager implementation."""

from __future__ import annotations

import json

from ...core.exceptions import NetworkError, NetworkNotFoundError
from ...core.managers import NetworkManager
from ...core.types import NetworkInfo
from .utils import format_labels, run_docker_command


class DockerNetworkManager(NetworkManager):
    """Docker implementation of NetworkManager."""

    def __init__(self, command: str = "docker"):
        """
        Initialize Docker network manager.

        Args:
            command: Docker command to use
        """
        self.command = command

    def create(
        self,
        name: str,
        driver: str = "bridge",
        labels: dict[str, str] | None = None,
    ) -> str:
        """Create a Docker network."""
        cmd = [self.command, "network", "create", "--driver", driver]

        if labels:
            cmd.extend(format_labels(labels))

        cmd.append(name)

        try:
            result = run_docker_command(cmd)
            return result.stdout.decode("utf-8").strip()
        except Exception as e:
            raise NetworkError(
                message=f"Failed to create network '{name}': {e}",
                command=cmd,
            ) from e

    def remove(self, name: str) -> None:
        """Remove a Docker network."""
        cmd = [self.command, "network", "rm", name]

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such network" in str(e):
                raise NetworkNotFoundError(name) from e
            raise NetworkError(
                message=f"Failed to remove network '{name}': {e}",
                command=cmd,
            ) from e

    def connect(self, network: str, container: str) -> None:
        """Connect a container to a Docker network."""
        cmd = [self.command, "network", "connect", network, container]

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such network" in str(e):
                raise NetworkNotFoundError(network) from e
            raise NetworkError(
                message=f"Failed to connect container '{container}' to network '{network}': {e}",
                command=cmd,
            ) from e

    def disconnect(
        self, network: str, container: str, force: bool = False
    ) -> None:
        """Disconnect a container from a Docker network."""
        cmd = [self.command, "network", "disconnect", network, container]
        if force:
            cmd.append("--force")

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such network" in str(e):
                raise NetworkNotFoundError(network) from e
            raise NetworkError(
                message=f"Failed to disconnect container '{container}' from network '{network}': {e}",
                command=cmd,
            ) from e

    def exists(self, name: str) -> bool:
        """Check if a Docker network exists."""
        cmd = [self.command, "network", "inspect", name]

        try:
            run_docker_command(cmd)
            return True
        except Exception:
            return False

    def inspect(self, name: str) -> NetworkInfo:
        """Get detailed information about a Docker network."""
        cmd = [self.command, "network", "inspect", name]

        try:
            result = run_docker_command(cmd)
            data = json.loads(result.stdout.decode("utf-8"))

            if not data:
                raise NetworkNotFoundError(name)

            net_data = data[0]

            return NetworkInfo(
                id=net_data.get("Id", "")[:12],
                name=net_data.get("Name", ""),
                driver=net_data.get("Driver", ""),
                scope=net_data.get("Scope", ""),
                labels=net_data.get("Labels") or {},
            )

        except json.JSONDecodeError as e:
            raise NetworkError(
                message=f"Failed to parse network info for '{name}': {e}",
                command=cmd,
            ) from e
        except Exception as e:
            if "No such network" in str(e):
                raise NetworkNotFoundError(name) from e
            raise NetworkError(
                message=f"Failed to inspect network '{name}': {e}",
                command=cmd,
            ) from e

    def list(self, filters: dict[str, str] | None = None) -> list[NetworkInfo]:
        """List Docker networks."""
        cmd = [self.command, "network", "ls", "--format", "{{json .}}"]

        if filters:
            for key, value in filters.items():
                cmd.extend(["--filter", f"{key}={value}"])

        try:
            result = run_docker_command(cmd)
            output = result.stdout.decode("utf-8").strip()

            if not output:
                return []

            networks = []
            for line in output.split("\n"):
                if line:
                    data = json.loads(line)
                    networks.append(
                        NetworkInfo(
                            id=data.get("ID", ""),
                            name=data.get("Name", ""),
                            driver=data.get("Driver", ""),
                            scope=data.get("Scope", ""),
                            labels=data.get("Labels") or {},
                        )
                    )

            return networks

        except Exception as e:
            raise NetworkError(
                message=f"Failed to list networks: {e}",
                command=cmd,
            ) from e

    def prune(self) -> dict[str, int]:
        """Remove unused Docker networks."""
        cmd = [self.command, "network", "prune", "--force"]

        try:
            result = run_docker_command(cmd)
            output = result.stdout.decode("utf-8")

            # Count deleted networks
            deleted = 0
            if "Deleted Networks:" in output:
                # Count lines after "Deleted Networks:"
                lines = output.split("\n")
                for i, line in enumerate(lines):
                    if "Deleted Networks:" in line:
                        # Count non-empty lines after this
                        deleted = sum(1 for l in lines[i + 1 :] if l.strip())
                        break

            return {"deleted": deleted}

        except Exception as e:
            raise NetworkError(
                message=f"Failed to prune networks: {e}",
                command=cmd,
            ) from e
