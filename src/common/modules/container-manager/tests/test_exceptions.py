"""Tests for container management exceptions."""


from dotfiles_container_manager.core import (
    ContainerError,
    ContainerNotFoundError,
    ContainerRuntimeError,
    ImageBuildError,
    ImageError,
    ImageNotFoundError,
    InvalidConfigError,
    NetworkError,
    NetworkNotFoundError,
    RuntimeNotAvailableError,
    VolumeError,
    VolumeNotFoundError,
)


class TestContainerError:
    """Tests for ContainerError exception."""

    def test_create_basic(self):
        """Test creating basic container error."""
        error = ContainerError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.command is None
        assert error.exit_code is None
        assert error.stderr is None
        assert str(error) == "Something went wrong"

    def test_create_with_command(self):
        """Test creating container error with command."""
        error = ContainerError(
            "Command failed", command=["docker", "run", "alpine"]
        )
        assert error.command == ["docker", "run", "alpine"]
        assert "Command: docker run alpine" in str(error)

    def test_create_with_exit_code(self):
        """Test creating container error with exit code."""
        error = ContainerError("Command failed", exit_code=1)
        assert error.exit_code == 1
        assert "Exit code: 1" in str(error)

    def test_create_with_stderr(self):
        """Test creating container error with stderr."""
        error = ContainerError("Command failed", stderr="Error output")
        assert error.stderr == "Error output"
        assert "Error output: Error output" in str(error)

    def test_create_with_all_fields(self):
        """Test creating container error with all fields."""
        error = ContainerError(
            "Command failed",
            command=["docker", "run"],
            exit_code=1,
            stderr="Error",
        )
        assert "Command failed" in str(error)
        assert "Command: docker run" in str(error)
        assert "Exit code: 1" in str(error)
        assert "Error output: Error" in str(error)


class TestImageError:
    """Tests for ImageError exception."""

    def test_create_basic(self):
        """Test creating basic image error."""
        error = ImageError("Image operation failed")
        assert error.message == "Image operation failed"
        assert isinstance(error, ContainerError)

    def test_create_with_command(self):
        """Test creating image error with command."""
        error = ImageError("Build failed", command=["docker", "build", "."])
        assert "Command: docker build ." in str(error)


class TestImageNotFoundError:
    """Tests for ImageNotFoundError exception."""

    def test_create(self):
        """Test creating image not found error."""
        error = ImageNotFoundError("alpine:nonexistent")
        assert error.image_name == "alpine:nonexistent"
        assert "Image not found: alpine:nonexistent" in str(error)
        assert isinstance(error, ImageError)


class TestImageBuildError:
    """Tests for ImageBuildError exception."""

    def test_create(self):
        """Test creating image build error."""
        error = ImageBuildError("Build failed")
        assert error.message == "Build failed"
        assert isinstance(error, ImageError)


class TestContainerRuntimeError:
    """Tests for ContainerRuntimeError exception."""

    def test_create(self):
        """Test creating container runtime error."""
        error = ContainerRuntimeError("Runtime operation failed")
        assert error.message == "Runtime operation failed"
        assert isinstance(error, ContainerError)


class TestContainerNotFoundError:
    """Tests for ContainerNotFoundError exception."""

    def test_create(self):
        """Test creating container not found error."""
        error = ContainerNotFoundError("container123")
        assert error.container_id == "container123"
        assert "Container not found: container123" in str(error)
        assert isinstance(error, ContainerRuntimeError)


class TestVolumeError:
    """Tests for VolumeError exception."""

    def test_create(self):
        """Test creating volume error."""
        error = VolumeError("Volume operation failed")
        assert error.message == "Volume operation failed"
        assert isinstance(error, ContainerError)


class TestVolumeNotFoundError:
    """Tests for VolumeNotFoundError exception."""

    def test_create(self):
        """Test creating volume not found error."""
        error = VolumeNotFoundError("my-volume")
        assert error.volume_name == "my-volume"
        assert "Volume not found: my-volume" in str(error)
        assert isinstance(error, VolumeError)


class TestNetworkError:
    """Tests for NetworkError exception."""

    def test_create(self):
        """Test creating network error."""
        error = NetworkError("Network operation failed")
        assert error.message == "Network operation failed"
        assert isinstance(error, ContainerError)


class TestNetworkNotFoundError:
    """Tests for NetworkNotFoundError exception."""

    def test_create(self):
        """Test creating network not found error."""
        error = NetworkNotFoundError("my-network")
        assert error.network_name == "my-network"
        assert "Network not found: my-network" in str(error)
        assert isinstance(error, NetworkError)


class TestRuntimeNotAvailableError:
    """Tests for RuntimeNotAvailableError exception."""

    def test_create(self):
        """Test creating runtime not available error."""
        error = RuntimeNotAvailableError("docker")
        assert error.runtime == "docker"
        assert "Container runtime 'docker' is not available" in str(error)
        assert "Please ensure it is installed and running" in str(error)
        assert isinstance(error, ContainerError)


class TestInvalidConfigError:
    """Tests for InvalidConfigError exception."""

    def test_create(self):
        """Test creating invalid config error."""
        error = InvalidConfigError("Invalid configuration")
        assert error.message == "Invalid configuration"
        assert isinstance(error, ContainerError)
