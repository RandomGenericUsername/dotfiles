# Wallpaper Orchestrator Real-Time Progress Integration Guide

## Overview

This document provides step-by-step instructions for integrating the socket module into the wallpaper orchestrator tool to enable real-time progress updates via WebSocket communication.

## Architecture

The wallpaper orchestrator uses the **pipeline module** to execute a 3-step process:
1. Generate color scheme (via colorscheme generator)
2. Create effect variants (via wallpaper effects processor)
3. Change wallpaper (via hyprpaper manager)

The socket integration will:
- Start a Unix socket server when pipeline execution begins
- Send progress updates as each step completes
- Stop the server when pipeline execution finishes
- Allow external clients (like swaync notification daemon) to connect and receive real-time updates

## Prerequisites

### 1. Socket Module Location
- **Module Path**: `src/common/modules/socket/`
- **Package Name**: `dotfiles-socket`
- **Already Installed**: Yes (via `make sync-module MODULE=socket`)

### 2. Wallpaper Orchestrator Location
- **Tool Path**: `src/common/tools/wallpaper-orchestrator/`
- **Package Name**: `dotfiles-wallpaper-orchestrator`
- **Uses Pipeline Module**: Yes (for orchestrating the 3-step process)

### 3. Pipeline Module Capabilities
- **Progress Tracking**: Pipeline module supports progress callbacks
- **Step Weighting**: Each step gets equal weight (1/n of total)
- **Callbacks**: `on_progress`, `on_step_start`, `on_step_complete`, `on_error`

## Implementation Steps

### Step 1: Add Socket Dependency

Add `dotfiles-socket` to the wallpaper orchestrator's `pyproject.toml`:

```toml
[project]
dependencies = [
    "dotfiles-socket",
    # ... other dependencies
]
```

Then run: `uv sync` in the wallpaper orchestrator directory.

### Step 2: Create Socket Manager Class

Create a new file: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/socket_manager.py`

```python
"""Socket manager for real-time progress updates."""

import logging
from pathlib import Path
from typing import Any

from dotfiles_socket import (
    SocketType,
    MessageType,
    create_server,
    create_message,
    UnixSocketServer,
)

logger = logging.getLogger(__name__)


class WallpaperProgressSocketManager:
    """Manages socket server for wallpaper orchestrator progress updates."""

    def __init__(
        self,
        event_name: str = "wallpaper_progress",
        socket_dir: str | Path | None = None,
    ):
        """Initialize socket manager.

        Args:
            event_name: Event name for the socket (default: wallpaper_progress)
            socket_dir: Directory for socket file (default: from config)
        """
        self._event_name = event_name
        self._socket_dir = socket_dir
        self._server: UnixSocketServer | None = None
        self._is_running = False

    def start(self) -> None:
        """Start the socket server."""
        if self._is_running:
            logger.warning("Socket server already running")
            return

        try:
            # Create server
            kwargs = {"event_name": self._event_name}
            if self._socket_dir:
                kwargs["socket_dir"] = self._socket_dir

            self._server = create_server(SocketType.UNIX, **kwargs)
            self._server.start()
            self._is_running = True

            logger.info(
                f"Socket server started for event '{self._event_name}'"
            )

        except Exception as e:
            logger.error(f"Failed to start socket server: {e}")
            raise

    def stop(self) -> None:
        """Stop the socket server."""
        if not self._is_running or not self._server:
            return

        try:
            self._server.stop()
            self._is_running = False
            self._server = None
            logger.info("Socket server stopped")

        except Exception as e:
            logger.error(f"Failed to stop socket server: {e}")

    def send_progress(
        self,
        step_name: str,
        progress_percent: float,
        status: str = "processing",
        extra_data: dict[str, Any] | None = None,
    ) -> None:
        """Send progress update to connected clients.

        Args:
            step_name: Name of current step
            progress_percent: Progress percentage (0-100)
            status: Status message (processing, complete, error)
            extra_data: Additional data to include in message
        """
        if not self._is_running or not self._server:
            logger.warning("Socket server not running, skipping progress update")
            return

        try:
            # Build message data
            data = {
                "step": step_name,
                "progress": round(progress_percent, 2),
                "status": status,
            }

            if extra_data:
                data.update(extra_data)

            # Create and send message
            message = create_message(
                self._event_name,
                MessageType.DATA,
                data,
            )
            self._server.send(message)

            logger.debug(
                f"Progress update sent: {step_name} - {progress_percent:.1f}%"
            )

        except Exception as e:
            logger.error(f"Failed to send progress update: {e}")

    def send_error(self, error_message: str, step_name: str | None = None) -> None:
        """Send error message to connected clients.

        Args:
            error_message: Error description
            step_name: Name of step where error occurred (optional)
        """
        if not self._is_running or not self._server:
            return

        try:
            data = {
                "error": error_message,
                "status": "error",
            }
            if step_name:
                data["step"] = step_name

            message = create_message(
                self._event_name,
                MessageType.ERROR,
                data,
            )
            self._server.send(message)

        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
