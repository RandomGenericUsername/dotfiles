# API Reference

## HyprpaperManager

Main class for managing hyprpaper wallpapers.

### Constructor

```python
HyprpaperManager(config: HyprpaperConfig | None = None)
```

**Parameters:**
- `config`: Optional configuration. Uses defaults if None.

### Status Methods

#### `is_running() -> bool`

Check if hyprpaper is running.

**Returns:** `True` if hyprpaper is running.

#### `get_status() -> HyprpaperStatus`

Get current hyprpaper status.

**Returns:** Status object with loaded/active wallpapers and monitors.

### Wallpaper Operations

#### `set_wallpaper(wallpaper, monitor="all", mode=WallpaperMode.COVER)`

Set wallpaper for monitor(s).

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
- `HyprpaperNotRunningError`: If hyprpaper not running
- `HyprpaperIPCError`: If IPC command fails

**Example:**
```python
# Just a name - searches in configured dirs
manager.set_wallpaper("mountain.jpg")

# Absolute path - uses directly
manager.set_wallpaper("/home/user/Pictures/beach.png", monitor="DP-1")

# Relative path - resolves from CWD
manager.set_wallpaper("./wallpapers/pattern.png", mode=WallpaperMode.TILE)

# Name without extension - auto-detects
manager.set_wallpaper("mountain")  # Finds mountain.jpg, mountain.png, etc.
```

#### `set_random_wallpaper(monitor="all", mode=WallpaperMode.COVER) -> Path`

Set random wallpaper.

**Parameters:**
- `monitor`: Monitor name, "all", or "focused" (default: "all")
- `mode`: Display mode (default: WallpaperMode.COVER)

**Returns:** Path to selected wallpaper.

**Example:**
```python
wallpaper = manager.set_random_wallpaper()
print(f"Set: {wallpaper}")
```

#### `preload_wallpaper(wallpaper)`

Preload wallpaper into memory.

**Parameters:**
- `wallpaper`: Wallpaper path or name (str or Path)

#### `unload_wallpaper(wallpaper)`

Unload wallpaper(s) from memory.

**Parameters:**
- `wallpaper`: Wallpaper path/name, "all", or "unused"

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
- `preload_on_set`: Preload before setting vs using reload (default: False)

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
