# Dotfiles State Management System - Design Concern

**Date:** 2025-11-08
**Project:** Dotfiles System
**Concern Type:** Infrastructure / Cross-Cutting Concern
**Scope:** System-Wide

---

## Executive Summary

This document outlines the design concern for implementing a **persistent state management system** for the dotfiles project. The system needs to track various runtime states, settings, and metadata across the entire dotfiles ecosystem to enable features like caching, state tracking, and intelligent decision-making.

---

## Problem Statement

### Current Situation

The dotfiles system currently operates in a **mostly stateless manner**:

- **Configuration:** Managed via TOML files (dynaconf + Pydantic)
- **Runtime State:** Exists only in memory during execution
- **Persistence:** Limited to file system artifacts (generated files, logs)
- **No Memory:** System cannot remember:
  - What wallpapers have been processed
  - When components were last updated
  - User preferences that aren't in config files
  - Historical data (usage patterns, errors, etc.)
  - Cross-session state

### User Need

> "My dotfiles system needs to keep track of several statuses in my system, things that I need to set, so I need some way that my dotfiles have 'memory'"

### Specific Use Cases

#### 1. Wallpaper Cache Management (Primary Driver)
- Track which wallpapers have been processed
- Store metadata about cached wallpapers (when cached, which backend, etc.)
- Enable fast cache lookups without scanning filesystem

#### 2. Installation State Tracking
- Track which components are installed
- Remember installation timestamps
- Store component versions
- Track configuration overrides applied

#### 3. System State Monitoring
- Current wallpaper per monitor
- Active color scheme
- Last successful backup
- Component health status

#### 4. User Preferences & History
- Recently used wallpapers
- Favorite configurations
- Command history
- Error history for debugging

---

## Current Architecture Context

### Existing Configuration System

The project uses a **hierarchical configuration system**:

```
Configuration Hierarchy (highest to lowest priority):
1. CLI arguments (runtime)
2. User settings.toml (project root)
3. Project settings.toml (component/config)
4. defaults.toml (component/config)
```

**Technology Stack:**
- **Dynaconf:** TOML file loading with merging
- **Pydantic:** Type-safe configuration models
- **File-based:** All configuration stored in TOML files

**Example:**
```python
# src/dotfiles-installer/cli/src/config/settings.py
class SettingsModel:
    def __init__(self, settings_files: list[str] | None = None):
        self.dynaconf_settings: Dynaconf = Dynaconf(
            settings_files=settings_files,
            merge_enabled=True,
        )
        self.settings: PydanticAppConfig = self.get_pydantic_config(...)
```

### Current "State" Locations

#### 1. File System Artifacts
```
~/.cache/
├── wallpaper/effects/     # Generated effect variants
├── colorscheme/           # Generated color schemes
└── dotfiles/logs/         # Application logs
```

#### 2. Configuration Files
```
~/Development/new/
├── settings.toml          # User overrides
└── src/dotfiles-installer/cli/config/
    └── defaults.toml      # Default settings
```

#### 3. Runtime Memory
- Pipeline context (during execution)
- Logger state
- Container manager state
- Hyprpaper pool state (in-memory only)

---

## Proposed Solutions

### Option 1: Redis (Lightweight In-Memory Database)

**Overview:** Use Redis as an in-memory key-value store with optional persistence.

#### Architecture
```python
# State management interface
from redis import Redis

class DotfilesStateManager:
    def __init__(self):
        self.redis = Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

    # Wallpaper cache
    def is_wallpaper_cached(self, wallpaper_path: Path) -> bool:
        key = f"wallpaper:cache:{wallpaper_path}"
        return self.redis.exists(key)

    def cache_wallpaper(self, wallpaper_path: Path, metadata: dict):
        key = f"wallpaper:cache:{wallpaper_path}"
        self.redis.hset(key, mapping=metadata)
        self.redis.expire(key, 86400 * 30)  # 30 days TTL

    # System state
    def set_current_wallpaper(self, monitor: str, wallpaper: Path):
        self.redis.hset("system:wallpapers", monitor, str(wallpaper))

    def get_current_wallpaper(self, monitor: str) -> Path | None:
        result = self.redis.hget("system:wallpapers", monitor)
        return Path(result) if result else None
```

