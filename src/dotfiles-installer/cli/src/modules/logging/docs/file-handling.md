# File Handling Guide

Comprehensive guide to file logging, rotation strategies, and file management in the logging module.

## 📁 File Handler Overview

The logging module supports three types of file handlers:

1. **FileHandler** - Basic file logging
2. **RotatingFileHandler** - Size-based rotation
3. **TimedRotatingFileHandler** - Time-based rotation

All file handlers are configured through type-safe settings classes and can be used simultaneously.

## 🔧 Basic File Logging

### Simple File Handler

```python
from cli.modules.logging import (
    Log, FileHandlerSpec, FileHandlerTypes, FileHandlerSettings
)

# Basic file logging
logger = Log.create_logger(
    "app",
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(
                filename="app.log",
                mode='a',           # 'a' for append, 'w' for overwrite
                encoding='utf-8',
                delay=False         # Open file immediately
            )
        )
    ]
)

logger.info("This message goes to app.log")
```

### FileHandlerSettings Options

```python
@dataclass
class FileHandlerSettings:
    filename: str                    # Required: Path to log file
    mode: str = 'a'                 # File open mode ('a' append, 'w' write)
    encoding: str = 'utf-8'         # File encoding
    delay: bool = False             # Delay file opening until first log
```

**Mode Options:**
- `'a'` - Append to existing file (default)
- `'w'` - Overwrite file on each run
- `'x'` - Create new file, fail if exists

**Delay Option:**
- `False` - Open file immediately when handler created
- `True` - Open file only when first log message is written

## 🔄 Rotating File Handler

### Size-Based Rotation

```python
from cli.modules.logging import RotatingFileHandlerSettings

# Rotating file handler
logger = Log.create_logger(
    "app",
    file_handlers=[
        FileHandlerSpec(
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
    ]
)
```

### How Rotation Works

When `app.log` reaches 10MB:
1. `app.log` → `app.log.1`
2. `app.log.1` → `app.log.2`
3. `app.log.2` → `app.log.3`
4. `app.log.3` → `app.log.4`
5. `app.log.4` → `app.log.5`
6. `app.log.5` is deleted
7. New `app.log` is created

### RotatingFileHandlerSettings Options

```python
@dataclass
class RotatingFileHandlerSettings:
    filename: str                    # Required: Path to log file
    max_bytes: int = 10_485_760     # Max file size (10MB default)
    backup_count: int = 5           # Number of backup files to keep
    mode: str = 'a'                 # File open mode
    encoding: str = 'utf-8'         # File encoding
    delay: bool = False             # Delay file opening
```

**Size Examples:**
```python
# 1MB
max_bytes=1_048_576

# 5MB
max_bytes=5_242_880

# 50MB
max_bytes=52_428_800

# 100MB
max_bytes=104_857_600
```

## ⏰ Timed Rotating File Handler

### Time-Based Rotation

```python
from cli.modules.logging import TimedRotatingFileHandlerSettings

# Daily rotation
logger = Log.create_logger(
    "app",
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(
                filename="daily.log",
                when='midnight',       # Rotate at midnight
                interval=1,           # Every 1 day
                backup_count=30,      # Keep 30 days
                encoding='utf-8',
                delay=False,
                utc=False            # Use local time
            )
        )
    ]
)
```

### Rotation Schedules

```python
# Hourly rotation
TimedRotatingFileHandlerSettings(
    filename="hourly.log",
    when='H',           # Every hour
    interval=1,
    backup_count=24     # Keep 24 hours
)

# Weekly rotation (Sunday)
TimedRotatingFileHandlerSettings(
    filename="weekly.log",
    when='W6',          # Sunday (0=Monday, 6=Sunday)
    interval=1,
    backup_count=52     # Keep 52 weeks
)

# Every 6 hours
TimedRotatingFileHandlerSettings(
    filename="6hour.log",
    when='H',
    interval=6,         # Every 6 hours
    backup_count=28     # Keep 7 days worth
)
```

