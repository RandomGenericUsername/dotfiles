# Bug Fixes Summary - v0.2.0

## Overview

This document summarizes all bugs fixed in v0.2.0 release, including root causes, solutions, and verification.

## Critical Bugs Fixed

### 🔴 Bug #1: Race Condition on Startup (CRITICAL)

**Symptom**: After installing and running for the first time, when hyprpaper is not running and the module is executed, it causes an error that changes the wallpaper to black. Only resolves after running the command again.

**Root Cause**:
- `is_running()` only checked if the hyprpaper process exists using `pgrep -x hyprpaper`
- During startup (100-500ms window), the process exists but the IPC socket isn't ready yet
- Commands fail with empty stderr, resulting in "Command failed: " error
- No retry logic to handle transient failures

**Solution Implemented**:
1. **New `is_ready()` method** in `HyprpaperIPC` (lines 76-137 in `ipc/client.py`):
   - Tests socket readiness by attempting `listloaded` command
   - Waits up to `startup_wait` seconds (default: 2.0s) for socket to become ready
   - Retries every 100ms until socket responds or timeout

2. **Socket readiness check in `_execute()`** (line 178 in `ipc/client.py`):
   - Checks socket readiness before executing any command
   - Prevents commands from failing due to socket not being ready

**Files Modified**:
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/ipc/client.py`
- `src/common/modules/hyprpaper-manager/config/settings.toml`
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/config/config.py`

**Verification**:
- Test: `tests/test_ipc_race_condition.py::TestSocketReadiness`
- Manual test: Start hyprpaper and immediately run `hyprpaper-manager set wallpaper.png`
- Expected: Wallpaper sets successfully without black screen

---

### 🔴 Bug #2: Empty Error Messages (HIGH)

**Symptom**: When IPC commands fail, error message shows "Command failed: " with no details.

**Root Cause**:
- `stderr` was empty when socket wasn't ready
- No context provided about what went wrong

**Solution Implemented**:
1. **Context-aware error messages** in `_execute()` (lines 240-273 in `ipc/client.py`):
   - Checks if stderr is empty
   - Provides helpful context: "hyprpaper IPC socket not responding (process may be starting or crashed)"
   - Includes stderr when available

**Files Modified**:
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/ipc/client.py`

**Verification**:
- Test: `tests/test_ipc_race_condition.py::TestImprovedErrorMessages`
- Manual test: Kill hyprpaper and run command
- Expected: Clear error message explaining the issue

---

## Medium Priority Issues Fixed

### 🟡 Issue #3: No Retry Logic (MEDIUM)

**Symptom**: Commands fail immediately without retries on transient errors.

**Root Cause**:
- No retry mechanism for transient failures
- Single attempt per command

**Solution Implemented**:
1. **Exponential backoff retry** in `_execute()` (lines 186-239 in `ipc/client.py`):
   - Configurable retry attempts (default: 3)
   - Exponential backoff delay: 0.5s, 1.0s, 2.0s, etc.
   - Logs retry attempts at warning level

**Configuration Added**:
```toml
ipc_retry_attempts = 3    # Number of retry attempts
ipc_retry_delay = 0.5     # Initial delay between retries
```

**Files Modified**:
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/ipc/client.py`
- `src/common/modules/hyprpaper-manager/config/settings.toml`
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/config/config.py`

**Verification**:
- Test: `tests/test_ipc_race_condition.py::TestRetryLogic`
- Expected: Commands retry on transient failures

---

### 🟡 Issue #5: No Logging (MEDIUM)

**Symptom**: No debug logging for troubleshooting issues.

**Root Cause**:
- No logging infrastructure
- Difficult to diagnose issues

**Solution Implemented**:
1. **Comprehensive logging** throughout codebase:
   - `ipc/client.py`: Debug/warning/error logs for all operations
   - `manager.py`: Info/debug logs for high-level operations
   - `cli.py`: Logging setup with `--verbose` flag

2. **CLI logging support**:
   - `--verbose` / `-v` flag on all commands
   - `HYPRPAPER_MANAGER_LOG_LEVEL` environment variable
   - Configurable log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Files Modified**:
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/ipc/client.py`
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/manager.py`
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/cli.py`

**Verification**:
- Manual test: `hyprpaper-manager set wallpaper.png --verbose`
- Expected: Detailed debug output showing execution flow

---

## Low Priority Issues Fixed

### 🟡 Issue #4: Timeout Not Configurable (LOW)

**Symptom**: Single timeout for all commands; some operations need longer timeouts.

