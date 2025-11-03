# Usage Patterns

This guide documents common usage patterns and best practices for the filesystem-path-builder module.

---

## Pattern 1: Application Configuration Directories

**Use Case:** Create and manage application configuration directories.

```python
from pathlib import Path
from filesystem_path_builder import ManagedPathTree, PathDefinition

# Define application directory structure
app_paths = ManagedPathTree(
    base=Path.home() / ".myapp",
    definitions=[
        PathDefinition(key="config", hidden=False),
        PathDefinition(key="data.cache", hidden=False),
        PathDefinition(key="data.logs", hidden=False),
        PathDefinition(key="plugins", hidden=False),
    ]
)

# Create all directories
app_paths.create()

# Use paths
config_file = app_paths.config / "settings.toml"
cache_dir = app_paths.data.cache
log_file = app_paths.data.logs / "app.log"
plugins_dir = app_paths.plugins
```

**Benefits:**
- Single source of truth for directory structure
- Bulk creation
- Easy navigation
- Type-safe

---

## Pattern 2: XDG Base Directory Specification

**Use Case:** Follow XDG Base Directory specification for Linux applications.

```python
from pathlib import Path
import os
from filesystem_path_builder import ManagedPathTree, PathDefinition

# Get XDG directories or use defaults
xdg_config_home = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
xdg_data_home = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share"))
xdg_cache_home = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))

# Create app-specific paths
app_name = "myapp"

config_paths = ManagedPathTree(
    base=xdg_config_home / app_name,
    definitions=[PathDefinition(key="", hidden=False)]
)

data_paths = ManagedPathTree(
    base=xdg_data_home / app_name,
    definitions=[
        PathDefinition(key="databases", hidden=False),
        PathDefinition(key="plugins", hidden=False),
    ]
)

cache_paths = ManagedPathTree(
    base=xdg_cache_home / app_name,
    definitions=[PathDefinition(key="", hidden=False)]
)

# Create all directories
config_paths.create()
data_paths.create()
cache_paths.create()

# Use paths
config_file = config_paths / "config.toml"
db_file = data_paths.databases / "app.db"
cache_file = cache_paths / "cache.json"
```

---

## Pattern 3: Hidden Dotfiles Management

**Use Case:** Manage hidden dotfiles and configuration directories.

```python
from pathlib import Path
from filesystem_path_builder import PathsBuilder

# Build dotfiles structure with hidden directories
builder = PathsBuilder(Path.home())
dotfiles = (builder
    .add("dotfiles.config", hidden=True)  # ~/.config
    .add("dotfiles.local.share", hidden=True)  # ~/.local/share
    .add("dotfiles.cache", hidden=True)  # ~/.cache
    .add("dotfiles.ssh", hidden=True)  # ~/.ssh
    .build())

# Create directories
dotfiles.create()

# Access hidden directories
config_dir = dotfiles.dotfiles.config  # ~/.config
share_dir = dotfiles.dotfiles.local.share  # ~/.local/share
ssh_dir = dotfiles.dotfiles.ssh  # ~/.ssh
```

**Benefits:**
- Automatic dot-prefix for hidden directories
- Clean, declarative configuration
- Type-safe navigation

---

## Pattern 4: Project Directory Structure

**Use Case:** Navigate existing project directory structure.

```python
from pathlib import Path
from filesystem_path_builder import PathTree

# Navigate project structure
project = PathTree(Path("/workspace/myproject"))

# Access various project paths
src_dir = project.src
tests_dir = project.tests
docs_dir = project.docs
build_dir = project.build.output

# Use with file operations
source_file = project.src.main / "app.py"
test_file = project.tests.unit / "test_app.py"
readme = project / "README.md"

# Check existence
if project.build.exists():
    # Clean build directory
    import shutil
    shutil.rmtree(project.build.to_path())
```

**Benefits:**
- No need to define structure (navigates existing)
- Type-safe navigation
- No filesystem I/O during navigation

---

## Pattern 5: Dynamic Path Building

**Use Case:** Build paths dynamically based on runtime configuration.

