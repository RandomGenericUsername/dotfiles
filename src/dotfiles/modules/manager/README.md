# Dotfiles Manager

Generic manager module for dotfiles components.

## Overview

The Dotfiles Manager provides a flexible framework for managing dotfiles components, configurations, and resources.

## Features

- **Generic Management Interface**: Extensible base for managing various dotfiles components
- **Type-Safe**: Full type hints and Pydantic configuration
- **Configurable**: TOML-based configuration with sensible defaults
- **Logging Integration**: Built-in logging support via dotfiles-logging

## Installation

```bash
cd src/dotfiles/modules/manager
uv sync
```

## Quick Start

```python
from dotfiles_manager import Manager

# Create manager instance
manager = Manager()

# Use manager functionality
# (Implementation details to be added based on specific requirements)
```

## Configuration

### Using Configuration Files

Create `config/settings.toml` or `~/.config/dotfiles-manager/settings.toml`:

```toml
[manager]
# Configuration options here
```

### Using Code

```python
from dotfiles_manager import Manager, ManagerConfig

# Custom configuration
config = ManagerConfig(
    # Configuration parameters
)
manager = Manager(config=config)
```

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

## Architecture

```
manager/
├── src/dotfiles_manager/
│   ├── __init__.py           # Main exports
│   ├── manager.py            # Manager implementation
│   ├── core/
│   │   └── base.py           # Base classes and interfaces
│   └── config/
│       ├── config.py         # Pydantic models
│       └── settings.py       # Settings loader
├── config/
│   └── settings.toml         # Default configuration
└── tests/                    # Test suite
```

## License

Part of the dotfiles project.
