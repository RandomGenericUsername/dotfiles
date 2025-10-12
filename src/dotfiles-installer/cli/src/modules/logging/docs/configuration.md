# Configuration Guide

Comprehensive guide to configuring the logging module for different use cases.

## 🎯 Configuration Overview

The logging module supports multiple configuration approaches:

1. **Direct Parameters** - Pass parameters to `Log.create_logger()`
2. **LogConfig Objects** - Use structured configuration objects
3. **Preset Configurations** - Pre-defined configurations for common scenarios
4. **Runtime Updates** - Dynamic configuration changes with `Log.update()`

## 📋 Configuration Hierarchy

Configuration parameters are applied in this order (later overrides earlier):

1. **Default values** from dataclass definitions
2. **LogConfig object** if provided
3. **Individual parameters** passed to create_logger/update
4. **Verbosity override** (if verbosity > 0, overrides log_level)

```python
# Example: config provides INFO, but verbosity=2 results in DEBUG
logger = Log.create_logger(
    "app",
    config=LogConfig(..., log_level=LogLevels.INFO),  # Step 2
    log_level=LogLevels.WARNING,                      # Step 3: overrides config
    verbosity=2                                       # Step 4: overrides log_level -> DEBUG
)
```

## 🔧 Core Configuration

### Log Levels

```python
from cli.modules.logging import LogLevels

# Direct log level
logger = Log.create_logger("app", log_level=LogLevels.DEBUG)

# Verbosity-based (overrides log_level)
logger = Log.create_logger("app", verbosity=2)  # Results in DEBUG
```

**Verbosity Mapping:**
- `0`: WARNING level
- `1`: INFO level
- `2`: DEBUG level
- `3+`: DEBUG level

### Format Styles

```python
from cli.modules.logging.log_types import LogFormatterStyleChoices

# Percent style (default)
logger = Log.create_logger(
    "app",
    formatter_style=LogFormatterStyleChoices.PERCENT,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Brace style
logger = Log.create_logger(
    "app",
    formatter_style=LogFormatterStyleChoices.BRACE,
    format="{asctime} | {levelname} | {message}"
)

# Dollar style
logger = Log.create_logger(
    "app",
    formatter_style=LogFormatterStyleChoices.DOLLAR,
    format="$asctime | $levelname | $message"
)
```

### Formatter Types

```python
from cli.modules.logging import LogFormatters

# Default formatter (plain text)
logger = Log.create_logger("app", formatter_type=LogFormatters.DEFAULT)

# Colored formatter (ANSI colors)
logger = Log.create_logger("app", formatter_type=LogFormatters.COLORED)

# Rich formatter (Rich markup to ANSI)
logger = Log.create_logger("app", formatter_type=LogFormatters.RICH)
```

## 🖥️ Console Configuration

### Console Handler Types

```python
from cli.modules.logging import ConsoleHandlers

# Default StreamHandler
logger = Log.create_logger("app", console_handler_type=ConsoleHandlers.DEFAULT)

# Rich Handler with enhanced features
logger = Log.create_logger("app", console_handler_type=ConsoleHandlers.RICH)
```

### Rich Handler Configuration

```python
from cli.modules.logging import RichHandlerSettings

# Basic Rich configuration
basic_settings = RichHandlerSettings(
    show_time=True,
    show_level=True,
    show_path=False,
    markup=True
)

# Development configuration
dev_settings = RichHandlerSettings(
    show_time=True,
    show_level=True,
    show_path=True,
    markup=True,
    rich_tracebacks=True,
    tracebacks_show_locals=True,
    keywords=['TODO', 'FIXME', 'DEBUG']
)

# Production configuration
prod_settings = RichHandlerSettings(
    show_time=True,
    show_level=True,
    show_path=False,
    markup=False,
    rich_tracebacks=False
)

logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=dev_settings
)
```

### Complete RichHandlerSettings Options

