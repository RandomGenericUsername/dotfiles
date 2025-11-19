# Event System Usage Guide

This guide explains how to use the event system in your dotfiles installation.

## Overview

The event system consists of three main components:

1. **event-protocol** - Type-safe message definitions (common module)
2. **daemon** - Persistent event router (common module)
3. **Integrated managers** - Services that publish events (dotfiles modules)

## Installation

The event system modules are automatically installed when you install your dotfiles:

```bash
# Install dotfiles (includes all modules and tools)
cd cli
make install

# Or install individual components
cd src/common/modules/event-protocol && make install
cd src/common/modules/daemon && make install
cd src/dotfiles/modules/manager && make install
```

## Running the Daemon

The daemon is a persistent background service that routes events. It's **optional** - your dotfiles work perfectly without it.

### Manual Start

```bash
# Start the daemon
cd src/common/modules/daemon
.venv/bin/python -m dotfiles_daemon

# Or with custom socket directory
.venv/bin/python -m dotfiles_daemon /custom/socket/dir
```

### Systemd Service (Recommended)

Create `~/.config/systemd/user/dotfiles-daemon.service`:

```ini
[Unit]
Description=Dotfiles Event Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=/path/to/new/src/common/modules/daemon/.venv/bin/python -m dotfiles_daemon
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable dotfiles-daemon
systemctl --user start dotfiles-daemon
```

## Using the Event System

### As a User

Once the daemon is running, you can monitor events in real-time:

```bash
# Monitor wallpaper change events
cd src/common/modules/daemon
.venv/bin/python examples/monitor.py
```

Then in another terminal, change your wallpaper:

```bash
cd src/dotfiles/modules/manager
.venv/bin/dotfiles-manager wallpaper change /path/to/wallpaper.jpg
```

You'll see real-time progress updates in the monitor!

### As a Developer

#### Publishing Events from a Service

```python
from dotfiles_daemon import DaemonPublisher
from dotfiles_event_protocol import MessageBuilder
from uuid import uuid4

class MyService:
    def __init__(self):
        self._publisher = DaemonPublisher()
    
    async def do_operation(self):
        # Connect to daemon (non-blocking)
        try:
            await self._publisher.connect(timeout=0.1)
        except Exception:
            pass  # Graceful degradation
        
        operation_id = str(uuid4())
        
        # Publish operation started
        msg = MessageBuilder.operation_started(
            event_type="my_service",
            operation_id=operation_id,
            operation_name="do_operation",
            parameters={"param1": "value1"},
        )
        await self._publisher.publish(msg)
        
        # Do work and publish progress
        for i in range(100):
            msg = MessageBuilder.operation_progress(
                event_type="my_service",
                operation_id=operation_id,
                step_id=f"step_{i}",
                step_progress=100.0,
                overall_progress=float(i),
            )
            await self._publisher.publish(msg)
        
        # Publish completion
        msg = MessageBuilder.operation_completed(
            event_type="my_service",
            operation_id=operation_id,
            duration_seconds=10.5,
            result={"status": "success"},
        )
        await self._publisher.publish(msg)
```

#### Monitoring Events

```python
import asyncio
import json
from pathlib import Path

async def monitor_events(event_type: str):
    socket_path = Path.home() / ".cache/dotfiles/sockets" / f"{event_type}_events.sock"
    
    reader, writer = await asyncio.open_unix_connection(socket_path)
    
    while True:
        # Read message length
        length_bytes = await reader.read(4)
        if not length_bytes:
            break
        
        message_length = int.from_bytes(length_bytes, "big")
        
        # Read message
        data = await reader.read(message_length)
        message = json.loads(data.decode("utf-8"))
        
        print(f"Event: {message}")

# Run monitor
asyncio.run(monitor_events("wallpaper"))
```

## Event Types

The system supports any event type. Currently implemented:

- **wallpaper** - Wallpaper change operations
- Add more as needed (backup, theme, etc.)

## Socket Layout

```
~/.cache/dotfiles/sockets/
├── command.sock              # Managers send events here
├── query.sock                # Monitors query here (future)
└── <event_type>_events.sock  # Created dynamically per event type
```

## Troubleshooting

### Daemon not starting

```bash
# Check if socket directory exists
ls -la ~/.cache/dotfiles/sockets/

# Check daemon logs
journalctl --user -u dotfiles-daemon -f
```

### Events not being received

1. Make sure daemon is running: `systemctl --user status dotfiles-daemon`
2. Check if event socket exists: `ls ~/.cache/dotfiles/sockets/*_events.sock`
3. Try the demo: `cd src/common/modules/daemon && .venv/bin/python examples/event_demo.py`

### Manager works but no events

This is normal! The system has graceful degradation - managers work perfectly without the daemon.

## Examples

See `src/common/modules/daemon/examples/` for:
- `event_demo.py` - Complete demo with simulated events
- `monitor.py` - Real-world event monitor

