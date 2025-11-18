# Socket Module Requirements

## Overview
Generic, agnostic socket communication module for real-time message passing between processes. Supports Unix domain sockets and TCP sockets with MessagePack serialization.

## Core Requirements

### 1. Architecture
- **Abstract Base Classes**: `SocketServer` and `SocketClient` in `core/`
- **Implementations**: Concrete implementations in `implementations/unix/` and `implementations/tcp/`
- **Factory Pattern**: `SocketFactory` for creating server/client instances
- **Configuration**: Pydantic models + dynaconf for settings management
- **Agnostic Design**: No specific use-case logic (e.g., no progress bar specifics)

### 2. Message Format
```python
@dataclass
class SocketMessage:
    event_name: str           # Event identifier
    timestamp_ms: int         # Unix timestamp in milliseconds
    timestamp_iso: str        # ISO format in configured timezone
    message_type: MessageType # DATA, ERROR, or CONTROL
    data: dict[str, Any]      # Arbitrary payload
```

**MessageType Enum:**
- `DATA`: Regular data messages
- `ERROR`: Error messages
- `CONTROL`: Control messages (ping, shutdown, etc.)

### 3. Event Names
- **Validation Pattern**: `^[a-zA-Z0-9_-]+$`
- **Max Length**: 64 characters
- **Valid Examples**: `wallpaper_change`, `color-scheme-update`, `system_status`
- **Invalid Examples**: `wallpaper/change`, `color.scheme`, `my event`

### 4. Socket Path Construction
- **Unix Sockets**: `{socket_dir}/{event_name}.sock`
- **TCP Sockets**: `{host}:{port}` (port auto-assigned from range)
- **Configurable**: Both `socket_dir` and event_name validation

### 5. Server Capabilities

#### Connection Management
- **Multiple Clients**: Support concurrent client connections
- **Max Connections**: Configurable limit (default: 10)
- **Connection Limit Behavior**: Reject new connections when limit reached
- **Client Tracking**: Track connected clients by ID

#### Message Handling
- **Broadcast**: Send message to all connected clients (default)
- **Unicast**: Send to specific client if `client_id` provided
- **Message Queue**: Queue messages when no clients connected
  - Configurable queue size (default: 100)
  - FIFO behavior
  - Deliver queued messages when client connects

#### Threading
- **Non-Blocking Mode** (default): Server runs in separate thread
- **Blocking Mode**: Server blocks main thread
- **Configurable**: Via `blocking_mode` setting

#### Client Send Permission
- **Server-Controlled**: `allow_client_send` config option
- **Default**: `true` (clients can send messages back)
- **Enforcement**: Server rejects client messages if disabled

### 6. Client Capabilities

#### Connection
- **Auto-Reconnect**: Configurable (default: true)
- **Reconnect Strategy**: Exponential backoff with max retries
- **Connection Timeout**: Configurable (default: 5 seconds)

#### Message Handling
- **Receive Messages**: Always supported
- **Send Messages**: Only if server allows (`allow_client_send = true`)
- **Message Buffer**: Client-side buffer for received messages
  - Configurable buffer size
  - Iterator interface for consuming messages

#### Modes
- **Bidirectional**: Can send and receive (if server allows)
- **Receive-Only**: Only receive messages (if server disallows send)

### 7. Serialization
- **Format**: MessagePack (binary, efficient)
- **Transparency**: Automatic encoding/decoding
- **User Interface**: Users work with `SocketMessage` objects, not raw bytes
- **Error Handling**: Graceful handling of malformed messages

### 8. Configuration Structure

```toml
[socket]
# Generic socket settings (all implementations)
socket_dir = "/tmp/sockets"
default_timeout = 5
buffer_size = 4096
timezone = "UTC"
message_queue_size = 100
blocking_mode = false
allow_client_send = true

[socket.unix]
# Unix domain socket specific settings
max_connections = 10
socket_permissions = "0600"
auto_remove_socket = true

[socket.tcp]
# TCP socket specific settings
host = "127.0.0.1"
port_range_start = 9000
port_range_end = 9100
max_connections = 10
```

### 9. Error Handling
- **Custom Exceptions**: Socket-specific exception hierarchy
  - `SocketError` (base)
  - `ConnectionError`
  - `MessageError`
  - `ValidationError`
  - `TimeoutError`
- **Graceful Degradation**: Handle client disconnections gracefully
- **Logging**: Comprehensive error logging via dotfiles-logging

### 10. Thread Safety
- **Server**: Thread-safe for concurrent client handling
- **Client**: Thread-safe for concurrent send/receive
- **Message Queue**: Thread-safe queue implementation
- **Locks**: Proper locking for shared resources

## Implementation-Specific Requirements

### Unix Domain Sockets
- **Socket File**: Create `.sock` file in configured directory
- **Permissions**: Configurable file permissions (default: 0600)
- **Cleanup**: Auto-remove socket file on server stop (configurable)
- **Path Validation**: Ensure socket_dir exists and is writable

### TCP Sockets
- **Port Assignment**: Auto-assign from configured port range
- **Host Binding**: Configurable host (default: 127.0.0.1)
- **Port Reuse**: Handle `SO_REUSEADDR` for quick restarts
- **Network Errors**: Handle network-specific errors

## Development Requirements

### Code Quality
- **Line Length**: 79 characters
- **Python Version**: 3.12+
- **Type Hints**: Full type annotations
- **Docstrings**: Comprehensive documentation
- **Formatters**: black, isort
- **Linter**: ruff (E, W, F, I, B, C4, UP, ARG, SIM, PTH, N)
- **Type Checker**: mypy (strict mode)

### Testing
- **Framework**: pytest
- **Coverage**: Aim for >90%
- **Test Types**: Unit, integration, concurrent access
- **Mock**: Mock external dependencies

### Documentation
- **README.md**: Module overview, installation, quick start
- **docs/**: Detailed guides and API reference
- **Examples**: Working examples for common use cases
- **Inline Docs**: Comprehensive docstrings

### Build System
- **Package Manager**: uv
- **Build Backend**: hatchling
- **Dependencies**: dotfiles-logging, dynaconf, pydantic, msgpack
- **Dev Dependencies**: pytest, mypy, black, ruff, isort, pre-commit

## Non-Requirements (Out of Scope)
- ❌ Progress bar implementations
- ❌ Specific use-case logic (wallpaper, color schemes, etc.)
- ❌ WebSocket support (only Unix/TCP sockets)
- ❌ Encryption/authentication (can be added later)
- ❌ Message persistence to disk
- ❌ Message acknowledgment/delivery guarantees

