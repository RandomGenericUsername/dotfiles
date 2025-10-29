# Migration Guide

Guide for migrating to the logging module from other logging systems.

## 🔄 Migration Overview

This guide covers migration from:

1. **Standard Python logging** - Direct logging module usage
2. **Other logging libraries** - loguru, structlog, etc.
3. **Custom logging solutions** - Homegrown logging systems
4. **Previous versions** - If upgrading from older versions

## 📦 From Standard Python Logging

### Basic Logger Creation

**Before (Standard logging):**
```python
import logging

# Basic setup
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('myapp')

# Advanced setup
logger = logging.getLogger('myapp')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**After (Logging module):**
```python
from cli.modules.logging import Log, LogLevels

# Basic setup
logger = Log.create_logger('myapp', log_level=LogLevels.INFO)

# Advanced setup with Rich
logger = Log.create_logger(
    'myapp',
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### File Logging

**Before:**
```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('myapp')
handler = RotatingFileHandler('app.log', maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

**After:**
```python
from cli.modules.logging import (
    Log, FileHandlerSpec, FileHandlerTypes, RotatingFileHandlerSettings
)

logger = Log.create_logger(
    'myapp',
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename='app.log',
                max_bytes=10*1024*1024,
                backup_count=5
            )
        )
    ]
)
```

### Multiple Handlers

**Before:**
```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

logger = logging.getLogger('myapp')

# Console handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

# File handler
file_handler = RotatingFileHandler('app.log', maxBytes=10*1024*1024, backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Error handler
error_handler = TimedRotatingFileHandler('error.log', when='midnight', backupCount=30)
error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(error_handler)
```

**After:**
```python
logger = Log.create_logger(
    'myapp',
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True),
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(filename='app.log', max_bytes=10*1024*1024, backup_count=5),
            format_override="%(asctime)s - %(levelname)s - %(message)s"
        ),
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(filename='error.log', when='midnight', backup_count=30),
            format_override="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    ]
)
```

## 🎨 From Loguru

### Basic Usage

**Before (Loguru):**
```python
from loguru import logger

# Basic usage
logger.info("Hello world")

# Custom format
logger.remove()
logger.add(sys.stderr, format="{time} | {level} | {message}")

# File logging
logger.add("app.log", rotation="10 MB", retention="10 days")
```

**After:**
```python
from cli.modules.logging import Log, LogLevels, ConsoleHandlers, RichHandlerSettings

# Basic usage
logger = Log.create_logger("app", log_level=LogLevels.INFO)
logger.info("Hello world")

# Custom format with Rich
logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True),
    format="{asctime} | {levelname} | {message}",
    formatter_style=LogFormatterStyleChoices.BRACE
)

# File logging with rotation
logger = Log.create_logger(
    "app",
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="app.log",
                max_bytes=10*1024*1024,  # 10 MB
                backup_count=10          # Keep 10 files (approximate retention)
            )
        )
    ]
)
```

### Structured Logging

**Before (Loguru):**
```python
from loguru import logger

logger.bind(user_id=123, request_id="abc").info("User action")
```

**After:**
```python
# Use extra parameter or format the message
logger.info("User action", extra={"user_id": 123, "request_id": "abc"})

# Or format the message directly
logger.info(f"User action - user_id: 123, request_id: abc")

# Or use Rich features for structured display
logger.table({
    "Field": ["user_id", "request_id", "action"],
    "Value": ["123", "abc", "User action"]
}, title="User Event")
```

## 🏗️ From Structlog

### Basic Configuration

**Before (Structlog):**
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("myapp")
```

**After:**
```python
from cli.modules.logging import Log, LogFormatters

# For JSON-like output, use custom format
logger = Log.create_logger(
    "myapp",
    formatter_type=LogFormatters.RICH,
    format='{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="structured.log")
        )
    ]
)

# Or extend with custom JSON formatter (see Extension Guide)
```

### Structured Data

**Before (Structlog):**
```python
logger.info("User login", user_id=123, ip="192.168.1.1", success=True)
```

**After:**
```python
# Format as structured message
logger.info(f"User login - user_id: 123, ip: 192.168.1.1, success: True")

# Or use Rich table for complex data
login_data = {
    "Field": ["user_id", "ip", "success", "timestamp"],
    "Value": ["123", "192.168.1.1", "True", "2025-10-01 13:02:29"]
}
logger.table(login_data, title="User Login Event")

# Or use Rich panel for important events
logger.panel(
    "User ID: 123\nIP: 192.168.1.1\nSuccess: True",
    title="User Login",
    border_style="green"
)
```

## 🔧 From Custom Solutions

### Configuration-Based Systems

**Before (Custom config):**
```python
# config.yaml
logging:
  level: INFO
  handlers:
    - type: console
      format: "%(levelname)s: %(message)s"
    - type: file
      filename: app.log
      format: "%(asctime)s - %(levelname)s - %(message)s"

# Python code
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Custom setup code...
```

**After:**
```python
from cli.modules.logging import LogConfig, LogLevels, LogFormatters

# Create equivalent LogConfig
config = LogConfig(
    name="app",
    log_level=LogLevels.INFO,
    verbosity=0,
    formatter_style=LogFormatterStyleChoices.PERCENT,
    format="%(levelname)s: %(message)s",
    formatter_type=LogFormatters.DEFAULT,
    console_handler=ConsoleHandlers.DEFAULT,
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="app.log"),
            format_override="%(asctime)s - %(levelname)s - %(message)s"
        )
    ]
)

logger = Log.create_logger("app", config=config)
```

### Factory-Based Systems

