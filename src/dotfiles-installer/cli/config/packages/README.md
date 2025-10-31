# Package Definitions

This directory contains distribution-specific package definitions for the dotfiles installer.

## Directory Structure

```
packages/
├── arch/           # Arch Linux package definitions
│   └── system.toml
├── debian/         # Debian/Ubuntu package definitions
│   └── system.toml
├── redhat/         # RedHat/Fedora package definitions
│   └── system.toml
└── README.md
```

## How It Works

The installer automatically loads the correct package definitions during settings initialization:

1. **Package Manager Detection** (during settings loading):
   - Detects which package manager is available on the system
   - Supports: pacman, yay, paru (Arch), apt, apt-get (Debian), dnf, yum (RedHat)
   - Maps the detected package manager to the appropriate distribution directory

2. **Load Distribution Config** (via dynaconf settings hierarchy):
   - The appropriate `system.toml` file is automatically included in the settings
   - Configuration hierarchy: project settings → distro packages → user overrides
   - Packages are available at `config.project.settings.system.packages`

### Package Manager to Distribution Mapping

| Package Manager | Distribution Directory |
|----------------|----------------------|
| pacman, yay, paru | arch |
| apt | debian |
| dnf | redhat |

### Distribution Detection

- **Arch Linux**: Uses `packages/arch/system.toml`
- **Debian/Ubuntu**: Uses `packages/debian/system.toml`
- **RedHat/Fedora**: Uses `packages/redhat/system.toml`

## Package Definition Format

Each `system.toml` file follows this structure:

```toml
[system.packages]
packages = [
    "package1",
    "package2",
    # ... more packages
]

# Package-specific configurations
[system.packages.config.package_name]
template_directory = "path/to/template.j2"

# Features with version specifications
[system.packages.features]
feature_name = { version = "x.y.z" }
```

### Sections

1. **`[system.packages]`**: List of system packages to install
   - Use distribution-specific package names
   - Example: `base-devel` (Arch) vs `build-essential` (Debian)

2. **`[system.packages.config.*]`**: Package-specific configuration
   - Define template directories for config files
   - Example: zsh, tmux configurations

3. **`[system.packages.features]`**: Features with version requirements
   - Language runtimes (python, nodejs, rust, etc.)
   - Version-pinned installations

## Adding New Distributions

To add support for a new distribution:

1. Create a new directory: `packages/<distro_name>/`
2. Create `system.toml` with distribution-specific package names
3. Update the package manager factory to detect the new distribution
4. Map the distribution to the appropriate package definition directory

## Notes

- Package names must match the distribution's package manager naming
- Keep common packages across distributions when possible
- Document distribution-specific packages with comments
- Version specifications in features should be compatible with the distribution's package manager
