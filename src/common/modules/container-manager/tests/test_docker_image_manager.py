"""Tests for DockerImageManager."""

import json
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_container_manager.core import (
    BuildContext,
    ImageBuildError,
    ImageError,
    ImageInfo,
    ImageNotFoundError,
)
from dotfiles_container_manager.implementations.docker import (
    DockerImageManager,
)


class TestDockerImageManager:
    """Tests for DockerImageManager."""

    def test_init_default_command(self):
        """Test initialization with default command."""
        manager = DockerImageManager()
        assert manager.command == "docker"

    def test_init_custom_command(self):
        """Test initialization with custom command."""
        manager = DockerImageManager(command="podman")
        assert manager.command == "podman"

    def test_build_basic(self, sample_build_context, mock_docker_command):
        """Test building an image with basic BuildContext."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123\nSuccessfully tagged test:latest"
            )

            manager = DockerImageManager()
            image_id = manager.build(sample_build_context, "test:latest")

            assert image_id == "abc123"
            mock_run.assert_called()

    def test_build_with_build_args(self, mock_docker_command):
        """Test building with build arguments."""
        context = BuildContext(
            dockerfile="FROM alpine:latest",
            build_args={"VERSION": "1.0", "ENV": "prod"},
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(context, "test:latest")

            # Verify build args are in command
            call_args = mock_run.call_args[0][0]
            assert any(arg.startswith("--build-arg") for arg in call_args)
            assert any("VERSION=1.0" in arg for arg in call_args)
            assert any("ENV=prod" in arg for arg in call_args)

    def test_build_with_labels(self, mock_docker_command):
        """Test building with labels."""
        context = BuildContext(
            dockerfile="FROM alpine:latest",
            labels={"app": "test", "version": "1.0"},
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(context, "test:latest")

            # Verify labels are in command
            call_args = mock_run.call_args[0][0]
            assert any(arg.startswith("--label") for arg in call_args)

    def test_build_with_target(self, mock_docker_command):
        """Test building with target for multi-stage builds."""
        context = BuildContext(
            dockerfile="FROM alpine:latest AS builder\nFROM alpine:latest",
            target="builder",
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(context, "test:latest")

            # Verify target is in command
            call_args = mock_run.call_args[0][0]
            assert "--target" in call_args
            assert "builder" in call_args

    def test_build_with_no_cache(self, mock_docker_command):
        """Test building with no_cache=True."""
        context = BuildContext(
            dockerfile="FROM alpine:latest",
            no_cache=True,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(context, "test:latest")

            # Verify --no-cache is in command
            call_args = mock_run.call_args[0][0]
            assert "--no-cache" in call_args

    def test_build_with_pull(self, mock_docker_command):
        """Test building with pull=True."""
        context = BuildContext(
            dockerfile="FROM alpine:latest",
            pull=True,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(context, "test:latest")

            # Verify --pull is in command
            call_args = mock_run.call_args[0][0]
            assert "--pull" in call_args

    def test_build_failure(self, sample_build_context):
        """Test build failure raises ImageBuildError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("Build failed"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageBuildError) as exc_info:
                manager.build(sample_build_context, "test:latest")

            assert "Failed to build image" in str(exc_info.value)

    def test_pull_success(self, mock_docker_command):
        """Test pulling an image successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"sha256:abc123"
            )

            manager = DockerImageManager()
            image_id = manager.pull("alpine:latest")

            assert image_id is not None
            # Verify pull command was called
            call_args = mock_run.call_args_list[0][0][0]
            assert call_args == ["docker", "pull", "alpine:latest"]

    def test_pull_failure(self):
        """Test pull failure raises ImageError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("Pull failed"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageError) as exc_info:
                manager.pull("nonexistent:latest")

            assert "Failed to pull image" in str(exc_info.value)

    def test_push_success(self, mock_docker_command):
        """Test pushing an image successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(
                stdout=b"The push refers to repository"
            ),
        ):
            manager = DockerImageManager()
            # Should not raise
            manager.push("myrepo/myimage:latest")

    def test_push_failure(self):
        """Test push failure raises ImageError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("Push failed"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageError) as exc_info:
                manager.push("myrepo/myimage:latest")

            assert "Failed to push image" in str(exc_info.value)

    def test_tag_success(self, mock_docker_command):
        """Test tagging an image successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerImageManager()
            # Should not raise
            manager.tag("alpine:latest", "myalpine:v1")

    def test_tag_failure(self):
        """Test tag failure raises ImageError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("Tag failed"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageError) as exc_info:
                manager.tag("nonexistent:latest", "newtag:latest")

            assert "Failed to tag image" in str(exc_info.value)

    def test_remove_success(self, mock_docker_command):
        """Test removing an image successfully."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerImageManager()
            # Should not raise
            manager.remove("alpine:latest")

    def test_remove_not_found(self):
        """Test removing non-existent image raises ImageNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("No such image: nonexistent"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageNotFoundError):
                manager.remove("nonexistent:latest")

    def test_remove_with_force(self, mock_docker_command):
        """Test removing image with force=True."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command()

            manager = DockerImageManager()
            manager.remove("alpine:latest", force=True)

            # Verify --force is in command
            call_args = mock_run.call_args[0][0]
            assert "--force" in call_args

    def test_exists_true(self, mock_docker_command):
        """Test exists() returns True for existing image."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(),
        ):
            manager = DockerImageManager()
            assert manager.exists("alpine:latest") is True

    def test_exists_false(self):
        """Test exists() returns False for non-existent image."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("No such image"),
        ):
            manager = DockerImageManager()
            assert manager.exists("nonexistent:latest") is False

    def test_inspect_success(self, mock_docker_command):
        """Test inspecting an image successfully."""
        inspect_data = [
            {
                "Id": "sha256:abc123def456",
                "RepoTags": ["alpine:latest"],
                "Size": 5242880,
                "Created": "2024-01-01T00:00:00Z",
                "Config": {"Labels": {"maintainer": "test"}},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(
                stdout=json.dumps(inspect_data).encode()
            ),
        ):
            manager = DockerImageManager()
            info = manager.inspect("alpine:latest")

            assert isinstance(info, ImageInfo)
            assert info.id == "abc123def456"
            assert "alpine:latest" in info.tags
            assert info.size == 5242880
            assert info.labels == {"maintainer": "test"}

    def test_inspect_not_found(self):
        """Test inspecting non-existent image raises ImageNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("No such image: nonexistent"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageNotFoundError):
                manager.inspect("nonexistent:latest")

    def test_list_success(self, mock_docker_command):
        """Test listing images successfully."""
        images_output = "\n".join(
            [
                json.dumps(
                    {
                        "ID": "abc123",
                        "Repository": "alpine",
                        "Tag": "latest",
                        "Size": "5MB",
                        "CreatedAt": "2024-01-01",
                    }
                ),
                json.dumps(
                    {
                        "ID": "def456",
                        "Repository": "ubuntu",
                        "Tag": "22.04",
                        "Size": "77MB",
                        "CreatedAt": "2024-01-02",
                    }
                ),
            ]
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(stdout=images_output.encode()),
        ):
            manager = DockerImageManager()
            images = manager.list()

            assert len(images) == 2
            assert all(isinstance(img, ImageInfo) for img in images)
            assert images[0].id == "abc123"
            assert images[1].id == "def456"

    def test_list_empty(self, mock_docker_command):
        """Test listing images when none exist."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(stdout=b""),
        ):
            manager = DockerImageManager()
            images = manager.list()

            assert images == []

    def test_list_with_filters(self, mock_docker_command):
        """Test listing images with filters."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(stdout=b"")

            manager = DockerImageManager()
            manager.list(filters={"reference": "alpine:*"})

            # Verify filter is in command
            call_args = mock_run.call_args[0][0]
            assert "--filter" in call_args
            assert "reference=alpine:*" in call_args

    def test_prune_success(self, mock_docker_command):
        """Test pruning unused images."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=mock_docker_command(
                stdout=b"Total reclaimed space: 1.5GB"
            ),
        ):
            manager = DockerImageManager()
            result = manager.prune()

            assert "deleted" in result
            assert "space_reclaimed" in result
            assert result["space_reclaimed"] > 0

    def test_prune_with_all(self, mock_docker_command):
        """Test pruning all unused images."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Total reclaimed space: 2GB"
            )

            manager = DockerImageManager()
            manager.prune(all=True)

            # Verify --all is in command
            call_args = mock_run.call_args[0][0]
            assert "--all" in call_args

    def test_prune_failure(self):
        """Test prune failure raises ImageError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("Prune failed"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageError) as exc_info:
                manager.prune()

            assert "Failed to prune images" in str(exc_info.value)

    def test_build_calls_correct_command(self, sample_build_context):
        """Test that build() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(sample_build_context, "test:latest")

            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "docker"
            assert call_args[1] == "build"
            assert "-t" in call_args
            assert "test:latest" in call_args

    def test_pull_calls_correct_command(self):
        """Test that pull() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"sha256:abc123")

            manager = DockerImageManager()
            manager.pull("alpine:latest")

            # First call is pull, second is inspect to get ID
            call_args = mock_run.call_args_list[0][0][0]
            assert call_args == ["docker", "pull", "alpine:latest"]

    def test_push_calls_correct_command(self):
        """Test that push() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerImageManager()
            manager.push("myrepo/myimage:latest")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "push", "myrepo/myimage:latest"]

    def test_tag_calls_correct_command(self):
        """Test that tag() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerImageManager()
            manager.tag("alpine:latest", "myalpine:v1")

            call_args = mock_run.call_args[0][0]
            assert call_args == [
                "docker",
                "tag",
                "alpine:latest",
                "myalpine:v1",
            ]

    def test_remove_calls_correct_command(self):
        """Test that remove() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerImageManager()
            manager.remove("alpine:latest")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "rmi", "alpine:latest"]

    def test_inspect_calls_correct_command(self):
        """Test that inspect() calls correct docker command."""
        inspect_data = [
            {
                "Id": "sha256:abc123",
                "RepoTags": ["alpine:latest"],
                "Size": 5242880,
                "Created": "2024-01-01T00:00:00Z",
                "Config": {"Labels": {}},
            }
        ]

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(
                stdout=json.dumps(inspect_data).encode()
            )

            manager = DockerImageManager()
            manager.inspect("alpine:latest")

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "image", "inspect", "alpine:latest"]

    def test_list_calls_correct_command(self):
        """Test that list() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout=b"")

            manager = DockerImageManager()
            manager.list()

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "images", "--format", "{{json .}}"]

    def test_prune_calls_correct_command(self):
        """Test that prune() calls correct docker command."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = MagicMock(
                stdout=b"Total reclaimed space: 0B"
            )

            manager = DockerImageManager()
            manager.prune()

            call_args = mock_run.call_args[0][0]
            assert call_args == ["docker", "image", "prune", "--force"]

    def test_build_with_network(self, mock_docker_command):
        """Test building with custom network."""
        context = BuildContext(
            dockerfile="FROM alpine:latest",
            network="host",
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(context, "test:latest")

            # Verify --network is in command
            call_args = mock_run.call_args[0][0]
            assert "--network" in call_args
            assert "host" in call_args

    def test_build_with_rm_false(self, mock_docker_command):
        """Test building with rm=False."""
        context = BuildContext(
            dockerfile="FROM alpine:latest",
            rm=False,
        )

        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command"
        ) as mock_run:
            mock_run.return_value = mock_docker_command(
                stdout=b"Successfully built abc123"
            )

            manager = DockerImageManager()
            manager.build(context, "test:latest")

            # Verify --rm=false is in command
            call_args = mock_run.call_args[0][0]
            assert "--rm=false" in call_args

    def test_inspect_empty_data(self):
        """Test inspect with empty data raises ImageNotFoundError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=MagicMock(stdout=b"[]"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageNotFoundError):
                manager.inspect("nonexistent:latest")

    def test_inspect_json_decode_error(self):
        """Test inspect with invalid JSON raises ImageError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            return_value=MagicMock(stdout=b"invalid json"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageError) as exc_info:
                manager.inspect("alpine:latest")

            assert "Failed to parse image info" in str(exc_info.value)

    def test_list_failure(self):
        """Test list failure raises ImageError."""
        with patch(
            "dotfiles_container_manager.implementations.docker.image.run_docker_command",
            side_effect=Exception("List failed"),
        ):
            manager = DockerImageManager()
            with pytest.raises(ImageError) as exc_info:
                manager.list()

            assert "Failed to list images" in str(exc_info.value)