**Before (Custom factory):**
```python
class LoggerFactory:
    @staticmethod
    def create_logger(name, level="INFO", handlers=None):
        # Custom implementation
        pass

logger = LoggerFactory.create_logger("app", level="DEBUG", handlers=["console", "file"])
```

**After:**
```python
# Direct replacement
logger = Log.create_logger(
    "app",
    log_level=LogLevels.DEBUG,
    console_handler_type=ConsoleHandlers.RICH,
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="app.log")
        )
    ]
)

# Or create wrapper for compatibility
class LoggerFactory:
    @staticmethod
    def create_logger(name, level="INFO", handlers=None):
        log_level = getattr(LogLevels, level.upper())

        file_handlers = []
        console_handler = ConsoleHandlers.DEFAULT

        if handlers:
            if "file" in handlers:
                file_handlers.append(
                    FileHandlerSpec(
                        handler_type=FileHandlerTypes.FILE,
                        config=FileHandlerSettings(filename=f"{name}.log")
                    )
                )
            if "rich" in handlers:
                console_handler = ConsoleHandlers.RICH

        return Log.create_logger(
            name,
            log_level=log_level,
            console_handler_type=console_handler,
            file_handlers=file_handlers if file_handlers else None
        )
```

## 📋 Migration Checklist

### Pre-Migration

- [ ] **Audit current logging usage** - Identify all loggers and handlers
- [ ] **Document current configuration** - Note formats, levels, file locations
- [ ] **Identify dependencies** - Check if Rich is available/installable
- [ ] **Plan testing strategy** - How to verify migration success
- [ ] **Backup current logs** - Preserve existing log data

### During Migration

- [ ] **Install dependencies** - `pip install rich` if using Rich features
- [ ] **Update imports** - Replace old logging imports
- [ ] **Convert configuration** - Transform to new format
- [ ] **Update logger creation** - Use `Log.create_logger()`
- [ ] **Test basic functionality** - Verify logging works
- [ ] **Test file handlers** - Verify file logging and rotation
- [ ] **Test Rich features** - If using Rich integration

### Post-Migration

- [ ] **Verify log output** - Check console and file output
- [ ] **Test error handling** - Ensure graceful fallbacks work
- [ ] **Performance testing** - Check for performance regressions
- [ ] **Update documentation** - Document new logging setup
- [ ] **Train team** - Ensure team understands new system

## 🔄 Gradual Migration Strategy

### Phase 1: Basic Replacement

```python
# Replace basic loggers first
# Before
logger = logging.getLogger('myapp')

# After
logger = Log.create_logger('myapp')
```

### Phase 2: Add Rich Features

```python
# Enhance with Rich features
logger = Log.create_logger(
    'myapp',
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)

# Start using Rich features gradually
logger.info("Starting process...")
logger.table(data, title="Configuration")
```

### Phase 3: File Handlers

```python
# Add file logging
logger = Log.create_logger(
    'myapp',
    console_handler_type=ConsoleHandlers.RICH,
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(filename="app.log")
        )
    ]
)
```

### Phase 4: Advanced Features

```python
# Add advanced features like multiple files, custom formats
logger = Log.create_logger(
    'myapp',
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(
        show_time=True,
        rich_tracebacks=True
    ),
    file_handlers=[
        # Multiple specialized log files
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(filename="app.log"),
            format_override="%(asctime)s | %(levelname)s | %(message)s"
        ),
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(filename="audit.log", when='midnight'),
            format_override='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
    ],
    rich_features=RichFeatureSettings(enabled=True)
)
```

## 🧪 Testing Migration

### Compatibility Tests

```python
def test_migration_compatibility():
    """Test that migrated logger works like old logger."""
    # Old logger behavior
    old_logger = logging.getLogger('test')

    # New logger
    new_logger = Log.create_logger('test')

    # Test basic methods exist
    assert hasattr(new_logger, 'info')
    assert hasattr(new_logger, 'warning')
    assert hasattr(new_logger, 'error')

    # Test they work
    new_logger.info("Test message")
    new_logger.warning("Test warning")
    new_logger.error("Test error")
```

### Output Comparison

```python
def test_output_format():
    """Compare output format before and after migration."""
    import io
    import sys

    # Capture output
    captured_output = io.StringIO()

    # Test new logger output
    logger = Log.create_logger(
        'test',
        console_handler_type=ConsoleHandlers.DEFAULT,
        format="%(levelname)s: %(message)s"
    )

    # Redirect stdout temporarily
    old_stdout = sys.stdout
    sys.stdout = captured_output

    logger.info("Test message")

    sys.stdout = old_stdout
    output = captured_output.getvalue()

    # Verify format matches expectations
    assert "INFO: Test message" in output
```

## 📝 Migration Best Practices

1. **Start Small** - Migrate one component at a time
2. **Test Thoroughly** - Verify each migration step
3. **Keep Backups** - Preserve original code and logs
4. **Document Changes** - Record what was changed and why
5. **Train Users** - Ensure team understands new features
6. **Monitor Performance** - Watch for performance impacts
7. **Plan Rollback** - Have a way to revert if needed
8. **Use Type Hints** - Take advantage of improved type safety

## 🆘 Migration Support

If you encounter issues during migration:

1. **Check the Troubleshooting Guide** - Common issues and solutions
2. **Review API Reference** - Verify correct usage
3. **Test with minimal configuration** - Isolate problems
4. **Compare with examples** - Use provided examples as reference
5. **Check dependencies** - Ensure all required packages are installed

Remember: Migration can be done gradually, and the new system is designed to be more powerful while remaining familiar to users of standard Python logging.