### TimedRotatingFileHandlerSettings Options

```python
@dataclass
class TimedRotatingFileHandlerSettings:
    filename: str                    # Required: Path to log file
    when: str = 'midnight'          # When to rotate
    interval: int = 1               # Interval between rotations
    backup_count: int = 7           # Number of backup files
    encoding: str = 'utf-8'         # File encoding
    delay: bool = False             # Delay file opening
    utc: bool = False              # Use UTC time for rotation
```

**When Options:**
- `'S'` - Seconds
- `'M'` - Minutes
- `'H'` - Hours
- `'D'` - Days
- `'midnight'` - Roll over at midnight
- `'W0'` to `'W6'` - Weekdays (0=Monday, 6=Sunday)

## 📊 Multiple File Handlers

### Different Files for Different Purposes

```python
logger = Log.create_logger(
    "app",
    file_handlers=[
        # Debug log - all messages, basic rotation
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="debug.log",
                max_bytes=50_000_000,  # 50MB
                backup_count=3
            )
        ),

        # Error log - errors only, longer retention
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="error.log",
                max_bytes=10_000_000,  # 10MB
                backup_count=10
            )
        ),

        # Audit log - daily rotation, long retention
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(
                filename="audit.log",
                when='midnight',
                backup_count=365       # Keep 1 year
            )
        ),

        # Performance log - hourly rotation
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(
                filename="performance.log",
                when='H',
                interval=1,
                backup_count=168       # Keep 1 week (24*7)
            )
        )
    ]
)
```

### Level-Specific File Handlers

```python
# Note: Currently all handlers receive all messages
# To filter by level, you would need custom handler implementation

class LevelFilterHandler(logging.Handler):
    def __init__(self, base_handler, min_level):
        super().__init__()
        self.base_handler = base_handler
        self.min_level = min_level

    def emit(self, record):
        if record.levelno >= self.min_level:
            self.base_handler.emit(record)

# Usage would require custom factory extension
```

## 🎨 Per-File Formatting

### Different Formats for Different Files

```python
logger = Log.create_logger(
    "app",
    format="%(asctime)s | %(levelname)s | %(message)s",  # Default format
    file_handlers=[
        # Detailed format for debugging
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="detailed.log"),
            format_override="%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
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
            config=FileHandlerSettings(filename="structured.log"),
            format_override='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        ),

        # CSV format for spreadsheet import
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="csv.log"),
            format_override="%(asctime)s,%(levelname)s,%(name)s,%(message)s"
        )
    ]
)
```

### Format Examples

**detailed.log:**
```
2025-10-01 13:02:29,836 | myapp | INFO | main.py:42 | main | Application started
```

**simple.log:**
```
INFO: Application started
```

**structured.log:**
```
{"timestamp": "2025-10-01 13:02:29,836", "level": "INFO", "logger": "myapp", "message": "Application started"}
```

**csv.log:**
```
2025-10-01 13:02:29,836,INFO,myapp,Application started
```

## 📂 File Organization Strategies

### Hierarchical Organization

```python
import os
from datetime import datetime

# Create date-based directory structure
today = datetime.now().strftime("%Y/%m/%d")
log_dir = f"logs/{today}"
os.makedirs(log_dir, exist_ok=True)

logger = Log.create_logger(
    "app",
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename=f"{log_dir}/app.log",
                max_bytes=10_000_000,
                backup_count=5
            )
        )
    ]
)
```

### Component-Based Organization

```python
# Different loggers for different components
components = ["api", "database", "auth", "cache"]

for component in components:
    logger = Log.create_logger(
        component,
        file_handlers=[
            FileHandlerSpec(
                handler_type=FileHandlerTypes.ROTATING_FILE,
                config=RotatingFileHandlerSettings(
                    filename=f"logs/{component}.log",
                    max_bytes=5_000_000,
                    backup_count=3
                )
            )
        ]
    )
```

