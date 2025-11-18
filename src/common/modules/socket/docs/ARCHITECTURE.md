# Socket Module Architecture

## Overview
The socket module provides a generic, agnostic communication layer for inter-process messaging using Unix domain sockets and TCP sockets. It follows the established architectural patterns of the dotfiles project.

## Design Principles

1. **Separation of Concerns**: Abstract interfaces separate from concrete implementations
2. **Agnostic Design**: No use-case specific logic (progress bars, wallpapers, etc.)
3. **Type Safety**: Full type hints and Pydantic validation
4. **Thread Safety**: Safe for concurrent operations
5. **Factory Pattern**: Easy instantiation via factory
6. **Configuration-Driven**: Behavior controlled via settings.toml

## Module Structure

```
socket/
├── config/
│   └── settings.toml              # Default configuration
├── src/dotfiles_socket/
│   ├── __init__.py                # Main exports
│   ├── core/                      # Abstract interfaces
│   │   ├── __init__.py
│   │   ├── server.py              # SocketServer (ABC)
│   │   ├── client.py              # SocketClient (ABC)
│   │   ├── types.py               # SocketMessage, MessageType, etc.
│   │   └── exceptions.py          # Custom exceptions
│   ├── implementations/           # Concrete implementations
│   │   ├── __init__.py
│   │   ├── unix/                  # Unix domain sockets
│   │   │   ├── __init__.py
│   │   │   ├── server.py          # UnixSocketServer
│   │   │   └── client.py          # UnixSocketClient
│   │   └── tcp/                   # TCP sockets
│   │       ├── __init__.py
│   │       ├── server.py          # TcpSocketServer
│   │       └── client.py          # TcpSocketClient
│   ├── config/                    # Configuration system
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic models
│   │   └── settings.py            # Settings loader
│   └── factory.py                 # SocketFactory
├── tests/                         # Test suite
├── examples/                      # Usage examples
├── docs/                          # Documentation
├── Makefile                       # Dev tools
├── pyproject.toml                 # Project config
└── README.md                      # Module overview
```

## Core Components

### 1. Abstract Base Classes

#### SocketServer (`core/server.py`)
Abstract interface for all server implementations.

**Key Methods:**
- `start()` - Start the server (blocking or non-blocking)
- `stop()` - Stop the server and cleanup
- `send(message, client_id=None)` - Send message (broadcast or unicast)
- `is_running()` - Check if server is running
- `get_connected_clients()` - Get list of connected clients

**Key Properties:**
- `event_name` - Event identifier for this server

**Responsibilities:**
- Accept client connections
- Manage connected clients
- Queue messages when no clients connected
- Enforce max_connections limit
- Handle client send permissions

#### SocketClient (`core/client.py`)
Abstract interface for all client implementations.

**Key Methods:**
- `connect()` - Connect to server
- `disconnect()` - Disconnect from server
- `send(message)` - Send message to server
- `receive()` - Receive single message (blocking)
- `receive_iter()` - Iterate over received messages
- `is_connected()` - Check connection status

**Responsibilities:**
- Connect to server
- Send/receive messages
- Auto-reconnect on connection loss
- Buffer received messages

### 2. Message System

#### SocketMessage (`core/types.py`)
Standard message format for all socket communication.

```python
@dataclass
class SocketMessage:
    event_name: str           # Event identifier
    timestamp_ms: int         # Unix timestamp in milliseconds
    timestamp_iso: str        # ISO format in configured TZ
    message_type: MessageType # DATA, ERROR, or CONTROL
    data: dict[str, Any]      # Arbitrary payload
```

#### MessageType (`core/types.py`)
Message channel/type enum.

```python
class MessageType(Enum):
    DATA = "data"        # Regular data messages
    ERROR = "error"      # Error messages
    CONTROL = "control"  # Control messages (ping, shutdown, etc.)
```

**Usage Pattern:**
Clients can filter messages by type, allowing them to handle errors separately from data:

```python
for message in client.receive_iter():
    if message.message_type == MessageType.ERROR:
        handle_error(message.data)
    elif message.message_type == MessageType.DATA:
        process_data(message.data)
```

### 3. Implementations

#### Unix Domain Sockets (`implementations/unix/`)
- **Socket Path**: `{socket_dir}/{event_name}.sock`
- **Use Case**: Local inter-process communication
- **Performance**: High (no network overhead)
- **Security**: File system permissions

**Features:**
- Configurable socket file permissions
- Auto-remove socket file on stop
- Fast local communication

#### TCP Sockets (`implementations/tcp/`)
- **Address**: `{host}:{port}`
- **Use Case**: Network communication or when Unix sockets unavailable
- **Performance**: Good (network overhead)
- **Security**: Network-level security needed

**Features:**
- Auto-assign port from configured range
- SO_REUSEADDR for quick restarts
- Network-capable communication

