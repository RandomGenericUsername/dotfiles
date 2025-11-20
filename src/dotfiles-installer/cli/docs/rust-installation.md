# Rust Toolchain Installation

## Overview

The dotfiles installer includes automated installation of the Rust programming language toolchain using Rustup, the official Rust toolchain manager. This is required for building Rust-based tools like Eww from source.

## Installation Process

The installer follows this two-step process:

1. **Install Rustup** - The Rust toolchain manager
2. **Install Rust** - The Rust compiler and tools (cargo, rustc, etc.)

## Installation Locations

### Directory Structure

- **Rustup Home**: `{install_root}/.dependencies/rustup/`
  - Contains Rustup's data files, toolchains, and settings
  - Environment variable: `RUSTUP_HOME`

- **Cargo Home**: `{install_root}/.dependencies/cargo/`
  - Contains all Rust binaries and tools
  - Environment variable: `CARGO_HOME`

### Important: Binary Locations

All Rust-related binaries are installed in `{install_root}/.dependencies/cargo/bin/`:
- `rustup` - Rustup toolchain manager
- `cargo` - Rust package manager
- `rustc` - Rust compiler
- `rust-analyzer` - Rust language server (if installed)
- Any other Rust tools installed via cargo

**Note**: Despite the name `RUSTUP_HOME`, the `rustup` binary itself is located in `CARGO_HOME/bin/`, not `RUSTUP_HOME/bin/`. This is the standard Rustup behavior.

## Configuration

### Rustup Configuration

Edit `cli/config/settings.toml`:

```toml
[project.settings.system.packages.features.rustup]
version = "latest"  # Always installs the latest version
```

Rustup is always installed with the latest version from the official installer script.

### Rust Configuration

Edit `cli/config/settings.toml`:

```toml
[project.settings.system.packages.features.rust]
version = "1.75.0"  # Specific version, or "stable", "nightly", "beta"
```

**Version Options:**
- Specific version: `"1.75.0"`, `"1.76.0"`, etc.
- Channel: `"stable"`, `"nightly"`, `"beta"`
- Default: `"stable"` if not specified

## Installation Details

### Rustup Installation

The installer:
1. Downloads the official rustup-init script from https://sh.rustup.rs
2. Executes with non-interactive flags:
   - `--no-modify-path` - Doesn't modify shell profile
   - `-y` - Accepts defaults
   - `--default-toolchain none` - Doesn't install a toolchain yet
3. Sets custom `RUSTUP_HOME` and `CARGO_HOME` environment variables
4. Verifies installation by checking for `rustup` binary

### Rust Toolchain Installation

The installer:
1. Uses the installed `rustup` to install the specified Rust version
2. Runs: `rustup toolchain install <version>`
3. Sets as default toolchain: `rustup default <version>`
4. Verifies installation by checking `rustc --version`

## Update Behavior

### Update Install (Default)
During an update installation:
- ✅ Rustup installation is **preserved**
- ✅ Cargo directory is **preserved**
- ✅ All installed Rust toolchains are **preserved**
- ✅ Installed cargo packages are **preserved**

If Rustup and Rust are already installed, the installer skips reinstallation.

### Clean Install
During a clean installation:
- ❌ Entire installation directory is deleted
- ❌ Rustup, Cargo, and all toolchains are removed
- ❌ Everything is reinstalled from scratch

## Verification

After installation, verify Rust is working:

```bash
# Check Rustup version
~/.tmp/inumaki-dotfiles/.dependencies/cargo/bin/rustup --version

# Check Rust version
~/.tmp/inumaki-dotfiles/.dependencies/cargo/bin/rustc --version

# Check Cargo version
~/.tmp/inumaki-dotfiles/.dependencies/cargo/bin/cargo --version

# List installed toolchains
~/.tmp/inumaki-dotfiles/.dependencies/cargo/bin/rustup toolchain list
```

## Usage

### Building Rust Projects

To use the installed Rust toolchain for building projects:

```bash
# Set environment variables
export RUSTUP_HOME=~/.tmp/inumaki-dotfiles/.dependencies/rustup
export CARGO_HOME=~/.tmp/inumaki-dotfiles/.dependencies/cargo
export PATH="$CARGO_HOME/bin:$PATH"

# Build a project
cargo build --release
```

### Installing Additional Tools

```bash
# Install a cargo package
~/.tmp/inumaki-dotfiles/.dependencies/cargo/bin/cargo install <package-name>

# Install additional toolchain
~/.tmp/inumaki-dotfiles/.dependencies/cargo/bin/rustup toolchain install nightly
```

## Troubleshooting

### Rustup Binary Not Found

If you see "rustup binary not found" errors:
- Check that `CARGO_HOME/bin/rustup` exists (not `RUSTUP_HOME/bin/rustup`)
- Verify environment variables are set correctly
- Ensure the installation completed successfully

### Permission Errors

If you encounter permission errors:
```bash
# Ensure directories are writable
chmod -R u+w ~/.tmp/inumaki-dotfiles/.dependencies/rustup
chmod -R u+w ~/.tmp/inumaki-dotfiles/.dependencies/cargo
```

### Network Issues

If rustup-init download fails:
- Check internet connectivity
- Verify https://sh.rustup.rs is accessible
- Try again later if the service is temporarily unavailable

## Environment Variables

The installer uses these environment variables during installation:

- `RUSTUP_HOME`: Directory for Rustup's data files
- `CARGO_HOME`: Directory for Cargo and all Rust binaries

These are automatically set during the installation process and when building Rust projects.

## Related Documentation

- [Rustup Official Documentation](https://rust-lang.github.io/rustup/)
- [Rust Official Documentation](https://www.rust-lang.org/)
- Eww Installation: See `eww-installation.md`
