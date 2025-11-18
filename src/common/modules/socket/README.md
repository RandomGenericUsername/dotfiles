# Socket Module

Generic, agnostic socket communication module for inter-process messaging. Supports Unix domain sockets and TCP sockets with MessagePack serialization.

## Features

- **Multiple Socket Types**: Unix domain sockets and TCP sockets
- **Message Channels**: DATA, ERROR, and CONTROL message types
- **Broadcast & Unicast**: Send to all clients or specific client
- **Message Queue**: Queue messages when no clients connected
- **Thread-Safe**: Safe for concurrent operations
- **Auto-Reconnect**: Configurable client reconnection
- **Type-Safe**: Full type hints and Pydantic validation
- **Efficient**: MessagePack binary serialization

## Installation

```bash
cd src/common/modules/socket
uv sync
```

## Quick Start

### Unix Socket Server

```python
from dotfiles_socket import UnixSocketServer, SocketMessage, MessageType

# Create server
server = UnixSocketServer(event_name="my_event")
server.start()

# Send message to all clients
message = SocketMessage(
    event_name="my_event",
    message_type=MessageType.DATA,
    data={"status": "processing", "progress": 50}
)
server.send(message)

# Stop server
server.stop()
```

### Unix Socket Client

```python
from dotfiles_socket import UnixSocketClient, MessageType

# Create client
client = UnixSocketClient(event_name="my_event")
client.connect()

# Receive messages
for message in client.receive_iter():
    if message.message_type == MessageType.ERROR:
        print(f"Error: {message.data}")
    elif message.message_type == MessageType.DATA:
        print(f"Data: {message.data}")

client.disconnect()
```

### Using Factory

```python
from dotfiles_socket import create_server, create_client, SocketType

# Create server (using enum)
server = create_server(SocketType.UNIX, "my_event")
server.start()

# Create client (using string)
client = create_client("unix", "my_event")
client.connect()
```

### TCP Socket Example

```python
from dotfiles_socket import TcpSocketServer, TcpSocketClient, MessageType

# Create TCP server (auto-selects port from range)
server = TcpSocketServer(event_name="my_event", host="127.0.0.1")
server.start()
print(f"Server listening on port {server.port}")

# Create TCP client
client = TcpSocketClient(
    event_name="my_event",
    host="127.0.0.1",
    port=server.port
)
client.connect()

# Send and receive messages
server.send({"status": "ready"})
for message in client.receive_iter():
    print(f"Received: {message.data}")
    break

server.stop()
client.disconnect()
```

## Configuration

Configuration is managed via `config/settings.toml`. See the file for all available options.

Key settings:
- `socket_dir`: Directory for Unix socket files (default: `/tmp/sockets`)
- `timezone`: Timezone for ISO timestamps (default: `UTC`)
- `message_queue_size`: Max queued messages (default: `100`)
- `blocking_mode`: Server threading mode (default: `false`)
- `allow_client_send`: Allow clients to send messages (default: `true`)

## Message Format

All messages use the `SocketMessage` format:

```python
@dataclass
class SocketMessage:
    event_name: str           # Event identifier
    timestamp_ms: int         # Unix timestamp in milliseconds
    timestamp_iso: str        # ISO format in configured timezone
    message_type: MessageType # DATA, ERROR, or CONTROL
    data: dict[str, Any]      # Arbitrary payload
```

## Message Types

- `MessageType.DATA`: Regular data messages
- `MessageType.ERROR`: Error messages
- `MessageType.CONTROL`: Control messages (ping, shutdown, etc.)

## Development

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run tests
make test

# Run all checks
make all-checks

# Enter dev shell
make dev-shell
```

## Advanced Usage

### Server Hooks

```python
from dotfiles_socket import UnixSocketServer

class MyServer(UnixSocketServer):
    def on_client_connected(self, client_id: str) -> None:
        print(f"Client {client_id} connected")

    def on_client_disconnected(self, client_id: str) -> None:
        print(f"Client {client_id} disconnected")

    def on_message_received(
        self, client_id: str, message: dict
    ) -> None:
        print(f"Received from {client_id}: {message}")

server = MyServer(event_name="my_event")
server.start()
```

### Message Queue

When no clients are connected, messages are queued (FIFO):

```python
server = UnixSocketServer(
    event_name="my_event",
    message_queue_size=100  # Max 100 queued messages
)
server.start()

# Send messages even with no clients
# They'll be delivered when a client connects
server.send({"status": "queued"})
```

### Unicast (Send to Specific Client)

```python
# Get connected client IDs
client_ids = server.get_connected_clients()

# Send to specific client
server.send({"private": "message"}, client_id=client_ids[0])
```

### TCP Port Configuration

```python
# Auto-select port from range
server = TcpSocketServer(
    event_name="my_event",
    host="127.0.0.1",
    port_range_start=9000,
    port_range_end=9100
)

# Or bind to specific port
server = TcpSocketServer(
    event_name="my_event",
    host="127.0.0.1",
    port=9050
)
```

## API Reference

### Factory Functions

- `create_server(socket_type, event_name, **kwargs)` - Create server
- `create_client(socket_type, event_name, **kwargs)` - Create client

### Server Classes

- `UnixSocketServer` - Unix domain socket server
- `TcpSocketServer` - TCP socket server

**Methods:**
- `start()` - Start the server
- `stop()` - Stop the server
- `send(data, client_id=None)` - Send message (broadcast or unicast)
- `get_connected_clients()` - Get list of connected client IDs

### Client Classes

- `UnixSocketClient` - Unix domain socket client
- `TcpSocketClient` - TCP socket client

**Methods:**
- `connect()` - Connect to server
- `disconnect()` - Disconnect from server
- `send(data)` - Send message to server (if allowed)
- `receive()` - Receive one message (blocking)
- `receive_iter()` - Iterate over messages

### Utility Functions

- `create_message(event_name, message_type, data)` - Create message
- `validate_event_name(name)` - Validate event name
- `get_timestamp_ms()` - Get current timestamp in milliseconds
- `get_timestamp_iso(tz_name="UTC")` - Get ISO timestamp

## Testing

The module includes comprehensive tests with 73% coverage:

```bash
# Run tests
make test

# Run tests with coverage
uv run pytest tests/ --cov=dotfiles_socket --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_unix_socket.py -v
```

## License

Part of the dotfiles project.

