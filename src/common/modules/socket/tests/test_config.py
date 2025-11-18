"""Tests for configuration system."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from dotfiles_socket.config import (
    AppConfig,
    SocketConfig,
    SocketModuleConfig,
    TcpSocketConfig,
    UnixSocketConfig,
    get_default_config,
    get_generic_socket_config,
    get_socket_config,
    get_tcp_socket_config,
    get_unix_socket_config,
)


class TestSocketConfig:
    """Tests for SocketConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = SocketConfig()

        assert config.socket_dir == Path("/tmp/sockets")
        assert config.default_timeout == 5
        assert config.buffer_size == 4096
        assert config.timezone == "UTC"
        assert config.message_queue_size == 100
        assert config.blocking_mode is False
        assert config.allow_client_send is True

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = SocketConfig(
            socket_dir=Path("/custom/path"),
            default_timeout=10,
            buffer_size=8192,
            timezone="America/New_York",
            message_queue_size=200,
            blocking_mode=True,
            allow_client_send=False,
        )

        assert config.socket_dir == Path("/custom/path")
        assert config.default_timeout == 10
        assert config.buffer_size == 8192
        assert config.timezone == "America/New_York"
        assert config.message_queue_size == 200
        assert config.blocking_mode is True
        assert config.allow_client_send is False

    def test_validation_positive_timeout(self) -> None:
        """Test timeout must be positive."""
        with pytest.raises(ValidationError):
            SocketConfig(default_timeout=0)

        with pytest.raises(ValidationError):
            SocketConfig(default_timeout=-1)

    def test_validation_positive_buffer_size(self) -> None:
        """Test buffer size must be positive."""
        with pytest.raises(ValidationError):
            SocketConfig(buffer_size=0)

        with pytest.raises(ValidationError):
            SocketConfig(buffer_size=-1)

    def test_validation_positive_queue_size(self) -> None:
        """Test message queue size must be positive."""
        with pytest.raises(ValidationError):
            SocketConfig(message_queue_size=0)

        with pytest.raises(ValidationError):
            SocketConfig(message_queue_size=-1)


class TestUnixSocketConfig:
    """Tests for UnixSocketConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = UnixSocketConfig()

        assert config.max_connections == 10
        assert config.socket_permissions == "0600"
        assert config.auto_remove_socket is True

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = UnixSocketConfig(
            max_connections=20,
            socket_permissions="0660",
            auto_remove_socket=False,
        )

        assert config.max_connections == 20
        assert config.socket_permissions == "0660"
        assert config.auto_remove_socket is False

    def test_validation_positive_max_connections(self) -> None:
        """Test max connections must be positive."""
        with pytest.raises(ValidationError):
            UnixSocketConfig(max_connections=0)

        with pytest.raises(ValidationError):
            UnixSocketConfig(max_connections=-1)


class TestTcpSocketConfig:
    """Tests for TcpSocketConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = TcpSocketConfig()

        assert config.host == "127.0.0.1"
        assert config.port_range_start == 9000
        assert config.port_range_end == 9100
        assert config.max_connections == 10

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = TcpSocketConfig(
            host="0.0.0.0",
            port_range_start=8000,
            port_range_end=8100,
            max_connections=20,
        )

        assert config.host == "0.0.0.0"
        assert config.port_range_start == 8000
        assert config.port_range_end == 8100
        assert config.max_connections == 20

    def test_validation_port_range(self) -> None:
        """Test port range validation."""
        with pytest.raises(ValidationError):
            TcpSocketConfig(port_range_start=1000)  # < 1024

        with pytest.raises(ValidationError):
            TcpSocketConfig(port_range_end=70000)  # > 65535

    def test_validation_positive_max_connections(self) -> None:
        """Test max connections must be positive."""
        with pytest.raises(ValidationError):
            TcpSocketConfig(max_connections=0)

        with pytest.raises(ValidationError):
            TcpSocketConfig(max_connections=-1)


class TestConfigLoaders:
    """Tests for configuration loader functions."""

    def test_get_default_config(self) -> None:
        """Test getting default configuration."""
        config = get_default_config()

        assert isinstance(config, AppConfig)
        assert isinstance(config.socket, SocketModuleConfig)

    def test_get_socket_config(self) -> None:
        """Test getting socket module config."""
        config = get_socket_config()

        assert isinstance(config, SocketModuleConfig)
        assert isinstance(config.socket, SocketConfig)
        assert isinstance(config.unix, UnixSocketConfig)
        assert isinstance(config.tcp, TcpSocketConfig)

    def test_get_generic_socket_config(self) -> None:
        """Test getting generic socket config."""
        config = get_generic_socket_config()

        assert isinstance(config, SocketConfig)

    def test_get_unix_socket_config(self) -> None:
        """Test getting Unix socket config."""
        config = get_unix_socket_config()

        assert isinstance(config, UnixSocketConfig)

    def test_get_tcp_socket_config(self) -> None:
        """Test getting TCP socket config."""
        config = get_tcp_socket_config()

        assert isinstance(config, TcpSocketConfig)
