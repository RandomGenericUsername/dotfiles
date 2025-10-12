# Troubleshooting Guide

Common issues, error messages, and solutions for the logging module.

## 🚨 Common Errors

### Configuration Errors

#### ValueError: max_bytes must be positive

**Error:**
```
ValueError: max_bytes must be positive
```

**Cause:** Invalid `max_bytes` value in `RotatingFileHandlerSettings`.

**Solution:**
```python
# ❌ Wrong
settings = RotatingFileHandlerSettings(filename="app.log", max_bytes=0)

# ✅ Correct
settings = RotatingFileHandlerSettings(filename="app.log", max_bytes=10_485_760)
```

#### ValueError: Invalid format '{message}' for '%' style

**Error:**
```
ValueError: Invalid format '{message}' for '%' style
```

**Cause:** Format string style doesn't match `formatter_style` setting.

**Solution:**
```python
# ❌ Wrong - Mismatched style and format
logger = Log.create_logger(
    "app",
    formatter_style=LogFormatterStyleChoices.PERCENT,  # % style
    format="{levelname}: {message}"                    # {} format
)

# ✅ Correct - Matching style and format
logger = Log.create_logger(
    "app",
    formatter_style=LogFormatterStyleChoices.BRACE,    # {} style
    format="{levelname}: {message}"                    # {} format
)
```

#### TypeError: __init__() missing required positional argument

**Error:**
```
TypeError: __init__() missing required positional argument: 'log_level'
```

**Cause:** Missing required fields in `LogConfig`.

**Solution:**
```python
# ❌ Wrong - Missing required fields
config = LogConfig(name="app")

# ✅ Correct - All required fields
config = LogConfig(
    name="app",
    log_level=LogLevels.INFO,
    verbosity=0,
    formatter_style=LogFormatterStyleChoices.PERCENT,
    format="%(levelname)s: %(message)s",
    formatter_type=LogFormatters.DEFAULT
)
```

### Rich-Related Errors

#### ImportError: Rich library not available

**Error:**
```
ImportError: Rich library not available
```

**Cause:** Rich library not installed but trying to use Rich features.

**Solution:**
```bash
# Install Rich
pip install rich
```

Or use fallback options:
```python
# Use non-Rich alternatives
logger = Log.create_logger(
    "app",
    formatter_type=LogFormatters.COLORED,      # Instead of RICH
    console_handler_type=ConsoleHandlers.DEFAULT  # Instead of RICH
)
```

#### AttributeError: 'NoneType' object has no attribute 'print'

**Error:**
```
AttributeError: 'NoneType' object has no attribute 'print'
```

**Cause:** Rich features trying to use console that wasn't registered.

**Solution:**
```python
# Ensure Rich handler is created before using Rich features
logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,  # This registers console
    rich_features=RichFeatureSettings(enabled=True)
)

# Now Rich features will work
logger.table(data, title="Results")
```

### File Handler Errors

#### PermissionError: [Errno 13] Permission denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'app.log'
```

**Cause:** No write permission to log file or directory.

**Solution:**
```python
import os

# Ensure directory exists and is writable
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
os.chmod(log_dir, 0o755)

# Use absolute path if needed
import os.path
log_file = os.path.abspath("logs/app.log")
```

#### FileNotFoundError: [Errno 2] No such file or directory

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'logs/app.log'
```

**Cause:** Log directory doesn't exist.

**Solution:**
```python
import os

# Create directory before creating logger
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logger = Log.create_logger(
    "app",
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename=f"{log_dir}/app.log")
        )
    ]
)
```

### Type Errors

#### AttributeError: 'ColoredFormatterColors' object has no attribute 'DEBUG'

**Error:**
```
AttributeError: 'ColoredFormatterColors' object has no attribute 'DEBUG'
```

**Cause:** Passing instance instead of class to `colors` parameter.

**Solution:**
```python
# ❌ Wrong - Passing instance
colors = ColoredFormatterColors()
logger = Log.create_logger("app", colors=colors)

# ✅ Correct - Passing class
logger = Log.create_logger("app", colors=ColoredFormatterColors)

# ✅ Also correct - Custom color class
class CustomColors(ColoredFormatterColors):
    DEBUG = "\033[36m"

logger = Log.create_logger("app", colors=CustomColors)
```

## 🔍 Debugging Techniques

### Enable Debug Logging

```python
# Enable debug logging for the logging module itself
import logging
logging.basicConfig(level=logging.DEBUG)

# Or create debug logger
debug_logger = Log.create_logger(
    "debug",
    log_level=LogLevels.DEBUG,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_path=True)
)
```

### Check Configuration

```python
def debug_logger_config(logger_name: str):
    """Debug logger configuration."""
    import logging

    logger = logging.getLogger(logger_name)
    print(f"Logger: {logger.name}")
    print(f"Level: {logger.level}")
    print(f"Handlers: {len(logger.handlers)}")

    for i, handler in enumerate(logger.handlers):
        print(f"  Handler {i}: {type(handler).__name__}")
        print(f"    Level: {handler.level}")
        print(f"    Formatter: {type(handler.formatter).__name__}")

# Usage
debug_logger_config("myapp")
```

### Check Rich Console

```python
def debug_rich_console(logger_name: str):
    """Debug Rich console availability."""
    from cli.modules.logging.rich_console_manager import RichConsoleManager

    manager = RichConsoleManager()
    console = manager.get_console(logger_name)

    if console:
        print(f"Console available for {logger_name}")
        print(f"Console type: {type(console)}")
        print(f"Console size: {console.size}")
        print(f"Console options: {console.options}")
    else:
        print(f"No console registered for {logger_name}")

# Usage
debug_rich_console("myapp")
```

### Validate Settings

