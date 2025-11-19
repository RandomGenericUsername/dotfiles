"""Tests for daemon."""

import asyncio

import pytest

from dotfiles_daemon.config import DaemonConfig
from dotfiles_daemon.daemon import DotfilesDaemon
from dotfiles_daemon.publisher import DaemonPublisher
from dotfiles_event_protocol import MessageBuilder


@pytest.mark.asyncio
async def test_daemon_starts_and_stops(tmp_path):
    """Test daemon can start and stop cleanly."""
    config = DaemonConfig(socket_dir=tmp_path)
    config.ensure_socket_dir()

    daemon = DotfilesDaemon(config=config)
    daemon_task = asyncio.create_task(daemon.start())

    # Give daemon time to start
    await asyncio.sleep(0.1)

    # Verify sockets were created
    assert config.get_command_socket_path().exists()
    assert config.get_query_socket_path().exists()

    # Stop daemon
    await daemon.stop()
    daemon_task.cancel()
    try:
        await daemon_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_publisher_connects_to_daemon(tmp_path):
    """Test publisher can connect to running daemon."""
    config = DaemonConfig(socket_dir=tmp_path)
    config.ensure_socket_dir()

    daemon = DotfilesDaemon(config=config)
    daemon_task = asyncio.create_task(daemon.start())
    await asyncio.sleep(0.1)

    try:
        publisher = DaemonPublisher(config=config)
        connected = await publisher.connect(timeout=1.0)
        assert connected

        await publisher.disconnect()

    finally:
        await daemon.stop()
        daemon_task.cancel()
        try:
            await daemon_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_publisher_can_publish_messages(tmp_path):
    """Test publisher can publish messages to daemon."""
    config = DaemonConfig(socket_dir=tmp_path)
    config.ensure_socket_dir()

    daemon = DotfilesDaemon(config=config)
    daemon_task = asyncio.create_task(daemon.start())
    await asyncio.sleep(0.1)

    try:
        publisher = DaemonPublisher(config=config)
        await publisher.connect(timeout=1.0)

        # Publish a message
        msg = MessageBuilder.operation_started(
            event_type="test",
            operation_id="test-123",
            operation_name="test_operation",
            parameters={},
        )
        result = await publisher.publish(msg)
        assert result is True

        # Event socket should be created
        await asyncio.sleep(0.1)
        assert config.get_event_socket_path("test").exists()

        await publisher.disconnect()

    finally:
        await daemon.stop()
        daemon_task.cancel()
        try:
            await daemon_task
        except asyncio.CancelledError:
            pass

