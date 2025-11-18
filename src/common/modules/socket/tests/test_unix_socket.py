"""Tests for Unix socket implementation."""

import time
from pathlib import Path

from dotfiles_socket.core import MessageType, create_message
from dotfiles_socket.implementations.unix import (
    UnixSocketClient,
    UnixSocketServer,
)


class TestUnixSocketServer:
    """Tests for UnixSocketServer."""

    def test_server_start_stop(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test server start and stop."""
        server = UnixSocketServer(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )

        assert not server.is_running()

        server.start()
        assert server.is_running()

        server.stop()
        assert not server.is_running()

    def test_socket_file_creation(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test socket file is created."""
        server = UnixSocketServer(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )

        server.start()
        time.sleep(0.2)

        socket_path = temp_socket_dir / f"{event_name}.sock"
        assert socket_path.exists()

        server.stop()

    def test_client_connection(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test client can connect to server."""
        server = UnixSocketServer(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        client = UnixSocketClient(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            auto_reconnect=False,
        )
        client.connect()
        time.sleep(0.2)

        clients = server.get_connected_clients()
        assert len(clients) == 1

        client.disconnect()
        server.stop()

    def test_message_send_receive(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test message sending and receiving."""
        server = UnixSocketServer(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        client = UnixSocketClient(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            auto_reconnect=False,
        )
        client.connect()
        time.sleep(0.2)

        # Send message from server to client
        message = create_message(
            event_name=event_name,
            message_type=MessageType.DATA,
            data={"test": "hello", "value": 42},
        )
        server.send(message)

        # Receive on client
        received = client.receive(timeout=2.0)
        assert received.data["test"] == "hello"
        assert received.data["value"] == 42

        client.disconnect()
        server.stop()

    def test_broadcast_to_multiple_clients(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test broadcasting to multiple clients."""
        server = UnixSocketServer(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        # Connect 3 clients
        clients = []
        for _ in range(3):
            client = UnixSocketClient(
                event_name=event_name,
                socket_dir=temp_socket_dir,
                auto_reconnect=False,
            )
            client.connect()
            clients.append(client)
            time.sleep(0.1)

        # Verify all connected
        assert len(server.get_connected_clients()) == 3

        # Broadcast message
        message = create_message(
            event_name=event_name,
            message_type=MessageType.DATA,
            data={"broadcast": True},
        )
        server.send(message)

        # All clients should receive
        for client in clients:
            received = client.receive(timeout=2.0)
            assert received.data["broadcast"] is True

        # Cleanup
        for client in clients:
            client.disconnect()
        server.stop()


class TestUnixSocketClient:
    """Tests for UnixSocketClient."""

    def test_client_connect_disconnect(
        self, temp_socket_dir: Path, event_name: str
    ) -> None:
        """Test client connect and disconnect."""
        server = UnixSocketServer(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        client = UnixSocketClient(
            event_name=event_name,
            socket_dir=temp_socket_dir,
            auto_reconnect=False,
        )

        assert not client.is_connected()

        client.connect()
        time.sleep(0.2)
        assert client.is_connected()

        client.disconnect()
        assert not client.is_connected()

        server.stop()
