"""Tests for daemon publisher."""

import asyncio
from pathlib import Path

import pytest

from dotfiles_daemon.config import DaemonConfig
from dotfiles_daemon.publisher import DaemonPublisher
from dotfiles_event_protocol import MessageBuilder


@pytest.mark.asyncio
async def test_publisher_creation():
    """Test creating a publisher."""
    publisher = DaemonPublisher()

    assert publisher.config is not None
    assert publisher.logger is not None
    assert not publisher._connected


@pytest.mark.asyncio
async def test_publisher_connect_no_daemon(tmp_path):
    """Test connecting when daemon is not running."""
    config = DaemonConfig(socket_dir=tmp_path)
    publisher = DaemonPublisher(config=config)

    # Should fail gracefully
    result = await publisher.connect(timeout=0.1)

    assert result is False
    assert not publisher._connected


@pytest.mark.asyncio
async def test_publisher_publish_no_daemon(tmp_path):
    """Test publishing when daemon is not running."""
    config = DaemonConfig(socket_dir=tmp_path)
    publisher = DaemonPublisher(config=config)

    message = MessageBuilder.operation_started(
        event_type="test",
        operation_id="test-123",
        operation_name="test_operation",
        parameters={},
    )

    # Should fail gracefully
    result = await publisher.publish(message)

    assert result is False


@pytest.mark.asyncio
async def test_publisher_context_manager(tmp_path):
    """Test publisher as context manager."""
    config = DaemonConfig(socket_dir=tmp_path)

    async with DaemonPublisher(config=config) as publisher:
        # Connection will fail but should not raise
        assert publisher is not None

