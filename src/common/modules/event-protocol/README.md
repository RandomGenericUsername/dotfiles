# dotfiles-event-protocol

Type-safe event protocol for the dotfiles event system.

## Overview

This module provides Pydantic models for type-safe message passing between:
- **dotfiles-manager** (CLI tool that executes operations)
- **dotfiles-daemon** (Event broker that manages sockets)
- **Monitoring clients** (Waybar widgets, notification daemons, etc.)

## Message Structure

All messages follow this structure:

```python
{
    "message_id": str,      # Unique identifier (auto-generated UUID)
    "timestamp": str,       # ISO8601 timestamp (auto-generated)
    "event_type": str,      # Event category for routing (e.g., "wallpaper", "backup")
    "payload": dict         # Generic dictionary with message-specific data
}
```

## Installation

```bash
make install
```

## Usage

### Using MessageBuilder (Recommended)

```python
from dotfiles_event_protocol import MessageBuilder

# Create operation progress message
message = MessageBuilder.operation_progress(
    event_type="wallpaper",
    operation_id="uuid-1234",
    step_id="generate_effects",
    step_progress=50.0,
    overall_progress=50.0,
)

# Serialize to dict for sending
data = message.to_dict()
```

### Using Typed Models Directly

```python
from dotfiles_event_protocol import (
    OperationProgressMessage,
    OperationProgressPayload,
)

# Create typed payload
payload = OperationProgressPayload(
    operation_id="uuid-1234",
    step_id="generate_effects",
    step_progress=50.0,
    overall_progress=50.0,
)

# Create typed message
msg = OperationProgressMessage(
    event_type="wallpaper",
    payload=payload,
)

# Convert to generic Message
generic = msg.to_generic()
```

### Validating Messages

```python
from dotfiles_event_protocol import MessageValidator

# Validate raw data
data = {
    "message_id": "test-123",
    "timestamp": "2024-01-15T10:30:00",
    "event_type": "wallpaper",
    "payload": {"type": "operation_progress"},
}

# Check if valid
if MessageValidator.is_valid_message(data):
    msg = MessageValidator.validate_message(data)
    print(f"Valid message: {msg.event_type}")
```

## Message Types

### operation_started

Sent when an operation begins.

```python
MessageBuilder.operation_started(
    event_type="wallpaper",
    operation_id="uuid-1234",
    operation_name="change_wallpaper",
    parameters={"wallpaper_path": "/path/to/image.png"},
)
```

### operation_progress

Sent during operation execution to report progress.

```python
MessageBuilder.operation_progress(
    event_type="wallpaper",
    operation_id="uuid-1234",
    step_id="generate_effects",
    step_progress=50.0,
    overall_progress=50.0,
)
```

### operation_completed

Sent when an operation completes successfully.

```python
MessageBuilder.operation_completed(
    event_type="wallpaper",
    operation_id="uuid-1234",
    duration_seconds=15.5,
    result={"wallpaper_path": "/path/to/image.png"},
)
```

### operation_failed

Sent when an operation fails.

```python
MessageBuilder.operation_failed(
    event_type="wallpaper",
    operation_id="uuid-1234",
    error_code="EFFECT_GENERATION_FAILED",
    error_message="Failed to generate effects",
)
```

### state_update

Sent to update daemon state.

```python
MessageBuilder.state_update(
    event_type="wallpaper",
    state_key="current_wallpaper:DP-1",
    state_value={"wallpaper_path": "/path/to/image.png"},
)
```

## Testing

```bash
make test
```

## Type Safety

All models use Pydantic for validation:

- ✅ Automatic validation on construction
- ✅ Type hints for IDE support
- ✅ Runtime type checking
- ✅ Clear error messages for invalid data

