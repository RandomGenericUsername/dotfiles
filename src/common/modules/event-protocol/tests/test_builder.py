"""Tests for message builder."""

from dotfiles_event_protocol import MessageBuilder, MessageType, QueryType


def test_operation_started():
    """Test building operation_started message."""
    msg = MessageBuilder.operation_started(
        event_type="wallpaper",
        operation_id="test-123",
        operation_name="change_wallpaper",
        parameters={"wallpaper_path": "/path/to/image.png"},
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == MessageType.OPERATION_STARTED
    assert msg.payload["operation_id"] == "test-123"
    assert msg.payload["operation_name"] == "change_wallpaper"
    assert msg.payload["parameters"]["wallpaper_path"] == "/path/to/image.png"


def test_operation_progress():
    """Test building operation_progress message."""
    msg = MessageBuilder.operation_progress(
        event_type="wallpaper",
        operation_id="test-123",
        step_id="generate_effects",
        step_progress=50.0,
        overall_progress=50.0,
        step_name="Generating effects",
        total_steps=3,
        current_step=2,
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == MessageType.OPERATION_PROGRESS
    assert msg.payload["operation_id"] == "test-123"
    assert msg.payload["step_id"] == "generate_effects"
    assert msg.payload["step_progress"] == 50.0
    assert msg.payload["overall_progress"] == 50.0
    assert msg.payload["step_name"] == "Generating effects"
    assert msg.payload["total_steps"] == 3
    assert msg.payload["current_step"] == 2


def test_operation_completed():
    """Test building operation_completed message."""
    msg = MessageBuilder.operation_completed(
        event_type="wallpaper",
        operation_id="test-123",
        duration_seconds=15.5,
        result={"wallpaper_path": "/path/to/image.png"},
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == MessageType.OPERATION_COMPLETED
    assert msg.payload["operation_id"] == "test-123"
    assert msg.payload["duration_seconds"] == 15.5
    assert msg.payload["result"]["wallpaper_path"] == "/path/to/image.png"


def test_operation_failed():
    """Test building operation_failed message."""
    msg = MessageBuilder.operation_failed(
        event_type="wallpaper",
        operation_id="test-123",
        error_code="EFFECT_GENERATION_FAILED",
        error_message="Failed to generate effects",
        step_id="generate_effects",
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == MessageType.OPERATION_FAILED
    assert msg.payload["operation_id"] == "test-123"
    assert msg.payload["error_code"] == "EFFECT_GENERATION_FAILED"
    assert msg.payload["error_message"] == "Failed to generate effects"
    assert msg.payload["step_id"] == "generate_effects"


def test_state_update():
    """Test building state_update message."""
    msg = MessageBuilder.state_update(
        event_type="wallpaper",
        state_key="current_wallpaper:DP-1",
        state_value={"wallpaper_path": "/path/to/image.png", "monitor": "DP-1"},
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == MessageType.STATE_UPDATE
    assert msg.payload["state_key"] == "current_wallpaper:DP-1"
    assert msg.payload["state_value"]["wallpaper_path"] == "/path/to/image.png"


def test_query_request():
    """Test building query_request message."""
    msg = MessageBuilder.query_request(
        event_type="wallpaper",
        query_type=QueryType.GET_CURRENT_STATE,
        parameters={"state_key": "current_wallpaper:DP-1"},
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == MessageType.QUERY_REQUEST
    assert msg.payload["query_type"] == QueryType.GET_CURRENT_STATE
    assert msg.payload["parameters"]["state_key"] == "current_wallpaper:DP-1"


def test_query_response():
    """Test building query_response message."""
    msg = MessageBuilder.query_response(
        event_type="wallpaper",
        query_id="query-123",
        result={"wallpaper_path": "/path/to/image.png"},
    )

    assert msg.event_type == "wallpaper"
    assert msg.payload["type"] == MessageType.QUERY_RESPONSE
    assert msg.payload["query_id"] == "query-123"
    assert msg.payload["result"]["wallpaper_path"] == "/path/to/image.png"
    assert msg.payload["error"] is None