### 4. Configuration System

#### Pydantic Models (`config/config.py`)
Type-safe configuration models with validation.

```python
class SocketConfig(BaseModel):
    socket_dir: Path
    default_timeout: int
    buffer_size: int
    timezone: str
    message_queue_size: int
    blocking_mode: bool
    allow_client_send: bool

class UnixSocketConfig(BaseModel):
    max_connections: int
    socket_permissions: str
    auto_remove_socket: bool

class TcpSocketConfig(BaseModel):
    host: str
    port_range_start: int
    port_range_end: int
    max_connections: int
```

#### Settings Loader (`config/settings.py`)
Dynaconf-based settings loader with environment variable support.

### 5. Factory Pattern (`factory.py`)

Simplifies creation of servers and clients:

```python
def create_server(
    socket_type: SocketType | str,
    event_name: str,
    **kwargs: Any
) -> SocketServer:
    """Create a server instance.

    Args:
        socket_type: SocketType.UNIX, SocketType.TCP, "unix", or "tcp"
        event_name: Event identifier
        **kwargs: Additional arguments passed to server constructor
    """

def create_client(
    socket_type: SocketType | str,
    event_name: str,
    **kwargs: Any
) -> SocketClient:
    """Create a client instance.

    Args:
        socket_type: SocketType.UNIX, SocketType.TCP, "unix", or "tcp"
        event_name: Event identifier
        **kwargs: Additional arguments passed to client constructor
    """
```

## Data Flow

### Server → Client (Broadcast)
```
1. Server.send(message)
2. Serialize with MessagePack
3. Send to all connected clients
4. Clients receive and deserialize
5. Clients get SocketMessage object
```

### Server → Client (Unicast)
```
1. Server.send(message, client_id="client_123")
2. Serialize with MessagePack
3. Send to specific client only
4. Client receives and deserializes
5. Client gets SocketMessage object
```

### Client → Server
```
1. Client.send(message)
2. Check if server allows client send
3. Serialize with MessagePack
4. Send to server
5. Server receives and deserializes
6. Server processes message
```

### Message Queue (No Clients)
```
1. Server.send(message)
2. No clients connected
3. Add to message queue (FIFO)
4. Queue size limited (configurable)
5. When client connects, deliver queued messages
```

## Threading Model

### Non-Blocking Mode (Default)
```
Main Thread:
  └─ server.start() returns immediately

Background Thread:
  └─ Accept connections
  └─ Handle client messages
  └─ Send messages to clients
```

### Blocking Mode
```
Main Thread:
  └─ server.start() blocks
  └─ Accept connections
  └─ Handle client messages
  └─ Send messages to clients
```

## Error Handling

### Exception Hierarchy
```
SocketError (base)
├── ConnectionError
├── MessageError
├── ValidationError
├── TimeoutError
└── MaxConnectionsError
```

### Error Propagation
- Exceptions raised for critical errors
- Graceful degradation for non-critical errors
- Comprehensive logging via dotfiles-logging

## Security Considerations

### Unix Sockets
- File permissions (default: 0600 - owner only)
- Socket file location validation
- Path traversal prevention

### TCP Sockets
- Bind to localhost by default (127.0.0.1)
- Port range restriction
- No authentication (can be added later)

### Message Validation
- Event name validation (alphanumeric + underscore/hyphen)
- Message size limits (buffer_size)
- Malformed message handling

## Performance Considerations

### Serialization
- MessagePack: Binary, compact, fast
- Automatic encoding/decoding
- Minimal overhead

### Threading
- One thread per server (non-blocking mode)
- Thread pool for client connections
- Thread-safe message queue

### Memory
- Bounded message queue (prevents memory leaks)
- Client buffer size limits
- Automatic cleanup on disconnect

## Integration Points

### With Pipeline Module
```python
# Server broadcasts pipeline progress
def progress_callback(step_idx, total, name, percent):
    server.send(SocketMessage(
        event_name="wallpaper_change",
        message_type=MessageType.DATA,
        data={"progress": percent, "step": name}
    ))

pipeline = Pipeline(steps, progress_callback=progress_callback)
```

### With Other Modules
- **Logging**: Uses dotfiles-logging for all logging
- **State Manager**: Can store connection state (optional)
- **Config**: Uses dynaconf + Pydantic like other modules

## Extension Points

### Adding New Socket Types
1. Create new directory in `implementations/`
2. Implement `SocketServer` and `SocketClient` abstractions
3. Add configuration to `config.py`
4. Update factory to support new type

### Custom Message Types
1. Extend `MessageType` enum
2. No code changes needed in implementations
3. Clients filter by new message type

### Custom Serialization
1. Create new serializer module
2. Replace MessagePack calls in implementations
3. Maintain transparent encoding/decoding

