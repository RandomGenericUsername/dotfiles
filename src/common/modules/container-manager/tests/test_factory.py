"""Tests for ContainerEngineFactory."""

from unittest.mock import patch

import pytest

from dotfiles_container_manager.core import (
    ContainerRuntime,
    RuntimeNotAvailableError,
)
from dotfiles_container_manager.factory import ContainerEngineFactory
from dotfiles_container_manager.implementations import DockerEngine


class TestContainerEngineFactory:
    """Tests for ContainerEngineFactory."""

    def test_create_docker_runtime(self, mock_docker_command):
        """Test creating engine with DOCKER runtime."""
        with patch.object(DockerEngine, "is_available", return_value=True):
            engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)

            assert engine is not None
            assert isinstance(engine, DockerEngine)
            assert engine.command == "docker"
            assert engine.runtime == ContainerRuntime.DOCKER

    def test_create_podman_runtime(self, mock_docker_command):
        """Test creating engine with PODMAN runtime."""
        with patch.object(DockerEngine, "is_available", return_value=True):
            engine = ContainerEngineFactory.create(ContainerRuntime.PODMAN)

            assert engine is not None
            assert isinstance(engine, DockerEngine)
            assert engine.command == "podman"

    def test_create_with_custom_command(self, mock_docker_command):
        """Test creating engine with custom command."""
        with patch.object(DockerEngine, "is_available", return_value=True):
            engine = ContainerEngineFactory.create(
                ContainerRuntime.DOCKER, command="custom-docker"
            )

            assert engine.command == "custom-docker"

    def test_create_docker_not_available(self):
        """Test creating engine when Docker is not available."""
        with patch.object(DockerEngine, "is_available", return_value=False):
            with pytest.raises(RuntimeNotAvailableError) as exc_info:
                ContainerEngineFactory.create(ContainerRuntime.DOCKER)

            assert "docker" in str(exc_info.value).lower()

    def test_create_podman_not_available(self):
        """Test creating engine when Podman is not available."""
        with patch.object(DockerEngine, "is_available", return_value=False):
            with pytest.raises(RuntimeNotAvailableError) as exc_info:
                ContainerEngineFactory.create(ContainerRuntime.PODMAN)

            assert "podman" in str(exc_info.value).lower()

    def test_create_calls_is_available(self):
        """Test that create() calls is_available() to verify runtime."""
        with patch.object(
            DockerEngine, "is_available", return_value=True
        ) as mock_available:
            ContainerEngineFactory.create(ContainerRuntime.DOCKER)

            mock_available.assert_called_once()

    def test_create_docker_success(self, mock_docker_command):
        """Test create_docker() with Docker available."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_docker()

            assert engine is not None
            assert isinstance(engine, DockerEngine)
            assert engine.command == "docker"

    def test_create_docker_custom_command(self, mock_docker_command):
        """Test create_docker() with custom command."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_docker(
                command="custom-docker"
            )

            assert engine.command == "custom-docker"

    def test_create_docker_not_available_raises(self):
        """Test create_docker() raises when Docker not available."""
        with patch.object(
            DockerEngine,
            "ensure_available",
            side_effect=RuntimeNotAvailableError("docker"),
        ), pytest.raises(RuntimeNotAvailableError):
            ContainerEngineFactory.create_docker()

    def test_create_docker_calls_ensure_available(self):
        """Test that create_docker() calls ensure_available()."""
        with patch.object(DockerEngine, "ensure_available") as mock_ensure:
            ContainerEngineFactory.create_docker()

            mock_ensure.assert_called_once()

    def test_create_podman_success(self, mock_docker_command):
        """Test create_podman() with Podman available."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_podman()

            assert engine is not None
            assert isinstance(engine, DockerEngine)
            assert engine.command == "podman"

    def test_create_podman_custom_command(self, mock_docker_command):
        """Test create_podman() with custom command."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_podman(
                command="custom-podman"
            )

            assert engine.command == "custom-podman"

    def test_create_podman_not_available_raises(self):
        """Test create_podman() raises when Podman not available."""
        with patch.object(
            DockerEngine,
            "ensure_available",
            side_effect=RuntimeNotAvailableError("podman"),
        ), pytest.raises(RuntimeNotAvailableError):
            ContainerEngineFactory.create_podman()

    def test_create_podman_calls_ensure_available(self):
        """Test that create_podman() calls ensure_available()."""
        with patch.object(DockerEngine, "ensure_available") as mock_ensure:
            ContainerEngineFactory.create_podman()

            mock_ensure.assert_called_once()

    def test_create_with_default_command(self, mock_docker_command):
        """Test that create() uses runtime value as default command."""
        with patch.object(DockerEngine, "is_available", return_value=True):
            engine = ContainerEngineFactory.create(ContainerRuntime.DOCKER)
            assert engine.command == "docker"

            engine = ContainerEngineFactory.create(ContainerRuntime.PODMAN)
            assert engine.command == "podman"

    def test_create_docker_returns_docker_engine(self):
        """Test that create_docker() returns DockerEngine instance."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_docker()
            assert isinstance(engine, DockerEngine)

    def test_create_podman_returns_docker_engine(self):
        """Test that create_podman() returns DockerEngine instance (for now)."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_podman()
            # Currently uses DockerEngine with podman command
            assert isinstance(engine, DockerEngine)

    def test_create_verifies_availability_before_returning(self):
        """Test that create() verifies availability before returning engine."""
        call_order = []

        def mock_init(self, command):
            call_order.append("init")
            self.command = command
            self._runtime = ContainerRuntime.DOCKER

        def mock_is_available(self):
            call_order.append("is_available")
            return True

        with patch.object(DockerEngine, "__init__", mock_init):
            with patch.object(DockerEngine, "is_available", mock_is_available):
                ContainerEngineFactory.create(ContainerRuntime.DOCKER)

        assert call_order == ["init", "is_available"]

    def test_create_docker_default_command_is_docker(self):
        """Test that create_docker() uses 'docker' as default command."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_docker()
            assert engine.command == "docker"

    def test_create_podman_default_command_is_podman(self):
        """Test that create_podman() uses 'podman' as default command."""
        with patch.object(DockerEngine, "ensure_available"):
            engine = ContainerEngineFactory.create_podman()
            assert engine.command == "podman"

    def test_create_with_none_command_uses_runtime_value(self):
        """Test that passing command=None uses runtime value."""
        with patch.object(DockerEngine, "is_available", return_value=True):
            engine = ContainerEngineFactory.create(
                ContainerRuntime.DOCKER, command=None
            )
            assert engine.command == "docker"

    def test_factory_creates_independent_instances(self):
        """Test that factory creates independent engine instances."""
        with patch.object(DockerEngine, "ensure_available"):
            engine1 = ContainerEngineFactory.create_docker()
            engine2 = ContainerEngineFactory.create_docker()

            assert engine1 is not engine2

    def test_create_with_both_runtimes(self):
        """Test creating engines for both Docker and Podman."""
        with patch.object(DockerEngine, "is_available", return_value=True):
            docker_engine = ContainerEngineFactory.create(
                ContainerRuntime.DOCKER
            )
            podman_engine = ContainerEngineFactory.create(
                ContainerRuntime.PODMAN
            )

            assert docker_engine.command == "docker"
            assert podman_engine.command == "podman"
            assert docker_engine is not podman_engine
