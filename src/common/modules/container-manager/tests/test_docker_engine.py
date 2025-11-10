"""Tests for DockerEngine."""

import json
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_container_manager.core import (
    ContainerError,
    ContainerRuntime,
    RuntimeNotAvailableError,
)
from dotfiles_container_manager.implementations.docker import (
    DockerContainerManager,
    DockerEngine,
    DockerImageManager,
    DockerNetworkManager,
    DockerVolumeManager,
)


class TestDockerEngine:
    """Tests for DockerEngine."""

    def test_init_default_command(self):
        """Test initialization with default command."""
        engine = DockerEngine()
        assert engine.command == "docker"

    def test_init_custom_command(self):
        """Test initialization with custom command."""
        engine = DockerEngine(command="custom-docker")
        assert engine.command == "custom-docker"

    def test_runtime_property(self):
        """Test that runtime property returns DOCKER."""
        engine = DockerEngine()
        assert engine.runtime == ContainerRuntime.DOCKER

    def test_images_property(self):
        """Test that images property returns DockerImageManager."""
        engine = DockerEngine()
        assert isinstance(engine.images, DockerImageManager)

    def test_containers_property(self):
        """Test that containers property returns DockerContainerManager."""
        engine = DockerEngine()
        assert isinstance(engine.containers, DockerContainerManager)

    def test_volumes_property(self):
        """Test that volumes property returns DockerVolumeManager."""
        engine = DockerEngine()
        assert isinstance(engine.volumes, DockerVolumeManager)

    def test_networks_property(self):
        """Test that networks property returns DockerNetworkManager."""
        engine = DockerEngine()
        assert isinstance(engine.networks, DockerNetworkManager)

    def test_managers_use_same_command(self):
        """Test that all managers use the same command as engine."""
        engine = DockerEngine(command="custom-docker")
        assert engine.images.command == "custom-docker"
        assert engine.containers.command == "custom-docker"
        assert engine.volumes.command == "custom-docker"
        assert engine.networks.command == "custom-docker"

    def test_is_available_success(self, mock_docker_command):
        """Test is_available() when Docker is available."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            return_value=mock_docker_command(stdout=b"Docker version 24.0.7"),
        ):
            engine = DockerEngine()
            assert engine.is_available() is True

    def test_is_available_failure(self):
        """Test is_available() when Docker is not available."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            side_effect=Exception("Command not found"),
        ):
            engine = DockerEngine()
            assert engine.is_available() is False

    def test_version_success(self, mock_docker_command):
        """Test version() returns Docker version."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            return_value=mock_docker_command(
                stdout=b"Docker version 24.0.7, build afdd53b"
            ),
        ):
            engine = DockerEngine()
            version = engine.version()
            assert version == "Docker version 24.0.7, build afdd53b"

    def test_version_failure(self):
        """Test version() raises ContainerError on failure."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            side_effect=Exception("Command failed"),
        ):
            engine = DockerEngine()
            with pytest.raises(ContainerError) as exc_info:
                engine.version()

            assert "Failed to get Docker version" in str(exc_info.value)

    def test_info_success(self, mock_docker_command):
        """Test info() returns Docker system information."""
        info_data = {
            "ServerVersion": "24.0.7",
            "OperatingSystem": "Ubuntu 22.04",
            "Architecture": "x86_64",
        }
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            return_value=mock_docker_command(
                stdout=json.dumps(info_data).encode()
            ),
        ):
            engine = DockerEngine()
            info = engine.info()

            assert info["ServerVersion"] == "24.0.7"
            assert info["OperatingSystem"] == "Ubuntu 22.04"
            assert info["Architecture"] == "x86_64"

    def test_info_failure(self):
        """Test info() raises ContainerError on failure."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            side_effect=Exception("Command failed"),
        ):
            engine = DockerEngine()
            with pytest.raises(ContainerError) as exc_info:
                engine.info()

            assert "Failed to get Docker info" in str(exc_info.value)

    def test_ping_success(self, mock_docker_command):
        """Test ping() returns True when daemon is responsive."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            return_value=mock_docker_command(stdout=b"Docker info output"),
        ):
            engine = DockerEngine()
            assert engine.ping() is True

    def test_ping_failure(self):
        """Test ping() returns False when daemon is not responsive."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            side_effect=Exception("Cannot connect to daemon"),
        ):
            engine = DockerEngine()
            assert engine.ping() is False

    def test_ensure_available_success(self, mock_docker_command):
        """Test ensure_available() succeeds when Docker is available."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            return_value=mock_docker_command(stdout=b"Docker version 24.0.7"),
        ):
            engine = DockerEngine()
            # Should not raise
            engine.ensure_available()

    def test_ensure_available_failure(self):
        """Test ensure_available() raises when Docker is not available."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command",
            side_effect=Exception("Command not found"),
        ):
            engine = DockerEngine()
            with pytest.raises(RuntimeNotAvailableError) as exc_info:
                engine.ensure_available()

            assert "docker" in str(exc_info.value).lower()

    def test_version_calls_correct_command(self):
        """Test that version() calls docker --version."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"Docker version 24.0.7")
            engine = DockerEngine()
            engine.version()

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["docker", "--version"]

    def test_info_calls_correct_command(self):
        """Test that info() calls docker info --format."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(
                stdout=b'{"ServerVersion": "24.0.7"}'
            )
            engine = DockerEngine()
            engine.info()

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["docker", "info", "--format", "{{json .}}"]

    def test_is_available_calls_correct_command(self):
        """Test that is_available() calls docker --version."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"Docker version 24.0.7")
            engine = DockerEngine()
            engine.is_available()

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["docker", "--version"]

    def test_ping_calls_correct_command(self):
        """Test that ping() calls docker info."""
        with patch(
            "dotfiles_container_manager.implementations.docker.engine.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"Docker info output")
            engine = DockerEngine()
            engine.ping()

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["docker", "info"]

    def test_managers_are_cached(self):
        """Test that manager properties return the same instance."""
        engine = DockerEngine()

        images1 = engine.images
        images2 = engine.images
        assert images1 is images2

        containers1 = engine.containers
        containers2 = engine.containers
        assert containers1 is containers2

        volumes1 = engine.volumes
        volumes2 = engine.volumes
        assert volumes1 is volumes2

        networks1 = engine.networks
        networks2 = engine.networks
        assert networks1 is networks2

    def test_custom_command_propagates_to_managers(self):
        """Test that custom command is used by all managers."""
        engine = DockerEngine(command="podman")

        assert engine.command == "podman"
        assert engine.images.command == "podman"
        assert engine.containers.command == "podman"
        assert engine.volumes.command == "podman"
        assert engine.networks.command == "podman"
