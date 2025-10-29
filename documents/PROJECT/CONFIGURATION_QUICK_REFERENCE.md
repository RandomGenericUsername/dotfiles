# Configuration Quick Reference

## Current Problems (TL;DR)

### 🔴 Critical Issues

1. **Paths scattered across 3+ places** - Hard to find and maintain
2. **Brittle project root detection** - `Path(__file__).parent.parent.parent.parent.parent.parent` breaks easily
3. **Duplicate defaults** - Same values in Python files AND TOML files
4. **Confusing hierarchy** - 6 different configuration layers
5. **Hardcoded paths** - Template directory hardcoded in Pydantic model

### 📍 Where Are Paths Currently?

```python
# Installation directory
config.install.directory                    # CliInstallSettings

# Installation subdirectories (dynamic)
config.install.get_paths().dependencies     # InstallationPaths
config.install.get_paths().config.packages  # InstallationPaths

# Host paths
config.host_paths.wallpapers_directory      # ProjectPaths
config.host_paths.screenshots_directory     # ProjectPaths

# Runtime paths
config.install.debug.log_directory          # InstallDebugSettings
config.install.backup_directory             # CliInstallSettings

# Template paths (HARDCODED!)
config.template_renderer.template_directory # TemplateRendererSettings
```

**Problem:** You need to remember 4+ different locations to find paths!

### 📂 Where Are Defaults Currently?

```
Defaults are in 6 DIFFERENT PLACES:

1. cli/src/config/cli_settings_defaults.py      (Python)
2. cli/src/config/project_settings_defaults.py  (Python)
3. cli/src/config/config.py                     (Pydantic Field defaults)
4. cli/config/directories.toml                  (TOML)
5. cli/config/settings.toml                     (TOML)
6. settings.toml                                (TOML - user overrides)
```

**Problem:** Which file do you edit to change a default? Hard to know!

### 🔧 Current Project Root Detection

```python
# In cli/src/config/settings.py
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
#                              ↑      ↑      ↑      ↑      ↑      ↑
#                              6 levels up - FRAGILE!
```

**Problem:** If you move `settings.py` to a different directory, this breaks!

## Proposed Solution (TL;DR)

### ✅ Unified Path Configuration

```python
# ALL paths in ONE place:
config.paths.project.root                   # Auto-detected project root
config.paths.project.templates              # Relative to root
config.paths.project.docker                 # Relative to root

config.paths.installation.directory         # Install directory
config.paths.installation.backup            # Backup directory
config.paths.installation.subdirs.*         # Dynamic subdirectories

config.paths.host.wallpapers                # Wallpapers directory
config.paths.host.screenshots               # Screenshots directory

config.paths.runtime.logs                   # Logs directory
config.paths.runtime.cache                  # Cache directory
```

**Benefit:** One place to find ALL paths!

### ✅ Robust Project Root Detection

```python
def find_project_root(marker_files: list[str] = None) -> Path:
    """Find project root by looking for marker files."""
    if marker_files is None:
        marker_files = ['pyproject.toml', '.git', 'settings.toml']
    
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in marker_files):
            return parent
    
    raise RuntimeError(f"Could not find project root. Looked for: {marker_files}")
```

**Benefit:** Works from any file, any depth, any location!

### ✅ Clear Configuration Hierarchy

```
Level 1: Project Constants (Python)
  └── find_project_root() - Auto-detect project root

Level 2: Project Defaults (TOML)
  ├── cli/config/defaults.toml      - ALL default values
  ├── cli/config/directories.toml   - Directory structure
  └── cli/config/settings.toml      - Project settings

Level 3: User Overrides (TOML)
  └── settings.toml                 - User customization
```

**Benefit:** Clear precedence, easy to understand!

### ✅ All Defaults in TOML

**Remove these Python files:**
- ❌ `cli/src/config/cli_settings_defaults.py`
- ❌ `cli/src/config/project_settings_defaults.py`

**Create this TOML file:**
- ✅ `cli/config/defaults.toml` - Contains ALL defaults

**Benefit:** Change TOML, not code!

## Configuration File Locations

### Current (Confusing)

```
project/
├── settings.toml                                    # User overrides
├── cli/
│   ├── src/
│   │   └── config/
│   │       ├── cli_settings_defaults.py            # Python defaults
│   │       ├── project_settings_defaults.py        # Python defaults
│   │       ├── config.py                           # Pydantic models with defaults
│   │       └── settings.py                         # Loader (brittle PROJECT_ROOT)
│   └── config/
│       ├── directories.toml                        # Directory structure
│       └── settings.toml                           # Project settings
```

