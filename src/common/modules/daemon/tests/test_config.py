"""Tests for daemon configuration."""

from pathlib import Path

import pytest

from dotfiles_daemon.config import DaemonConfig


def test_default_config():
    """Test default configuration."""
    config = DaemonConfig()

    assert config.socket_dir == Path.home() / ".cache" / "dotfiles" / "sockets"
    assert config.command_socket_name == "command.sock"
    assert config.query_socket_name == "query.sock"
    assert config.event_socket_suffix == "_events.sock"


def test_custom_socket_dir():
    """Test custom socket directory."""
    custom_dir = Path("/tmp/test-sockets")
    config = DaemonConfig(socket_dir=custom_dir)

    assert config.socket_dir == custom_dir


def test_get_command_socket_path():
    """Test getting command socket path."""
    config = DaemonConfig(socket_dir=Path("/tmp/sockets"))
    path = config.get_command_socket_path()

    assert path == Path("/tmp/sockets/command.sock")


def test_get_query_socket_path():
    """Test getting query socket path."""
    config = DaemonConfig(socket_dir=Path("/tmp/sockets"))
    path = config.get_query_socket_path()

    assert path == Path("/tmp/sockets/query.sock")


def test_get_event_socket_path():
    """Test getting event socket path."""
    config = DaemonConfig(socket_dir=Path("/tmp/sockets"))
    path = config.get_event_socket_path("wallpaper")

    assert path == Path("/tmp/sockets/wallpaper_events.sock")


def test_ensure_socket_dir(tmp_path):
    """Test ensuring socket directory exists."""
    socket_dir = tmp_path / "test-sockets"
    config = DaemonConfig(socket_dir=socket_dir)

    assert not socket_dir.exists()

    config.ensure_socket_dir()

    assert socket_dir.exists()
    assert socket_dir.is_dir()


def test_model_dump():
    """Test model dump converts Path to str."""
    config = DaemonConfig(socket_dir=Path("/tmp/sockets"))
    data = config.model_dump()

    assert isinstance(data["socket_dir"], str)
    assert data["socket_dir"] == "/tmp/sockets"

