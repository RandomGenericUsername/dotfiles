# Dotfiles State Manager

Generic state persistence layer with SQLite and Redis backend support.

## Overview

The State Manager provides a **Redis-like API** for persistent state management, backed by either **SQLite** (default, zero dependencies) or **Redis** (optional, for high-performance scenarios).

This is a **generic abstraction layer** - not tied to any specific use case. Tools can use it however they need for state persistence.

## Features

- **Redis-like API**: Familiar interface with key-value, hash, list, and set operations
- **Multiple Backends**: SQLite (default) or Redis
- **TTL Support**: Automatic expiration of keys
- **Zero Dependencies**: SQLite backend uses Python stdlib only
- **Type-Safe**: Full type hints and Pydantic configuration
- **Context Manager**: Automatic resource cleanup

## Installation

```bash
# Install with SQLite backend (default)
cd src/common/modules/state-manager
uv sync

# Install with Redis backend support
uv sync --extra redis
```

## Quick Start

```python
from dotfiles_state_manager import StateManager

# Create state manager (uses SQLite by default)
state = StateManager()

# Key-value operations
state.set("my_key", "my_value")
value = state.get("my_key")  # "my_value"

# Hash operations (like Redis hashes)
state.hset("user:1", "name", "John")
state.hset("user:1", "email", "john@example.com")
user = state.hgetall("user:1")  # {"name": "John", "email": "john@example.com"}

# List operations
state.rpush("tasks", "task1")
state.rpush("tasks", "task2")
tasks = state.lrange("tasks", 0, -1)  # ["task1", "task2"]

# Set operations
state.sadd("tags", "python", "redis", "sqlite")
tags = state.smembers("tags")  # {"python", "redis", "sqlite"}

# TTL/Expiration
state.set("temp_key", "temp_value")
state.expire("temp_key", 3600)  # Expire in 1 hour
ttl = state.ttl("temp_key")  # Remaining seconds

# Cleanup
state.close()
```

## Configuration

### Using Configuration Files

Create `config/settings.toml` or `~/.config/state-manager/settings.toml`:

```toml
[state_manager]
backend = "sqlite"  # or "redis"
state_dir = "~/.local/share/dotfiles"

[state_manager.sqlite]
db_path = "~/.local/share/dotfiles/state.db"
wal_mode = true
auto_cleanup_enabled = true
cleanup_interval_days = 7

[state_manager.redis]
host = "localhost"
port = 6379
db = 0
password = ""
key_prefix = "dotfiles:"
```

### Using Code

```python
from dotfiles_state_manager import StateManager, StateManagerConfig, SQLiteConfig
from pathlib import Path

# Custom SQLite configuration
config = StateManagerConfig(
    backend="sqlite",
    sqlite=SQLiteConfig(
        db_path=Path("/custom/path/state.db"),
        wal_mode=True,
    )
)
state = StateManager(config=config)

# Or use a specific backend directly
from dotfiles_state_manager import SQLiteBackend

backend = SQLiteBackend(db_path=Path("custom.db"))
state = StateManager(backend=backend)
```

## API Reference

### Key-Value Operations

```python
state.set(key, value)              # Store value
state.get(key, default=None)       # Retrieve value
state.delete(key)                  # Delete key
state.exists(key)                  # Check if key exists
state.keys(pattern=None)           # List keys (supports glob patterns)
```

### Hash Operations

```python
state.hset(hash_key, field, value)      # Set field in hash
state.hget(hash_key, field, default)    # Get field from hash
state.hgetall(hash_key)                 # Get all fields
state.hdel(hash_key, field)             # Delete field
state.hexists(hash_key, field)          # Check if field exists
```

### List Operations

```python
state.lpush(list_key, value)            # Prepend to list
state.rpush(list_key, value)            # Append to list
state.lrange(list_key, start, end)      # Get range of elements
state.llen(list_key)                    # Get list length
state.lpop(list_key)                    # Remove and return first element
state.rpop(list_key)                    # Remove and return last element
```

### Set Operations