```python
RichHandlerSettings(
    # Core display
    show_time=True,                    # Show timestamp
    show_level=True,                   # Show log level
    show_path=True,                    # Show file path and line number
    markup=False,                      # Enable Rich markup processing

    # Time formatting
    omit_repeated_times=True,          # Omit repeated timestamps
    log_time_format="[%x %X]",         # Time format string

    # Path options
    enable_link_path=True,             # Make paths clickable

    # Highlighting
    keywords=None,                     # Keywords to highlight

    # Traceback configuration
    rich_tracebacks=False,             # Use Rich tracebacks
    tracebacks_width=None,             # Traceback width
    tracebacks_extra_lines=3,          # Extra context lines
    tracebacks_theme=None,             # Syntax highlighting theme
    tracebacks_show_locals=False,      # Show local variables

    # Local variable display
    locals_max_length=10,              # Max items in collections
    locals_max_string=80,              # Max string length
)
```

## 📁 File Handler Configuration

### Basic File Logging

```python
from cli.modules.logging import FileHandlerSpec, FileHandlerTypes, FileHandlerSettings

file_spec = FileHandlerSpec(
    handler_type=FileHandlerTypes.FILE,
    config=FileHandlerSettings(
        filename="app.log",
        mode='a',           # 'a' for append, 'w' for overwrite
        encoding='utf-8',
        delay=False         # Whether to delay file opening
    )
)

logger = Log.create_logger("app", file_handlers=[file_spec])
```

### Rotating File Handler

```python
from cli.modules.logging import RotatingFileHandlerSettings

rotating_spec = FileHandlerSpec(
    handler_type=FileHandlerTypes.ROTATING_FILE,
    config=RotatingFileHandlerSettings(
        filename="app.log",
        max_bytes=10_485_760,  # 10MB
        backup_count=5,        # Keep 5 backup files
        mode='a',
        encoding='utf-8',
        delay=False
    )
)
```

### Timed Rotating File Handler

```python
from cli.modules.logging import TimedRotatingFileHandlerSettings

timed_spec = FileHandlerSpec(
    handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
    config=TimedRotatingFileHandlerSettings(
        filename="daily.log",
        when='midnight',       # When to rotate
        interval=1,           # Interval between rotations
        backup_count=7,       # Keep 7 backup files
        encoding='utf-8',
        delay=False,
        utc=False            # Use UTC time for rotation
    )
)
```

**Valid 'when' values:**
- `'S'` - Seconds
- `'M'` - Minutes
- `'H'` - Hours
- `'D'` - Days
- `'midnight'` - Roll over at midnight
- `'W0'` to `'W6'` - Roll over on specific weekday (0=Monday, 6=Sunday)

### Multiple File Handlers

```python
logger = Log.create_logger(
    "app",
    file_handlers=[
        # Debug log - all messages
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="debug.log")
        ),
        # Application log - rotating
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="app.log",
                max_bytes=5_000_000,
                backup_count=3
            )
        ),
        # Daily audit log
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(
                filename="audit.log",
                when='midnight',
                backup_count=30
            )
        ),
    ]
)
```

### Per-File Custom Formatting

```python
logger = Log.create_logger(
    "app",
    format="%(asctime)s | %(levelname)s | %(message)s",  # Default format
    file_handlers=[
        # Detailed format for debugging
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="detailed.log"),
            format_override="%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
        ),
        # Simple format for production
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="simple.log"),
            format_override="%(levelname)s: %(message)s"
        ),
        # JSON format for log analysis
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="json.log"),
            format_override='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        ),
    ]
)
```

## 🎨 Rich Features Configuration

```python
from cli.modules.logging import RichFeatureSettings

rich_features = RichFeatureSettings(
    enabled=True,                    # Enable Rich features

    # Table defaults
    table_show_header=True,          # Show table headers
    table_show_lines=False,          # Show lines between rows
    table_expand=False,              # Expand tables to full width

    # Panel defaults
    panel_border_style="blue",       # Panel border color
    panel_box_style="rounded",       # Panel box style
    panel_expand=True,               # Expand panels to full width

    # Rule defaults
    rule_style="rule.line",          # Rule line style
    rule_align="center",             # Rule title alignment

    # Progress defaults
    progress_auto_refresh=True,      # Auto-refresh progress bars

    # Status defaults
    status_spinner="dots"            # Default spinner style
)

logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_features
)
```

## 📦 LogConfig Objects

### Creating LogConfig

