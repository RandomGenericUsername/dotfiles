# Migration Guide: v0.1.x → v0.2.0

This guide helps you migrate from hyprpaper-manager v0.1.x to v0.2.0.

## Summary of Changes

v0.2.0 fixes critical bugs and adds reliability improvements:
- ✅ Fixed race condition on hyprpaper startup (no more black wallpapers!)
- ✅ Added automatic retry logic for transient failures
- ✅ Improved error messages with context
- ✅ Added comprehensive logging support
- ✅ Made timeouts configurable per-command

## Breaking Changes

### 1. `HyprpaperIPC.__init__()` Signature

**If you're using `HyprpaperManager`**: ✅ **No changes needed** - it reads from config automatically.

**If you're creating `HyprpaperIPC` directly**:

#### Before (v0.1.x)
```python
from hyprpaper_manager.ipc.client import HyprpaperIPC

ipc = HyprpaperIPC(timeout=5)
```

#### After (v0.2.0)
```python
from hyprpaper_manager.ipc.client import HyprpaperIPC

# Option 1: Use defaults (recommended)
ipc = HyprpaperIPC()

# Option 2: Customize parameters
ipc = HyprpaperIPC(
    timeout=5,           # Default command timeout
    retry_attempts=3,    # Number of retries
    retry_delay=0.5,     # Initial retry delay
    startup_wait=2.0,    # Max wait for socket on startup
)
```

**Migration**: Add new parameters if you need custom values, otherwise use defaults.

## New Features

### 1. Configuration Options

Add these to your `config/settings.toml` (optional - defaults work well):

```toml
[hyprpaper]
# IPC settings
ipc_enabled = true
ipc_timeout = 5              # Default command timeout in seconds
ipc_retry_attempts = 3       # Number of retry attempts
ipc_retry_delay = 0.5        # Initial delay between retries
ipc_startup_wait = 2.0       # Max wait for socket on startup
```

### 2. Socket Readiness Check

New method to check if hyprpaper is ready:

```python
from hyprpaper_manager.ipc.client import HyprpaperIPC

ipc = HyprpaperIPC()

# Check if socket is ready (waits up to 2 seconds)
if ipc.is_ready():
    print("hyprpaper is ready!")
else:
    print("hyprpaper socket not ready")

# Custom wait time
if ipc.is_ready(max_wait=5.0):
    print("hyprpaper is ready after waiting up to 5 seconds")
```

**Use Case**: Check readiness before executing commands in scripts.

### 3. Per-Command Timeouts

All IPC methods now accept optional `timeout` parameter:

```python
from pathlib import Path
from hyprpaper_manager.ipc.client import HyprpaperIPC

ipc = HyprpaperIPC()

# Use default timeout
ipc.preload(Path("/path/to/wallpaper.png"))

# Use custom timeout for large wallpaper
ipc.preload(Path("/path/to/large_wallpaper.png"), timeout=10)

# List loaded wallpapers with custom timeout
loaded = ipc.listloaded(timeout=2)
```

**Use Case**: Large wallpapers may need longer timeouts.

### 4. Logging Support

#### CLI Usage

```bash
# Enable debug logging with --verbose flag
hyprpaper-manager set wallpaper.png --verbose

# Or use environment variable
HYPRPAPER_MANAGER_LOG_LEVEL=DEBUG hyprpaper-manager set wallpaper.png
```

#### Python API Usage

```python
import logging
from hyprpaper_manager import HyprpaperManager

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now all operations will log
manager = HyprpaperManager()
manager.set("wallpaper.png")
```

**Log Levels**:
- `DEBUG`: Detailed execution flow, command outputs, retry attempts
- `INFO`: High-level operations (wallpaper set, manager initialized)
- `WARNING`: Retries, socket not ready warnings
- `ERROR`: Fatal errors, process not running

## Behavior Changes

### 1. Automatic Retry on Failures

Commands now automatically retry on transient failures:

**Before (v0.1.x)**:
```python
# Failed immediately on first error
ipc.preload(wallpaper)  # Raises HyprpaperIPCError
```

**After (v0.2.0)**:
```python
# Retries up to 3 times with exponential backoff
ipc.preload(wallpaper)  # Succeeds if error is transient
```

