# Changelog

All notable changes to hyprpaper-manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-07

### Fixed

#### 🔴 CRITICAL: Race Condition on Startup
- **Fixed**: Race condition when hyprpaper is starting up that caused wallpapers to turn black
- **Root Cause**: `is_running()` only checked if process exists, not if IPC socket was ready
- **Solution**: Added `is_ready()` method that waits for IPC socket to be ready before executing commands
- **Impact**: First command after hyprpaper startup now succeeds reliably

#### 🔴 HIGH: Empty Error Messages
- **Fixed**: Empty error messages when IPC commands failed ("Command failed: ")
- **Root Cause**: `stderr` was empty when socket wasn't ready
- **Solution**: Added context-aware error messages that check socket readiness and provide helpful hints
- **Impact**: Users now get clear error messages explaining what went wrong

#### 🟡 MEDIUM: No Retry Logic
- **Fixed**: Commands failed immediately without retries on transient errors
- **Solution**: Implemented exponential backoff retry mechanism (default: 3 attempts)
- **Impact**: Transient failures are now handled gracefully without user intervention

#### 🟡 MEDIUM: No Logging
- **Fixed**: No debug logging for troubleshooting
- **Solution**: Added comprehensive structured logging throughout the codebase
- **Impact**: Issues can now be diagnosed with `--verbose` flag or `HYPRPAPER_MANAGER_LOG_LEVEL` env var

#### 🟡 LOW: Timeout Not Configurable
- **Fixed**: Single timeout for all commands (some operations need longer)
- **Solution**: Added per-command timeout overrides
- **Impact**: Large wallpaper preloads can use longer timeouts

### Added

#### New Configuration Options

All new options are in `[hyprpaper]` section of `config/settings.toml`:

```toml
# IPC settings (NEW)
ipc_timeout = 5              # Default command timeout in seconds
ipc_retry_attempts = 3       # Number of retry attempts for transient failures
ipc_retry_delay = 0.5        # Initial delay between retries (exponential backoff)
ipc_startup_wait = 2.0       # Max wait for hyprpaper socket on startup
```

#### New API Methods

**`HyprpaperIPC.is_ready(max_wait: float | None = None) -> bool`**
- Check if hyprpaper IPC socket is ready for commands
- Waits up to `max_wait` seconds for socket to become ready
- Returns `True` if socket is ready and accepting commands
- **Use Case**: Check socket readiness before executing commands

**Example:**
```python
from hyprpaper_manager.ipc.client import HyprpaperIPC

ipc = HyprpaperIPC()
if ipc.is_ready(max_wait=2.0):
    ipc.preload(Path("/path/to/wallpaper.png"))
```

#### Enhanced API Methods

All IPC methods now support optional `timeout` parameter:

**`HyprpaperIPC.preload(wallpaper: Path, timeout: int | None = None) -> None`**
**`HyprpaperIPC.wallpaper(monitor: str, wallpaper: Path, mode: str | None = None, timeout: int | None = None) -> None`**
**`HyprpaperIPC.unload(target: Path | str, timeout: int | None = None) -> None`**
**`HyprpaperIPC.reload(monitor: str, wallpaper: Path, mode: str | None = None, timeout: int | None = None) -> None`**
**`HyprpaperIPC.listloaded(timeout: int | None = None) -> list[Path]`**
**`HyprpaperIPC.listactive(timeout: int | None = None) -> dict[str, Path]`**

**Example:**
```python
# Use longer timeout for large wallpaper
ipc.preload(large_wallpaper, timeout=10)
```

#### New CLI Options

**`--verbose` / `-v` flag** (all commands)
- Enable debug logging to see detailed execution flow
- **Example**: `hyprpaper-manager set wallpaper.png --verbose`

**Environment Variable: `HYPRPAPER_MANAGER_LOG_LEVEL`**
- Set logging level globally: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `HYPRPAPER_MANAGER_LOG_LEVEL=DEBUG hyprpaper-manager set wallpaper.png`

### Changed

#### Breaking Changes

**`HyprpaperIPC.__init__()` signature changed:**

**Before:**
```python
def __init__(self, timeout: int = 5):
```

**After:**
```python
def __init__(
    self,
    timeout: int = 5,
    retry_attempts: int = 3,
    retry_delay: float = 0.5,
    startup_wait: float = 2.0,
):
```

**Migration**: If you're creating `HyprpaperIPC` directly, you can:
1. Use defaults (no changes needed): `ipc = HyprpaperIPC()`
2. Pass new parameters: `ipc = HyprpaperIPC(timeout=10, retry_attempts=5)`

**Note**: If using `HyprpaperManager`, it automatically reads from config - no changes needed.

#### Behavior Changes

**`HyprpaperIPC._execute()` now includes:**
- Automatic socket readiness check before execution
- Retry logic with exponential backoff (default: 3 attempts)
- Enhanced error messages with context
- Detailed debug logging

**Impact**: Commands are more reliable but may take slightly longer on first execution after hyprpaper startup (up to `ipc_startup_wait` seconds).

**`HyprpaperIPC.is_running()` documentation updated:**
- Now explicitly documents that it only checks process existence
- Recommends using `is_ready()` to check socket readiness

### Improved

#### Error Messages

**Before:**
```
Error: Command failed:
```

**After:**
```
Error: Command failed: hyprpaper IPC socket not responding (process may be starting or crashed)
```

#### Logging

All operations now log at appropriate levels:
- `DEBUG`: Detailed execution flow, command outputs, retry attempts
- `INFO`: High-level operations (wallpaper set, manager initialized)
- `WARNING`: Retries, socket not ready warnings
- `ERROR`: Fatal errors, process not running

**Example debug output:**
```
2025-11-07 10:30:15 - hyprpaper_manager.ipc.client - DEBUG - Initialized HyprpaperIPC: timeout=5s, retry_attempts=3, retry_delay=0.5s, startup_wait=2.0s
2025-11-07 10:30:15 - hyprpaper_manager.ipc.client - DEBUG - Checking if hyprpaper socket is ready (max_wait=2.0s)
2025-11-07 10:30:15 - hyprpaper_manager.ipc.client - DEBUG - hyprpaper socket ready after 0.15s (2 attempts)
2025-11-07 10:30:15 - hyprpaper_manager.manager - INFO - Setting wallpaper: wallpaper.png on monitor=all, mode=WallpaperMode.COVER
```

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- Basic hyprpaper IPC control
- Wallpaper pool management
- CLI tool
- Configuration via dynaconf
