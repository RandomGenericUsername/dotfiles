# Dotfiles Manager

Central management module for the dotfiles system, providing wallpaper orchestration, state management, and extensible hooks.

## Overview

The Dotfiles Manager is the central control point for the entire dotfiles system. It orchestrates wallpaper changes, manages system state, and provides an extensible hook system for post-wallpaper-change actions.

## Features

- **Wallpaper Orchestration**: Integrates wallpaper-orchestrator for seamless wallpaper changes with effects and colorscheme generation
- **State Management**: Persistent state tracking using SQLite for wallpaper history per monitor
- **Hook System**: Extensible plugin-like system for post-wallpaper-change actions (e.g., wlogout icons/styles generation)
- **Monitor Auto-Detection**: Automatically detects the focused monitor using hyprpaper-manager
- **Dependency Injection**: Clean architecture using dependency-injector for IoC
- **Type-Safe**: Full type hints and Pydantic configuration validation
- **CLI Interface**: Rich CLI with typer for easy command-line usage

## Installation

```bash
cd src/dotfiles/modules/manager
uv sync
```

## Quick Start

### CLI Usage

```bash
# Change wallpaper (auto-detects monitor)
dotfiles-manager change-wallpaper /path/to/wallpaper.jpg

# Change wallpaper on specific monitor
dotfiles-manager change-wallpaper /path/to/wallpaper.jpg --monitor DP-1

# Force rebuild containers
dotfiles-manager change-wallpaper /path/to/wallpaper.jpg --force-rebuild

# Check system status
dotfiles-manager status

# Check status for specific monitor
dotfiles-manager status --monitor eDP-2
```

### Python API

```python
from dotfiles_manager.container import Container

# Initialize container
container = Container.initialize()

# Get wallpaper service
wallpaper_service = container.wallpaper_service()

# Change wallpaper
result = wallpaper_service.change_wallpaper(
    wallpaper_path=Path("/path/to/wallpaper.jpg"),
    monitor="DP-1",
    force_rebuild=False
)

print(f"Wallpaper changed: {result['wallpaper_path']}")
print(f"From cache: {result['from_cache']}")
print(f"Hook results: {result['hook_results']}")
```

## Configuration

### Settings File

The manager uses `config/settings.toml` for configuration:

```toml
[system]
font_family = "JetBrains Mono"
font_size = 14
monitors = []  # Empty = auto-detect

[paths]
install_root = "/home/user/.local/share/dotfiles"
wallpaper_orchestrator_path = "{install_root}/.dependencies/tools/wallpaper-orchestrator"
wlogout_icons_templates_dir = "{install_root}/dotfiles/wlogout/templates/icons"
wlogout_style_template_path = "{install_root}/dotfiles/wlogout/templates/style.css.tpl"
wlogout_icons_output_dir = "{install_root}/dotfiles/wlogout/icons"
wlogout_style_output_path = "{install_root}/dotfiles/wlogout/style.css"

[state]
database_path = "{install_root}/state/manager/system.db"

[hooks]
enabled = ["wlogout_icons"]

[hooks.wlogout_icons]
color_key = "foreground"
```

## Architecture

The manager follows a clean architecture with dependency injection:

```
manager/
├── src/dotfiles_manager/
│   ├── cli.py                    # CLI interface (typer)
│   ├── container.py              # DI container
│   ├── commands/
│   │   ├── change_wallpaper.py  # Wallpaper change command
│   │   └── status.py            # Status command
│   ├── services/
│   │   ├── wallpaper_service.py # Wallpaper orchestration
│   │   └── wlogout_service.py   # Wlogout generation
│   ├── repositories/
│   │   ├── system_attributes.py # System attributes repo
│   │   └── wallpaper_state.py   # Wallpaper state repo
│   ├── hooks/
│   │   ├── base.py              # Hook base class
│   │   ├── registry.py          # Hook registry
│   │   └── wlogout_hook.py      # Wlogout icons hook
│   ├── models/
│   │   └── models.py            # Domain models
│   └── config/
│       ├── config.py            # Pydantic models
│       └── settings.py          # Settings loader
├── config/
│   └── settings.toml            # Default configuration
└── tests/                       # Test suite
```

### Key Components

#### Services Layer
- **WallpaperService**: Orchestrates wallpaper changes, manages cache, executes hooks
- **WlogoutService**: Generates wlogout icons and styles from templates

#### Repository Layer
- **SystemAttributesRepository**: Manages system-wide attributes (font, monitors)
- **WallpaperStateRepository**: Tracks wallpaper state per monitor

#### Hook System
- **HookBase**: Abstract base class for all hooks
- **HookRegistry**: Manages hook registration and execution
- **WlogoutIconsHook**: Generates wlogout icons/styles after wallpaper change

#### Container
- Uses `dependency-injector` for IoC
- Provides singleton instances of services and repositories
- Manages configuration and dependencies

## Hook System

The manager provides an extensible hook system for post-wallpaper-change actions.

### Creating a Custom Hook

```python
from pathlib import Path
from dotfiles_manager.hooks.base import HookBase, HookContext, HookResult

class MyCustomHook(HookBase):
    @property
    def name(self) -> str:
        return "my_custom_hook"

    def execute(self, context: HookContext) -> HookResult:
        # Your hook logic here
        # Access context.wallpaper_path, context.monitor, etc.

        return HookResult(
            success=True,
            message="Custom hook executed successfully"
        )
```

### Registering a Hook

```python
from dotfiles_manager.hooks.registry import HookRegistry

# Register hook
registry = HookRegistry(config, logger)
registry.register(MyCustomHook(config, logger))

# Execute all hooks
results = registry.execute_all(context)
```

## State Management

The manager uses SQLite for persistent state tracking:

- **Wallpaper State**: Current wallpaper per monitor, last changed timestamp, cache status
- **System Attributes**: Font family, font size, monitor list

State is stored in `{install_root}/state/manager/system.db`.

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

## Dependencies

- **dotfiles-logging**: Logging infrastructure
- **dotfiles-pipeline**: Pipeline execution framework
- **dotfiles-state-manager**: State persistence layer
- **dotfiles-template-renderer**: Jinja2 template rendering
- **hyprpaper-manager**: Hyprpaper integration and monitor detection
- **wallpaper-orchestrator**: Wallpaper effects and colorscheme generation
- **dynaconf**: Configuration management
- **pydantic**: Data validation
- **typer**: CLI framework
- **rich**: Terminal formatting
- **dependency-injector**: Dependency injection

## License

Part of the dotfiles project.