```python
def validate_settings(settings):
    """Validate settings object."""
    try:
        # This will trigger __post_init__ validation
        if hasattr(settings, '__post_init__'):
            settings.__post_init__()
        print("Settings validation passed")
    except Exception as e:
        print(f"Settings validation failed: {e}")

# Usage
settings = RichHandlerSettings(tracebacks_extra_lines=-1)
validate_settings(settings)  # Will show validation error
```

## 🔧 Performance Issues

### Slow File Logging

**Symptoms:** Application becomes slow when logging to files.

**Causes:**
- Synchronous file I/O
- Large log messages
- Frequent logging

**Solutions:**
```python
# Use delay=True to defer file opening
FileHandlerSettings(filename="app.log", delay=True)

# Reduce log level in production
logger = Log.create_logger("app", log_level=LogLevels.WARNING)

# Use rotating handlers to prevent huge files
RotatingFileHandlerSettings(
    filename="app.log",
    max_bytes=10_000_000,  # 10MB
    backup_count=5
)
```

### Memory Usage

**Symptoms:** High memory usage with logging.

**Causes:**
- Too many handlers
- Large log messages kept in memory
- Rich objects not being garbage collected

**Solutions:**
```python
# Limit backup count
RotatingFileHandlerSettings(backup_count=3)  # Instead of 10

# Use simpler formatters in production
formatter_type=LogFormatters.DEFAULT  # Instead of RICH

# Disable Rich features if not needed
rich_features=RichFeatureSettings(enabled=False)
```

## 🧪 Testing Issues

### Tests Failing with Rich Features

**Problem:** Tests fail when Rich features are used.

**Solution:**
```python
import pytest
from unittest.mock import patch

def test_with_rich_disabled():
    """Test with Rich features disabled."""
    with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', False):
        logger = Log.create_logger("test")
        # Rich features should be no-ops
        logger.table([["A", "B"]], title="Test")  # Should not raise

def test_with_mock_console():
    """Test with mocked Rich console."""
    from unittest.mock import Mock

    mock_console = Mock()
    with patch('cli.modules.logging.rich_console_manager.RichConsoleManager.get_console',
               return_value=mock_console):
        logger = Log.create_logger("test", console_handler_type=ConsoleHandlers.RICH)
        logger.table([["A", "B"]], title="Test")
        mock_console.print.assert_called_once()
```

### File Handler Tests

**Problem:** File handler tests interfere with each other.

**Solution:**
```python
import tempfile
import os

def test_file_logging():
    """Test file logging with temporary files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test.log")

        logger = Log.create_logger(
            "test",
            file_handlers=[
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.FILE,
                    config=FileHandlerSettings(filename=log_file)
                )
            ]
        )

        logger.info("Test message")

        # Verify file content
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Test message" in content
```

## 🔄 Migration Issues

### Upgrading from Old API

**Problem:** Code using old logging API breaks.

**Solution:**
```python
# Old API (if it existed)
# logger = create_logger(name="app", level="INFO")

# New API
logger = Log.create_logger(
    name="app",
    log_level=LogLevels.INFO  # Use enum instead of string
)
```

### Configuration Format Changes

**Problem:** Old configuration format no longer works.

**Solution:**
```python
# Old format (dict-based)
# config = {"show_time": True, "show_level": True}

# New format (dataclass-based)
config = RichHandlerSettings(
    show_time=True,
    show_level=True
)
```

## 📊 Monitoring and Diagnostics

### Log Health Check

```python
def log_health_check():
    """Perform logging system health check."""
    issues = []

    # Check Rich availability
    try:
        import rich
        print("✓ Rich library available")
    except ImportError:
        issues.append("✗ Rich library not available")

    # Check log directory
    log_dir = "logs"
    if os.path.exists(log_dir) and os.access(log_dir, os.W_OK):
        print("✓ Log directory writable")
    else:
        issues.append("✗ Log directory not writable")

    # Check disk space
    import shutil
    free_space = shutil.disk_usage(".").free
    if free_space > 1_000_000_000:  # 1GB
        print("✓ Sufficient disk space")
    else:
        issues.append("✗ Low disk space")

    return issues

# Usage
issues = log_health_check()
if issues:
    print("Issues found:")
    for issue in issues:
        print(f"  {issue}")
```

### Performance Monitoring

```python
import time
from contextlib import contextmanager

@contextmanager
def log_performance_monitor():
    """Monitor logging performance."""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        if duration > 0.1:  # Warn if logging takes > 100ms
            print(f"Warning: Logging took {duration:.3f} seconds")

# Usage
with log_performance_monitor():
    logger.info("This is a test message")
```

## 📝 Best Practices for Troubleshooting

1. **Check Error Messages Carefully** - They usually indicate the exact problem
2. **Validate Configuration Early** - Use type hints and validation
3. **Test with Minimal Configuration** - Start simple and add complexity
4. **Use Debug Logging** - Enable debug output to see what's happening
5. **Check File Permissions** - Ensure log directories are writable
6. **Monitor Resource Usage** - Watch disk space and memory
7. **Test Rich Features Separately** - Isolate Rich-related issues
8. **Use Temporary Files in Tests** - Avoid test interference
9. **Keep Backups** - Don't lose important log data
10. **Document Custom Extensions** - Make troubleshooting easier

## 🆘 Getting Help

If you encounter issues not covered here:

1. **Check the error message** - Often contains the solution
2. **Review the configuration** - Ensure all required fields are present
3. **Test with minimal setup** - Isolate the problem
4. **Check dependencies** - Ensure Rich is installed if using Rich features
5. **Review file permissions** - Ensure log files are writable
6. **Consult the API reference** - Verify correct usage
7. **Create a minimal reproduction** - Helps identify the root cause

Remember: The logging module is designed to fail gracefully, so most issues are configuration-related rather than bugs in the module itself.
