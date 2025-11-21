# Architecture

## Overview

The rofi-wallpaper-selector module provides a rofi-based interface for selecting wallpapers and effects. It follows a clean separation of concerns with distinct components for listing, handling, and managing wallpaper state.

## Components

### CLI Interface (`cli.py`)

Entry point for the module. Provides two Typer commands:

- `wallpapers`: List wallpapers or handle wallpaper selection
- `effects`: List effects or handle effect selection

Both commands detect `ROFI_RETV` environment variable to determine mode:
- `ROFI_RETV=0`: List mode (output items for rofi)
- `ROFI_RETV=1`: Handle mode (process selection from stdin)

### Selectors

**Wallpaper Selector** (`selectors/wallpaper_selector.py`)
- Scans wallpapers directory for image files
- Outputs wallpapers in rofi format with thumbnails
- Supports PNG, JPG, JPEG formats

**Effect Selector** (`selectors/effect_selector.py`)
- Queries dotfiles-manager for current wallpaper
- Scans effects cache directory for generated effects
- Always includes "off" option to revert to original
- Shows only effects that exist in cache

### Handlers

**Wallpaper Handler** (`handlers/wallpaper_handler.py`)
- Processes wallpaper selection
- Calls dotfiles-manager with:
  - `generate_colorscheme=True`
  - `generate_effects=True`
- Generates both colorscheme and all effect variants

**Effect Handler** (`handlers/effect_handler.py`)
- Processes effect selection
- Handles "off" option (revert to original)
- Calls dotfiles-manager with:
  - `generate_colorscheme=True`
  - `generate_effects=False`
- Only regenerates colorscheme (effects already exist)

### Utilities

**Rofi Formatter** (`utils/rofi_formatter.py`)
- Formats items for rofi output
- Supports icon display: `label\x00icon\x1f/path/to/icon`

**Effects Cache** (`utils/effects_cache.py`)
- Queries effects cache directory
- Returns list of available effects for a wallpaper
- Cache structure: `{effects_cache_dir}/{wallpaper_name}/{effect_name}.png`

**Manager Client** (`utils/manager_client.py`)
- Subprocess-based client for dotfiles-manager CLI
- Calls manager CLI commands instead of importing module
- Avoids venv dependency conflicts
- Provides methods:
  - `get_current_wallpaper(monitor)`: Get current wallpaper path via `dotfiles-manager status`
  - `change_wallpaper(...)`: Change wallpaper via `dotfiles-manager change-wallpaper`

## Data Flow

### Wallpaper Selection Flow

1. User opens rofi with wallpapers mode
2. Rofi calls `rofi-wallpaper-selector wallpapers` with `ROFI_RETV=0`
3. Wallpaper selector scans wallpapers directory
4. Outputs wallpapers in rofi format with thumbnails
5. User selects wallpaper
6. Rofi calls `rofi-wallpaper-selector wallpapers` with `ROFI_RETV=1`
7. Wallpaper handler processes selection
8. Calls dotfiles-manager to change wallpaper
9. Manager generates colorscheme and all effects
10. Effects are cached for future use

### Effect Selection Flow

1. User switches to effects mode in rofi
2. Rofi calls `rofi-wallpaper-selector effects` with `ROFI_RETV=0`
3. Effect selector queries manager for current wallpaper
4. Scans effects cache for available effects
5. Outputs effects in rofi format with thumbnails
6. User selects effect (or "off")
7. Rofi calls `rofi-wallpaper-selector effects` with `ROFI_RETV=1`
8. Effect handler processes selection
9. Calls dotfiles-manager to change wallpaper
10. Manager only regenerates colorscheme (effects already exist)

## Configuration

Configuration uses Dynaconf + Pydantic pattern:

- `config/settings.toml`: Default settings
- `config/settings.py`: Pydantic models for validation
- Settings overridden by installer at install time

## Integration Points

### Dotfiles Manager

- Accessed through `ManagerClient` via subprocess calls
- Calls manager CLI: `{manager_path}/.venv/bin/dotfiles-manager`
- Commands used:
  - `dotfiles-manager status --monitor <monitor>`: Get current wallpaper
  - `dotfiles-manager change-wallpaper <path> --monitor <monitor> [--colorscheme|--no-colorscheme] [--effects|--no-effects]`: Change wallpaper
- Parses CLI output (table format) to extract wallpaper information

### Installer

- Module installed by `InstallModuleStep`
- Settings overridden via `module_settings_overrides` dict
- Rofi config rendered by `InstallRofiConfigStep`
- Paths resolved from installer context

## Design Decisions

### Dynamic Effects Discovery

Uses cache directory scanning (Option C) instead of API queries because:
- Shows only effects that actually exist
- No dependency on effects processor module
- Simple filesystem query
- Accurate UX (user sees what's available)

### Generation Logic

Critical distinction:
- **Wallpaper selection**: Generate both colorscheme AND effects
- **Effect selection**: Generate ONLY colorscheme (effects already exist)

This prevents redundant effect regeneration and improves performance.

### Manager Access via Subprocess

Uses `ManagerClient` with subprocess calls instead of direct module import because:
- **Venv Isolation**: Each module has its own venv with different dependencies
  - rofi-wallpaper-selector: typer, dynaconf, pydantic
  - dotfiles-manager: dependency_injector, dotfiles-state-manager, etc.
- **Avoids Dependency Conflicts**: Importing manager would require all its dependencies in rofi-wallpaper-selector's venv
- **Clean Integration**: Uses manager's CLI interface as designed
- **Maintainability**: Changes to manager's internal API don't break rofi-wallpaper-selector
- **Proper Isolation**: Each module runs in its own environment