```

### Step 3: Integrate with Pipeline Module

Modify the wallpaper orchestrator's main execution logic to use the socket manager with pipeline callbacks.

**Location**: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/orchestrator.py` (or similar)

```python
from dotfiles_pipeline import Pipeline, PipelineStep
from .socket_manager import WallpaperProgressSocketManager


class WallpaperOrchestrator:
    """Orchestrates wallpaper changes with real-time progress updates."""

    def __init__(self):
        self.socket_manager = WallpaperProgressSocketManager()
        # ... other initialization

    def change_wallpaper(self, wallpaper_path: str) -> None:
        """Change wallpaper with real-time progress updates.

        Args:
            wallpaper_path: Path to wallpaper image
        """
        # Start socket server
        with self.socket_manager:
            try:
                # Create pipeline with 3 steps
                pipeline = Pipeline(
                    name="wallpaper_change",
                    steps=[
                        PipelineStep(
                            name="generate_colorscheme",
                            func=self._generate_colorscheme,
                            args=(wallpaper_path,),
                        ),
                        PipelineStep(
                            name="create_effects",
                            func=self._create_effects,
                            args=(wallpaper_path,),
                        ),
                        PipelineStep(
                            name="change_wallpaper",
                            func=self._change_wallpaper,
                            args=(wallpaper_path,),
                        ),
                    ],
                )

                # Set up progress callbacks
                def on_progress(step_name: str, progress: float):
                    self.socket_manager.send_progress(
                        step_name=step_name,
                        progress_percent=progress,
                        status="processing",
                    )

                def on_step_complete(step_name: str):
                    # Pipeline will call on_progress with 100% for this step
                    pass

                def on_error(step_name: str, error: Exception):
                    self.socket_manager.send_error(
                        error_message=str(error),
                        step_name=step_name,
                    )

                # Execute pipeline with callbacks
                pipeline.execute(
                    on_progress=on_progress,
                    on_error=on_error,
                )

                # Send completion message
                self.socket_manager.send_progress(
                    step_name="complete",
                    progress_percent=100.0,
                    status="complete",
                )

            except Exception as e:
                self.socket_manager.send_error(
                    error_message=f"Pipeline failed: {e}"
                )
                raise

    def _generate_colorscheme(self, wallpaper_path: str):
        """Generate color scheme from wallpaper."""
        # Implementation here
        pass

    def _create_effects(self, wallpaper_path: str):
        """Create wallpaper effect variants."""
        # Implementation here
        pass

    def _change_wallpaper(self, wallpaper_path: str):
        """Change wallpaper via hyprpaper."""
        # Implementation here
        pass
```

### Step 4: Update CLI Command

Update the CLI command to use the new orchestrator with socket support.

**Location**: `src/common/tools/wallpaper-orchestrator/src/dotfiles_wallpaper_orchestrator/cli.py`