**Impact**: Commands are more reliable but may take slightly longer (up to ~2 seconds on retries).

**Disable retries** (if needed):
```python
# Internal method - not recommended for normal use
ipc._execute("preload", str(wallpaper), retry=False)
```

### 2. Socket Readiness Check

Commands now wait for socket to be ready before execution:

**Before (v0.1.x)**:
```python
# Immediately after starting hyprpaper
subprocess.Popen(["hyprpaper"])
time.sleep(0.1)  # Manual wait
ipc.preload(wallpaper)  # Might fail with "Command failed: "
```

**After (v0.2.0)**:
```python
# Immediately after starting hyprpaper
subprocess.Popen(["hyprpaper"])
ipc.preload(wallpaper)  # Automatically waits for socket (up to 2s)
```

**Impact**: No more manual waits needed after starting hyprpaper.

### 3. Improved Error Messages

**Before (v0.1.x)**:
```
Error: Command failed:
```

**After (v0.2.0)**:
```
Error: Command failed: hyprpaper IPC socket not responding (process may be starting or crashed)
```

**Impact**: Easier to diagnose issues.

## Testing Your Migration

### 1. Test Startup Race Condition Fix

```bash
# Kill hyprpaper if running
pkill hyprpaper

# Start hyprpaper in background
hyprpaper &

# Immediately try to set wallpaper (should work now!)
hyprpaper-manager set /path/to/wallpaper.png
```

**Expected**: Wallpaper sets successfully without black screen.

### 2. Test Retry Logic

```bash
# Enable debug logging to see retries
hyprpaper-manager set wallpaper.png --verbose
```

**Expected**: If transient errors occur, you'll see retry attempts in logs.

### 3. Test Logging

```bash
# Test verbose flag
hyprpaper-manager set wallpaper.png --verbose

# Test environment variable
HYPRPAPER_MANAGER_LOG_LEVEL=DEBUG hyprpaper-manager status
```

**Expected**: Detailed debug output showing execution flow.

## Common Issues

### Issue: "hyprpaper IPC socket not ready"

**Cause**: hyprpaper is starting up or crashed.

**Solution**:
1. Check if hyprpaper is running: `pgrep hyprpaper`
2. Start hyprpaper: `hyprpaper &`
3. Check hyprpaper logs for errors

### Issue: Commands taking longer than before

**Cause**: Automatic retry logic and socket readiness checks.

**Solution**: This is expected behavior for reliability. If you need faster execution:
1. Reduce `ipc_retry_attempts` in config
2. Reduce `ipc_startup_wait` in config

```toml
[hyprpaper]
ipc_retry_attempts = 1    # Disable retries
ipc_startup_wait = 0.5    # Shorter wait
```

### Issue: Too much logging output

**Cause**: Debug logging enabled.

**Solution**:
1. Remove `--verbose` flag from CLI commands
2. Unset `HYPRPAPER_MANAGER_LOG_LEVEL` environment variable
3. Set logging level to `WARNING` or higher in your code

## Rollback

If you need to rollback to v0.1.x:

```bash
# Using uv
cd src/common/modules/hyprpaper-manager
uv pip install -e . --force-reinstall

# Or reinstall from git tag
uv pip install git+https://github.com/yourusername/hyprpaper-manager.git@v0.1.0
```

## Support

If you encounter issues during migration:

1. Check the [CHANGELOG.md](../CHANGELOG.md) for detailed changes
2. Enable debug logging: `--verbose` or `HYPRPAPER_MANAGER_LOG_LEVEL=DEBUG`
3. Check hyprpaper logs: `journalctl --user -u hyprpaper -f`
4. Open an issue with debug logs

## Summary Checklist

- [ ] Update config with new IPC settings (optional)
- [ ] Update `HyprpaperIPC` initialization if used directly
- [ ] Test startup race condition fix
- [ ] Test with `--verbose` flag to verify logging
- [ ] Update any scripts that manually wait after starting hyprpaper
- [ ] Review error handling code (better error messages now)
- [ ] Consider using per-command timeouts for large wallpapers

**Most users**: ✅ No code changes needed - just update and enjoy the fixes!
