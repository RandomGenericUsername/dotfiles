"""Tests for factory functions."""

import time
from pathlib import Path

import pytest

from dotfiles_socket import (
    MessageType,
    SocketType,
    TcpSocketClient,
    TcpSocketServer,
    UnixSocketClient,
    UnixSocketServer,
    create_client,
    create_message,
    create_server,
)


class TestCreateServer:
    """Tests for create_server factory function."""

    def test_create_unix_server_with_enum(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test creating Unix server with SocketType enum."""
        server = create_server(
            SocketType.UNIX,
            event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )

        assert isinstance(server, UnixSocketServer)
        server.start()
        assert server.is_running()
        server.stop()

    def test_create_unix_server_with_string(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test creating Unix server with string socket type."""
        server = create_server(
            "unix",
            event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )

        assert isinstance(server, UnixSocketServer)
        server.start()
        assert server.is_running()
        server.stop()

    def test_create_tcp_server_with_enum(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test creating TCP server with SocketType enum."""
        server = create_server(
            SocketType.TCP,
            event_name,
            host=tcp_host,
            blocking_mode=False,
        )

        assert isinstance(server, TcpSocketServer)
        server.start()
        assert server.is_running()
        server.stop()

    def test_create_tcp_server_with_string(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test creating TCP server with string socket type."""
        server = create_server(
            "tcp",
            event_name,
            host=tcp_host,
            blocking_mode=False,
        )

        assert isinstance(server, TcpSocketServer)
        server.start()
        assert server.is_running()
        server.stop()

    def test_invalid_socket_type(self, event_name: str) -> None:
        """Test creating server with invalid socket type."""
        with pytest.raises(ValueError, match="Invalid socket_type"):
            create_server("invalid", event_name)


class TestCreateClient:
    """Tests for create_client factory function."""

    def test_create_unix_client_with_enum(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test creating Unix client with SocketType enum."""
        client = create_client(
            SocketType.UNIX,
            event_name,
            socket_dir=temp_socket_dir,
            auto_reconnect=False,
        )

        assert isinstance(client, UnixSocketClient)

    def test_create_unix_client_with_string(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test creating Unix client with string socket type."""
        client = create_client(
            "unix",
            event_name,
            socket_dir=temp_socket_dir,
            auto_reconnect=False,
        )

        assert isinstance(client, UnixSocketClient)

    def test_create_tcp_client_with_enum(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test creating TCP client with SocketType enum."""
        client = create_client(
            SocketType.TCP,
            event_name,
            host=tcp_host,
            port=9000,
            auto_reconnect=False,
        )

        assert isinstance(client, TcpSocketClient)

    def test_create_tcp_client_with_string(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test creating TCP client with string socket type."""
        client = create_client(
            "tcp",
            event_name,
            host=tcp_host,
            port=9000,
            auto_reconnect=False,
        )

        assert isinstance(client, TcpSocketClient)

    def test_invalid_socket_type(self, event_name: str) -> None:
        """Test creating client with invalid socket type."""
        with pytest.raises(ValueError, match="Invalid socket_type"):
            create_client("invalid", event_name)


class TestFactoryIntegration:
    """Integration tests using factory functions."""

    def test_unix_socket_communication(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test Unix socket communication using factory."""
        server = create_server(
            SocketType.UNIX,
            event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        client = create_client(
            SocketType.UNIX,
            event_name,
            socket_dir=temp_socket_dir,
            auto_reconnect=False,
        )
        client.connect()
        time.sleep(0.2)

        message = create_message(
            event_name=event_name,
            message_type=MessageType.DATA,
            data={"factory": "test"},
        )
        server.send(message)

        received = client.receive(timeout=2.0)
        assert received.data["factory"] == "test"

        client.disconnect()
        server.stop()

    def test_tcp_socket_communication(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test TCP socket communication using factory."""
        server = create_server(
            SocketType.TCP,
            event_name,
            host=tcp_host,
            blocking_mode=False,
        )
        assert isinstance(server, TcpSocketServer)
        server.start()
        time.sleep(0.2)

        client = create_client(
            SocketType.TCP,
            event_name,
            host=tcp_host,
            port=server.port,
            auto_reconnect=False,
        )
        client.connect()
        time.sleep(0.2)

        message = create_message(
            event_name=event_name,
            message_type=MessageType.DATA,
            data={"factory": "test"},
        )
        server.send(message)

        received = client.receive(timeout=2.0)
        assert received.data["factory"] == "test"

        client.disconnect()
        server.stop()
