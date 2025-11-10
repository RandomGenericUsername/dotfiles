"""Tests for container management types."""

from pathlib import Path

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


class TestVolumeMount:
    """Tests for VolumeMount dataclass."""

    def test_create_basic(self):
        """Test creating basic volume mount."""
        mount = VolumeMount(source="/host", target="/container")
        assert mount.source == "/host"
        assert mount.target == "/container"
        assert mount.read_only is False
        assert mount.type == "bind"

    def test_create_with_path(self):
        """Test creating volume mount with Path objects."""
        mount = VolumeMount(source=Path("/host"), target=Path("/container"))
        assert mount.source == Path("/host")
        assert mount.target == Path("/container")

    def test_create_read_only(self):
        """Test creating read-only volume mount."""
        mount = VolumeMount(
            source="/host", target="/container", read_only=True
        )
        assert mount.read_only is True

    def test_create_volume_type(self):
        """Test creating volume mount with volume type."""
        mount = VolumeMount(
            source="my-volume", target="/container", type="volume"
        )
        assert mount.type == "volume"

    def test_create_tmpfs_type(self):
        """Test creating tmpfs volume mount."""
        mount = VolumeMount(source="", target="/tmp", type="tmpfs")
        assert mount.type == "tmpfs"


class TestPortMapping:
    """Tests for PortMapping dataclass."""

    def test_create_basic(self):
        """Test creating basic port mapping."""
        port = PortMapping(container_port=8080)
        assert port.container_port == 8080
        assert port.host_port is None
        assert port.protocol == "tcp"
        assert port.host_ip == "0.0.0.0"

    def test_create_with_host_port(self):
        """Test creating port mapping with host port."""
        port = PortMapping(container_port=8080, host_port=80)
        assert port.container_port == 8080
        assert port.host_port == 80

    def test_create_udp_protocol(self):
        """Test creating UDP port mapping."""
        port = PortMapping(container_port=53, protocol="udp")
        assert port.protocol == "udp"

    def test_create_custom_host_ip(self):
        """Test creating port mapping with custom host IP."""
        port = PortMapping(container_port=8080, host_ip="127.0.0.1")
        assert port.host_ip == "127.0.0.1"


class TestBuildContext:
    """Tests for BuildContext dataclass."""

    def test_create_basic(self):
        """Test creating basic build context."""
        context = BuildContext(dockerfile="FROM alpine")
        assert context.dockerfile == "FROM alpine"
        assert context.files == {}
        assert context.build_args == {}
        assert context.labels == {}
        assert context.target is None
        assert context.network is None
        assert context.no_cache is False
        assert context.pull is False
        assert context.rm is True

    def test_create_with_files(self):
        """Test creating build context with files."""
        files = {"app.py": b"print('hello')"}
        context = BuildContext(dockerfile="FROM alpine", files=files)
        assert context.files == files

    def test_create_with_build_args(self):
        """Test creating build context with build args."""
        build_args = {"VERSION": "1.0", "ENV": "prod"}
        context = BuildContext(dockerfile="FROM alpine", build_args=build_args)
        assert context.build_args == build_args

    def test_create_with_labels(self):
        """Test creating build context with labels."""
        labels = {"app": "myapp", "version": "1.0"}
        context = BuildContext(dockerfile="FROM alpine", labels=labels)
        assert context.labels == labels

    def test_create_with_target(self):
        """Test creating build context with target."""
        context = BuildContext(dockerfile="FROM alpine", target="production")
        assert context.target == "production"

    def test_create_with_network(self):
        """Test creating build context with network."""
        context = BuildContext(dockerfile="FROM alpine", network="host")
        assert context.network == "host"

    def test_create_no_cache(self):
        """Test creating build context with no cache."""
        context = BuildContext(dockerfile="FROM alpine", no_cache=True)
        assert context.no_cache is True

    def test_create_pull(self):
        """Test creating build context with pull."""
        context = BuildContext(dockerfile="FROM alpine", pull=True)
        assert context.pull is True

    def test_create_no_rm(self):
        """Test creating build context without rm."""
        context = BuildContext(dockerfile="FROM alpine", rm=False)
        assert context.rm is False


