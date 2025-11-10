"""Tests for DockerContainerManager."""

import json
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_container_manager.core import (
    ContainerInfo,
    ContainerNotFoundError,
    ContainerRuntimeError,
    NetworkMode,
    PortMapping,
    RestartPolicy,
    RunConfig,
    VolumeMount,
)
from dotfiles_container_manager.implementations.docker import (
    DockerContainerManager,
)


class TestDockerContainerManager:
    """Tests for DockerContainerManager."""

    def test_init_default_command(self):
        """Test initialization with default command."""
        manager = DockerContainerManager()
        assert manager.command == "docker"

    def test_init_custom_command(self):
        """Test initialization with custom command."""
        manager = DockerContainerManager(command="podman")
        assert manager.command == "podman"

    def test_run_basic(self, sample_run_config, mock_docker_command):
        """Test running a container with basic config."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(stdout=b"abc123def456"),
        ):
            manager = DockerContainerManager()
            container_id = manager.run(sample_run_config)

            assert container_id == "abc123def456"

    def test_run_with_volumes(self, mock_docker_command):
        """Test running container with volume mounts."""
        config = RunConfig(
            image="alpine:latest",
            volumes=[
                VolumeMount(source="/host/path", target="/container/path"),
                VolumeMount(source="my-volume", target="/data", type="volume"),
            ],
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify volumes are in command
            call_args = mock_run.call_args[0][0]
            assert any(arg.startswith(("-v", "--volume")) for arg in call_args)

    def test_run_with_ports(self, mock_docker_command):
        """Test running container with port mappings."""
        config = RunConfig(
            image="alpine:latest",
            ports=[
                PortMapping(container_port=8080, host_port=8080),
                PortMapping(container_port=443, host_port=443),
            ],
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify ports are in command
            call_args = mock_run.call_args[0][0]
            assert any(
                arg.startswith(("-p", "--publish")) for arg in call_args
            )

    def test_run_with_environment(self, mock_docker_command):
        """Test running container with environment variables."""
        config = RunConfig(
            image="alpine:latest",
            environment={"VAR1": "value1", "VAR2": "value2"},
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify environment variables are in command
            call_args = mock_run.call_args[0][0]
            assert any(arg.startswith(("-e", "--env")) for arg in call_args)

    def test_run_with_custom_command(self, mock_docker_command):
        """Test running container with custom command."""
        config = RunConfig(
            image="alpine:latest",
            command=["sh", "-c", "echo hello"],
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify command is in args
            call_args = mock_run.call_args[0][0]
            assert "sh" in call_args
            assert "-c" in call_args
            assert "echo hello" in call_args

    def test_run_with_entrypoint(self, mock_docker_command):
        """Test running container with entrypoint override."""
        config = RunConfig(
            image="alpine:latest",
            entrypoint=["/bin/sh"],
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify entrypoint is in command
            call_args = mock_run.call_args[0][0]
            assert "--entrypoint" in call_args

    def test_run_with_network_mode(self, mock_docker_command):
        """Test running container with network mode."""
        config = RunConfig(
            image="alpine:latest",
            network=NetworkMode.HOST,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify network is in command
            call_args = mock_run.call_args[0][0]
            assert "--network" in call_args
            assert "host" in call_args

    def test_run_with_restart_policy(self, mock_docker_command):
        """Test running container with restart policy."""
        config = RunConfig(
            image="alpine:latest",
            restart_policy=RestartPolicy.ALWAYS,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify restart policy is in command
            call_args = mock_run.call_args[0][0]
            assert "--restart" in call_args
            assert "always" in call_args

    def test_run_detached(self, mock_docker_command):
        """Test running container in detached mode."""
        config = RunConfig(
            image="alpine:latest",
            detach=True,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --detach is in command
            call_args = mock_run.call_args[0][0]
            assert "--detach" in call_args

    def test_run_with_remove(self, mock_docker_command):
        """Test running container with remove=True."""
        config = RunConfig(
            image="alpine:latest",
            remove=True,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --rm is in command
            call_args = mock_run.call_args[0][0]
            assert "--rm" in call_args

    def test_run_with_privileged(self, mock_docker_command):
        """Test running container with privileged=True."""
        config = RunConfig(
            image="alpine:latest",
            privileged=True,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --privileged is in command
            call_args = mock_run.call_args[0][0]
            assert "--privileged" in call_args

    def test_run_with_name(self, mock_docker_command):
        """Test running container with custom name."""
        config = RunConfig(
            image="alpine:latest",
            name="my-container",
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --name is in command
            call_args = mock_run.call_args[0][0]
            assert "--name" in call_args
            assert "my-container" in call_args

    def test_run_failure(self, sample_run_config):
        """Test run failure raises ContainerRuntimeError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("Run failed"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerRuntimeError) as exc_info:
                manager.run(sample_run_config)

            assert "Failed to run container" in str(exc_info.value)

    def test_start_success(self, mock_docker_command):
        """Test starting a container successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerContainerManager()
            # Should not raise
            manager.start("test-container")

    def test_start_not_found(self):
        """Test starting non-existent container raises ContainerNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container: test-container"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerNotFoundError):
                manager.start("test-container")

    def test_stop_success(self, mock_docker_command):
        """Test stopping a container successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerContainerManager()
            # Should not raise
            manager.stop("test-container")

    def test_stop_with_timeout(self, mock_docker_command):
        """Test stopping container with custom timeout."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command()

            manager = DockerContainerManager()
            manager.stop("test-container", timeout=30)

            # Verify timeout is in command
            call_args = mock_run.call_args[0][0]
            assert "--time" in call_args
            assert "30" in call_args

    def test_stop_not_found(self):
        """Test stopping non-existent container raises ContainerNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container: test-container"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerNotFoundError):
                manager.stop("test-container")

    def test_restart_success(self, mock_docker_command):
        """Test restarting a container successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerContainerManager()
            # Should not raise
            manager.restart("test-container")

    def test_restart_not_found(self):
        """Test restarting non-existent container raises ContainerNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container: test-container"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerNotFoundError):
                manager.restart("test-container")

    def test_remove_success(self, mock_docker_command):
        """Test removing a container successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerContainerManager()
            # Should not raise
            manager.remove("test-container")

    def test_remove_with_force(self, mock_docker_command):
        """Test removing container with force=True."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command()

            manager = DockerContainerManager()
            manager.remove("test-container", force=True)

            # Verify --force is in command
            call_args = mock_run.call_args[0][0]
            assert "--force" in call_args

    def test_remove_with_volumes(self, mock_docker_command):
        """Test removing container with volumes=True."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command()

            manager = DockerContainerManager()
            manager.remove("test-container", volumes=True)

            # Verify --volumes is in command
            call_args = mock_run.call_args[0][0]
            assert "--volumes" in call_args

    def test_remove_not_found(self):
        """Test removing non-existent container raises ContainerNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container: test-container"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerNotFoundError):
                manager.remove("test-container")

    def test_exists_true(self, mock_docker_command):
        """Test exists() returns True for existing container."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerContainerManager()
            assert manager.exists("test-container") is True

    def test_exists_false(self):
        """Test exists() returns False for non-existent container."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container"),
        ):
            manager = DockerContainerManager()
            assert manager.exists("test-container") is False

    def test_inspect_success(self, mock_docker_command):
        """Test inspecting a container successfully."""
        inspect_data = [
            {
                "Id": "abc123def456",
                "Name": "/test-container",
                "Config": {
                    "Image": "alpine:latest",
                    "Labels": {"app": "test"},
                },
                "State": {
                    "Status": "running",
                    "Running": True,
                    "ExitCode": 0,
                },
                "Created": "2024-01-01T00:00:00Z",
                "NetworkSettings": {"Ports": {}},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(
                stdout=json.dumps(inspect_data).encode()
            ),
        ):
            manager = DockerContainerManager()
            info = manager.inspect("test-container")

            assert isinstance(info, ContainerInfo)
            assert info.id == "abc123def456"
            assert info.name == "test-container"
            assert info.image == "alpine:latest"
            assert info.labels == {"app": "test"}

    def test_inspect_not_found(self):
        """Test inspecting non-existent container raises ContainerNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container: test-container"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerNotFoundError):
                manager.inspect("test-container")

    def test_list_success(self, mock_docker_command):
        """Test listing containers successfully."""
        containers_output = "\n".join(
            [
                json.dumps(
                    {
                        "ID": "abc123",
                        "Names": "container1",
                        "Image": "alpine:latest",
                        "State": "running",
                        "Status": "Up 5 minutes",
                        "CreatedAt": "2024-01-01",
                    }
                ),
                json.dumps(
                    {
                        "ID": "def456",
                        "Names": "container2",
                        "Image": "ubuntu:22.04",
                        "State": "exited",
                        "Status": "Exited (0)",
                        "CreatedAt": "2024-01-02",
                    }
                ),
            ]
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(
                stdout=containers_output.encode()
            ),
        ):
            manager = DockerContainerManager()
            containers = manager.list()

            assert len(containers) == 2
            assert all(isinstance(c, ContainerInfo) for c in containers)

    def test_list_empty(self, mock_docker_command):
        """Test listing containers when none exist."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(stdout=b""),
        ):
            manager = DockerContainerManager()
            containers = manager.list()

            assert containers == []

    def test_list_with_all(self, mock_docker_command):
        """Test listing all containers including stopped ones."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"")

            manager = DockerContainerManager()
            manager.list(all=True)

            # Verify --all is in command
            call_args = mock_run.call_args[0][0]
            assert "--all" in call_args

    def test_list_with_filters(self, mock_docker_command):
        """Test listing containers with filters."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"")

            manager = DockerContainerManager()
            manager.list(filters={"status": "running"})

            # Verify filter is in command
            call_args = mock_run.call_args[0][0]
            assert "--filter" in call_args
            assert "status=running" in call_args

    def test_logs_success(self, mock_docker_command):
        """Test getting container logs."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(stdout=b"Container log output"),
        ):
            manager = DockerContainerManager()
            logs = manager.logs("test-container")

            assert logs == "Container log output"

    def test_logs_with_tail(self, mock_docker_command):
        """Test getting container logs with tail parameter."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Last 10 lines"
            )

            manager = DockerContainerManager()
            manager.logs("test-container", tail=10)

            # Verify --tail is in command
            call_args = mock_run.call_args[0][0]
            assert "--tail" in call_args
            assert "10" in call_args

    def test_logs_not_found(self):
        """Test getting logs for non-existent container raises ContainerNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container: test-container"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerNotFoundError):
                manager.logs("test-container")

    def test_exec_success(self, mock_docker_command):
        """Test executing command in container."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(stdout=b"Command output"),
        ):
            manager = DockerContainerManager()
            exit_code, output = manager.exec(
                "test-container", ["echo", "hello"]
            )

            assert exit_code == 0
            assert output == "Command output"

    def test_exec_not_found(self):
        """Test exec on non-existent container raises ContainerNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            side_effect=Exception("No such container: test-container"),
        ):
            manager = DockerContainerManager()
            with pytest.raises(ContainerNotFoundError):
                manager.exec("test-container", ["echo", "hello"])

    def test_prune_success(self, mock_docker_command):
        """Test pruning stopped containers."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command",
            return_value=mock_docker_command(
                stdout=b"Total reclaimed space: 1GB"
            ),
        ):
            manager = DockerContainerManager()
            result = manager.prune()

            assert "deleted" in result

    def test_run_calls_correct_command(self, sample_run_config):
        """Test that run() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(sample_run_config)

            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "docker"
            assert call_args[1] == "run"

    def test_start_calls_correct_command(self):
        """Test that start() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerContainerManager()
            manager.start("test-container")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "start", "test-container"]

    def test_stop_calls_correct_command(self):
        """Test that stop() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerContainerManager()
            manager.stop("test-container", timeout=10)

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "stop",
                "--time",
                "10",
                "test-container",
            ]

    def test_restart_calls_correct_command(self):
        """Test that restart() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerContainerManager()
            manager.restart("test-container", timeout=10)

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "restart",
                "--time",
                "10",
                "test-container",
            ]

    def test_remove_calls_correct_command(self):
        """Test that remove() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerContainerManager()
            manager.remove("test-container")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "rm", "test-container"]

    def test_inspect_calls_correct_command(self):
        """Test that inspect() calls correct docker command."""
        inspect_data = [
            {
                "Id": "abc123",
                "Name": "/test-container",
                "Config": {"Image": "alpine:latest", "Labels": {}},
                "State": {"Status": "running", "ExitCode": 0},
                "Created": "2024-01-01T00:00:00Z",
                "NetworkSettings": {"Ports": {}},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(
                stdout=json.dumps(inspect_data).encode()
            )

            manager = DockerContainerManager()
            manager.inspect("test-container")

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "container",
                "inspect",
                "test-container",
            ]

    def test_list_calls_correct_command(self):
        """Test that list() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerContainerManager()
            manager.list()

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "ps", "--format", "{{json .}}"]

    def test_run_with_user(self, mock_docker_command):
        """Test running container with custom user."""
        config = RunConfig(
            image="alpine:latest",
            user="1000:1000",
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --user is in command
            call_args = mock_run.call_args[0][0]
            assert "--user" in call_args
            assert "1000:1000" in call_args

    def test_run_with_working_dir(self, mock_docker_command):
        """Test running container with custom working directory."""
        config = RunConfig(
            image="alpine:latest",
            working_dir="/app",
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --workdir is in command
            call_args = mock_run.call_args[0][0]
            assert "--workdir" in call_args
            assert "/app" in call_args

    def test_run_with_hostname(self, mock_docker_command):
        """Test running container with custom hostname."""
        config = RunConfig(
            image="alpine:latest",
            hostname="my-host",
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --hostname is in command
            call_args = mock_run.call_args[0][0]
            assert "--hostname" in call_args
            assert "my-host" in call_args

    def test_run_with_labels(self, mock_docker_command):
        """Test running container with labels."""
        config = RunConfig(
            image="alpine:latest",
            labels={"app": "test", "version": "1.0"},
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.container.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"abc123")

            manager = DockerContainerManager()
            manager.run(config)

            # Verify --label is in command
            call_args = mock_run.call_args[0][0]
            assert any(arg.startswith("--label") for arg in call_args)
