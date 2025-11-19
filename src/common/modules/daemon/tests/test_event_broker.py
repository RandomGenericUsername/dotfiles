"""Tests for event broker."""

import pytest
from dotfiles_daemon.config import DaemonConfig
from dotfiles_daemon.event_broker import EventBroker
from dotfiles_daemon.logger import Logger
from dotfiles_event_protocol import Message


@pytest.mark.asyncio
async def test_event_broker_creation(tmp_path):
    """Test creating an event broker."""
    config = DaemonConfig(socket_dir=tmp_path)
    logger = Logger("test-broker")
    broker = EventBroker(config=config, logger=logger)

    assert broker.config == config
    assert broker.logger is not None
    assert len(broker._event_servers) == 0


@pytest.mark.asyncio
async def test_event_broker_start_stop(tmp_path):
    """Test starting and stopping event broker."""
    config = DaemonConfig(socket_dir=tmp_path)
    logger = Logger("test-broker")
    broker = EventBroker(config=config, logger=logger)

    # Start broker
    await broker.start()

    # Stop broker
    await broker.stop()


@pytest.mark.asyncio
async def test_event_broker_broadcast_creates_socket(tmp_path):
    """Test that broadcasting creates event socket dynamically."""
    config = DaemonConfig(socket_dir=tmp_path)
    config.ensure_socket_dir()
    logger = Logger("test-broker")
    broker = EventBroker(config=config, logger=logger)

    await broker.start()

    # Create a test message
    message = Message(
        message_id="test-123",
        timestamp="2025-01-01T00:00:00",
        event_type="test",
        payload={"type": "test_event"},
    )

    # Broadcast should create the socket
    await broker.broadcast(message)

    # Check socket was created
    socket_path = config.get_event_socket_path("test")
    assert socket_path.exists()

    await broker.stop()


@pytest.mark.asyncio
async def test_event_broker_multiple_event_types(tmp_path):
    """Test broker handles multiple event types."""
    config = DaemonConfig(socket_dir=tmp_path)
    config.ensure_socket_dir()
    logger = Logger("test-broker")
    broker = EventBroker(config=config, logger=logger)

    await broker.start()

    # Broadcast different event types
    for event_type in ["wallpaper", "backup", "theme"]:
        message = Message(
            message_id=f"test-{event_type}",
            timestamp="2025-01-01T00:00:00",
            event_type=event_type,
            payload={"type": "test"},
        )
        await broker.broadcast(message)

    # Check all sockets were created
    for event_type in ["wallpaper", "backup", "theme"]:
        socket_path = config.get_event_socket_path(event_type)
        assert socket_path.exists()

    await broker.stop()


@pytest.mark.asyncio
async def test_event_broker_cleanup_on_stop(tmp_path):
    """Test that broker cleans up sockets on stop."""
    config = DaemonConfig(socket_dir=tmp_path)
    config.ensure_socket_dir()
    logger = Logger("test-broker")
    broker = EventBroker(config=config, logger=logger)

    await broker.start()

    # Create some event sockets
    message = Message(
        message_id="test-123",
        timestamp="2025-01-01T00:00:00",
        event_type="test",
        payload={"type": "test"},
    )
    await broker.broadcast(message)

    socket_path = config.get_event_socket_path("test")
    assert socket_path.exists()

    # Stop should clean up
    await broker.stop()

    # Socket should be removed
    assert not socket_path.exists()