class TestRunConfig:
    """Tests for RunConfig dataclass."""

    def test_create_basic(self):
        """Test creating basic run config."""
        config = RunConfig(image="alpine:latest")
        assert config.image == "alpine:latest"
        assert config.name is None
        assert config.command is None
        assert config.entrypoint is None
        assert config.environment == {}
        assert config.volumes == []
        assert config.ports == []
        assert config.network == NetworkMode.BRIDGE
        assert config.restart_policy == RestartPolicy.NO
        assert config.detach is True
        assert config.remove is False
        assert config.privileged is False

    def test_create_with_name(self):
        """Test creating run config with name."""
        config = RunConfig(image="alpine:latest", name="my-container")
        assert config.name == "my-container"

    def test_create_with_command(self):
        """Test creating run config with command."""
        config = RunConfig(image="alpine:latest", command=["echo", "hello"])
        assert config.command == ["echo", "hello"]

    def test_create_with_entrypoint(self):
        """Test creating run config with entrypoint."""
        config = RunConfig(image="alpine:latest", entrypoint=["/bin/sh", "-c"])
        assert config.entrypoint == ["/bin/sh", "-c"]

    def test_create_with_environment(self):
        """Test creating run config with environment."""
        env = {"VAR1": "value1", "VAR2": "value2"}
        config = RunConfig(image="alpine:latest", environment=env)
        assert config.environment == env

    def test_create_with_volumes(self):
        """Test creating run config with volumes."""
        volumes = [VolumeMount(source="/host", target="/container")]
        config = RunConfig(image="alpine:latest", volumes=volumes)
        assert config.volumes == volumes

    def test_create_with_ports(self):
        """Test creating run config with ports."""
        ports = [PortMapping(container_port=8080, host_port=80)]
        config = RunConfig(image="alpine:latest", ports=ports)
        assert config.ports == ports

    def test_create_with_network_mode(self):
        """Test creating run config with network mode."""
        config = RunConfig(image="alpine:latest", network=NetworkMode.HOST)
        assert config.network == NetworkMode.HOST

    def test_create_with_restart_policy(self):
        """Test creating run config with restart policy."""
        config = RunConfig(
            image="alpine:latest", restart_policy=RestartPolicy.ALWAYS
        )
        assert config.restart_policy == RestartPolicy.ALWAYS

    def test_create_detach_false(self):
        """Test creating run config with detach false."""
        config = RunConfig(image="alpine:latest", detach=False)
        assert config.detach is False

    def test_create_remove_true(self):
        """Test creating run config with remove true."""
        config = RunConfig(image="alpine:latest", remove=True)
        assert config.remove is True

    def test_create_privileged(self):
        """Test creating run config with privileged."""
        config = RunConfig(image="alpine:latest", privileged=True)
        assert config.privileged is True


class TestImageInfo:
    """Tests for ImageInfo dataclass."""

    def test_create_basic(self):
        """Test creating basic image info."""
        info = ImageInfo(
            id="sha256:abc123",
            tags=["alpine:latest"],
            size=5242880,
            created="2024-01-01T00:00:00Z",
        )
        assert info.id == "sha256:abc123"
        assert info.tags == ["alpine:latest"]
        assert info.size == 5242880
        assert info.created == "2024-01-01T00:00:00Z"

    def test_create_with_labels(self):
        """Test creating image info with labels."""
        labels = {"maintainer": "test@example.com"}
        info = ImageInfo(
            id="sha256:abc123",
            tags=["alpine:latest"],
            size=5242880,
            created="2024-01-01T00:00:00Z",
            labels=labels,
        )
        assert info.labels == labels


class TestContainerInfo:
    """Tests for ContainerInfo dataclass."""

    def test_create_basic(self):
        """Test creating basic container info."""
        info = ContainerInfo(
            id="container123",
            name="test-container",
            image="alpine:latest",
            state=ContainerState.RUNNING,
            status="Up 5 minutes",
            created="2024-01-01T00:00:00Z",
        )
        assert info.id == "container123"
        assert info.name == "test-container"
        assert info.image == "alpine:latest"
        assert info.state == ContainerState.RUNNING
        assert info.status == "Up 5 minutes"
        assert info.created == "2024-01-01T00:00:00Z"


class TestVolumeInfo:
    """Tests for VolumeInfo dataclass."""

    def test_create_basic(self):
        """Test creating basic volume info."""
        info = VolumeInfo(
            name="test-volume",
            driver="local",
            mountpoint="/var/lib/docker/volumes/test-volume/_data",
        )
        assert info.name == "test-volume"
        assert info.driver == "local"
        assert info.mountpoint == "/var/lib/docker/volumes/test-volume/_data"


class TestNetworkInfo:
    """Tests for NetworkInfo dataclass."""

    def test_create_basic(self):
        """Test creating basic network info."""
        info = NetworkInfo(
            id="network123",
            name="test-network",
            driver="bridge",
            scope="local",
        )
        assert info.id == "network123"
        assert info.name == "test-network"
        assert info.driver == "bridge"
        assert info.scope == "local"