#### Data Structure Examples
```
# Wallpaper cache
wallpaper:cache:/path/to/wallpaper.png -> {
    "cached_at": "2025-11-08T10:30:00",
    "effects_dir": "~/.cache/wallpaper/effects/wallpaper",
    "colorscheme_dir": "~/.cache/colorscheme/wallpaper",
    "backend": "pywal",
    "effect_count": 8,
    "valid": "true"
}

# System state
system:wallpapers -> {
    "DP-1": "/path/to/wallpaper1.png",
    "HDMI-1": "/path/to/wallpaper2.png"
}

# Installation state
component:installed:hyprpaper-manager -> {
    "installed_at": "2025-11-08T09:00:00",
    "version": "1.0.0",
    "config_overrides": "..."
}
```

#### Pros
- ✅ **Fast:** In-memory operations (microsecond latency)
- ✅ **Rich data types:** Hashes, sets, sorted sets, lists
- ✅ **TTL support:** Automatic expiration
- ✅ **Pub/Sub:** Can notify components of state changes
- ✅ **Persistence options:** RDB snapshots or AOF logs
- ✅ **Mature ecosystem:** Well-documented, widely used
- ✅ **Python client:** `redis-py` is excellent

#### Cons
- ❌ **External dependency:** Requires Redis server running
- ❌ **Setup complexity:** User needs to install/configure Redis
- ❌ **Overkill:** May be too heavy for simple use cases
- ❌ **Memory usage:** Keeps all data in RAM
- ❌ **Single point of failure:** If Redis down, state unavailable

#### Installation Requirements
```bash
# System package
sudo pacman -S redis  # Arch
sudo apt install redis-server  # Debian/Ubuntu

# Python client
uv add redis

# Start Redis
systemctl start redis
```

---

### Option 2: SQLite (Embedded Relational Database)

**Overview:** Use SQLite as a lightweight embedded database with SQL interface.

#### Architecture
```python
import sqlite3
from pathlib import Path
from datetime import datetime

class DotfilesStateManager:
    def __init__(self, db_path: Path = Path.home() / ".local/share/dotfiles/state.db"):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS wallpaper_cache (
                wallpaper_path TEXT PRIMARY KEY,
                cached_at TIMESTAMP,
                effects_dir TEXT,
                colorscheme_dir TEXT,
                backend TEXT,
                effect_count INTEGER,
                valid BOOLEAN
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP
            )
        """)

        self.conn.commit()

    def is_wallpaper_cached(self, wallpaper_path: Path) -> bool:
        cursor = self.conn.execute(
            "SELECT valid FROM wallpaper_cache WHERE wallpaper_path = ?",
            (str(wallpaper_path),)
        )
        result = cursor.fetchone()
        return result and result[0]

    def cache_wallpaper(self, wallpaper_path: Path, metadata: dict):
        self.conn.execute("""
            INSERT OR REPLACE INTO wallpaper_cache
            (wallpaper_path, cached_at, effects_dir, colorscheme_dir, backend, effect_count, valid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(wallpaper_path),
            datetime.now(),
            metadata['effects_dir'],
            metadata['colorscheme_dir'],
            metadata['backend'],
            metadata['effect_count'],
            True
        ))
        self.conn.commit()
```

