"""Example usage of the event protocol."""

from uuid import uuid4

from dotfiles_event_protocol import MessageBuilder, MessageValidator, QueryType


def example_manager_publishing_events():
    """Example: Manager publishing events during wallpaper operation."""
    print("=== Manager Publishing Events ===\n")

    operation_id = str(uuid4())

    # 1. Operation started
    msg = MessageBuilder.operation_started(
        event_type="wallpaper",
        operation_id=operation_id,
        operation_name="change_wallpaper",
        parameters={
            "wallpaper_path": "/path/to/image.png",
            "monitor": "DP-1",
        },
    )
    print(f"1. Operation Started:\n{msg.to_dict()}\n")

    # 2. Progress update (step 1)
    msg = MessageBuilder.operation_progress(
        event_type="wallpaper",
        operation_id=operation_id,
        step_id="generate_colorscheme",
        step_name="Generating colorscheme",
        step_progress=100.0,
        overall_progress=33.3,
        total_steps=3,
        current_step=1,
    )
    print(f"2. Progress (Step 1):\n{msg.to_dict()}\n")

    # 3. Progress update (step 2)
    msg = MessageBuilder.operation_progress(
        event_type="wallpaper",
        operation_id=operation_id,
        step_id="generate_effects",
        step_name="Generating effects",
        step_progress=50.0,
        overall_progress=50.0,
        total_steps=3,
        current_step=2,
    )
    print(f"3. Progress (Step 2):\n{msg.to_dict()}\n")

    # 4. Operation completed
    msg = MessageBuilder.operation_completed(
        event_type="wallpaper",
        operation_id=operation_id,
        duration_seconds=15.5,
        result={
            "wallpaper_path": "/path/to/image.png",
            "monitor": "DP-1",
            "from_cache": False,
        },
    )
    print(f"4. Operation Completed:\n{msg.to_dict()}\n")

    # 5. State update
    msg = MessageBuilder.state_update(
        event_type="wallpaper",
        state_key="current_wallpaper:DP-1",
        state_value={
            "wallpaper_path": "/path/to/image.png",
            "monitor": "DP-1",
            "set_at": "2024-01-15T10:30:15Z",
        },
    )
    print(f"5. State Update:\n{msg.to_dict()}\n")


def example_monitor_querying_state():
    """Example: Monitor querying daemon for current state."""
    print("=== Monitor Querying State ===\n")

    # Monitor sends query request
    query_msg = MessageBuilder.query_request(
        event_type="wallpaper",
        query_type=QueryType.GET_CURRENT_STATE,
        parameters={"state_key": "current_wallpaper:DP-1"},
    )
    print(f"Query Request:\n{query_msg.to_dict()}\n")

    # Daemon responds with query response
    response_msg = MessageBuilder.query_response(
        event_type="wallpaper",
        query_id=query_msg.message_id,
        result={
            "wallpaper_path": "/path/to/image.png",
            "monitor": "DP-1",
            "set_at": "2024-01-15T10:30:15Z",
        },
    )
    print(f"Query Response:\n{response_msg.to_dict()}\n")


def example_validation():
    """Example: Validating messages."""
    print("=== Message Validation ===\n")

    # Valid message
    valid_data = {
        "message_id": "test-123",
        "timestamp": "2024-01-15T10:30:00",
        "event_type": "wallpaper",
        "payload": {
            "type": "operation_progress",
            "operation_id": "uuid-1234",
            "step_id": "generate_effects",
            "step_progress": 50.0,
            "overall_progress": 50.0,
        },
    }

    if MessageValidator.is_valid_message(valid_data):
        msg = MessageValidator.validate_message(valid_data)
        print(f"✅ Valid message: {msg.event_type}")
        print(f"   Message type: {MessageValidator.get_message_type(msg)}\n")

    # Invalid message (missing required field)
    invalid_data = {
        "message_id": "test-123",
        "timestamp": "2024-01-15T10:30:00",
        # Missing event_type
        "payload": {},
    }

    if not MessageValidator.is_valid_message(invalid_data):
        print("❌ Invalid message: missing required field\n")


def example_error_handling():
    """Example: Handling operation failures."""
    print("=== Error Handling ===\n")

    operation_id = str(uuid4())

    # Operation failed
    msg = MessageBuilder.operation_failed(
        event_type="wallpaper",
        operation_id=operation_id,
        error_code="EFFECT_GENERATION_FAILED",
        error_message="Failed to generate effects: insufficient memory",
        step_id="generate_effects",
        traceback="Traceback (most recent call last):\n  ...",
    )
    print(f"Operation Failed:\n{msg.to_dict()}\n")


if __name__ == "__main__":
    example_manager_publishing_events()
    example_monitor_querying_state()
    example_validation()
    example_error_handling()

