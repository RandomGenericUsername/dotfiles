# Architecture

## Overview

The Dotfiles Manager follows a clean architecture pattern with clear separation of concerns:

- **CLI Layer**: User interface (typer-based CLI)
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access and persistence
- **Hook System**: Extensible plugin architecture
- **Container**: Dependency injection and lifecycle management

## Layers

### CLI Layer (`cli.py`)

The CLI layer provides the user interface using typer:

- `change-wallpaper`: Change wallpaper with optional monitor specification
- `status`: Display system status and wallpaper state

**Responsibilities:**
- Parse command-line arguments
- Auto-detect monitor if not specified (using hyprpaper-manager)
- Delegate to service layer
- Format and display results

### Service Layer

#### WallpaperService (`services/wallpaper_service.py`)

Orchestrates the entire wallpaper change workflow:

1. Calls wallpaper-orchestrator to generate effects and colorscheme
2. Sets wallpaper via hyprpaper
3. Saves state to database
4. Executes registered hooks

**Key Methods:**
- `change_wallpaper()`: Main orchestration method
- `_execute_hooks()`: Execute all registered hooks with pipeline

#### WlogoutService (`services/wlogout_service.py`)

Generates wlogout icons and styles from templates:

**Key Methods:**
- `generate_icons()`: Render SVG icon templates with color
- `generate_style()`: Render CSS style template with variables
- `generate_all()`: Generate both icons and style

### Repository Layer

#### SystemAttributesRepository (`repositories/system_attributes.py`)

Manages system-wide attributes using state-manager:

**Data:**
- Font family
- Font size
- Monitor list

**Methods:**
- `get_attributes()`: Retrieve current attributes
- `set_attributes()`: Update attributes

#### WallpaperStateRepository (`repositories/wallpaper_state.py`)

Tracks wallpaper state per monitor:

**Data:**
- Current wallpaper path per monitor
- Last changed timestamp
- Cache status (loaded from cache or freshly generated)

**Methods:**
- `get_current_wallpaper()`: Get wallpaper for specific monitor
- `set_current_wallpaper()`: Update wallpaper state
- `get_all_wallpapers()`: Get all monitor wallpapers

### Hook System

#### HookBase (`hooks/base.py`)

Abstract base class for all hooks:

```python
class HookBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Hook identifier"""
        pass

    @abstractmethod
    def execute(self, context: HookContext) -> HookResult:
        """Execute hook logic"""
        pass
```

#### HookRegistry (`hooks/registry.py`)

Manages hook registration and execution:

- Registers hooks from configuration
- Executes hooks using pipeline (serial execution)
- Collects and returns results

#### WlogoutIconsHook (`hooks/wlogout_hook.py`)

Generates wlogout icons and styles after wallpaper change:

1. Extracts color from colorscheme JSON
2. Calls WlogoutService to generate icons and style
3. Returns success/failure result

### Container (`container.py`)

Dependency injection container using `dependency-injector`:

**Singletons:**
- Configuration
- Logger
- State manager
- Repositories
- Services
- Hook registry

**Benefits:**
- Centralized dependency management
- Easy testing with mock injection
- Lazy initialization
- Lifecycle management

## Data Flow

### Wallpaper Change Flow

```
CLI (change-wallpaper)
  ↓
WallpaperService.change_wallpaper()
  ↓
  ├─→ WallpaperOrchestrator (external)
  │     ├─→ Generate effects
  │     ├─→ Generate colorscheme
  │     └─→ Set wallpaper via hyprpaper
  │
  ├─→ WallpaperStateRepository.set_current_wallpaper()
  │     └─→ Save to SQLite
  │
  └─→ HookRegistry.execute_all()
        └─→ WlogoutIconsHook.execute()
              └─→ WlogoutService.generate_all()
                    ├─→ Generate 6 SVG icons
                    └─→ Generate style.css
```

### Status Query Flow

```
CLI (status)
  ↓
StatusCommand
  ↓
  ├─→ SystemAttributesRepository.get_attributes()
  │     └─→ Read from SQLite
  │
  └─→ WallpaperStateRepository.get_all_wallpapers()
        └─→ Read from SQLite
```

## Configuration

Configuration is loaded via dynaconf with Pydantic validation:

1. Load from `config/settings.toml`
2. Override with environment variables
3. Validate with Pydantic models
4. Inject into container

## State Management

State is persisted using dotfiles-state-manager with SQLite backend:

**Database:** `{install_root}/state/manager/system.db`

**Keys:**
- `system:attributes:font_family`
- `system:attributes:font_size`
- `system:attributes:monitors`
- `system:wallpapers:{monitor}` - Current wallpaper path
- `system:wallpapers:last_changed:{monitor}` - ISO timestamp
- `system:wallpapers:from_cache:{monitor}` - Boolean string
