"""Tests for DockerVolumeManager."""

import json
from unittest.mock import patch

import pytest

from dotfiles_container_manager.core import (
    VolumeError,
    VolumeInfo,
    VolumeNotFoundError,
)
from dotfiles_container_manager.implementations.docker import (
    DockerVolumeManager,
)


class TestDockerVolumeManager:
    """Tests for DockerVolumeManager."""

    def test_init_default_command(self):
        """Test initialization with default command."""
        manager = DockerVolumeManager()
        assert manager.command == "docker"

    def test_init_custom_command(self):
        """Test initialization with custom command."""
        manager = DockerVolumeManager(command="podman")
        assert manager.command == "podman"

    def test_create_success(self, mock_docker_command):
        """Test creating a volume successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            return_value=mock_docker_command(stdout=b"my-volume"),
        ):
            manager = DockerVolumeManager()
            volume_name = manager.create("my-volume")

            assert volume_name == "my-volume"

    def test_create_with_driver(self, mock_docker_command):
        """Test creating volume with custom driver."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"my-volume")

            manager = DockerVolumeManager()
            manager.create("my-volume", driver="nfs")

            # Verify driver is in command
            call_args = mock_run.call_args[0][0]
            assert "--driver" in call_args
            assert "nfs" in call_args

    def test_create_with_labels(self, mock_docker_command):
        """Test creating volume with labels."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"my-volume")

            manager = DockerVolumeManager()
            manager.create("my-volume", labels={"app": "test", "env": "dev"})

            # Verify labels are in command
            call_args = mock_run.call_args[0][0]
            assert any(arg.startswith("--label") for arg in call_args)

    def test_create_failure(self):
        """Test create failure raises VolumeError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            side_effect=Exception("Create failed"),
        ):
            manager = DockerVolumeManager()
            with pytest.raises(VolumeError) as exc_info:
                manager.create("my-volume")

            assert "Failed to create volume" in str(exc_info.value)

    def test_remove_success(self, mock_docker_command):
        """Test removing a volume successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerVolumeManager()
            # Should not raise
            manager.remove("my-volume")

    def test_remove_with_force(self, mock_docker_command):
        """Test removing volume with force=True."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command()

            manager = DockerVolumeManager()
            manager.remove("my-volume", force=True)

            # Verify --force is in command
            call_args = mock_run.call_args[0][0]
            assert "--force" in call_args

    def test_remove_not_found(self):
        """Test removing non-existent volume raises VolumeNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            side_effect=Exception("No such volume: my-volume"),
        ):
            manager = DockerVolumeManager()
            with pytest.raises(VolumeNotFoundError):
                manager.remove("my-volume")

    def test_exists_true(self, mock_docker_command):
        """Test exists() returns True for existing volume."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerVolumeManager()
            assert manager.exists("my-volume") is True

    def test_exists_false(self):
        """Test exists() returns False for non-existent volume."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            side_effect=Exception("No such volume"),
        ):
            manager = DockerVolumeManager()
            assert manager.exists("my-volume") is False

    def test_inspect_success(self, mock_docker_command):
        """Test inspecting a volume successfully."""
        inspect_data = [
            {
                "Name": "my-volume",
                "Driver": "local",
                "Mountpoint": "/var/lib/docker/volumes/my-volume/_data",
                "Labels": {"app": "test"},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            return_value=mock_docker_command(
                stdout=json.dumps(inspect_data).encode()
            ),
        ):
            manager = DockerVolumeManager()
            info = manager.inspect("my-volume")

            assert isinstance(info, VolumeInfo)
            assert info.name == "my-volume"
            assert info.driver == "local"
            assert info.labels == {"app": "test"}

    def test_inspect_not_found(self):
        """Test inspecting non-existent volume raises VolumeNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            side_effect=Exception("No such volume: my-volume"),
        ):
            manager = DockerVolumeManager()
            with pytest.raises(VolumeNotFoundError):
                manager.inspect("my-volume")

    def test_list_success(self, mock_docker_command):
        """Test listing volumes successfully."""
        volumes_output = "\n".join(
            [
                json.dumps(
                    {
                        "Name": "volume1",
                        "Driver": "local",
                        "Mountpoint": "/path1",
                        "Labels": {},
                    }
                ),
                json.dumps(
                    {
                        "Name": "volume2",
                        "Driver": "local",
                        "Mountpoint": "/path2",
                        "Labels": {},
                    }
                ),
            ]
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            return_value=mock_docker_command(stdout=volumes_output.encode()),
        ):
            manager = DockerVolumeManager()
            volumes = manager.list()

            assert len(volumes) == 2
            assert all(isinstance(v, VolumeInfo) for v in volumes)

    def test_list_empty(self, mock_docker_command):
        """Test listing volumes when none exist."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            return_value=mock_docker_command(stdout=b""),
        ):
            manager = DockerVolumeManager()
            volumes = manager.list()

            assert volumes == []

    def test_list_with_filters(self, mock_docker_command):
        """Test listing volumes with filters."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"")

            manager = DockerVolumeManager()
            manager.list(filters={"driver": "local"})

            # Verify filter is in command
            call_args = mock_run.call_args[0][0]
            assert "--filter" in call_args
            assert "driver=local" in call_args

    def test_prune_success(self, mock_docker_command):
        """Test pruning unused volumes."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command",
            return_value=mock_docker_command(
                stdout=b"Total reclaimed space: 1.5GB"
            ),
        ):
            manager = DockerVolumeManager()
            result = manager.prune()

            assert "deleted" in result
            assert "space_reclaimed" in result

    def test_create_calls_correct_command(self):
        """Test that create() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type(
                "obj", (object,), {"stdout": b"my-volume"}
            )()

            manager = DockerVolumeManager()
            manager.create("my-volume")

            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "docker"
            assert call_args[1] == "volume"
            assert call_args[2] == "create"
            assert "my-volume" in call_args

    def test_remove_calls_correct_command(self):
        """Test that remove() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type("obj", (object,), {"stdout": b""})()

            manager = DockerVolumeManager()
            manager.remove("my-volume")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "volume", "rm", "my-volume"]

    def test_inspect_calls_correct_command(self):
        """Test that inspect() calls correct docker command."""
        inspect_data = [
            {
                "Name": "my-volume",
                "Driver": "local",
                "Mountpoint": "/path",
                "Labels": {},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type(
                "obj", (object,), {"stdout": json.dumps(inspect_data).encode()}
            )()

            manager = DockerVolumeManager()
            manager.inspect("my-volume")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "volume", "inspect", "my-volume"]

    def test_list_calls_correct_command(self):
        """Test that list() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type("obj", (object,), {"stdout": b""})()

            manager = DockerVolumeManager()
            manager.list()

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "volume",
                "ls",
                "--format",
                "{{json .}}",
            ]

    def test_prune_calls_correct_command(self):
        """Test that prune() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.volume.run_docker_command"
        ) as mock_run:
            mock_run.return_value = type(
                "obj", (object,), {"stdout": b"Total reclaimed space: 0B"}
            )()

            manager = DockerVolumeManager()
            manager.prune()

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "volume", "prune", "--force"]
