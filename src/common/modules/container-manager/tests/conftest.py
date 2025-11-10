"""Shared fixtures for container-manager tests."""

import subprocess
from unittest.mock import MagicMock

import pytest

from dotfiles_container_manager.core import (
    BuildContext,
    ContainerInfo,
    ContainerState,
    ImageInfo,
    NetworkInfo,
    NetworkMode,
    PortMapping,
    RestartPolicy,
    RunConfig,
    VolumeInfo,
    VolumeMount,
)


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for command execution."""
    mock = MagicMock(spec=subprocess.CompletedProcess)
    mock.returncode = 0
    mock.stdout = ""
    mock.stderr = ""
    return mock


@pytest.fixture
def sample_volume_mount():
    """Create a sample VolumeMount."""
    return VolumeMount(
        source="/host/path",
        target="/container/path",
        read_only=False,
        type="bind",
    )


@pytest.fixture
def sample_port_mapping():
    """Create a sample PortMapping."""
    return PortMapping(
        container_port=8080,
        host_port=8080,
        protocol="tcp",
        host_ip="0.0.0.0",
    )


@pytest.fixture
def sample_build_context():
    """Create a sample BuildContext."""
    return BuildContext(
        dockerfile="FROM alpine:latest\nRUN echo 'test'",
        files={},
        build_args={"VERSION": "1.0"},
        labels={"app": "test"},
        target=None,
        network=None,
        no_cache=False,
        pull=False,
        rm=True,
    )


@pytest.fixture
def sample_run_config():
    """Create a sample RunConfig."""
    return RunConfig(
        image="alpine:latest",
        name="test-container",
        command=["echo", "hello"],
        entrypoint=None,
        environment={"ENV_VAR": "value"},
        volumes=[],
        ports=[],
        network=NetworkMode.BRIDGE,
        restart_policy=RestartPolicy.NO,
        detach=True,
        remove=False,
        privileged=False,
        user=None,
        working_dir=None,
        hostname=None,
        labels={},
    )


@pytest.fixture
def sample_image_info():
    """Create a sample ImageInfo."""
    return ImageInfo(
        id="sha256:abc123",
        tags=["alpine:latest"],
        size=5242880,  # 5 MB
        created="2024-01-01T00:00:00Z",
        labels={"maintainer": "test"},
    )


@pytest.fixture
def sample_container_info():
    """Create a sample ContainerInfo."""
    return ContainerInfo(
        id="container123",
        name="test-container",
        image="alpine:latest",
        state=ContainerState.RUNNING,
        status="Up 5 minutes",
        created="2024-01-01T00:00:00Z",
        ports=[],
        labels={},
    )


@pytest.fixture
def sample_volume_info():
    """Create a sample VolumeInfo."""
    return VolumeInfo(
        name="test-volume",
        driver="local",
        mountpoint="/var/lib/docker/volumes/test-volume/_data",
        labels={},
    )


@pytest.fixture
def sample_network_info():
    """Create a sample NetworkInfo."""
    return NetworkInfo(
        id="network123",
        name="test-network",
        driver="bridge",
        scope="local",
        labels={},
    )


@pytest.fixture
def mock_docker_command():
    """Mock docker command execution."""

    def _mock_command(stdout="", stderr="", returncode=0):
        """Create a mock command result."""
        result = MagicMock(spec=subprocess.CompletedProcess)
        result.stdout = stdout
        result.stderr = stderr
        result.returncode = returncode
        return result

    return _mock_command


@pytest.fixture
def temp_dockerfile(tmp_path):
    """Create a temporary Dockerfile."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM alpine:latest\nRUN echo 'test'")
    return dockerfile


@pytest.fixture
def temp_build_context(tmp_path):
    """Create a temporary build context directory."""
    context_dir = tmp_path / "build_context"
    context_dir.mkdir()
    dockerfile = context_dir / "Dockerfile"
    dockerfile.write_text("FROM alpine:latest\nRUN echo 'test'")
    return context_dir
