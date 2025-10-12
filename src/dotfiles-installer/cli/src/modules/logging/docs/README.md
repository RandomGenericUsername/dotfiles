# Logging Module Documentation

A comprehensive, type-safe logging system with Rich integration, file handling, and extensible architecture.

## 📚 Documentation Index

### Core Documentation
- **[Architecture Overview](./architecture.md)** - System design, patterns, and component relationships
- **[API Reference](./api-reference.md)** - Complete API documentation with signatures and examples
- **[Usage Guide](./usage-guide.md)** - Practical examples and common patterns
- **[Configuration Guide](./configuration.md)** - All configuration options and settings

### Rich Features
- **[Rich Features Guide](./rich-features.md)** - Tables, panels, progress bars, and more
- **[Rich Integration](./rich-integration.md)** - How Rich features integrate with logging

### Advanced Topics
- **[Extension Guide](./extension-guide.md)** - How to extend the logging system
- **[File Handling](./file-handling.md)** - File logging, rotation, and management
- **[Type Safety](./type-safety.md)** - Type-safe configuration and validation
- **[Migration Guide](./migration.md)** - Migrating from other logging systems

### Development
- **[Development Guide](./development.md)** - Contributing and development setup
- **[Testing Guide](./testing.md)** - Testing patterns and examples
- **[Troubleshooting](./troubleshooting.md)** - Common issues and solutions

## 🚀 Quick Start

### Basic Usage
```python
from cli.modules.logging import Log, LogLevels, ConsoleHandlers

# Simple logger
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
logger.info("Hello, world!")

# Rich logger with features
logger = Log.create_logger(
    "myapp",
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)

# Use Rich features
logger.table(data, title="Results")
logger.panel("Important message", title="Alert")
with logger.progress("Processing...") as progress:
    # work here
    pass
```

### Console + File Logging
```python
from cli.modules.logging import (
    Log, ConsoleHandlers, RichHandlerSettings,
    FileHandlerSpec, FileHandlerTypes, FileHandlerSettings
)

logger = Log.create_logger(
    "myapp",
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True),
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.ROTATING_FILE,
            config=RotatingFileHandlerSettings(
                filename="app.log",
                max_bytes=10_000_000,
                backup_count=5
            )
        )
    ]
)

logger.info("Logged to both console and file!")
```

## 🏗️ Architecture Overview

The logging module follows a clean, extensible architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        Log (Facade)                        │
├─────────────────────────────────────────────────────────────┤
│  • create_logger()  • update()  • Static interface         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    LogConfigurator                         │
├─────────────────────────────────────────────────────────────┤
│  • configure()  • Orchestrates setup  • Type validation    │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    Formatters       │ │    Handlers     │ │  Rich Features  │
├─────────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • ColoredFormatter  │ │ • ConsoleHandler│ │ • RichLogger    │
│ • RichFormatter     │ │ • FileHandler   │ │ • RichConsole   │
│ • DefaultFormatter  │ │ • RichHandler   │ │ • Manager       │
└─────────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🎯 Key Features

### ✅ Type Safety
- **Dataclass-based configuration** with validation
- **IDE autocomplete** and error detection
- **Runtime validation** with helpful error messages

### ✅ Rich Integration
- **Beautiful console output** with colors and formatting
- **Rich features** - tables, panels, progress bars, rules
- **Console sharing** between logging and Rich features
- **Graceful fallback** when Rich is unavailable

### ✅ File Handling
- **Multiple file handlers** with different configurations
- **File rotation** - size-based and time-based
- **Per-file formatting** - different formats for different files
- **Type-safe configuration** for all file handler types

### ✅ Extensible Architecture
- **Factory patterns** for formatters and handlers
- **Plugin-style extension** points
- **Clean separation of concerns**
- **Easy to add new features**

### ✅ Developer Experience
- **Simple API** - create_logger() and update()
- **Preset configurations** for common use cases
- **Comprehensive documentation** and examples
- **Backward compatibility** with standard logging

## 🔧 Configuration Options

### Console Handlers
- `ConsoleHandlers.DEFAULT` - Basic StreamHandler
- `ConsoleHandlers.RICH` - Rich-enhanced output

### Formatters
- `LogFormatters.DEFAULT` - Plain text
- `LogFormatters.COLORED` - ANSI colors
- `LogFormatters.RICH` - Rich markup

### File Handlers
- `FileHandlerTypes.FILE` - Basic file logging
- `FileHandlerTypes.ROTATING_FILE` - Size-based rotation
- `FileHandlerTypes.TIMED_ROTATING_FILE` - Time-based rotation

### Rich Features
- **Tables** with customizable styling and data formats
- **Panels** with borders, titles, and custom styling
- **Progress bars** with multiple tasks and live updates
- **Status indicators** with spinners and custom messages
- **Rules** for section separation and organization
- **Tree displays** for hierarchical data structures
- **Multi-column layouts** for organized content presentation
- **Syntax highlighting** for code display with multiple themes
- **Markdown rendering** with full Rich formatting support
- **JSON pretty printing** with syntax highlighting
- **Live updates** for real-time display changes
- **Bar charts** for simple data visualization
- **Text styling** and alignment with Rich markup
- **Interactive prompts** for user input and confirmations
- **Object inspection** and pretty printing for debugging

## 📖 Documentation Structure

This documentation is organized into focused guides:

1. **Getting Started** - Quick examples and basic usage
2. **Core Concepts** - Understanding the architecture
3. **Configuration** - All available options and settings
4. **Rich Features** - Advanced UI elements
5. **File Handling** - Logging to files with rotation
6. **Extension** - Adding new features and customization
7. **Reference** - Complete API documentation

Each guide includes:
- Clear explanations of concepts
- Practical code examples
- Common patterns and best practices
- Troubleshooting tips

## 🤝 Contributing

See the [Development Guide](./development.md) for information on:
- Setting up the development environment
- Code style and conventions
- Testing requirements
- Submitting contributions

## 📝 License

This logging module is part of the dotfiles-installer project.

---

**Next Steps:**
- Read the [Architecture Overview](./architecture.md) to understand the system design
- Check the [Usage Guide](./usage-guide.md) for practical examples
- Explore [Rich Features](./rich-features.md) for advanced UI capabilities
