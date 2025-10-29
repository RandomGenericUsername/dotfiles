# Configuration Architecture Analysis

## Executive Summary

The dotfiles installer configuration system has significant architectural issues that make it confusing, hard to maintain, and fragile. This document analyzes the current state and proposes a comprehensive reorganization.

## Current State Analysis

### Configuration Layers (Current)

The configuration is currently spread across **6 different layers**:

1. **Root Level Settings** (`/settings.toml`)
   - User-level overrides (highest priority)
   - Contains: install directory, backup_directory, type, hidden, debug settings, host_paths

2. **CLI Project Settings** (`cli/config/settings.toml`)
   - Project-level defaults
   - Contains: package_manager settings, safety.directory_deletion settings

3. **CLI Directory Structure** (`cli/config/directories.toml`)
   - Directory structure configuration
   - Contains: install.subdirectories structure

4. **CLI Python Defaults** (`cli/src/config/cli_settings_defaults.py`)
   - Hardcoded Python defaults
   - Contains: install_path, log_directory, backup_directory, wallpapers_directory, screenshots_directory, log_level, output_to_file

5. **Project Python Defaults** (`cli/src/config/project_settings_defaults.py`)
   - Hardcoded Python defaults
   - Contains: python_version, nodejs_version, protected_directories, dangerous_keywords, minimum_path_depth, protect_user_homes, keyword_check_depth_threshold

6. **Pydantic Model Defaults** (`cli/src/config/config.py`)
   - Field-level defaults in model definitions
   - Contains: Various defaults including hardcoded paths like `template_directory = Path("src/dotfiles-installer/docker/templates")`

### Loading Order (Current)

```python
# Actual loading order:
1. Python defaults (cli_settings_defaults.py, project_settings_defaults.py)
2. Pydantic Field defaults
3. directories.toml
4. cli/config/settings.toml
5. root/settings.toml (highest priority)
```

## Critical Problems Identified

### 1. Path Configuration Scattered Across Multiple Places

**Problem:** Paths are defined in at least 3 different locations with no clear organization:

- `install.directory` - Installation root directory
- `install.paths` - Dynamic InstallationPaths (subdirectories)
- `host_paths.wallpapers_directory` - Host wallpapers path
- `host_paths.screenshots_directory` - Host screenshots path
- `install.debug.log_directory` - Logging directory
- `install.backup_directory` - Backup directory
- `template_renderer.template_directory` - Template directory (hardcoded!)

**Impact:** 
- Users don't know where to look for path configuration
- Hard to get a complete picture of all paths used
- Inconsistent organization makes maintenance difficult

### 2. Brittle Project Root Path Detection

**Current Implementation:**
```python
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
```

**Problems:**
- Uses **6 levels** of `.parent` - extremely fragile!
- If `settings.py` moves to a different directory depth, this breaks
- If project structure changes, this breaks
- No validation that the calculated path is actually the project root
- Hard to understand and maintain
- Difficult to debug when it fails

**Example Failure Scenario:**
```
# Current: cli/src/config/settings.py
# 6 parents: settings.py → config → src → cli → dotfiles-installer → src → PROJECT_ROOT

# If we move settings.py to cli/config/settings.py:
# Now needs 5 parents, but code still uses 6 → WRONG PATH!
```

### 3. Confusing Default Value Hierarchy

**Problem:** Defaults are defined in multiple places with unclear precedence:

1. Python files (`cli_settings_defaults.py`, `project_settings_defaults.py`)
2. Pydantic `Field(default=...)` definitions
3. TOML files (`directories.toml`, `cli/config/settings.toml`)
4. Dynaconf loading order

**Example of Confusion:**
```python
# In cli_settings_defaults.py:
install_path: Path = Path.home() / "dotfiles"

# In config.py:
directory: Path = Field(default=install_path, description="...")

# In settings.toml:
[install]
directory = "$HOME/.tmp/install"

# Which one wins? Hard to tell without understanding the entire loading chain!
```

### 4. Duplicate Configuration

**Problem:** Same configuration defined in multiple places:

```python
# In project_settings_defaults.py:
protected_directories: list[str] = ["/", "/root", "/usr", ...]

# In cli/config/settings.toml:
[safety.directory_deletion]
protected_directories = ["/", "/root", "/usr", ...]
```

**Questions:**
- Which is the source of truth?
- If I want to change defaults, which file do I edit?
- Why maintain the same list in two places?

### 5. Inconsistent Path Types

**Problem:** No clear pattern for path types:

```python
# Relative path (from where?)
template_directory = Path("src/dotfiles-installer/docker/templates")

# Absolute path with env var
directory = "$HOME/.tmp/install"

# Dynamic paths
paths = InstallationPaths(...)

# Home-relative
install_path = Path.home() / "dotfiles"
```