```python
state.sadd(set_key, *values)            # Add values to set
state.smembers(set_key)                 # Get all members
state.sismember(set_key, value)         # Check if value in set
state.srem(set_key, *values)            # Remove values from set
state.scard(set_key)                    # Get set size
```

### TTL/Expiration Operations

```python
state.expire(key, seconds)              # Set expiration
state.ttl(key)                          # Get remaining TTL
state.persist(key)                      # Remove expiration
```

### Maintenance Operations

```python
state.cleanup_expired()                 # Remove expired keys
state.clear_all()                       # Clear all data (dangerous!)
state.close()                           # Close connection
```

## Usage Examples

### Wallpaper Cache Manager

```python
from dotfiles_state_manager import StateManager
from pathlib import Path
from datetime import datetime

class WallpaperCacheManager:
    def __init__(self):
        self.state = StateManager()
    
    def is_cached(self, wallpaper_path: Path) -> bool:
        key = f"wallpaper:cache:{wallpaper_path}"
        return self.state.exists(key)
    
    def cache_wallpaper(self, wallpaper_path: Path, metadata: dict):
        key = f"wallpaper:cache:{wallpaper_path}"
        self.state.hset(key, "effects_dir", str(metadata['effects_dir']))
        self.state.hset(key, "cached_at", datetime.now().isoformat())
        self.state.expire(key, 30 * 86400)  # 30 days
    
    def get_cache_info(self, wallpaper_path: Path) -> dict:
        key = f"wallpaper:cache:{wallpaper_path}"
        return self.state.hgetall(key)
```

### Component Installation Tracker

```python
from dotfiles_state_manager import StateManager
from datetime import datetime

class ComponentInstaller:
    def __init__(self):
        self.state = StateManager()
    
    def mark_installed(self, component: str, version: str):
        self.state.hset(f"component:{component}", "version", version)
        self.state.hset(f"component:{component}", "installed_at", 
                       datetime.now().isoformat())
    
    def is_installed(self, component: str) -> bool:
        return self.state.exists(f"component:{component}")
    
    def list_installed(self) -> list[str]:
        keys = self.state.keys("component:*")
        return [k.replace("component:", "") for k in keys]
```

### System State Tracking

```python
from dotfiles_state_manager import StateManager
from pathlib import Path

class SystemStateTracker:
    def __init__(self):
        self.state = StateManager()
    
    def set_current_wallpaper(self, monitor: str, path: Path):
        self.state.hset("current_wallpapers", monitor, str(path))
    
    def get_current_wallpaper(self, monitor: str) -> Path | None:
        value = self.state.hget("current_wallpapers", monitor)
        return Path(value) if value else None
    
    def get_all_wallpapers(self) -> dict[str, Path]:
        data = self.state.hgetall("current_wallpapers")
        return {k: Path(v) for k, v in data.items()}
```

## Backend Comparison

| Feature | SQLite | Redis |
|---------|--------|-------|
| Dependencies | None (stdlib) | redis-py |
| Setup | Automatic | Requires Redis server |
| Performance | Good (disk I/O) | Excellent (in-memory) |
| Persistence | File-based | Optional (RDB/AOF) |
| TTL | Manual cleanup | Automatic |
| Concurrency | Good (WAL mode) | Excellent |
| Use Case | Default, simple | High-performance |

## Development

```bash
# Install dependencies
make install

# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run tests
make test

# Run all checks
make all-checks
```

## Architecture

```
state-manager/
├── src/dotfiles_state_manager/
│   ├── __init__.py           # Main exports
│   ├── manager.py            # StateManager facade
│   ├── backends/
│   │   ├── base.py           # Abstract backend interface
│   │   ├── sqlite_backend.py # SQLite implementation
│   │   └── redis_backend.py  # Redis implementation
│   └── config/
│       ├── config.py         # Pydantic models
│       └── settings.py       # Settings loader
├── config/
│   └── settings.toml         # Default configuration
└── tests/                    # Test suite
```

## License

Part of the dotfiles project.

