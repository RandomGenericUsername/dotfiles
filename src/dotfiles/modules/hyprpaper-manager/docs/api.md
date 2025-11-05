# API Reference

## HyprpaperManager

Main class for managing hyprpaper wallpapers.

### Constructor

```python
HyprpaperManager(config: HyprpaperConfig | None = None)
```

**Parameters:**
- `config`: Optional configuration. Uses defaults if None.

**Behavior:**
- Automatically creates `~/.config/hypr/hyprpaper.conf` if it doesn't exist and `auto_create_config` is enabled (default: True)
- The generated config file includes IPC settings and helpful comments
- Initializes wallpaper pool for memory management

### Status Methods

#### `is_running() -> bool`

Check if hyprpaper is running.

**Returns:** `True` if hyprpaper is running.

#### `get_status() -> HyprpaperStatus`

Get current hyprpaper status.

**Returns:** Status object with loaded/active wallpapers and monitors.

### Wallpaper Operations

#### `set(wallpaper, monitor="all", mode=WallpaperMode.COVER)`

Smart method that automatically preloads wallpaper if needed, then sets it. Manages pool size automatically.

**Smart Path Resolution:**
1. **Absolute path** (e.g., `/home/user/pics/mountain.jpg`) → Use directly
2. **Relative path** (e.g., `./mountain.jpg`, `../pics/mountain.jpg`) → Resolve from current directory
3. **Just a name** (e.g., `mountain.jpg`, `mountain`) → Search in configured wallpaper directories

**Parameters:**
- `wallpaper`: Wallpaper path or name (str or Path)
- `monitor`: Monitor name, "all", or "focused" (default: "all")
- `mode`: Display mode (default: WallpaperMode.COVER)

**Raises:**
- `WallpaperNotFoundError`: If wallpaper not found
- `WallpaperTooLargeError`: If wallpaper exceeds size limits
- `HyprpaperNotRunningError`: If hyprpaper not running
- `HyprpaperIPCError`: If IPC command fails

**Behavior:**
1. Validates wallpaper size against limits
2. Auto-preloads if not already in pool
3. Sets wallpaper on specified monitor(s)
4. Marks as displayed in pool
5. Cleans up pool if over size limit

**Example:**
```python
# Simple usage
manager.set("mountain.jpg")  # Auto-preloads, sets, manages pool

# Absolute path
manager.set("/home/user/Pictures/beach.png", monitor="DP-1")

# Relative path
manager.set("./wallpapers/pattern.png", mode=WallpaperMode.TILE)
```

#### `set_wallpaper(wallpaper, monitor="all", mode=WallpaperMode.COVER)`

Alias for `set()`. Provided for backwards compatibility.

#### `set_random_wallpaper(monitor="all", mode=WallpaperMode.COVER) -> Path`

Set random wallpaper.

**Parameters:**
- `monitor`: Monitor name, "all", or "focused" (default: "all")
- `mode`: Display mode (default: WallpaperMode.COVER)

**Returns:** Path to selected wallpaper.

#### `preload(wallpaper)`

Explicitly preload wallpaper into memory (for building pool).

**Parameters:**
- `wallpaper`: Wallpaper path or name (str or Path)

**Raises:**
- `WallpaperNotFoundError`: If wallpaper not found
- `WallpaperTooLargeError`: If wallpaper exceeds size limits

**Example:**
```python
# Preload multiple wallpapers for instant switching
manager.preload("wp1.jpg")
manager.preload("wp2.jpg")
manager.preload("wp3.jpg")

# Now switching is instant
manager.set("wp1.jpg")  # Fast!
manager.set("wp2.jpg")  # Fast!
```

#### `preload_wallpaper(wallpaper)`

Alias for `preload()`. Provided for backwards compatibility.

#### `unload(wallpaper)`

Unload wallpaper from memory.

**Parameters:**
- `wallpaper`: Wallpaper path or name (str or Path)

#### `unload_wallpaper(wallpaper)`

Alias for `unload()`. Provided for backwards compatibility.

#### `unload_unused() -> list[Path]`

Unload wallpapers not currently displayed.

**Returns:** List of wallpaper paths that were unloaded.

#### `unload_all() -> list[Path]`

Unload all wallpapers from memory.

**Returns:** List of wallpaper paths that were unloaded.

### Batch Operations

#### `preload_batch(wallpapers: list[Path | str])`

Preload multiple wallpapers at once.

**Parameters:**
- `wallpapers`: List of wallpaper paths or names

**Example:**
```python
manager.preload_batch(["wp1.jpg", "wp2.jpg", "wp3.jpg"])
```

#### `unload_batch(wallpapers: list[Path | str])`

Unload multiple wallpapers at once.

**Parameters:**
- `wallpapers`: List of wallpaper paths or names

### Pool Management

#### `get_pool_status() -> dict`

Get wallpaper pool status information.