**Impact:**
- Confusion about what paths are relative to
- Runtime errors if current directory is not project root
- Hard to reason about path resolution

### 6. Hardcoded Template Directory

**Current:**
```python
class TemplateRendererSettings(BaseModel):
    template_directory: Path = Field(
        default=Path("src/dotfiles-installer/docker/templates"),
        description="Directory containing templates",
    )
```

**Problems:**
- Hardcoded relative path in Pydantic model
- Relative to what? Current directory? Project root?
- Breaks if executed from different directory
- Should be calculated from project root or made configurable
- Not in TOML configuration files

### 7. No Central Path Registry

**Problem:** No single place to see all paths used by the application

**Current State:**
- Installation paths in `CliInstallSettings`
- Host paths in `ProjectPaths`
- Template paths in `TemplateRendererSettings`
- Log paths in `InstallDebugSettings`
- Backup paths in `CliInstallSettings`

**Impact:**
- Hard to ensure consistency
- Can't easily validate all paths
- Difficult to document
- Confusing for users

### 8. Unclear Settings Loading Order

**Problem:** The actual loading order is not well documented:

```python
settings_files = [
    str(DIRECTORIES_CONFIG),  # 1. Directory structure defaults
    str(PROJECT_SETTINGS),    # 2. Project-level defaults
    str(SETTINGS_FILE),       # 3. User overrides (highest priority)
]
```

But Python defaults are loaded BEFORE these files, so actual order is:
1. Python defaults
2. Pydantic Field defaults
3. directories.toml
4. cli/config/settings.toml
5. root/settings.toml

This is not documented anywhere clearly.

## Proposed Solution

### 1. Establish Clear 3-Level Configuration Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│ Level 1: Project Constants (Python)                         │
│ ├── Project root detection (marker file approach)           │
│ ├── Immutable project structure paths                       │
│ └── Minimal hardcoded constants                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Level 2: Project Defaults (TOML in cli/config/)            │
│ ├── defaults.toml - All default values (NEW)               │
│ ├── directories.toml - Installation directory structure     │
│ └── packages/{distro}/system.toml - Distro packages        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Level 3: User Configuration (TOML at project root)         │
│ └── settings.toml - User overrides only                    │
└─────────────────────────────────────────────────────────────┘
```

### 2. Centralize All Paths in PathsConfig

Create a new unified `PathsConfig` model:

```python
class ProjectPaths(BaseModel):
    """Paths within the project repository (auto-detected)."""
    root: Path  # Auto-detected project root
    templates: Path  # Relative to root
    docker: Path  # Relative to root
    cli_config: Path  # Relative to root

class InstallationPaths(BaseModel):
    """Paths for dotfiles installation (user-configurable)."""
    directory: Path  # Main install directory
    backup: Path  # Backup directory
    subdirs: DynamicSubdirectories  # Dynamic subdirectories

class HostPaths(BaseModel):
    """Paths on the host system (user-configurable)."""
    wallpapers: Path
    screenshots: Path

class RuntimePaths(BaseModel):
    """Runtime paths for logs, cache, etc (user-configurable)."""
    logs: Path
    cache: Path

class PathsConfig(BaseModel):
    """Unified path configuration - single source of truth."""
    project: ProjectPaths
    installation: InstallationPaths
    host: HostPaths
    runtime: RuntimePaths
```

### 3. Fix Project Root Detection

Replace brittle `.parent.parent.parent...` with robust marker-based detection:

```python
def find_project_root(marker_files: list[str] = None) -> Path:
    """Find project root by looking for marker files.
    
    Args:
        marker_files: Files that indicate project root.
                     Defaults to ['pyproject.toml', '.git', 'settings.toml']
    
    Returns:
        Path to project root
        
    Raises:
        RuntimeError: If project root cannot be found
    """
    if marker_files is None:
        marker_files = ['pyproject.toml', '.git', 'settings.toml']
    
    current = Path(__file__).resolve()
    
    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in marker_files):
            return parent
    
    raise RuntimeError(
        f"Could not find project root. Looked for: {marker_files}"
    )

# Usage:
PROJECT_ROOT = find_project_root()
```

**Benefits:**
- Works regardless of file location
- Self-documenting (marker files are explicit)
- Easy to debug (clear error message)
- Robust to project restructuring
- Standard pattern used by many tools

### 4. Consolidate All Defaults to TOML

**Remove:**
- `cli/src/config/cli_settings_defaults.py`
- `cli/src/config/project_settings_defaults.py`

**Create:**
- `cli/config/defaults.toml` with ALL default values

**Example `cli/config/defaults.toml`:**
```toml
[paths.project]
# Project paths are relative to auto-detected root
templates = "src/dotfiles-installer/docker/templates"
docker = "src/dotfiles-installer/docker"
cli_config = "src/dotfiles-installer/cli/config"