#### Schema Design
```sql
-- Wallpaper cache
CREATE TABLE wallpaper_cache (
    wallpaper_path TEXT PRIMARY KEY,
    wallpaper_hash TEXT,
    cached_at TIMESTAMP,
    effects_dir TEXT,
    colorscheme_dir TEXT,
    backend TEXT,
    effect_count INTEGER,
    colorscheme_formats TEXT,  -- JSON array
    valid BOOLEAN,
    last_validated TIMESTAMP
);

-- System state (key-value)
CREATE TABLE system_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
);

-- Component installation
CREATE TABLE component_installed (
    component_name TEXT PRIMARY KEY,
    installed_at TIMESTAMP,
    version TEXT,
    config_overrides TEXT  -- JSON
);

-- History/audit log
CREATE TABLE event_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP,
    event_type TEXT,
    component TEXT,
    details TEXT  -- JSON
);
```

#### Pros
- ✅ **Zero dependencies:** SQLite included in Python stdlib
- ✅ **No server:** Embedded database (just a file)
- ✅ **ACID transactions:** Data integrity guarantees
- ✅ **SQL interface:** Powerful queries, joins, aggregations
- ✅ **Portable:** Single file database
- ✅ **Mature:** Battle-tested, stable
- ✅ **Low overhead:** Minimal memory/CPU usage

#### Cons
- ❌ **Slower than Redis:** Disk I/O vs in-memory
- ❌ **No TTL:** Need to implement expiration manually
- ❌ **No pub/sub:** Can't notify components of changes
- ❌ **Schema management:** Need migrations for schema changes
- ❌ **Concurrency:** Write locks (not an issue for single-user dotfiles)

#### Installation Requirements
```bash
# No system packages needed (Python stdlib)

# Optional: Better Python interface
uv add sqlalchemy  # ORM (optional)
```

---

### Option 3: JSON/TOML Files (Lightweight File-Based)

**Overview:** Use structured files (JSON/TOML) for state persistence.

#### Architecture
```python
import json
from pathlib import Path
from datetime import datetime
from typing import Any

class DotfilesStateManager:
    def __init__(self, state_dir: Path = Path.home() / ".local/share/dotfiles"):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.wallpaper_cache_file = state_dir / "wallpaper_cache.json"
        self.system_state_file = state_dir / "system_state.json"

    def _load_json(self, file: Path) -> dict:
        if file.exists():
            return json.loads(file.read_text())
        return {}

    def _save_json(self, file: Path, data: dict):
        file.write_text(json.dumps(data, indent=2, default=str))

    def is_wallpaper_cached(self, wallpaper_path: Path) -> bool:
        cache = self._load_json(self.wallpaper_cache_file)
        key = str(wallpaper_path)
        return key in cache and cache[key].get('valid', False)

    def cache_wallpaper(self, wallpaper_path: Path, metadata: dict):
        cache = self._load_json(self.wallpaper_cache_file)
        cache[str(wallpaper_path)] = {
            **metadata,
            'cached_at': datetime.now().isoformat(),
            'valid': True
        }
        self._save_json(self.wallpaper_cache_file, cache)
```

#### File Structure
```
~/.local/share/dotfiles/
├── wallpaper_cache.json
├── system_state.json
├── component_state.json
└── event_log.jsonl  # JSON Lines for append-only log
```

#### Example Files
```json
// wallpaper_cache.json
{
  "/home/user/wallpapers/mountain.png": {
    "cached_at": "2025-11-08T10:30:00",
    "effects_dir": "~/.cache/wallpaper/effects/mountain",
    "colorscheme_dir": "~/.cache/colorscheme/mountain",
    "backend": "pywal",
    "effect_count": 8,
    "valid": true
  }
}

// system_state.json
{
  "current_wallpapers": {
    "DP-1": "/home/user/wallpapers/mountain.png",
    "HDMI-1": "/home/user/wallpapers/beach.png"
  },
  "last_backup": "2025-11-08T09:00:00",
  "active_colorscheme": "pywal"
}
```

