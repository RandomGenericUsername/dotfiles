# Eww (ElKowar's Wacky Widgets) Installation

## Overview

The dotfiles installer includes automated installation of [Eww](https://github.com/elkowar/eww), a standalone widget system written in Rust that allows you to create custom widgets for any window manager.

Eww is built from source using the Rust toolchain (Rustup + Cargo) and supports both Wayland and X11 display servers.

## Installation Process

The installer follows this pipeline:

1. **Install Rustup** - Rust toolchain manager
2. **Install Rust** - Rust compiler and tools (version 1.75.0 by default)
3. **Build Eww** - Clone and compile from source with specified features
4. **Install Config** - Copy widget configuration files

## Installation Locations

### Binary Installation
- **Eww Binary**: `{install_root}/.dependencies/eww/bin/eww`
- **Eww Source**: `{install_root}/.dependencies/eww-source/` (git repository)
- **Rustup**: `{install_root}/.dependencies/rustup/`
- **Cargo**: `{install_root}/.dependencies/cargo/`

Where `{install_root}` is your configured installation directory (default: `~/dotfiles`).

### Configuration Files
- **Eww Config**: `{install_root}/dotfiles/eww/`
- **Widget Directories**: `{install_root}/dotfiles/eww/status-bar/` (example)

## Configuration

### Feature Configuration

Edit `cli/config/settings.toml`:

```toml
[project.settings.system.packages.features.eww]
version = "master"  # Git branch/tag to use
git_url = "https://github.com/elkowar/eww"
branch = "master"
features = ["wayland", "x11"]  # Build features
```

**Available Features:**
- `wayland` - Wayland support
- `x11` - X11 support
- You can specify both or just one depending on your display server

### Config Files Location

Edit `cli/config/settings.toml`:

```toml
[project.settings.system.packages.config.eww]
type = "directory"
path = "src/dotfiles/config-files/eww"
```

### Directory Structure

The installer creates widget-based subdirectories as defined in `cli/config/directories.toml`:

```toml
dotfiles_eww = "{dotfiles}/eww"
dotfiles_eww_status_bar = "{dotfiles_eww}/status-bar"
```

Add more widget directories by editing this file.

## Build Dependencies

The installer automatically installs required system packages for building Eww:

### Fedora/RHEL
- gtk3-devel
- gtk-layer-shell-devel
- pango-devel
- gdk-pixbuf2-devel
- cairo-devel
- glib2-devel
- libdbusmenu-gtk3-devel

### Debian/Ubuntu
- libgtk-3-dev
- libgtk-layer-shell-dev
- libpango1.0-dev
- libgdk-pixbuf2.0-dev
- libcairo2-dev
- libglib2.0-dev
- libdbusmenu-gtk3-dev

### Arch Linux
- gtk3
- gtk-layer-shell
- pango
- gdk-pixbuf2
- cairo
- glib2
- gcc-libs
- libdbusmenu-gtk3

## Update Behavior

### Update Install (Default)
During an update installation:
- ✅ Eww source repository is **preserved**
- ✅ Rustup and Cargo are **preserved**
- ✅ Eww binary is **preserved**
- ✅ Only config files in `dotfiles/eww/` are updated

If Eww is already installed, the installer skips rebuilding and just updates configuration files.

### Clean Install
During a clean installation:
- ❌ Entire installation directory is deleted
- ❌ Eww source, Rustup, Cargo, and binary are removed
- ❌ Everything is rebuilt from scratch

## Verification

After installation, verify Eww is working:

```bash
# Check version
~/.tmp/inumaki-dotfiles/.dependencies/eww/bin/eww --version

# View help
~/.tmp/inumaki-dotfiles/.dependencies/eww/bin/eww --help

# Start daemon
~/.tmp/inumaki-dotfiles/.dependencies/eww/bin/eww daemon
```

## Troubleshooting

### Build Failures

If Eww fails to build, check:
1. All build dependencies are installed
2. Rust version is compatible (1.75.0 or later recommended)
3. Git repository is accessible
4. Sufficient disk space for build artifacts

### Missing Dependencies

If you see pkg-config errors, ensure all development packages are installed:
```bash
# Fedora
sudo dnf install gtk3-devel gtk-layer-shell-devel libdbusmenu-gtk3-devel

# Debian/Ubuntu
sudo apt install libgtk-3-dev libgtk-layer-shell-dev libdbusmenu-gtk3-dev

# Arch
sudo pacman -S gtk3 gtk-layer-shell libdbusmenu-gtk3
```

## Related Documentation

- [Eww Official Documentation](https://elkowar.github.io/eww/)
- [Eww GitHub Repository](https://github.com/elkowar/eww)
- Rust Installation: See `rust-installation.md`
