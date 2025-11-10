"""Tests for DockerNetworkManager."""

import json
from unittest.mock import patch

import pytest

from dotfiles_container_manager.core import (
    NetworkError,
    NetworkInfo,
    NetworkNotFoundError,
)
from dotfiles_container_manager.implementations.docker import (
    DockerNetworkManager,
)


class TestDockerNetworkManager:
    """Tests for DockerNetworkManager."""

    def test_init_default_command(self):
        """Test initialization with default command."""
        manager = DockerNetworkManager()
        assert manager.command == "docker"

    def test_init_custom_command(self):
        """Test initialization with custom command."""
        manager = DockerNetworkManager(command="podman")
        assert manager.command == "podman"

    def test_create_success(self, mock_docker_command):
        """Test creating a network successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(stdout=b"abc123def456"),
        ):
            manager = DockerNetworkManager()
            network_id = manager.create("my-network")

            assert network_id == "abc123def456"

    def test_create_with_driver(self, mock_docker_command):
        """Test creating network with custom driver."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerNetworkManager()
            manager.create("my-network", driver="overlay")

            # Verify driver is in command
            call_args = mock_run.call_args[0][0]
            assert "--driver" in call_args
            assert "overlay" in call_args

    def test_create_with_labels(self, mock_docker_command):
        """Test creating network with labels."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerNetworkManager()
            manager.create("my-network", labels={"app": "test", "env": "dev"})

            # Verify labels are in command
            call_args = mock_run.call_args[0][0]
            assert any(arg.startswith("--label") for arg in call_args)

    def test_create_failure(self):
        """Test create failure raises NetworkError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            side_effect=Exception("Create failed"),
        ):
            manager = DockerNetworkManager()
            with pytest.raises(NetworkError) as exc_info:
                manager.create("my-network")

            assert "Failed to create network" in str(exc_info.value)

    def test_remove_success(self, mock_docker_command):
        """Test removing a network successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerNetworkManager()
            # Should not raise
            manager.remove("my-network")

    def test_remove_not_found(self):
        """Test removing non-existent network raises NetworkNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            side_effect=Exception("No such network: my-network"),
        ):
            manager = DockerNetworkManager()
            with pytest.raises(NetworkNotFoundError):
                manager.remove("my-network")

    def test_connect_success(self, mock_docker_command):
        """Test connecting container to network successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerNetworkManager()
            # Should not raise
            manager.connect("my-network", "my-container")

    def test_connect_network_not_found(self):
        """Test connecting to non-existent network raises NetworkNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            side_effect=Exception("No such network: my-network"),
        ):
            manager = DockerNetworkManager()
            with pytest.raises(NetworkNotFoundError):
                manager.connect("my-network", "my-container")

    def test_disconnect_success(self, mock_docker_command):
        """Test disconnecting container from network successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerNetworkManager()
            # Should not raise
            manager.disconnect("my-network", "my-container")

    def test_disconnect_with_force(self, mock_docker_command):
        """Test disconnecting with force=True."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command()

            manager = DockerNetworkManager()
            manager.disconnect("my-network", "my-container", force=True)

            # Verify --force is in command
            call_args = mock_run.call_args[0][0]
            assert "--force" in call_args

    def test_disconnect_network_not_found(self):
        """Test disconnecting from non-existent network raises NetworkNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            side_effect=Exception("No such network: my-network"),
        ):
            manager = DockerNetworkManager()
            with pytest.raises(NetworkNotFoundError):
                manager.disconnect("my-network", "my-container")

    def test_exists_true(self, mock_docker_command):
        """Test exists() returns True for existing network."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerNetworkManager()
            assert manager.exists("my-network") is True

    def test_exists_false(self):
        """Test exists() returns False for non-existent network."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            side_effect=Exception("No such network"),
        ):
            manager = DockerNetworkManager()
            assert manager.exists("my-network") is False

    def test_inspect_success(self, mock_docker_command):
        """Test inspecting a network successfully."""
        inspect_data = [
            {
                "Id": "abc123def456",
                "Name": "my-network",
                "Driver": "bridge",
                "Scope": "local",
                "Labels": {"app": "test"},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(
                stdout=json.dumps(inspect_data).encode()
            ),
        ):
            manager = DockerNetworkManager()
            info = manager.inspect("my-network")

            assert isinstance(info, NetworkInfo)
            assert info.id == "abc123def456"
            assert info.name == "my-network"
            assert info.driver == "bridge"
            assert info.labels == {"app": "test"}

    def test_inspect_not_found(self):
        """Test inspecting non-existent network raises NetworkNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            side_effect=Exception("No such network: my-network"),
        ):
            manager = DockerNetworkManager()
            with pytest.raises(NetworkNotFoundError):
                manager.inspect("my-network")

    def test_list_success(self, mock_docker_command):
        """Test listing networks successfully."""
        networks_output = "\n".join(
            [
                json.dumps(
                    {
                        "ID": "abc123",
                        "Name": "network1",
                        "Driver": "bridge",
                        "Scope": "local",
                        "Labels": {},
                    }
                ),
                json.dumps(
                    {
                        "ID": "def456",
                        "Name": "network2",
                        "Driver": "overlay",
                        "Scope": "swarm",
                        "Labels": {},
                    }
                ),
            ]
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(stdout=networks_output.encode()),
        ):
            manager = DockerNetworkManager()
            networks = manager.list()

            assert len(networks) == 2
            assert all(isinstance(n, NetworkInfo) for n in networks)

    def test_list_empty(self, mock_docker_command):
        """Test listing networks when none exist."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(stdout=b""),
        ):
            manager = DockerNetworkManager()
            networks = manager.list()

            assert networks == []

    def test_list_with_filters(self, mock_docker_command):
        """Test listing networks with filters."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"")

            manager = DockerNetworkManager()
            manager.list(filters={"driver": "bridge"})

            # Verify filter is in command
            call_args = mock_run.call_args[0][0]
            assert "--filter" in call_args
            assert "driver=bridge" in call_args

    def test_prune_success(self, mock_docker_command):
        """Test pruning unused networks."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command",
            return_value=mock_docker_command(
                stdout=b"Deleted Networks:\nnetwork1\nnetwork2"
            ),
        ):
            manager = DockerNetworkManager()
            result = manager.prune()

            assert "deleted" in result

    def test_create_calls_correct_command(self):
        """Test that create() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type(
                "obj", (object,), {"stdout": b"abc123"}
            )()

            manager = DockerNetworkManager()
            manager.create("my-network")

            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "docker"
            assert call_args[1] == "network"
            assert call_args[2] == "create"
            assert "my-network" in call_args

    def test_remove_calls_correct_command(self):
        """Test that remove() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type("obj", (object,), {"stdout": b""})()

            manager = DockerNetworkManager()
            manager.remove("my-network")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "network", "rm", "my-network"]

    def test_connect_calls_correct_command(self):
        """Test that connect() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type("obj", (object,), {"stdout": b""})()

            manager = DockerNetworkManager()
            manager.connect("my-network", "my-container")

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "network",
                "connect",
                "my-network",
                "my-container",
            ]

    def test_disconnect_calls_correct_command(self):
        """Test that disconnect() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type("obj", (object,), {"stdout": b""})()

            manager = DockerNetworkManager()
            manager.disconnect("my-network", "my-container")

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "network",
                "disconnect",
                "my-network",
                "my-container",
            ]

    def test_inspect_calls_correct_command(self):
        """Test that inspect() calls correct docker command."""
        inspect_data = [
            {
                "Id": "abc123",
                "Name": "my-network",
                "Driver": "bridge",
                "Scope": "local",
                "Labels": {},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type(
                "obj", (object,), {"stdout": json.dumps(inspect_data).encode()}
            )()

            manager = DockerNetworkManager()
            manager.inspect("my-network")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "network", "inspect", "my-network"]

    def test_list_calls_correct_command(self):
        """Test that list() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type("obj", (object,), {"stdout": b""})()

            manager = DockerNetworkManager()
            manager.list()

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "network",
                "ls",
                "--format",
                "{{json .}}",
            ]

    def test_prune_calls_correct_command(self):
        """Test that prune() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.network.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type(
                "obj", (object,), {"stdout": b"Deleted Networks:"}
            )()

            manager = DockerNetworkManager()
            manager.prune()

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "network", "prune", "--force"]
