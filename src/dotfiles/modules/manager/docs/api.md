# API Reference

## CLI Commands

### change-wallpaper

Change wallpaper and execute hooks.

**Usage:**
```bash
dotfiles-manager change-wallpaper WALLPAPER_PATH [OPTIONS]
```

**Arguments:**
- `WALLPAPER_PATH`: Path to wallpaper image (required)

**Options:**
- `--monitor, -m TEXT`: Monitor name (default: auto-detect focused monitor)
- `--force-rebuild`: Force rebuild containers
- `--help`: Show help message

**Examples:**
```bash
# Auto-detect monitor
dotfiles-manager change-wallpaper ~/wallpapers/sunset.jpg

# Specific monitor
dotfiles-manager change-wallpaper ~/wallpapers/sunset.jpg --monitor DP-1

# Force rebuild
dotfiles-manager change-wallpaper ~/wallpapers/sunset.jpg --force-rebuild
```

**Output:**
```
✓ Wallpaper changed: /home/user/wallpapers/sunset.jpg
  Monitor: eDP-2
  From cache: False

Hook Results:
  ✓ wlogout_icons: Generated 6 icons and style.css
```

### status

Display system status and wallpaper state.

**Usage:**
```bash
dotfiles-manager status [OPTIONS]
```

**Options:**
- `--monitor, -m TEXT`: Show status for specific monitor only
- `--help`: Show help message

**Examples:**
```bash
# Show all monitors
dotfiles-manager status

# Specific monitor
dotfiles-manager status --monitor eDP-2
```

**Output:**
```
       System Attributes
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Attribute   ┃ Value          ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Font Family │ JetBrains Mono │
│ Font Size   │ 14px           │
│ Monitors    │ auto-detect    │
└─────────────┴────────────────┘

                    Wallpaper Status
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Monitor ┃ Wallpaper                 ┃ Last Changed        ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ eDP-2   │ /home/user/wallpapers/... │ 2025-11-15 00:13:27 │
└─────────┴───────────────────────────┴─────────────────────┘
```

## Python API

### Container

Initialize the dependency injection container:

```python
from dotfiles_manager.container import Container

# Initialize container
container = Container.initialize()

# Get services
wallpaper_service = container.wallpaper_service()
wlogout_service = container.wlogout_service()

# Get repositories
wallpaper_state_repo = container.wallpaper_state_repo()
system_attrs_repo = container.system_attributes_repo()
```

### WallpaperService

#### change_wallpaper()

Change wallpaper and execute hooks.

```python
from pathlib import Path

result = wallpaper_service.change_wallpaper(
    wallpaper_path=Path("/path/to/wallpaper.jpg"),
    monitor="eDP-2",
    force_rebuild=False
)

# Result structure:
{
    "wallpaper_path": Path("/path/to/wallpaper.jpg"),
    "monitor": "eDP-2",
    "from_cache": False,
    "hook_results": {
        "wlogout_icons": HookResult(success=True, message="...")
    }
}
```

**Parameters:**
- `wallpaper_path` (Path): Path to wallpaper image
- `monitor` (str): Monitor name
- `force_rebuild` (bool): Force rebuild containers

**Returns:**
- `dict`: Result dictionary with wallpaper info and hook results

### WlogoutService

#### generate_icons()

Generate wlogout icon SVGs from templates.

```python
from pathlib import Path

icons = wlogout_service.generate_icons(
    color="#ffffff",
    output_dir=Path("/output/icons")
)

# Returns: dict[str, Path]
# {
#     "shutdown": Path("/output/icons/shutdown.svg"),
#     "reboot": Path("/output/icons/reboot.svg"),
#     ...
# }
```

#### generate_style()

Generate wlogout style.css from template.

```python
from pathlib import Path

style_path = wlogout_service.generate_style(
    font_family="JetBrains Mono",
    font_size=14,
    colors_css_path=Path("/path/to/colors.css"),
    background_image=Path("/path/to/wallpaper.jpg"),
    icons_dir=Path("/path/to/icons"),
    output_path=Path("/output/style.css")
)

# Returns: Path("/output/style.css")
```

#### generate_all()

Generate both icons and style.

```python
result = wlogout_service.generate_all(
    color="#ffffff",
    font_family="JetBrains Mono",
    font_size=14,
    colors_css_path=Path("/path/to/colors.css"),
    background_image=Path("/path/to/wallpaper.jpg"),
    icons_output_dir=Path("/output/icons"),
    style_output_path=Path("/output/style.css")
)

# Returns: dict with icons and style_path
```

### Repositories

#### SystemAttributesRepository

```python
# Get attributes
attrs = system_attrs_repo.get_attributes()
print(attrs.font_family)  # "JetBrains Mono"
print(attrs.font_size)    # 14
print(attrs.monitors)     # []

# Set attributes
system_attrs_repo.set_attributes(
    font_family="Fira Code",
    font_size=16,
    monitors=["eDP-2", "DP-1"]
)
```

#### WallpaperStateRepository

```python
# Get current wallpaper for monitor
wallpaper = wallpaper_state_repo.get_current_wallpaper("eDP-2")
print(wallpaper.path)          # Path("/path/to/wallpaper.jpg")
print(wallpaper.last_changed)  # datetime object
print(wallpaper.from_cache)    # False

# Set wallpaper
wallpaper_state_repo.set_current_wallpaper(
    wallpaper_path=Path("/path/to/wallpaper.jpg"),
    monitor="eDP-2",
    from_cache=False
)

# Get all wallpapers
all_wallpapers = wallpaper_state_repo.get_all_wallpapers()
# Returns: dict[str, WallpaperInfo]
```