```python
from cli.modules.logging import LogConfig

config = LogConfig(
    name="myapp",                                    # Required
    log_level=LogLevels.INFO,                       # Required
    verbosity=0,                                    # Required
    formatter_style=LogFormatterStyleChoices.PERCENT, # Required
    format="%(asctime)s | %(levelname)s | %(message)s", # Required
    formatter_type=LogFormatters.RICH,              # Required

    # Optional fields
    console_handler=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True),
    file_handlers=[...],
    colors=None,
    rich_features=RichFeatureSettings(enabled=True)
)

logger = Log.create_logger("myapp", config=config)
```

### Preset Configurations

```python
# Development preset
DEV_CONFIG = LogConfig(
    name="dev",
    log_level=LogLevels.DEBUG,
    verbosity=3,
    formatter_style=LogFormatterStyleChoices.BRACE,
    format="[{asctime}] {levelname:<8} {message}",
    formatter_type=LogFormatters.RICH,
    console_handler=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(
        show_path=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True
    ),
    rich_features=RichFeatureSettings(enabled=True)
)

# Production preset
PROD_CONFIG = LogConfig(
    name="prod",
    log_level=LogLevels.INFO,
    verbosity=0,
    formatter_style=LogFormatterStyleChoices.PERCENT,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    formatter_type=LogFormatters.COLORED,
    console_handler=ConsoleHandlers.DEFAULT,
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="app.log",
                max_bytes=10_000_000,
                backup_count=5
            )
        )
    ]
)

# Use presets
dev_logger = Log.create_logger("myapp", config=DEV_CONFIG)
prod_logger = Log.create_logger("myapp", config=PROD_CONFIG)

# Preset with overrides
logger = Log.create_logger(
    "myapp",
    config=DEV_CONFIG,
    log_level=LogLevels.WARNING  # Override preset's DEBUG
)
```

## 🔄 Runtime Configuration Updates

### Updating Existing Loggers

```python
# Create initial logger
logger = Log.create_logger("app", log_level=LogLevels.WARNING)

# Update log level
logger = Log.update("app", log_level=LogLevels.DEBUG)

# Update to Rich handler
logger = Log.update(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True)
)

# Add file logging
logger = Log.update(
    "app",
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(filename="runtime.log")
        )
    ]
)

# Update with new config
new_config = LogConfig(...)
logger = Log.update("app", config=new_config)

# Config with parameter overrides
logger = Log.update(
    "app",
    config=new_config,
    log_level=LogLevels.ERROR  # Override config's level
)
```

## 🎨 Color Configuration

### Custom Colors

```python
from cli.modules.logging import ColoredFormatterColors

class CustomColors(ColoredFormatterColors):
    DEBUG = "\033[94m"    # Light Blue
    INFO = "\033[92m"     # Light Green
    WARNING = "\033[93m"  # Light Yellow
    ERROR = "\033[91m"    # Light Red
    CRITICAL = "\033[95m" # Light Magenta

logger = Log.create_logger(
    "app",
    formatter_type=LogFormatters.COLORED,
    colors=CustomColors  # Pass class, not instance
)
```

## 🔍 Configuration Validation

All configuration objects validate their parameters:

```python
# This will raise ValueError
try:
    settings = RotatingFileHandlerSettings(
        filename="app.log",
        max_bytes=-1,  # Invalid: must be positive
        backup_count=-5  # Invalid: must be non-negative
    )
except ValueError as e:
    print(f"Configuration error: {e}")

# This will raise TypeError
try:
    logger = Log.create_logger(
        "app",
        colors=ColoredFormatterColors()  # Wrong: should be class, not instance
    )
except TypeError as e:
    print(f"Type error: {e}")
```

## 📝 Configuration Best Practices

1. **Use LogConfig for complex setups** - Better organization and reusability
2. **Create presets for environments** - Development, staging, production
3. **Validate early** - Use type hints and let dataclasses catch errors
4. **Separate concerns** - Different files for different purposes
5. **Use rotating handlers** - Prevent log files from growing too large
6. **Configure once, use everywhere** - Create loggers early and reuse
7. **Update dynamically** - Use `Log.update()` for runtime changes