#### Pros
- ✅ **Zero dependencies:** Pure Python stdlib
- ✅ **Simple:** Easy to understand and debug
- ✅ **Human-readable:** Can manually inspect/edit
- ✅ **Version control friendly:** Can commit state files
- ✅ **No setup:** Just works
- ✅ **Portable:** Works anywhere

#### Cons
- ❌ **Slow for large datasets:** Load entire file for each operation
- ❌ **No transactions:** Risk of corruption on crash
- ❌ **No indexing:** Linear search for queries
- ❌ **Concurrency issues:** Race conditions with multiple processes
- ❌ **No TTL:** Need manual cleanup
- ❌ **Limited query capabilities:** No SQL-like queries

---

### Option 4: Hybrid Approach (Recommended)

**Overview:** Combine file-based state with optional Redis for performance.

#### Architecture
```python
class DotfilesStateManager:
    def __init__(self, use_redis: bool = False):
        self.file_backend = FileStateBackend()
        self.redis_backend = RedisStateBackend() if use_redis else None

    def is_wallpaper_cached(self, wallpaper_path: Path) -> bool:
        # Try Redis first (fast)
        if self.redis_backend:
            result = self.redis_backend.is_wallpaper_cached(wallpaper_path)
            if result is not None:
                return result

        # Fallback to file (slower but always available)
        return self.file_backend.is_wallpaper_cached(wallpaper_path)

    def cache_wallpaper(self, wallpaper_path: Path, metadata: dict):
        # Write to both backends
        self.file_backend.cache_wallpaper(wallpaper_path, metadata)
        if self.redis_backend:
            self.redis_backend.cache_wallpaper(wallpaper_path, metadata)
```

#### Configuration
```toml
[state_management]
# Backend: "file", "redis", or "hybrid"
backend = "file"

# File backend settings
file_backend.state_dir = "~/.local/share/dotfiles"
file_backend.format = "json"  # "json" or "toml"

# Redis backend settings (optional)
redis_backend.host = "localhost"
redis_backend.port = 6379
redis_backend.db = 0
redis_backend.enabled = false
```

#### Pros
- ✅ **Best of both worlds:** Fast when Redis available, works without it
- ✅ **Graceful degradation:** Falls back to file if Redis unavailable
- ✅ **Flexible:** Users can choose their preference
- ✅ **Future-proof:** Easy to add more backends

#### Cons
- ❌ **Complexity:** More code to maintain
- ❌ **Consistency:** Need to keep backends in sync
- ❌ **Configuration:** More options to configure

---

## Recommendation

### Phase 1: Start with SQLite (Option 2)

**Rationale:**
1. **Zero dependencies** - Works out of the box
2. **Good performance** - Fast enough for dotfiles use case
3. **ACID guarantees** - Data integrity
4. **SQL interface** - Powerful queries for future features
5. **Single file** - Easy backup/restore
6. **No server** - No setup complexity

**Implementation Priority:**
```python
# Minimal viable state manager
class DotfilesStateManager:
    """Lightweight state management using SQLite."""

    def __init__(self, db_path: Path | None = None):
        if db_path is None:
            db_path = Path.home() / ".local/share/dotfiles/state.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_schema()

    # Core methods for wallpaper caching
    def is_wallpaper_cached(self, wallpaper_path: Path) -> bool: ...
    def cache_wallpaper(self, wallpaper_path: Path, metadata: dict): ...
    def invalidate_wallpaper_cache(self, wallpaper_path: Path): ...

    # System state methods
    def set_state(self, key: str, value: Any): ...
    def get_state(self, key: str) -> Any: ...
```

### Phase 2: Add Redis Support (Optional)

If performance becomes an issue or advanced features needed:
- Add Redis backend as optional dependency
- Implement hybrid approach
- Keep SQLite as fallback

---

## Integration with Existing System

### 1. Module Structure

