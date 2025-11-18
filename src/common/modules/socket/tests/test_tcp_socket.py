"""Tests for TCP socket implementation."""

import time

from dotfiles_socket.core import MessageType, create_message
from dotfiles_socket.implementations.tcp import (
    TcpSocketClient,
    TcpSocketServer,
)


class TestTcpSocketServer:
    """Tests for TcpSocketServer."""

    def test_server_start_stop(self, event_name: str, tcp_host: str) -> None:
        """Test server start and stop."""
        server = TcpSocketServer(
            event_name=event_name,
            host=tcp_host,
            blocking_mode=False,
        )

        assert not server.is_running()

        server.start()
        assert server.is_running()
        assert server.port is not None

        server.stop()
        assert not server.is_running()

    def test_port_auto_selection(self, event_name: str, tcp_host: str) -> None:
        """Test automatic port selection from range."""
        server = TcpSocketServer(
            event_name=event_name,
            host=tcp_host,
            blocking_mode=False,
        )

        server.start()
        port = server.port

        assert port is not None
        assert 9000 <= port <= 9100  # Default range

        server.stop()

    def test_specific_port_binding(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test binding to specific port."""
        server = TcpSocketServer(
            event_name=event_name,
            host=tcp_host,
            port=9050,
            blocking_mode=False,
        )

        server.start()
        assert server.port == 9050

        server.stop()

    def test_client_connection(self, event_name: str, tcp_host: str) -> None:
        """Test client can connect to server."""
        server = TcpSocketServer(
            event_name=event_name,
            host=tcp_host,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        client = TcpSocketClient(
            event_name=event_name,
            host=tcp_host,
            port=server.port,
            auto_reconnect=False,
        )
        client.connect()
        time.sleep(0.2)

        clients = server.get_connected_clients()
        assert len(clients) == 1

        client.disconnect()
        server.stop()

    def test_message_send_receive(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test message sending and receiving."""
        server = TcpSocketServer(
            event_name=event_name,
            host=tcp_host,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        client = TcpSocketClient(
            event_name=event_name,
            host=tcp_host,
            port=server.port,
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
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test broadcasting to multiple clients."""
        server = TcpSocketServer(
            event_name=event_name,
            host=tcp_host,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        # Connect 3 clients
        clients = []
        for _ in range(3):
            client = TcpSocketClient(
                event_name=event_name,
                host=tcp_host,
                port=server.port,
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


class TestTcpSocketClient:
    """Tests for TcpSocketClient."""

    def test_client_connect_disconnect(
        self, event_name: str, tcp_host: str
    ) -> None:
        """Test client connect and disconnect."""
        server = TcpSocketServer(
            event_name=event_name,
            host=tcp_host,
            blocking_mode=False,
        )
        server.start()
        time.sleep(0.2)

        client = TcpSocketClient(
            event_name=event_name,
            host=tcp_host,
            port=server.port,
            auto_reconnect=False,
        )

        assert not client.is_connected()

        client.connect()
        time.sleep(0.2)
        assert client.is_connected()

        client.disconnect()
        assert not client.is_connected()

        server.stop()