**Root Cause**:
- Fixed 5-second timeout for all commands
- Large wallpaper preloads may need longer timeouts

**Solution Implemented**:
1. **Per-command timeout overrides**:
   - All IPC methods accept optional `timeout` parameter
   - Falls back to default timeout if not specified

2. **Configurable default timeout**:
```toml
ipc_timeout = 5  # Default command timeout in seconds
```

**Files Modified**:
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/ipc/client.py`
- `src/common/modules/hyprpaper-manager/config/settings.toml`
- `src/common/modules/hyprpaper-manager/src/hyprpaper_manager/config/config.py`

**Verification**:
- Test: `tests/test_ipc_race_condition.py::TestPerCommandTimeout`
- API: `ipc.preload(large_wallpaper, timeout=10)`

---

## API Changes

### New Methods

**`HyprpaperIPC.is_ready(max_wait: float | None = None) -> bool`**
- Check if hyprpaper IPC socket is ready for commands
- Waits up to `max_wait` seconds for socket to become ready
- Returns `True` if socket is ready and accepting commands

### Modified Methods

All IPC methods now accept optional `timeout` parameter:
- `preload(wallpaper: Path, timeout: int | None = None)`
- `wallpaper(monitor: str, wallpaper: Path, mode: str | None = None, timeout: int | None = None)`
- `unload(target: Path | str, timeout: int | None = None)`
- `reload(monitor: str, wallpaper: Path, mode: str | None = None, timeout: int | None = None)`
- `listloaded(timeout: int | None = None)`
- `listactive(timeout: int | None = None)`

### Breaking Changes

**`HyprpaperIPC.__init__()` signature changed:**

Before:
```python
def __init__(self, timeout: int = 5):
```

After:
```python
def __init__(
    self,
    timeout: int = 5,
    retry_attempts: int = 3,
    retry_delay: float = 0.5,
    startup_wait: float = 2.0,
):
```

**Migration**: Use defaults (no changes needed) or pass new parameters if customization needed.

---

## Configuration Changes

### New Settings

Added to `config/settings.toml`:

```toml
[hyprpaper]
# IPC settings (NEW in v0.2.0)
ipc_timeout = 5              # Default command timeout in seconds
ipc_retry_attempts = 3       # Number of retry attempts
ipc_retry_delay = 0.5        # Initial delay between retries
ipc_startup_wait = 2.0       # Max wait for socket on startup
```

---

## Testing

### New Test Suite

**`tests/test_ipc_race_condition.py`** - 14 tests covering:
- Socket readiness checking (4 tests)
- Retry logic (4 tests)
- Improved error messages (3 tests)
- Per-command timeouts (3 tests)

**Test Results**: ✅ All 14 tests passing

---

## Documentation

### New Documentation Files

1. **`CHANGELOG.md`** - Detailed version history
2. **`docs/MIGRATION_v0.2.md`** - Migration guide from v0.1.x to v0.2.0
3. **`docs/BUG_FIXES_SUMMARY.md`** - This document

### Updated Documentation

1. **`README.md`** - Updated features, configuration, troubleshooting
2. **API documentation** - Updated with new methods and parameters

---

## Verification Checklist

- [x] Bug #1 (Race condition) - Fixed and tested
- [x] Bug #2 (Empty errors) - Fixed and tested
- [x] Issue #3 (No retry) - Fixed and tested
- [x] Issue #5 (No logging) - Fixed and tested
- [x] Issue #4 (Timeout) - Fixed and tested
- [x] Configuration updated
- [x] Documentation updated
- [x] Tests added and passing
- [x] Migration guide created

---

## User Impact

### Positive Changes
- ✅ No more black wallpapers on first command
- ✅ Clear error messages when things go wrong
- ✅ Automatic retry on transient failures
- ✅ Debug logging for troubleshooting
- ✅ Configurable timeouts for large wallpapers

### Potential Issues
- ⚠️ Commands may take slightly longer (up to 2s on first execution after hyprpaper startup)
- ⚠️ Breaking change in `HyprpaperIPC.__init__()` signature (but defaults work for most users)

### Migration Required?
- **Most users**: ✅ No changes needed - just update and enjoy the fixes!
- **Direct `HyprpaperIPC` users**: ⚠️ May need to update initialization (see migration guide)

---

## Next Steps

1. Update to v0.2.0
2. Test with `--verbose` flag to verify logging
3. Report any issues with debug logs
4. Enjoy reliable wallpaper management! 🎨
