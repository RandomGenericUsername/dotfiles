"""Tests for container management enums."""


from dotfiles_container_manager.core import (
    ContainerRuntime,
    ContainerState,
    LogDriver,
    NetworkMode,
    RestartPolicy,
    VolumeDriver,
)


class TestContainerRuntime:
    """Tests for ContainerRuntime enum."""

    def test_docker_value(self):
        """Test Docker runtime value."""
        assert ContainerRuntime.DOCKER.value == "docker"

    def test_podman_value(self):
        """Test Podman runtime value."""
        assert ContainerRuntime.PODMAN.value == "podman"

    def test_all_runtimes(self):
        """Test all runtime values are present."""
        runtimes = [r.value for r in ContainerRuntime]
        assert "docker" in runtimes
        assert "podman" in runtimes


class TestContainerState:
    """Tests for ContainerState enum."""

    def test_created_value(self):
        """Test created state value."""
        assert ContainerState.CREATED.value == "created"

    def test_running_value(self):
        """Test running state value."""
        assert ContainerState.RUNNING.value == "running"

    def test_paused_value(self):
        """Test paused state value."""
        assert ContainerState.PAUSED.value == "paused"

    def test_restarting_value(self):
        """Test restarting state value."""
        assert ContainerState.RESTARTING.value == "restarting"

    def test_removing_value(self):
        """Test removing state value."""
        assert ContainerState.REMOVING.value == "removing"

    def test_exited_value(self):
        """Test exited state value."""
        assert ContainerState.EXITED.value == "exited"

    def test_dead_value(self):
        """Test dead state value."""
        assert ContainerState.DEAD.value == "dead"

    def test_all_states(self):
        """Test all state values are present."""
        states = [s.value for s in ContainerState]
        assert len(states) == 7


class TestRestartPolicy:
    """Tests for RestartPolicy enum."""

    def test_no_value(self):
        """Test no restart policy value."""
        assert RestartPolicy.NO.value == "no"

    def test_on_failure_value(self):
        """Test on-failure restart policy value."""
        assert RestartPolicy.ON_FAILURE.value == "on-failure"

    def test_always_value(self):
        """Test always restart policy value."""
        assert RestartPolicy.ALWAYS.value == "always"

    def test_unless_stopped_value(self):
        """Test unless-stopped restart policy value."""
        assert RestartPolicy.UNLESS_STOPPED.value == "unless-stopped"

    def test_all_policies(self):
        """Test all restart policy values are present."""
        policies = [p.value for p in RestartPolicy]
        assert len(policies) == 4


class TestNetworkMode:
    """Tests for NetworkMode enum."""

    def test_bridge_value(self):
        """Test bridge network mode value."""
        assert NetworkMode.BRIDGE.value == "bridge"

    def test_host_value(self):
        """Test host network mode value."""
        assert NetworkMode.HOST.value == "host"

    def test_none_value(self):
        """Test none network mode value."""
        assert NetworkMode.NONE.value == "none"

    def test_container_value(self):
        """Test container network mode value."""
        assert NetworkMode.CONTAINER.value == "container"

    def test_all_modes(self):
        """Test all network mode values are present."""
        modes = [m.value for m in NetworkMode]
        assert len(modes) == 4


class TestVolumeDriver:
    """Tests for VolumeDriver enum."""

    def test_local_value(self):
        """Test local volume driver value."""
        assert VolumeDriver.LOCAL.value == "local"

    def test_nfs_value(self):
        """Test NFS volume driver value."""
        assert VolumeDriver.NFS.value == "nfs"

    def test_tmpfs_value(self):
        """Test tmpfs volume driver value."""
        assert VolumeDriver.TMPFS.value == "tmpfs"

    def test_all_drivers(self):
        """Test all volume driver values are present."""
        drivers = [d.value for d in VolumeDriver]
        assert len(drivers) == 3


class TestLogDriver:
    """Tests for LogDriver enum."""

    def test_json_file_value(self):
        """Test json-file log driver value."""
        assert LogDriver.JSON_FILE.value == "json-file"

    def test_syslog_value(self):
        """Test syslog log driver value."""
        assert LogDriver.SYSLOG.value == "syslog"

    def test_journald_value(self):
        """Test journald log driver value."""
        assert LogDriver.JOURNALD.value == "journald"

    def test_none_value(self):
        """Test none log driver value."""
        assert LogDriver.NONE.value == "none"

    def test_all_drivers(self):
        """Test all log driver values are present."""
        drivers = [d.value for d in LogDriver]
        assert len(drivers) == 4
