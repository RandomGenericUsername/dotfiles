# Dotfiles Daemon

Persistent event daemon for the dotfiles management system.

## Overview

The daemon is a **generic event router** that:

1. Receives events from managers via command socket
2. Dynamically creates event sockets based on `event_type`
3. Broadcasts events to monitors via event sockets
4. Handles queries from monitors via query socket

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ dotfiles-daemon (PERSISTENT SERVICE)                         │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ EventBroker (Dynamic Socket Manager)                     │ │
│ │                                                          │ │
│ │ • Creates <event_type>_events.sock on first message     │ │
│ │ • Maintains registry of active event sockets            │ │
│ │ • Broadcasts to appropriate socket based on event_type  │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Command Server (command.sock)                            │ │
│ │ • Receives events from managers                          │ │
│ │ • Passes to EventBroker for broadcasting                 │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Query Server (query.sock)                                │ │
│ │ • Receives queries from monitors                         │ │
│ │ • Returns current state/status                           │ │
│ └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Components

### DotfilesDaemon

Main daemon class that:
- Manages command and query servers
- Coordinates event broker
- Handles lifecycle (start/stop)

### EventBroker

Manages dynamic event sockets:
- Creates event sockets on-demand
- Maintains client connections
- Broadcasts events to subscribers

### DaemonPublisher

Client for managers to publish events:
- Non-blocking connection with timeout
- Fire-and-forget message sending
- Graceful degradation if daemon unavailable

## Usage

### Running the Daemon

```bash
# Run with default socket directory
python -m dotfiles_daemon

# Run with custom socket directory
python -m dotfiles_daemon /path/to/sockets
```

### Publishing Events (Manager)

```python
from dotfiles_daemon import DaemonPublisher
from dotfiles_event_protocol import MessageBuilder

# Create publisher
publisher = DaemonPublisher()

# Publish event
message = MessageBuilder.operation_progress(
    event_type="wallpaper",
    operation_id="uuid-1234",
    step_id="generate_effects",
    step_progress=50.0,
    overall_progress=50.0,
)

await publisher.publish(message)
```

### Subscribing to Events (Monitor)

```python
import asyncio
import json

# Connect to event socket
reader, writer = await asyncio.open_unix_connection(
    "/path/to/sockets/wallpaper_events.sock"
)

# Receive events
while True:
    # Read message length
    length_bytes = await reader.readexactly(4)
    message_length = int.from_bytes(length_bytes, "big")

    # Read message
    data = await reader.readexactly(message_length)
    message = json.loads(data.decode("utf-8"))

    print(f"Received: {message}")
```

## Configuration

```python
from dotfiles_daemon import DaemonConfig

config = DaemonConfig(
    socket_dir=Path("/custom/socket/dir"),
    command_socket_name="command.sock",
    query_socket_name="query.sock",
    event_socket_suffix="_events.sock",
    max_message_size=1024 * 1024,  # 1MB
    connection_timeout=5.0,
)
```

## Socket Layout

```
~/.cache/dotfiles/sockets/
├── command.sock              # Managers send events here
├── query.sock                # Monitors query here
├── wallpaper_events.sock     # Wallpaper events (created dynamically)
├── backup_events.sock        # Backup events (created dynamically)
└── <event_type>_events.sock  # Any future event type
```

## Key Features

- ✅ **Generic** - Works with ANY event type
- ✅ **Dynamic** - Creates sockets on-demand
- ✅ **Persistent** - Runs as background service
- ✅ **Robust** - Graceful degradation if unavailable
- ✅ **Type-Safe** - Uses event-protocol for validation
- ✅ **Async** - Built on asyncio for performance

## Installation

```bash
make install
```

## Testing

```bash
make test
```

