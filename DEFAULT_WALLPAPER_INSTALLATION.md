# Default Wallpaper Installation Feature

## Overview

This feature adds automatic default wallpaper configuration during the dotfiles installation process. When the installation completes, a default wallpaper is automatically set with generated colorscheme and effects, providing an immediate visual experience without manual configuration.

## Implementation Details

### Components

1. **Configuration Model** (`cli/src/config/config.py`)
   - `WallpaperInstallationSettings`: Pydantic model for wallpaper installation settings
   - `InstallationSettings`: Container for installation-related settings
   - Integrated into `ProjectSettings` for app-wide configuration access

2. **Configuration File** (`cli/config/settings.toml`)
   - New `[installation.wallpaper]` section with configurable options
   - Default wallpaper name and target monitors

3. **Utility Function** (`cli/src/pipeline_steps/utils.py`)
   - `set_default_wallpaper()`: Core implementation that handles wallpaper setup
   - Searches for wallpaper file with multiple extension support
   - Calls dotfiles-manager CLI via subprocess
   - Generates colorscheme and effects during installation

4. **Pipeline Step** (`cli/src/pipeline_steps/pipeline.py`)
   - `SetDefaultWallpaperStep`: Pipeline step class
   - Critical step (installation fails if wallpaper setup fails)
   - 6-minute timeout for colorscheme/effects generation

5. **Pipeline Integration** (`cli/src/commands/install.py`)
   - Added `SetDefaultWallpaperStep` after `StartDaemonServiceStep`
   - Ensures daemon is running before setting wallpaper

## Configuration

### Settings (`cli/config/settings.toml`)

```toml
[installation.wallpaper]
# Default wallpaper filename (without extension) to set during installation
default_wallpaper = "default"

# Target monitor(s) for default wallpaper: "all", "focused", or specific monitor name
target_monitors = "all"
```

### Configuration Options

- **`default_wallpaper`**: Wallpaper filename without extension (default: `"default"`)
  - The installer searches for this file in the extracted wallpapers directory
  - Supports multiple image formats: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`

- **`target_monitors`**: Which monitors to apply the wallpaper to (default: `"all"`)
  - `"all"`: Apply to all monitors
  - `"focused"`: Apply to currently focused monitor
  - Specific monitor name: Apply to named monitor

## How It Works

### Pipeline Flow

```
Installation Pipeline:
├─ ...
├─ ExtractWallpapersStep          # Extracts wallpapers.tar.gz
├─ [Install modules/tools]
├─ ConfigureDotfilesManagerStep   # Configure dotfiles-manager
├─ StartDaemonServiceStep         # Start daemon service
└─ SetDefaultWallpaperStep        # ← NEW: Set default wallpaper
    ├─ Read configuration
    ├─ Find default wallpaper file
    ├─ Call dotfiles-manager change-wallpaper
    ├─ Generate colorscheme (using pywal)
    ├─ Generate effects (blur, brightness, etc.)
    └─ Set wallpaper on target monitors
```

### Execution Details

1. **Configuration Loading**: Reads `default_wallpaper` and `target_monitors` from settings
2. **Wallpaper Discovery**: Searches for wallpaper file in `{install_root}/dotfiles/wallpapers/`
3. **Manager Invocation**: Calls `dotfiles-manager change-wallpaper` with:
   - Wallpaper path
   - `--monitor {target_monitors}`
   - `--colorscheme` flag (generates colorscheme)
   - `--effects` flag (generates effects)
4. **Colorscheme Generation**: Uses pywal to extract colors from wallpaper
5. **Effects Generation**: Creates blur, brightness, and other effect variants
6. **Wallpaper Application**: Sets wallpaper via hyprpaper IPC

### Caching

The wallpaper orchestrator uses a sophisticated caching system:
- **Effects cache**: `~/.cache/wallpaper/effects/{wallpaper_stem}/`
- **Colorscheme cache**: `~/.cache/wallpaper/colorschemes/{wallpaper_stem}/`
- **Cache metadata**: SQLite database at `~/.cache/wallpaper/cache.db`

First installation generates everything (slower), but subsequent wallpaper changes use cached data (much faster).

## Error Handling

- **Critical Step**: Installation fails if wallpaper cannot be set
- **File Not Found**: Clear error if default wallpaper doesn't exist
- **Timeout**: 6-minute timeout for generation process
- **Detailed Logging**: All steps logged with debug information

## Files Modified

1. `src/dotfiles-installer/cli/config/settings.toml`
2. `src/dotfiles-installer/cli/src/config/config.py`
3. `src/dotfiles-installer/cli/src/pipeline_steps/utils.py`
4. `src/dotfiles-installer/cli/src/pipeline_steps/pipeline.py`
5. `src/dotfiles-installer/cli/src/commands/install.py`

## Benefits

- **Immediate Visual Experience**: Users see a configured desktop immediately after installation
- **Consistent Setup**: Ensures colorscheme and effects are generated during installation
- **Configurable**: Easy to change default wallpaper via settings
- **Robust**: Proper error handling and timeout management
- **Cached**: Subsequent operations are fast due to caching system