Create new module:
```
src/common/modules/state-manager/
├── src/
│   └── dotfiles_state_manager/
│       ├── __init__.py
│       ├── manager.py          # Main StateManager class
│       ├── backends/
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract backend interface
│       │   ├── sqlite.py       # SQLite backend
│       │   ├── file.py         # JSON/TOML backend
│       │   └── redis.py        # Redis backend (optional)
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       └── types.py
├── config/
│   └── settings.toml
├── pyproject.toml
├── Makefile
└── README.md
```

### 2. Configuration Integration

Add to root `settings.toml`:
```toml
[state_management]
enabled = true
backend = "sqlite"  # "sqlite", "file", "redis", or "hybrid"
db_path = "~/.local/share/dotfiles/state.db"

[state_management.cache]
# Wallpaper cache settings
wallpaper_cache_enabled = true
wallpaper_cache_ttl_days = 30

[state_management.cleanup]
# Automatic cleanup
auto_cleanup_enabled = true
cleanup_interval_days = 7
```

### 3. Usage in Tools

```python
# In wallpaper-cache-manager tool
from dotfiles_state_manager import StateManager

class WallpaperCacheManager:
    def __init__(self):
        self.state = StateManager()
        self.orchestrator = WallpaperOrchestrator()

    def process(self, wallpaper_path: Path) -> WallpaperResult:
        # Check state manager first
        if self.state.is_wallpaper_cached(wallpaper_path):
            logger.info("✓ Wallpaper found in cache")
            return self._load_from_cache(wallpaper_path)

        # Process and cache
        result = self.orchestrator.process(wallpaper_path)
        self.state.cache_wallpaper(wallpaper_path, {
            'effects_dir': str(result.effects_output_dir),
            'colorscheme_dir': str(result.colorscheme_output_dir),
            'backend': 'pywal',
            'effect_count': len(result.effect_variants),
        })

        return result
```

---

## Open Questions for Refinement

1. **State location:** Where should state database live?
   - `~/.local/share/dotfiles/` (XDG standard)
   - `~/.cache/dotfiles/` (cache-like data)
   - `~/.config/dotfiles/` (configuration-like)

2. **State scope:** What should be tracked?
   - Only wallpaper cache?
   - Full system state?
   - Historical data?

3. **State lifetime:** How long should state persist?
   - Forever (until manually cleared)?
   - TTL-based expiration?
   - LRU eviction?

4. **State migration:** How to handle schema changes?
   - Manual migration scripts?
   - Automatic migration on version bump?
   - Wipe and rebuild?

5. **State backup:** Should state be backed up?
   - Include in dotfiles backup?
   - Separate backup mechanism?
   - Ephemeral (can be rebuilt)?

6. **Multi-user:** Should state be per-user or system-wide?
   - Per-user (current assumption)
   - System-wide (shared cache)

---

## Success Criteria

### Functional Requirements
- ✅ Persist state across sessions
- ✅ Fast lookups (<10ms for cache checks)
- ✅ Data integrity (no corruption)
- ✅ Easy to inspect/debug
- ✅ Automatic cleanup of stale data

### Non-Functional Requirements
- ✅ Zero or minimal dependencies
- ✅ Simple setup (ideally automatic)
- ✅ Low resource usage (<10MB memory, <100MB disk)
- ✅ Reliable (handles crashes gracefully)

---

## Next Steps

1. **Decide on backend** (Recommendation: SQLite)
2. **Design schema** (wallpaper cache + system state tables)
3. **Implement state manager module** (following existing module patterns)
4. **Add configuration** (settings.toml integration)
5. **Integrate with wallpaper cache manager** (primary use case)
6. **Add CLI commands** (inspect state, clear cache, etc.)
7. **Document usage** (README, API docs)

---

## References

- Current configuration system: `src/dotfiles-installer/cli/src/config/`
- Module structure examples: `src/common/modules/`
- Dynaconf documentation: https://www.dynaconf.com/
- SQLite Python docs: https://docs.python.org/3/library/sqlite3.html
- Redis Python client: https://redis-py.readthedocs.io/