### Environment-Based Organization

```python
import os

environment = os.getenv("ENVIRONMENT", "development")

logger = Log.create_logger(
    "app",
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
            config=TimedRotatingFileHandlerSettings(
                filename=f"logs/{environment}/app.log",
                when='midnight',
                backup_count=30 if environment == "production" else 7
            )
        )
    ]
)
```

## 🔍 File Handler Monitoring

### Log File Size Monitoring

```python
import os

def monitor_log_files(log_directory: str):
    """Monitor log file sizes."""
    for filename in os.listdir(log_directory):
        if filename.endswith('.log'):
            filepath = os.path.join(log_directory, filename)
            size = os.path.getsize(filepath)
            size_mb = size / (1024 * 1024)
            print(f"{filename}: {size_mb:.2f} MB")

# Usage
monitor_log_files("logs/")
```

### Rotation Status Check

```python
def check_rotation_status(base_filename: str):
    """Check how many rotated files exist."""
    import glob

    pattern = f"{base_filename}.*"
    rotated_files = glob.glob(pattern)

    print(f"Base file: {base_filename}")
    print(f"Rotated files: {len(rotated_files)}")

    for file in sorted(rotated_files):
        size = os.path.getsize(file)
        print(f"  {file}: {size / (1024*1024):.2f} MB")

# Usage
check_rotation_status("app.log")
```

## 🧹 Log File Cleanup

### Automated Cleanup Script

```python
import os
import time
from datetime import datetime, timedelta

def cleanup_old_logs(log_directory: str, days_to_keep: int = 30):
    """Remove log files older than specified days."""
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)

    for filename in os.listdir(log_directory):
        if filename.endswith('.log') or '.log.' in filename:
            filepath = os.path.join(log_directory, filename)

            if os.path.getmtime(filepath) < cutoff_time:
                print(f"Removing old log file: {filename}")
                os.remove(filepath)

def compress_old_logs(log_directory: str, days_to_compress: int = 7):
    """Compress log files older than specified days."""
    import gzip
    import shutil

    cutoff_time = time.time() - (days_to_compress * 24 * 60 * 60)

    for filename in os.listdir(log_directory):
        if filename.endswith('.log') and not filename.endswith('.gz'):
            filepath = os.path.join(log_directory, filename)

            if os.path.getmtime(filepath) < cutoff_time:
                compressed_path = f"{filepath}.gz"
                print(f"Compressing: {filename}")

                with open(filepath, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                os.remove(filepath)

# Usage
cleanup_old_logs("logs/", days_to_keep=30)
compress_old_logs("logs/", days_to_compress=7)
```

## ⚠️ File Handler Best Practices

1. **Use Rotation** - Always use rotating handlers to prevent huge files
2. **Monitor Disk Space** - Set appropriate backup_count values
3. **Separate by Purpose** - Different files for different types of logs
4. **Consider Performance** - File I/O can be slow, use appropriate buffering
5. **Handle Permissions** - Ensure log directory is writable
6. **Plan for Growth** - Consider log volume in production
7. **Backup Strategy** - Include log files in backup procedures
8. **Security** - Protect log files containing sensitive information

## 🚨 Common Issues and Solutions

### Permission Errors
```python
# Ensure directory exists and is writable
import os
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
os.chmod(log_dir, 0o755)
```

### Disk Space Issues
```python
# Monitor available space
import shutil
free_space = shutil.disk_usage("logs/").free
if free_space < 1_000_000_000:  # Less than 1GB
    print("Warning: Low disk space for logs")
```

### File Locking Issues
```python
# Use delay=True to avoid immediate file opening
FileHandlerSettings(
    filename="app.log",
    delay=True  # Open file only when needed
)
```

This comprehensive file handling system ensures robust, scalable logging with proper rotation and organization strategies.