```python
from pathlib import Path
from filesystem_path_builder import PathsBuilder

def create_user_directories(username: str, groups: list[str]):
    """Create user-specific directory structure."""
    builder = PathsBuilder(Path(f"/home/{username}"))

    # Add standard directories
    builder.add("documents", hidden=False)
    builder.add("downloads", hidden=False)

    # Add group-specific directories
    for group in groups:
        builder.add(f"projects.{group}", hidden=False)

    # Build and create
    paths = builder.build()
    paths.create()

    return paths

# Usage
user_paths = create_user_directories("alice", ["dev", "research"])
# Creates: /home/alice/documents
#          /home/alice/downloads
#          /home/alice/projects/dev
#          /home/alice/projects/research
```

---

## Pattern 6: Temporary Directory Management

**Use Case:** Manage temporary directories with automatic cleanup.

```python
from pathlib import Path
import tempfile
import shutil
from filesystem_path_builder import ManagedPathTree, PathDefinition

class TempWorkspace:
    """Temporary workspace with structured directories."""

    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.paths = ManagedPathTree(
            base=self.temp_dir,
            definitions=[
                PathDefinition(key="input", hidden=False),
                PathDefinition(key="output", hidden=False),
                PathDefinition(key="cache", hidden=False),
            ]
        )
        self.paths.create()

    def __enter__(self):
        return self.paths

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir)

# Usage
with TempWorkspace() as workspace:
    input_file = workspace.input / "data.txt"
    output_file = workspace.output / "result.txt"

    # Do work...
    input_file.to_path().write_text("data")

# Automatic cleanup when exiting context
```

---

## Pattern 7: Multi-Environment Configuration

**Use Case:** Manage paths for different environments (dev, staging, prod).

```python
from pathlib import Path
from filesystem_path_builder import ManagedPathTree, PathDefinition
from enum import Enum

class Environment(Enum):
    DEV = "development"
    STAGING = "staging"
    PROD = "production"

def get_app_paths(env: Environment) -> ManagedPathTree:
    """Get application paths for specific environment."""
    base = Path(f"/var/app/{env.value}")

    paths = ManagedPathTree(
        base=base,
        definitions=[
            PathDefinition(key="config", hidden=False),
            PathDefinition(key="data", hidden=False),
            PathDefinition(key="logs", hidden=False),
            PathDefinition(key="temp", hidden=False),
        ]
    )

    paths.create()
    return paths

# Usage
dev_paths = get_app_paths(Environment.DEV)
prod_paths = get_app_paths(Environment.PROD)

dev_config = dev_paths.config / "settings.toml"
prod_config = prod_paths.config / "settings.toml"
```

---

## Pattern 8: Backup Directory Management

**Use Case:** Create timestamped backup directories.

```python
from pathlib import Path
from datetime import datetime
from filesystem_path_builder import PathTree

def create_backup_dir(base: Path) -> Path:
    """Create timestamped backup directory."""
    backups = PathTree(base)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backups / timestamp
    backup_dir.to_path().mkdir(parents=True, exist_ok=True)
    return backup_dir.to_path()

# Usage
backup_base = Path("/backups/myapp")
backup_dir = create_backup_dir(backup_base)
# Creates: /backups/myapp/20251029_143022
```

---

## Pattern 9: Plugin Directory Discovery

**Use Case:** Discover and load plugins from directory structure.

```python
from pathlib import Path
from filesystem_path_builder import PathTree

def discover_plugins(app_dir: Path) -> dict[str, Path]:
    """Discover plugins in application directory."""
    paths = PathTree(app_dir)
    plugins_dir = paths.plugins.to_path()

    if not plugins_dir.exists():
        return {}

    plugins = {}
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir():
            plugin_file = plugin_dir / "plugin.py"
            if plugin_file.exists():
                plugins[plugin_dir.name] = plugin_file

    return plugins

# Usage
app_paths = PathTree(Path("/opt/myapp"))
plugins = discover_plugins(app_paths.to_path())
for name, path in plugins.items():
    print(f"Found plugin: {name} at {path}")
```

---

## Pattern 10: Configuration File Hierarchy

**Use Case:** Search for configuration files in multiple locations.

```python
from pathlib import Path
from filesystem_path_builder import PathTree

def find_config_file(app_name: str, config_name: str) -> Path | None:
    """Find configuration file in standard locations."""
    search_paths = [
        PathTree(Path.cwd()) / config_name,  # Current directory
        PathTree(Path.home()) / f".{app_name}" / config_name,  # User config
        PathTree(Path("/etc")) / app_name / config_name,  # System config
    ]

    for path_tree in search_paths:
        path = path_tree.to_path()
        if path.exists():
            return path

    return None

# Usage
config_file = find_config_file("myapp", "config.toml")
if config_file:
    print(f"Found config: {config_file}")
else:
    print("No config file found")
```

