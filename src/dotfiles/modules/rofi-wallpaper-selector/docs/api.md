# API Documentation

## CLI Commands

### `rofi-wallpaper-selector wallpapers`

List wallpapers or handle wallpaper selection.

**Options:**
- `--monitor, -m`: Monitor to set wallpaper on (default: from config)
- `--config, -c`: Path to settings.toml (default: module config)

**Environment Variables:**
- `ROFI_RETV=0`: List mode - outputs wallpapers for rofi
- `ROFI_RETV=1`: Handle mode - processes selection from stdin

**Examples:**
```bash
# List wallpapers
ROFI_RETV=0 rofi-wallpaper-selector wallpapers

# Handle selection
echo "mountain" | ROFI_RETV=1 rofi-wallpaper-selector wallpapers --monitor DP-1
```

### `rofi-wallpaper-selector effects`

List effects or handle effect selection.

**Options:**
- `--monitor, -m`: Monitor to set wallpaper on (default: from config)
- `--config, -c`: Path to settings.toml (default: module config)

**Environment Variables:**
- `ROFI_RETV=0`: List mode - outputs effects for rofi
- `ROFI_RETV=1`: Handle mode - processes selection from stdin

**Examples:**
```bash
# List effects
ROFI_RETV=0 rofi-wallpaper-selector effects

# Handle selection
echo "blur" | ROFI_RETV=1 rofi-wallpaper-selector effects
```

## Python API

### Selectors

#### `list_wallpapers(config: AppConfig) -> None`

List all available wallpapers in rofi format.

**Parameters:**
- `config`: Application configuration

**Output:**
Prints to stdout in rofi format:
- With icons: `name\x00icon\x1f/path/to/image.png`
- Without icons: `name`

#### `list_effects(config: AppConfig, monitor: str) -> None`

List all available effects for current wallpaper.

**Parameters:**
- `config`: Application configuration
- `monitor`: Monitor name

**Output:**
Prints to stdout in rofi format with "off" option first, then available effects.

### Handlers

#### `handle_wallpaper_selection(selected: str, config: AppConfig, monitor: str) -> None`

Handle wallpaper selection.

**Parameters:**
- `selected`: Selected wallpaper name (without extension)
- `config`: Application configuration
- `monitor`: Monitor name

**Behavior:**
- Finds wallpaper file in wallpapers directory
- Calls dotfiles-manager with `generate_colorscheme=True, generate_effects=True`

#### `handle_effect_selection(selected: str, config: AppConfig, monitor: str) -> None`

Handle effect selection.

**Parameters:**
- `selected`: Selected effect name (or "off" for original)
- `config`: Application configuration
- `monitor`: Monitor name

**Behavior:**
- Gets current wallpaper from manager
- Handles "off" option (revert to original)
- Calls dotfiles-manager with `generate_colorscheme=True, generate_effects=False`

### Utilities

#### `format_rofi_item(label: str, icon_path: str | None) -> str`

Format item for rofi with icon.

**Parameters:**
- `label`: Item label
- `icon_path`: Path to icon image (or None for no icon)

**Returns:**
Formatted string for rofi

**Examples:**
```python
>>> format_rofi_item("wallpaper1", "/path/to/wallpaper1.png")
'wallpaper1\\x00icon\\x1f/path/to/wallpaper1.png'
>>> format_rofi_item("off", None)
'off'
```

#### `get_available_effects(wallpaper_name: str, effects_cache_dir: Path) -> list[str]`

Get list of effects that exist for a wallpaper.

**Parameters:**
- `wallpaper_name`: Name of the wallpaper (without extension)
- `effects_cache_dir`: Effects cache directory

**Returns:**
Sorted list of effect names (without .png extension)

**Examples:**
```python
>>> get_available_effects("mountain", Path("~/.cache/wallpaper-effects"))
['blur', 'grayscale', 'pixelate']
```

### Manager Client

#### `class ManagerClient`

Subprocess-based client for dotfiles-manager CLI.

**Methods:**

##### `__init__(manager_path: Path)`

Initialize manager client.

**Parameters:**
- `manager_path`: Path to dotfiles-manager module

**Raises:**
- `FileNotFoundError`: If manager CLI not found at `{manager_path}/.venv/bin/dotfiles-manager`

##### `get_current_wallpaper(monitor: str) -> Path | None`

Get current wallpaper path for monitor via subprocess call to `dotfiles-manager status`.

**Parameters:**
- `monitor`: Monitor name

**Returns:**
Path to current wallpaper or None if not set

**Implementation:**
- Calls: `dotfiles-manager status --monitor <monitor>`
- Parses table output to extract wallpaper path from column 2

##### `change_wallpaper(wallpaper_path: Path, monitor: str, generate_colorscheme: bool = True, generate_effects: bool = True) -> None`

Change wallpaper via subprocess call to `dotfiles-manager change-wallpaper`.

**Parameters:**
- `wallpaper_path`: Path to wallpaper image
- `monitor`: Monitor name
- `generate_colorscheme`: Whether to generate colorscheme
- `generate_effects`: Whether to generate effects

**Implementation:**
- Calls: `dotfiles-manager change-wallpaper <path> --monitor <monitor> [--colorscheme|--no-colorscheme] [--effects|--no-effects]`
- Runs in subprocess with manager's own venv

## Configuration API

### `load_config(config_file: Path | None = None) -> AppConfig`

Load configuration from TOML file.

**Parameters:**
- `config_file`: Path to settings.toml file. If None, uses default location.

**Returns:**
Validated AppConfig instance

### Configuration Models

#### `PathsConfig`

- `wallpapers_dir: Path` - Directory containing wallpapers
- `effects_cache_dir: Path` - Directory containing wallpaper effects cache
- `dotfiles_manager_path: Path` - Path to dotfiles-manager module

#### `RofiConfig`

- `show_icons: bool` - Show icons in rofi (default: True)
- `icon_size: int` - Icon size in pixels (default: 100)
- `wallpaper_mode_name: str` - Wallpaper mode name (default: "wallpapers")
- `effect_mode_name: str` - Effect mode name (default: "effects")

#### `WallpaperConfig`

- `default_monitor: str` - Default monitor (default: "focused")
- `auto_generate_effects: bool` - Auto-generate effects on wallpaper selection (default: True)
- `auto_generate_colorscheme: bool` - Auto-generate colorscheme on wallpaper change (default: True)