### Proposed (Clear)

```
project/
├── settings.toml                                    # User overrides ONLY
└── cli/
    ├── src/
    │   └── config/
    │       ├── config.py                           # Pydantic models (no defaults)
    │       ├── settings.py                         # Loader (robust root detection)
    │       └── project_root.py                     # find_project_root() function
    └── config/
        ├── defaults.toml                           # ALL defaults (NEW)
        ├── directories.toml                        # Directory structure
        └── settings.toml                           # Project settings
```

## Loading Order

### Current (Unclear)

```
1. Python defaults (cli_settings_defaults.py, project_settings_defaults.py)
2. Pydantic Field defaults
3. directories.toml
4. cli/config/settings.toml
5. settings.toml (highest priority)
```

**Problem:** Not documented, hard to understand precedence

### Proposed (Clear)

```
1. cli/config/defaults.toml      - Project defaults
2. cli/config/directories.toml   - Directory structure
3. cli/config/settings.toml      - Project settings
4. settings.toml                 - User overrides (highest priority)
```

**Benefit:** Simple, linear, documented!

## Example: Finding a Path

### Current (Confusing)

**Q:** Where is the template directory configured?

**A:** It's hardcoded in `cli/src/config/config.py`:
```python
class TemplateRendererSettings(BaseModel):
    template_directory: Path = Field(
        default=Path("src/dotfiles-installer/docker/templates"),
        ...
    )
```

**To change it:** Edit Python code, understand Pydantic, rebuild...

### Proposed (Clear)

**Q:** Where is the template directory configured?

**A:** In `cli/config/defaults.toml`:
```toml
[paths.project]
templates = "src/dotfiles-installer/docker/templates"
```

**To change it:** Edit TOML file, done!

## Example: Changing a Default

### Current (Confusing)

**Q:** How do I change the default log level?

**A:** Could be in:
1. `cli/src/config/cli_settings_defaults.py` - `log_level: LogLevels = LogLevels.ERROR`
2. `cli/src/config/config.py` - `Field(default=log_level, ...)`
3. `settings.toml` - `log_level = "info"`

**Which one do I edit?** 🤷

### Proposed (Clear)

**Q:** How do I change the default log level?

**A:** Edit `cli/config/defaults.toml`:
```toml
[install.debug]
log_level = "error"  # Change this
```

**Clear and simple!** ✅

## Migration Checklist

### Phase 1: Add New Structure
- [ ] Create `cli/config/defaults.toml`
- [ ] Add `PathsConfig` model to `config.py`
- [ ] Add `find_project_root()` function
- [ ] Update `SettingsModel` to use new approach
- [ ] Keep old files for backward compatibility

### Phase 2: Update Code
- [ ] Update all code to use `config.paths.*`
- [ ] Update tests
- [ ] Update documentation

### Phase 3: Remove Old Structure
- [ ] Delete `cli_settings_defaults.py`
- [ ] Delete `project_settings_defaults.py`
- [ ] Remove old path attributes from models
- [ ] Clean up deprecated code

## Key Benefits Summary

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Path locations** | 4+ different places | 1 unified `PathsConfig` |
| **Project root** | Brittle `.parent` chain | Robust marker detection |
| **Defaults** | 6 different files | 1 TOML file |
| **Hierarchy** | Unclear, undocumented | Clear 3-level structure |
| **Maintenance** | Edit Python code | Edit TOML files |
| **Understanding** | Hard, scattered | Easy, organized |
| **Robustness** | Breaks on restructure | Resilient to changes |

## Quick Decision Guide

### "Where should I put this configuration?"

```
Is it a path?
├─ Yes → config.paths.*
│  ├─ Project internal? → config.paths.project.*
│  ├─ Installation? → config.paths.installation.*
│  ├─ Host system? → config.paths.host.*
│  └─ Runtime (logs/cache)? → config.paths.runtime.*
└─ No → Appropriate section (install, system, package_manager, etc.)
```

### "Where should I define this default?"

```
Current: 🤷 Could be anywhere...

Proposed: ✅ cli/config/defaults.toml
```

### "How do I find the project root?"

```
Current: 🔴 Path(__file__).parent.parent.parent.parent.parent.parent

Proposed: ✅ find_project_root()
```

## Conclusion

The proposed architecture makes configuration:
- **Easier to find** - One place for paths
- **Easier to change** - Edit TOML, not code
- **Easier to understand** - Clear hierarchy
- **More robust** - Proper root detection
- **Better organized** - Logical structure

**Next Steps:** Review the full analysis in `CONFIGURATION_ARCHITECTURE_ANALYSIS.md`