---

## Pattern 11: Data Migration Paths

**Use Case:** Manage paths for data migration between versions.

```python
from pathlib import Path
from filesystem_path_builder import ManagedPathTree, PathDefinition

def setup_migration_workspace(version_from: str, version_to: str) -> ManagedPathTree:
    """Setup workspace for data migration."""
    base = Path(f"/tmp/migration_{version_from}_to_{version_to}")

    workspace = ManagedPathTree(
        base=base,
        definitions=[
            PathDefinition(key="source", hidden=False),
            PathDefinition(key="target", hidden=False),
            PathDefinition(key="backup", hidden=False),
            PathDefinition(key="logs", hidden=False),
        ]
    )

    workspace.create()
    return workspace

# Usage
migration = setup_migration_workspace("1.0", "2.0")
source_data = migration.source / "data.db"
target_data = migration.target / "data.db"
backup_data = migration.backup / "data.db.bak"
log_file = migration.logs / "migration.log"
```

---

## Pattern 12: Test Fixture Directories

**Use Case:** Create test fixture directories for unit tests.

```python
from pathlib import Path
import pytest
from filesystem_path_builder import ManagedPathTree, PathDefinition

@pytest.fixture
def test_workspace(tmp_path):
    """Create test workspace with structured directories."""
    workspace = ManagedPathTree(
        base=tmp_path,
        definitions=[
            PathDefinition(key="input", hidden=False),
            PathDefinition(key="output", hidden=False),
            PathDefinition(key="expected", hidden=False),
        ]
    )
    workspace.create()

    # Setup test data
    (workspace.input / "test.txt").to_path().write_text("test data")
    (workspace.expected / "result.txt").to_path().write_text("expected result")

    return workspace

def test_processing(test_workspace):
    """Test data processing."""
    input_file = test_workspace.input / "test.txt"
    output_file = test_workspace.output / "result.txt"
    expected_file = test_workspace.expected / "result.txt"

    # Process data
    data = input_file.to_path().read_text()
    output_file.to_path().write_text(data.upper())

    # Verify
    assert output_file.to_path().exists()
```

---

## Best Practices Summary

### 1. Choose the Right Tool

- **PathTree**: Simple navigation, no creation needed
- **PathsBuilder**: Explicit configuration, hidden directories
- **ManagedPathTree**: Bulk creation, registry management

### 2. Use Type Hints

```python
from filesystem_path_builder import PathTree, ManagedPathTree

def get_config_dir(base: Path) -> PathTree:
    paths = PathTree(base)
    return paths.config
```

### 3. Convert to Path for Operations

```python
# Good
paths = PathTree(Path("/home/user"))
config_path = paths.config.to_path()
config_path.mkdir(parents=True, exist_ok=True)

# Bad
paths.config.mkdir()  # Error: PathTree has no mkdir
```

### 4. Use Context Managers for Cleanup

```python
class ManagedWorkspace:
    def __enter__(self):
        self.paths = ManagedPathTree(...)
        self.paths.create()
        return self.paths

    def __exit__(self, *args):
        # Cleanup
        shutil.rmtree(self.paths.to_path())
```

### 5. Validate Paths

```python
paths = PathTree(Path("/home/user"))

if not paths.config.exists():
    paths.config.to_path().mkdir(parents=True, exist_ok=True)
```

---

## Anti-Patterns to Avoid

### 1. Don't Modify Frozen Objects

```python
# Wrong
paths = PathTree(Path("/home/user"))
paths._base = Path("/other")  # Error: frozen dataclass

# Correct
paths = PathTree(Path("/other"))
```

### 2. Don't Use PathTree with os Functions

```python
# Wrong
paths = PathTree(Path("/home/user"))
os.listdir(paths.config)  # Error: no __fspath__

# Correct
os.listdir(paths.config.to_path())
# Or use ManagedPathTree
```

### 3. Don't Create Paths in Loops

```python
# Inefficient
for i in range(100):
    path = PathTree(Path("/home/user")).config.to_path()

# Better
paths = PathTree(Path("/home/user"))
config = paths.config.to_path()
for i in range(100):
    # Use config
    pass
```

---

**Next:** [Integration Guide](integration.md) | [Best Practices](best_practices.md)