**Returns:** Dictionary with:
- `preloaded_wallpapers`: List of preloaded wallpapers with details
- `total_size_mb`: Total size of pool in MB
- `max_size_mb`: Maximum pool size in MB
- `usage_percent`: Pool usage percentage
- `max_single_wallpaper_mb`: Maximum allowed single wallpaper size
- `is_over_limit`: Whether pool exceeds size limit

**Example:**
```python
status = manager.get_pool_status()
print(f"Pool: {status['total_size_mb']}MB / {status['max_size_mb']}MB")
print(f"Usage: {status['usage_percent']}%")
print(f"Wallpapers: {len(status['preloaded_wallpapers'])}")
```

### Monitor Operations

#### `get_monitors() -> list[MonitorInfo]`

Get all monitors.

**Returns:** List of monitor information.

#### `get_focused_monitor() -> MonitorInfo`

Get focused monitor.

**Returns:** Focused monitor information.

**Raises:**
- `MonitorNotFoundError`: If no focused monitor found

### Wallpaper Discovery

#### `list_wallpapers() -> list[Path]`

List available wallpapers in configured directories.

**Returns:** List of wallpaper paths.

#### `find_wallpaper(name) -> Path`

Find wallpaper by name or path with smart resolution.

**Smart Resolution:**
1. **Absolute path** → Use directly
2. **Relative path** (contains `/` or starts with `./` or `../`) → Resolve from current directory
3. **Just a name** → Search in configured wallpaper directories

**Parameters:**
- `name`: Wallpaper name or path

**Returns:** Resolved wallpaper path.

**Raises:**
- `WallpaperNotFoundError`: If wallpaper not found

**Examples:**
```python
# Just a name
manager.find_wallpaper("mountain.jpg")
manager.find_wallpaper("mountain")  # Auto-detects extension

# Absolute path
manager.find_wallpaper("/home/user/pics/beach.png")

# Relative path
manager.find_wallpaper("./wallpapers/forest.jpg")
```

## Types

### WallpaperMode

Enum for wallpaper display modes.

**Values:**
- `COVER`: Cover the monitor (default)
- `CONTAIN`: Contain within monitor
- `TILE`: Tile across monitor

### MonitorSelector

Enum for monitor selection.

**Values:**
- `ALL`: All monitors
- `FOCUSED`: Currently focused monitor
- `SPECIFIC`: Specific monitor by name

### MonitorInfo

Information about a monitor.

**Fields:**
- `name`: Monitor name (str)
- `description`: Monitor description (str | None)
- `focused`: Whether monitor is focused (bool)
- `current_wallpaper`: Current wallpaper path (Path | None)

### HyprpaperStatus

Current hyprpaper status.

**Fields:**
- `loaded_wallpapers`: List of loaded wallpaper paths
- `active_wallpapers`: Dict mapping monitor names to wallpaper paths
- `monitors`: List of MonitorInfo objects

## Configuration

### HyprpaperConfig

Configuration for hyprpaper manager.

**Fields:**
- `config_file`: Path to hyprpaper config file (default: ~/.config/hypr/hyprpaper.conf)
- `ipc_enabled`: Enable IPC control (default: True)
- `splash_enabled`: Enable Hyprland splash (default: False)
- `splash_offset`: Splash offset percentage (default: 2.0)
- `splash_color`: Splash color in ARGB (default: "55ffffff")
- `wallpaper_dirs`: List of directories to search for wallpapers
- `auto_unload_unused`: Automatically unload unused wallpapers (default: True)
- `auto_create_config`: Automatically create config file if missing (default: True)
- `max_preload_pool_mb`: Maximum memory (MB) for preloaded wallpapers pool (default: 100)
- `max_wallpaper_size_multiplier`: Max single wallpaper size = pool_size × multiplier (default: 2.0)

## ConfigManager

Manages hyprpaper configuration file creation and validation.

### `ensure_config_exists() -> bool`

Ensure config file exists, create if needed and `auto_create_config` is enabled.

**Returns:** `True` if config was created, `False` if already existed.

### `validate_config() -> tuple[bool, str]`

Validate config file exists and is readable.

**Returns:** Tuple of `(is_valid, error_message)`.

## Exceptions

### HyprpaperError

Base exception for all hyprpaper operations.

### HyprpaperNotRunningError

Raised when hyprpaper is not running.

### HyprpaperIPCError

Raised when IPC communication fails.

**Attributes:**
- `command`: Command that failed
- `exit_code`: Exit code of failed command

### WallpaperNotFoundError

Raised when wallpaper file doesn't exist.

### MonitorNotFoundError

Raised when monitor doesn't exist.

### WallpaperNotLoadedError

Raised when trying to use unloaded wallpaper.

### WallpaperTooLargeError

Raised when wallpaper exceeds maximum allowed size.

**Attributes:**
- `wallpaper_size_mb`: Size of the wallpaper in MB
- `max_allowed_mb`: Maximum allowed size in MB
