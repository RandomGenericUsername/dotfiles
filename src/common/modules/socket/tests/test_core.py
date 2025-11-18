"""Tests for core types and utilities."""

import time

import pytest

from dotfiles_socket.core import (
    MessageType,
    SocketMessage,
    create_message,
    get_timestamp_iso,
    get_timestamp_ms,
    validate_event_name,
)


class TestMessageType:
    """Tests for MessageType enum."""

    def test_message_types(self) -> None:
        """Test MessageType enum values."""
        assert MessageType.DATA.value == "data"
        assert MessageType.ERROR.value == "error"
        assert MessageType.CONTROL.value == "control"


class TestValidateEventName:
    """Tests for event name validation."""

    def test_valid_event_names(self) -> None:
        """Test valid event names."""
        validate_event_name("test")
        validate_event_name("test_event")
        validate_event_name("test-event")
        validate_event_name("test123")
        validate_event_name("TEST_EVENT")
        validate_event_name("a" * 64)  # Max length

    def test_invalid_event_names(self) -> None:
        """Test invalid event names."""
        with pytest.raises(ValueError, match="empty"):
            validate_event_name("")

        with pytest.raises(ValueError, match="too long"):
            validate_event_name("a" * 65)

        with pytest.raises(ValueError, match="Invalid event name"):
            validate_event_name("test event")  # Space

        with pytest.raises(ValueError, match="Invalid event name"):
            validate_event_name("test@event")  # Special char

        with pytest.raises(ValueError, match="Invalid event name"):
            validate_event_name("test.event")  # Dot


class TestTimestamps:
    """Tests for timestamp utilities."""

    def test_get_timestamp_ms(self) -> None:
        """Test millisecond timestamp generation."""
        ts1 = get_timestamp_ms()
        time.sleep(0.01)
        ts2 = get_timestamp_ms()

        assert isinstance(ts1, int)
        assert isinstance(ts2, int)
        assert ts2 > ts1

    def test_get_timestamp_iso(self) -> None:
        """Test ISO timestamp generation."""
        ts = get_timestamp_iso()
        assert isinstance(ts, str)
        assert "T" in ts  # ISO format has T separator
        assert len(ts) > 0

    def test_get_timestamp_iso_with_timezone(self) -> None:
        """Test ISO timestamp with custom timezone."""
        ts_utc = get_timestamp_iso(tz_name="UTC")
        ts_est = get_timestamp_iso(tz_name="America/New_York")

        # Both should be valid ISO format strings
        # Note: Currently both return UTC time
        # (timezone support not yet implemented)
        assert isinstance(ts_utc, str)
        assert isinstance(ts_est, str)
        assert "T" in ts_utc
        assert "T" in ts_est


class TestSocketMessage:
    """Tests for SocketMessage dataclass."""

    def test_create_message(self) -> None:
        """Test message creation."""
        msg = create_message(
            event_name="test",
            message_type=MessageType.DATA,
            data={"key": "value"},
        )

        assert msg.event_name == "test"
        assert msg.message_type == MessageType.DATA
        assert msg.data == {"key": "value"}
        assert isinstance(msg.timestamp_ms, int)
        assert isinstance(msg.timestamp_iso, str)

    def test_message_to_dict(self) -> None:
        """Test message serialization to dict."""
        msg = create_message(
            event_name="test",
            message_type=MessageType.ERROR,
            data={"error": "test error"},
        )

        msg_dict = msg.to_dict()

        assert msg_dict["event_name"] == "test"
        assert msg_dict["message_type"] == "error"
        assert msg_dict["data"] == {"error": "test error"}
        assert "timestamp_ms" in msg_dict
        assert "timestamp_iso" in msg_dict

    def test_message_from_dict(self) -> None:
        """Test message deserialization from dict."""
        msg_dict = {
            "event_name": "test",
            "message_type": "control",
            "data": {"command": "stop"},
            "timestamp_ms": 1234567890,
            "timestamp_iso": "2023-01-01T00:00:00+00:00",
        }

        msg = SocketMessage.from_dict(msg_dict)

        assert msg.event_name == "test"
        assert msg.message_type == MessageType.CONTROL
        assert msg.data == {"command": "stop"}
        assert msg.timestamp_ms == 1234567890
        assert msg.timestamp_iso == "2023-01-01T00:00:00+00:00"

    def test_message_roundtrip(self) -> None:
        """Test message serialization roundtrip."""
        original = create_message(
            event_name="test",
            message_type=MessageType.DATA,
            data={"test": True, "value": 42},
        )

        msg_dict = original.to_dict()
        restored = SocketMessage.from_dict(msg_dict)

        assert restored.event_name == original.event_name
        assert restored.message_type == original.message_type
        assert restored.data == original.data
        assert restored.timestamp_ms == original.timestamp_ms
        assert restored.timestamp_iso == original.timestamp_iso
