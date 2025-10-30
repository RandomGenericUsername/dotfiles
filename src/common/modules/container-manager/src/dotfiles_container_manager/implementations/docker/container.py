"""Docker container manager implementation."""

from __future__ import annotations

import json

from ...core.exceptions import ContainerNotFoundError, ContainerRuntimeError
from ...core.managers import ContainerManager
from ...core.types import ContainerInfo, PortMapping, RunConfig
from .utils import (
    format_env_vars,
    format_labels,
    format_port_mappings,
    format_volume_mounts,
    run_docker_command,
)


class DockerContainerManager(ContainerManager):
    """Docker implementation of ContainerManager."""

    def __init__(self, command: str = "docker"):
        """
        Initialize Docker container manager.

        Args:
            command: Docker command to use
        """
        self.command = command

    def run(self, config: RunConfig) -> str:
        """
        Run a Docker container.

        Args:
            config: Container run configuration

        Returns:
            - If config.detach=True: Container ID (12-character short ID)
            - If config.detach=False: Container stdout as string

        Note:
            For long-running containers or when you need to inspect/wait for
            completion, use detach=True and poll with inspect().
        """
        cmd = [self.command, "run"]

        # Detach mode
        if config.detach:
            cmd.append("--detach")

        # Remove on exit
        if config.remove:
            cmd.append("--rm")

        # Container name
        if config.name:
            cmd.extend(["--name", config.name])

        # Environment variables
        if config.environment:
            cmd.extend(format_env_vars(config.environment))

        # Volumes
        if config.volumes:
            cmd.extend(format_volume_mounts(config.volumes))

        # Ports
        if config.ports:
            cmd.extend(format_port_mappings(config.ports))

        # Network
        if config.network:
            network_value = (
                config.network.value
                if hasattr(config.network, "value")
                else config.network
            )
            cmd.extend(["--network", network_value])

        # Restart policy
        if config.restart_policy:
            cmd.extend(["--restart", config.restart_policy.value])

        # User
        if config.user:
            cmd.extend(["--user", config.user])

        # Working directory
        if config.working_dir:
            cmd.extend(["--workdir", config.working_dir])

        # Hostname
        if config.hostname:
            cmd.extend(["--hostname", config.hostname])

        # Labels
        if config.labels:
            cmd.extend(format_labels(config.labels))

        # Log driver
        if config.log_driver:
            cmd.extend(["--log-driver", config.log_driver.value])

        # Privileged
        if config.privileged:
            cmd.append("--privileged")

        # Read-only
        if config.read_only:
            cmd.append("--read-only")

        # Resource limits
        if config.memory_limit:
            cmd.extend(["--memory", config.memory_limit])
        if config.cpu_limit:
            cmd.extend(["--cpus", config.cpu_limit])

        # Entrypoint
        if config.entrypoint:
            cmd.append("--entrypoint")
            cmd.append(config.entrypoint[0])

        # Image
        cmd.append(config.image)

        # Command
        if config.command:
            cmd.extend(config.command)
        elif config.entrypoint and len(config.entrypoint) > 1:
            cmd.extend(config.entrypoint[1:])

        try:
            result = run_docker_command(cmd)
            container_id = result.stdout.decode("utf-8").strip()
            return container_id

        except Exception as e:
            raise ContainerRuntimeError(
                message=f"Failed to run container from image '{config.image}': {e}",
                command=cmd,
            ) from e

    def start(self, container: str) -> None:
        """Start a stopped Docker container."""
        cmd = [self.command, "start", container]

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such container" in str(e):
                raise ContainerNotFoundError(container) from e
            raise ContainerRuntimeError(
                message=f"Failed to start container '{container}': {e}",
                command=cmd,
            ) from e

    def stop(self, container: str, timeout: int = 10) -> None:
        """Stop a running Docker container."""
        cmd = [self.command, "stop", "--time", str(timeout), container]

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such container" in str(e):
                raise ContainerNotFoundError(container) from e
            raise ContainerRuntimeError(
                message=f"Failed to stop container '{container}': {e}",
                command=cmd,
            ) from e

    def restart(self, container: str, timeout: int = 10) -> None:
        """Restart a Docker container."""
        cmd = [self.command, "restart", "--time", str(timeout), container]

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such container" in str(e):
                raise ContainerNotFoundError(container) from e
            raise ContainerRuntimeError(
                message=f"Failed to restart container '{container}': {e}",
                command=cmd,
            ) from e

    def remove(
        self, container: str, force: bool = False, volumes: bool = False
    ) -> None:
        """Remove a Docker container."""
        cmd = [self.command, "rm", container]
        if force:
            cmd.append("--force")
        if volumes:
            cmd.append("--volumes")

        try:
            run_docker_command(cmd)
        except Exception as e:
            if "No such container" in str(e):
                raise ContainerNotFoundError(container) from e
            raise ContainerRuntimeError(
                message=f"Failed to remove container '{container}': {e}",
                command=cmd,
            ) from e

    def exists(self, container: str) -> bool:
        """Check if a Docker container exists."""
        cmd = [self.command, "container", "inspect", container]

        try:
            run_docker_command(cmd)
            return True
        except Exception:
            return False

    def inspect(self, container: str) -> ContainerInfo:
        """Get detailed information about a Docker container."""
        cmd = [self.command, "container", "inspect", container]

        try:
            result = run_docker_command(cmd)
            data = json.loads(result.stdout.decode("utf-8"))

            if not data:
                raise ContainerNotFoundError(container)

            cont_data = data[0]

            # Parse port mappings
            ports = []
            port_bindings = cont_data.get("NetworkSettings", {}).get(
                "Ports", {}
            )
            for container_port, bindings in port_bindings.items():
                if bindings:
                    for binding in bindings:
                        port, protocol = container_port.split("/")
                        ports.append(
                            PortMapping(
                                container_port=int(port),
                                host_port=int(binding.get("HostPort", 0)),
                                protocol=protocol,
                                host_ip=binding.get("HostIp", "0.0.0.0"),
                            )
                        )

            return ContainerInfo(
                id=cont_data.get("Id", "")[:12],
                name=cont_data.get("Name", "").lstrip("/"),
                image=cont_data.get("Config", {}).get("Image", ""),
                state=cont_data.get("State", {}).get("Status", ""),
                status=cont_data.get("State", {}).get("Status", ""),
                created=cont_data.get("Created"),
                ports=ports,
                labels=cont_data.get("Config", {}).get("Labels") or {},
                exit_code=cont_data.get("State", {}).get("ExitCode"),
            )

        except json.JSONDecodeError as e:
            raise ContainerRuntimeError(
                message=f"Failed to parse container info for '{container}': {e}",
                command=cmd,
            ) from e
        except Exception as e:
            if "No such container" in str(e):
                raise ContainerNotFoundError(container) from e
            raise ContainerRuntimeError(
                message=f"Failed to inspect container '{container}': {e}",
                command=cmd,
            ) from e

    def list(
        self,
        all: bool = False,
        filters: dict[str, str] | None = None,
    ) -> list[ContainerInfo]:
        """List Docker containers."""
        cmd = [self.command, "ps", "--format", "{{json .}}"]

        if all:
            cmd.append("--all")

        if filters:
            for key, value in filters.items():
                cmd.extend(["--filter", f"{key}={value}"])

        try:
            result = run_docker_command(cmd)
            output = result.stdout.decode("utf-8").strip()

            if not output:
                return []

            containers = []
            for line in output.split("\n"):
                if line:
                    data = json.loads(line)
                    containers.append(
                        ContainerInfo(
                            id=data.get("ID", ""),
                            name=data.get("Names", ""),
                            image=data.get("Image", ""),
                            state=data.get("State", ""),
                            status=data.get("Status", ""),
                            created=data.get("CreatedAt"),
                        )
                    )

            return containers

        except Exception as e:
            raise ContainerRuntimeError(
                message=f"Failed to list containers: {e}",
                command=cmd,
            ) from e

    def logs(
        self,
        container: str,
        follow: bool = False,
        tail: int | None = None,
    ) -> str:
        """Get Docker container logs."""
        cmd = [self.command, "logs", container]

        if follow:
            cmd.append("--follow")
        if tail is not None:
            cmd.extend(["--tail", str(tail)])

        try:
            result = run_docker_command(cmd)
            return result.stdout.decode("utf-8")
        except Exception as e:
            if "No such container" in str(e):
                raise ContainerNotFoundError(container) from e
            raise ContainerRuntimeError(
                message=f"Failed to get logs for container '{container}': {e}",
                command=cmd,
            ) from e

    def exec(
        self,
        container: str,
        command: list[str],
        detach: bool = False,
        user: str | None = None,
    ) -> tuple[int, str]:
        """Execute a command in a running Docker container."""
        cmd = [self.command, "exec"]

        if detach:
            cmd.append("--detach")
        if user:
            cmd.extend(["--user", user])

        cmd.append(container)
        cmd.extend(command)

        try:
            result = run_docker_command(cmd)
            return (0, result.stdout.decode("utf-8"))
        except Exception as e:
            if "No such container" in str(e):
                raise ContainerNotFoundError(container) from e
            # Extract exit code if available
            exit_code = getattr(e, "exit_code", 1)
            stderr = getattr(e, "stderr", str(e))
            return (exit_code, stderr)

    def prune(self) -> dict[str, int]:
        """Remove stopped Docker containers."""
        cmd = [self.command, "container", "prune", "--force"]

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
            raise ContainerRuntimeError(
                message=f"Failed to prune containers: {e}",
                command=cmd,
            ) from e