```python
import click
from .orchestrator import WallpaperOrchestrator


@click.command()
@click.argument("wallpaper_path", type=click.Path(exists=True))
@click.option(
    "--socket-dir",
    type=click.Path(),
    help="Directory for socket file (optional)",
)
def change_wallpaper(wallpaper_path: str, socket_dir: str | None):
    """Change wallpaper with real-time progress updates.

    Starts a Unix socket server that broadcasts progress updates.
    External clients can connect to receive real-time status.
    """
    orchestrator = WallpaperOrchestrator()

    # Override socket directory if provided
    if socket_dir:
        orchestrator.socket_manager._socket_dir = socket_dir

    orchestrator.change_wallpaper(wallpaper_path)
```

## Testing the Integration

### Test 1: Basic Functionality

```bash
# Terminal 1: Start wallpaper change
cd src/common/tools/wallpaper-orchestrator
uv run dotfiles-wallpaper-orchestrator change /path/to/wallpaper.jpg
```

```bash
# Terminal 2: Connect client to receive updates
cd src/common/modules/socket
uv run python -c "
from dotfiles_socket import create_client, SocketType

client = create_client(SocketType.UNIX, 'wallpaper_progress')
client.connect()

print('Connected! Waiting for progress updates...')
for msg in client.receive_iter():
    data = msg.data
    if data.get('status') == 'complete':
        print(f'✅ Complete!')
        break
    elif data.get('status') == 'error':
        print(f'❌ Error: {data.get(\"error\")}')
        break
    else:
        print(f'📊 {data.get(\"step\")}: {data.get(\"progress\")}%')

client.disconnect()
"
```

### Test 2: Multiple Clients

You can connect multiple clients simultaneously - all will receive the same progress updates (broadcast mode).

## Message Format

### Progress Update (DATA message)
```json
{
  "event_name": "wallpaper_progress",
  "timestamp_ms": 1700000000000,
  "timestamp_iso": "2024-11-17T10:30:00+00:00",
  "message_type": "data",
  "data": {
    "step": "generate_colorscheme",
    "progress": 33.33,
    "status": "processing"
  }
}
```

### Error Message (ERROR message)
```json
{
  "event_name": "wallpaper_progress",
  "timestamp_ms": 1700000000000,
  "timestamp_iso": "2024-11-17T10:30:00+00:00",
  "message_type": "error",
  "data": {
    "error": "Failed to generate colorscheme",
    "step": "generate_colorscheme",
    "status": "error"
  }
}
```

## Configuration

### Socket Configuration

The socket module uses Dynaconf for configuration. Create or update:
`src/common/tools/wallpaper-orchestrator/config/settings.toml`

```toml
[socket]
socket_dir = "/tmp/dotfiles/sockets"
default_timeout = 5
buffer_size = 4096
timezone = "UTC"

[socket.unix]
max_connections = 10
socket_permissions = "0600"
auto_remove_socket = true
```

## Important Notes

1. **Socket Lifecycle**: The socket server starts when `change_wallpaper()` is called and stops when it completes (via context manager).

2. **Event Name**: Default is `"wallpaper_progress"`. Clients must use the same event name to connect.

3. **Socket Location**: Default is `/tmp/sockets/wallpaper_progress.sock`. Can be overridden via config or CLI option.

4. **Thread Safety**: The socket server runs in a separate thread, so it won't block the pipeline execution.

5. **Error Handling**: If socket server fails to start, it logs an error but doesn't prevent wallpaper change from proceeding.

6. **Client Connection Timing**: Clients can connect before or after the wallpaper change starts. If they connect after, they'll receive queued messages (up to 100 by default).

## Troubleshooting

### Socket file already exists
- The socket module auto-removes old socket files on startup (if `auto_remove_socket = true`)
- If issues persist, manually remove: `rm /tmp/sockets/wallpaper_progress.sock`

### No messages received
- Check that client is using correct event name
- Check that socket_dir matches between server and client
- Check logs: `dotfiles-wallpaper-orchestrator change /path/to/wallpaper.jpg --log-level debug`

### Permission denied
- Check socket file permissions (default: 0600)
- Ensure socket_dir is writable

## Next Steps

After integration:
1. Test with actual wallpaper changes
2. Integrate with swaync notification daemon
3. Add progress bar UI component
4. Consider adding WebSocket bridge for web-based clients (future enhancement)

