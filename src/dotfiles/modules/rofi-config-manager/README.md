# Rofi Config Manager

Generic rofi configuration manager for the dotfiles system.

## Overview

This module manages rofi configuration files by:
- Querying dotfiles-manager for system state (colorscheme, font, wallpaper)
- Rendering rofi templates with inline values (no file imports)
- Supporting multiple config types with extensible architecture
- Integrating with dotfiles-manager hooks for automatic regeneration

## Features

- **Backend Agnostic**: Works with any colorscheme backend (pywal, wallust, custom)
- **Inline Colors**: No external file imports - all values inline in templates
- **Modi Support**: First-class support for rofi modi configuration
- **Hierarchical Config**: Global defaults with per-config overrides
- **Hook Integration**: Automatically regenerates on wallpaper change

## Installation

```bash
make install
```

## Usage

### Generate All Configs

```bash
rofi-config-manager generate --all
```

### Generate Specific Config

```bash
rofi-config-manager generate --type wallpaper-selector
```

### List Available Config Types

```bash
rofi-config-manager list
```

## Configuration

Edit `config/settings.toml` to customize:
- Output directory
- Border widths (global and per-config)
- Modi configuration
- Enabled configs

## Architecture

- **Models**: Pydantic models for Modi, RenderContext, ConfigSchema
- **Services**: RofiConfigService for rendering logic
- **Client**: ManagerClient for querying dotfiles-manager state
- **Templates**: Jinja2 templates with inline colors and conditional modi

## Development

```bash
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
