# Colorscheme Orchestrator

CLI tool for orchestrating containerized colorscheme generation backends.

## Overview

The Colorscheme Orchestrator provides a simple CLI interface for generating colorschemes from images using containerized backends. It uses the `colorscheme-generator` and `container-manager` common modules to provide isolated, reproducible colorscheme generation.

## Features

- **Multiple Backends**: Support for pywal, wallust, and custom backends
- **Container Isolation**: Each backend runs in its own container
- **Configurable**: Settings file with CLI overrides
- **Simple CLI**: Easy-to-use Typer-based interface
- **Beautiful Output**: Rich terminal output with progress and status

## Installation

```bash
# From the colorscheme-orchestrator directory
make install
```

This will:
1. Install common module dependencies (logging, container-manager, colorscheme-generator)
2. Install the orchestrator in editable mode
3. Make the `colorscheme-gen` command available

## Usage

### Generate Colorscheme

```bash
# Basic usage with default backend (from settings)
colorscheme-gen -i wallpaper.png

# Specify backend
colorscheme-gen --backend pywal --image wallpaper.png

# Custom output directory
colorscheme-gen -b wallust -i wallpaper.png -o ~/my-colors

# Specify formats
colorscheme-gen -b custom -i wallpaper.png -f json,css,yaml

# Custom backend with algorithm
colorscheme-gen -b custom -i wallpaper.png -a median_cut -c 8
```

### List Backends

```bash
colorscheme-gen list
```

### Build Container Images

```bash
# Build specific backend
colorscheme-gen build -b pywal

# Build all backends
colorscheme-gen build --all

# Build without cache
colorscheme-gen build -b pywal --no-cache
```

### Clean Up

```bash
# Clean all containers and images
colorscheme-gen clean

# Clean specific backend
colorscheme-gen clean -b pywal
```

## Configuration

Settings are in `src/colorscheme_orchestrator/config/settings.toml`:

```toml
[orchestrator]
default_backend = "pywal"
default_output_dir = "$HOME/.cache/colorscheme"
default_formats = ["json", "css", "yaml", "sh"]
default_color_count = 16
container_runtime = "docker"  # or "podman"
auto_cleanup = true
keep_images = true
log_level = "INFO"
verbose = false

[backends.pywal]
image_name = "colorscheme-pywal"
image_tag = "latest"
use_library = true

[backends.wallust]
image_name = "colorscheme-wallust"
image_tag = "latest"
output_format = "json"
backend_type = "resized"

[backends.custom]
image_name = "colorscheme-custom"
image_tag = "latest"
algorithm = "kmeans"
n_clusters = 16
```

All settings can be overridden via CLI parameters.

## CLI Options

### Generate Command

```
Options:
  -b, --backend TEXT        Backend to use (pywal, wallust, custom)
  -i, --image PATH          Path to source image [required]
  -o, --output PATH         Output directory
  -f, --formats TEXT        Comma-separated formats (json,css,yaml,sh)
  -c, --colors INTEGER      Number of colors to extract
  -a, --algorithm TEXT      Algorithm for custom backend
  --runtime TEXT            Container runtime (docker, podman)
  --rebuild                 Force rebuild container image
  --keep-container          Don't remove container after completion
  -v, --verbose             Enable verbose logging
  -h, --help                Show help message
```

### Build Command

```
Options:
  -b, --backend TEXT        Build specific backend
  --all                     Build all backend images
  --no-cache                Build without using cache
  -h, --help                Show help message
```

### List Command

```
Lists available backends and their status
```

### Clean Command

```
Options:
  -b, --backend TEXT        Clean specific backend only
  -h, --help                Show help message
```

## Architecture

```
CLI (Typer)
    ↓
Orchestrator
    ↓
    ├─→ Builder (builds container images)
    └─→ Runner (runs containers)
            ↓
        Container Engine (Docker/Podman)
            ↓
        Backend Containers
            ↓
        Colorscheme Files
```

## Development

### Project Structure

```
src/common/tools/colorscheme-orchestrator/
├── pyproject.toml
├── Makefile
├── README.md
├── src/colorscheme_orchestrator/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # Typer CLI
│   ├── orchestrator.py     # Main orchestrator
│   ├── exceptions.py       # Custom exceptions
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py     # Pydantic models
│   │   └── settings.toml   # Configuration
│   └── containers/
│       ├── __init__.py
│       ├── builder.py      # Image builder
│       ├── runner.py       # Container runner
│       └── registry.py     # Backend registry
└── containers/             # Container definitions (Phase 2)
    ├── pywal/
    │   ├── Dockerfile
    │   └── entrypoint.py
    ├── wallust/
    │   ├── Dockerfile
    │   └── entrypoint.py
    └── custom/
        ├── Dockerfile
        └── entrypoint.py
```

### Makefile Commands

```bash
make help           # Show all commands
make install        # Install everything
make install-deps   # Install common modules
make install-local  # Install orchestrator only
make build          # Build package
make test           # Run tests
make lint           # Run linters
make format         # Format code
make clean          # Clean build artifacts
```

## Implementation Status

### Phase 1: Core Infrastructure ✓
- [x] Project structure
- [x] Configuration system (settings.toml + Pydantic)
- [x] CLI with Typer
- [x] Orchestrator skeleton
- [x] Builder skeleton
- [x] Runner skeleton
- [x] Registry
- [x] Makefile

### Phase 2: Container Definitions (Next)
- [ ] Dockerfiles for all backends
- [ ] Entrypoint scripts
- [ ] Builder implementation
- [ ] Runner implementation
- [ ] Integration with container-manager

### Phase 3: Polish (Future)
- [ ] Error handling improvements
- [ ] Progress bars
- [ ] Logging integration
- [ ] Tests
- [ ] Documentation

## Dependencies

- **colorscheme-generator**: Color extraction backends
- **container-manager**: Container orchestration
- **dotfiles-logging**: Logging (Phase 3)
- **typer**: CLI framework
- **rich**: Terminal output
- **pydantic**: Configuration models
- **dynaconf**: Settings management

## License

MIT
