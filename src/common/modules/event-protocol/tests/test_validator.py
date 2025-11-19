"""Tests for message validator."""

from dotfiles_event_protocol import Message, MessageType, MessageValidator


def test_validate_message():
    """Test message validation."""
    data = {
        "message_id": "test-123",
        "timestamp": "2024-01-15T10:30:00",
        "event_type": "wallpaper",
        "payload": {"type": "operation_progress"},
    }

    msg = MessageValidator.validate_message(data)
    assert isinstance(msg, Message)
    assert msg.event_type == "wallpaper"


def test_is_valid_message():
    """Test is_valid_message check."""
    # Valid message
    valid_data = {
        "message_id": "test-123",
        "timestamp": "2024-01-15T10:30:00",
        "event_type": "wallpaper",
        "payload": {},
    }
    assert MessageValidator.is_valid_message(valid_data) is True

    # Invalid message (missing required field)
    invalid_data = {
        "message_id": "test-123",
        "timestamp": "2024-01-15T10:30:00",
        # Missing event_type
        "payload": {},
    }
    assert MessageValidator.is_valid_message(invalid_data) is False


def test_validate_payload_type():
    """Test payload type validation."""
    msg = Message(
        event_type="wallpaper",
        payload={"type": "operation_progress"},
    )

    assert MessageValidator.validate_payload_type(msg, MessageType.OPERATION_PROGRESS) is True
    assert MessageValidator.validate_payload_type(msg, MessageType.OPERATION_STARTED) is False


def test_get_message_type():
    """Test getting message type from payload."""
    msg = Message(
        event_type="wallpaper",
        payload={"type": "operation_progress"},
    )

    msg_type = MessageValidator.get_message_type(msg)
    assert msg_type == MessageType.OPERATION_PROGRESS

    # Message without type
    msg_no_type = Message(
        event_type="wallpaper",
        payload={},
    )
    assert MessageValidator.get_message_type(msg_no_type) is None

