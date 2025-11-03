"""Utility functions for Docker operations."""

import io
import json
import re
import subprocess
import tarfile
from typing import Any

from ...core.exceptions import ContainerError


def run_docker_command(
    command: list[str],
    timeout: int | None = None,
    input_data: bytes | None = None,
) -> subprocess.CompletedProcess:
    """
    Run a Docker command.

    Args:
        command: Command to run
        timeout: Timeout in seconds
        input_data: Data to pipe to stdin

    Returns:
        CompletedProcess result

    Raises:
        ContainerError: If command fails
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            input=input_data,
            check=False,
        )

        if result.returncode != 0:
            raise ContainerError(
                message="Docker command failed",
                command=command,
                exit_code=result.returncode,
                stderr=result.stderr.decode("utf-8", errors="replace"),
            )

        return result

    except subprocess.TimeoutExpired as e:
        raise ContainerError(
            message=f"Docker command timed out after {timeout} seconds",
            command=command,
        ) from e
    except FileNotFoundError as e:
        raise ContainerError(
            message="Docker command not found. Is Docker installed?",
            command=command,
        ) from e


def create_build_context_tar(
    dockerfile_content: str,
    files: dict[str, bytes] | None = None,
) -> bytes:
    """
    Create a tar archive for Docker build context.

    Args:
        dockerfile_content: Content of the Dockerfile
        files: Additional files to include (path -> content)

    Returns:
        Tar archive as bytes
    """
    tar_buffer = io.BytesIO()

    with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
        # Add Dockerfile
        dockerfile_bytes = dockerfile_content.encode("utf-8")
        dockerfile_info = tarfile.TarInfo(name="Dockerfile")
        dockerfile_info.size = len(dockerfile_bytes)
        tar.addfile(dockerfile_info, io.BytesIO(dockerfile_bytes))

        # Add additional files
        if files:
            for file_path, file_content in files.items():
                file_info = tarfile.TarInfo(name=file_path)
                file_info.size = len(file_content)
                tar.addfile(file_info, io.BytesIO(file_content))

    return tar_buffer.getvalue()


def parse_docker_output(output: str) -> dict[str, Any]:
    """
    Parse Docker JSON output.

    Args:
        output: Docker command output

    Returns:
        Parsed JSON data
    """
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"raw": output}


def extract_image_id(output: str) -> str:
    """
    Extract image ID from Docker build output.

    Args:
        output: Docker build output

    Returns:
        Image ID (short form)
    """
    # Look for "Successfully built <id>"
    match = re.search(r"Successfully built ([a-f0-9]+)", output)
    if match:
        return match.group(1)

    # Look for "sha256:<id>"
    match = re.search(r"sha256:([a-f0-9]+)", output)
    if match:
        return match.group(1)[:12]  # Return short form

    # If no match, return empty string
    return ""


def format_labels(labels: dict[str, str]) -> list[str]:
    """
    Format labels for Docker command.

    Args:
        labels: Label dictionary

    Returns:
        List of --label arguments
    """
    return [f"--label={key}={value}" for key, value in labels.items()]


def format_build_args(build_args: dict[str, str]) -> list[str]:
    """
    Format build arguments for Docker command.

    Args:
        build_args: Build argument dictionary

    Returns:
        List of --build-arg arguments
    """
    return [f"--build-arg={key}={value}" for key, value in build_args.items()]


def format_env_vars(env_vars: dict[str, str]) -> list[str]:
    """
    Format environment variables for Docker command.

    Args:
        env_vars: Environment variable dictionary

    Returns:
        List of --env arguments
    """
    return [f"--env={key}={value}" for key, value in env_vars.items()]


def format_port_mappings(ports: list) -> list[str]:
    """
    Format port mappings for Docker command.

    Args:
        ports: List of PortMapping objects

    Returns:
        List of --publish arguments
    """
    result = []
    for port in ports:
        if port.host_port:
            mapping = (
                f"{port.host_ip}:{port.host_port}:"
                f"{port.container_port}/{port.protocol}"
            )
        else:
            mapping = f"{port.container_port}/{port.protocol}"
        result.append(f"--publish={mapping}")
    return result


def format_volume_mounts(volumes: list) -> list[str]:
    """
    Format volume mounts for Docker command.

    Args:
        volumes: List of VolumeMount objects

    Returns:
        List of --volume arguments
    """
    result = []
    for volume in volumes:
        mount = f"{volume.source}:{volume.target}"
        if volume.read_only:
            mount += ":ro"
        result.append(f"--volume={mount}")
    return result