[paths.installation]
directory = "$HOME/dotfiles"
backup = "$HOME/.dotfiles-backup"

[paths.host]
wallpapers = "$HOME/wallpapers"
screenshots = "$HOME/Pictures/Screenshots"

[paths.runtime]
logs = "$HOME/.local/share/dotfiles/logs"
cache = "$HOME/.cache/dotfiles"

[install]
type = "update"
hidden = true

[install.debug]
log_level = "error"
output_to_file = false

[package_manager]
prefer_third_party = true
update_system_before_install = false
remove_dependencies = true

[safety.directory_deletion]
protected_directories = ["/", "/root", "/usr", ...]
dangerous_keywords = ["system", "root", "backup", "config"]
minimum_path_depth = 3
protect_user_homes = true
keyword_check_depth_threshold = 4
```

### 5. Reorganize AppConfig Structure

```python
class AppConfig(BaseModel):
    """Application configuration with clear organization."""
    
    # ALL paths in one place
    paths: PathsConfig = Field(
        default_factory=PathsConfig,
        description="All path configuration"
    )
    
    # Installation settings (no paths here!)
    install: InstallSettings = Field(
        default_factory=InstallSettings,
        description="Installation behavior settings"
    )
    
    # System configuration
    system: SystemConfig = Field(
        default_factory=SystemConfig,
        description="System packages and features"
    )
    
    # Tool configurations
    package_manager: PackageManagerSettings
    container_manager: ContainerManagerSettings
    template_renderer: TemplateRendererSettings
    
    # Safety settings
    safety: SafetySettings
```

### 6. Update Settings Loading

```python
# Clear, documented loading order
PROJECT_ROOT = find_project_root()

settings_files = [
    PROJECT_ROOT / "cli/config/defaults.toml",      # 1. Project defaults
    PROJECT_ROOT / "cli/config/directories.toml",   # 2. Directory structure
    PROJECT_ROOT / "cli/config/settings.toml",      # 3. Project settings
    PROJECT_ROOT / "settings.toml",                 # 4. User overrides (highest)
]

class SettingsModel:
    def __init__(self, settings_files: list[Path], project_root: Path):
        self.project_root = project_root
        
        # Load with dynaconf
        self.dynaconf_settings = Dynaconf(
            settings_files=[str(f) for f in settings_files],
        )
        
        # Convert and validate
        settings_dict = self._convert_dict_to_lower_case(
            self._resolve_environment_variables(
                self.dynaconf_settings.to_dict()
            )
        )
        
        # Inject project root for path resolution
        settings_dict['paths'] = settings_dict.get('paths', {})
        settings_dict['paths']['project'] = settings_dict['paths'].get('project', {})
        settings_dict['paths']['project']['root'] = project_root
        
        self.settings = PydanticAppConfig(**settings_dict)
```

## Migration Plan

### Phase 1: Add New Structure (Non-Breaking)
1. Create `cli/config/defaults.toml` with all defaults
2. Add `PathsConfig` model to `config.py`
3. Add `find_project_root()` function
4. Update `SettingsModel` to use new approach
5. Keep old files for backward compatibility

### Phase 2: Update Code to Use New Structure
1. Update all code to use `config.paths.*` instead of scattered paths
2. Update tests
3. Update documentation

### Phase 3: Remove Old Structure
1. Delete `cli_settings_defaults.py`
2. Delete `project_settings_defaults.py`
3. Remove old path attributes from models
4. Clean up deprecated code

## Benefits of Proposed Solution

1. **Single Source of Truth for Paths** - All paths in `PathsConfig`
2. **Robust Project Root Detection** - Marker-based, not fragile
3. **Clear Configuration Hierarchy** - Easy to understand precedence
4. **All Defaults in TOML** - No Python files to maintain
5. **Better Organization** - Logical grouping of related settings
6. **Easier Maintenance** - Change TOML, not code
7. **Self-Documenting** - Structure makes purpose clear
8. **Flexible** - Easy to add new paths or settings

## Conclusion

The current configuration architecture has grown organically and accumulated technical debt. The proposed reorganization will make the system:

- **Easier to understand** - Clear hierarchy and organization
- **Easier to maintain** - Centralized configuration
- **More robust** - Proper project root detection
- **Better documented** - Self-explanatory structure
- **Less error-prone** - Single source of truth

This is a significant refactoring but will pay dividends in long-term maintainability.

