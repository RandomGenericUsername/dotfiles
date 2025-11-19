"""Tests for event protocol models."""

import pytest
from pydantic import ValidationError

from dotfiles_event_protocol import (
    Message,
    MessageType,
    OperationProgressMessage,
    OperationProgressPayload,
)


def test_message_creation():
    """Test creating a basic message."""
    msg = Message(
        event_type="wallpaper",
        payload={"type": "operation_progress", "operation_id": "test-123"},
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == "operation_progress"
    assert msg.message_id is not None
    assert msg.timestamp is not None


def test_message_validation():
    """Test message validation."""
    # Valid message
    msg = Message(
        event_type="wallpaper",
        payload={"type": "operation_progress"},
    )
    assert msg.event_type == "wallpaper"

    # Invalid timestamp
    with pytest.raises(ValidationError):
        Message(
            timestamp="invalid-timestamp",
            event_type="wallpaper",
            payload={},
        )


def test_operation_progress_payload():
    """Test OperationProgressPayload validation."""
    # Valid payload
    payload = OperationProgressPayload(
        operation_id="test-123",
        step_id="generate_effects",
        step_progress=50.0,
        overall_progress=50.0,
    )

    assert payload.type == MessageType.OPERATION_PROGRESS
    assert payload.operation_id == "test-123"
    assert payload.step_progress == 50.0

    # Invalid progress (out of range)
    with pytest.raises(ValidationError):
        OperationProgressPayload(
            operation_id="test-123",
            step_id="generate_effects",
            step_progress=150.0,  # Invalid: > 100
            overall_progress=50.0,
        )


def test_typed_message():
    """Test typed message creation."""
    payload = OperationProgressPayload(
        operation_id="test-123",
        step_id="generate_effects",
        step_progress=50.0,
        overall_progress=50.0,
    )

    msg = OperationProgressMessage(
        event_type="wallpaper",
        payload=payload,
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload.operation_id == "test-123"

    # Convert to generic
    generic = msg.to_generic()
    assert isinstance(generic, Message)
    assert generic.event_type == "wallpaper"
    assert generic.payload["operation_id"] == "test-123"


def test_message_serialization():
    """Test message serialization."""
    msg = Message(
        event_type="wallpaper",
        payload={"type": "operation_progress", "operation_id": "test-123"},
    )

    # To dict
    data = msg.to_dict()
    assert isinstance(data, dict)
    assert data["event_type"] == "wallpaper"

    # From dict
    msg2 = Message.from_dict(data)
    assert msg2.event_type == msg.event_type
    assert msg2.payload == msg.payload

