# Architecture Overview

The logging module is designed with clean architecture principles, emphasizing separation of concerns, type safety, and extensibility.

## 🏗️ System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                         │
├─────────────────────────────────────────────────────────────┤
│  Log.create_logger()  │  Log.update()  │  RichLogger API   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Configuration Layer                      │
├─────────────────────────────────────────────────────────────┤
│  LogConfig  │  RichHandlerSettings  │  FileHandlerSpecs   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                       │
├─────────────────────────────────────────────────────────────┤
│              LogConfigurator (Central Hub)                 │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Formatter Layer    │ │  Handler Layer  │ │  Rich Layer     │
├─────────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • FormatterFactory  │ │ • HandlerFactory│ │ • RichLogger    │
│ • ColoredFormatter  │ │ • ConsoleHandler│ │ • ConsoleManager│
│ • RichFormatter     │ │ • FileHandlers  │ │ • FeatureSettings│
│ • DefaultFormatter  │ │ • RichHandler   │ │ • Fallbacks     │
└─────────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🎯 Design Principles

### 1. Separation of Concerns
Each component has a single, well-defined responsibility:

- **Log (Facade)**: Simple API for users
- **LogConfigurator**: Orchestrates component setup
- **Factories**: Create specific types of formatters/handlers
- **Settings Classes**: Type-safe configuration
- **RichLogger**: Enhanced logger with Rich features

### 2. Type Safety First
All configuration uses dataclasses with validation:

```python
@dataclass
class RichHandlerSettings:
    show_time: bool = True
    show_level: bool = True
    markup: bool = False

    def __post_init__(self):
        # Validation logic here
        pass
```

### 3. Factory Pattern
Consistent creation patterns for all components:

```python
class FormatterFactory:
    @staticmethod
    def get_formatter(formatter_type: LogFormatters, **kwargs) -> logging.Formatter:
        # Factory logic
        pass
```

### 4. Graceful Fallbacks
System works even when dependencies are unavailable:

```python
try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback implementations
```

## 🔧 Core Components

### Log (Facade Pattern)

The main entry point that provides a simple, consistent API:

```python
class Log:
    @staticmethod
    def create_logger(name: str, **kwargs) -> RichLogger:
        """Create a new logger with specified configuration."""

    @staticmethod
    def update(name: str, **kwargs) -> RichLogger:
        """Update existing logger configuration."""
```

**Responsibilities:**
- Parameter validation and defaults
- LogConfig creation and merging
- Delegating to LogConfigurator
- Returning enhanced RichLogger instances

### LogConfigurator (Orchestrator)

Central component that coordinates logger setup:

```python
class LogConfigurator:
    def configure(self, config: LogConfig) -> None:
        """Configure logger with all handlers and formatters."""
```

**Responsibilities:**
- Creating and configuring formatters
- Setting up console and file handlers
- Applying log levels and formats
- Managing handler lifecycle

### Factory Classes

#### FormatterFactory
Creates appropriate formatter instances:

```python
class FormatterFactory:
    @staticmethod
    def get_formatter(
        formatter_type: LogFormatters,
        format_string: str,
        style: LogFormatterStyleChoices,
        colors: type[ColoredFormatterColors] | None = None
    ) -> logging.Formatter:
```

**Supported Formatters:**
- `DEFAULT`: Standard logging.Formatter
- `COLORED`: ANSI color formatter
- `RICH`: Rich markup formatter

#### HandlerFactory
Creates console and file handlers:

```python
class ConsoleHandlerFactory:
    @staticmethod
    def get_handler(
        handler_type: ConsoleHandlers,
        config: RichHandlerSettings | None = None,
        logger_name: str | None = None
    ) -> logging.Handler:
```

**Supported Handlers:**
- Console: StreamHandler, RichHandler
- File: FileHandler, RotatingFileHandler, TimedRotatingFileHandler

### Rich Integration Layer

#### RichLogger (Wrapper Pattern)
Enhanced logger that adds Rich features while maintaining compatibility:

```python
class RichLogger:
    def __init__(self, logger: logging.Logger, rich_settings: RichFeatureSettings):
        self._logger = logger
        self._rich_settings = rich_settings

    # Standard logging methods (delegated)
    def info(self, message): return self._logger.info(message)

    # Rich feature methods
    def table(self, data, **kwargs): # Rich table implementation
    def panel(self, content, **kwargs): # Rich panel implementation
    def progress(self, **kwargs): # Rich progress implementation
```

#### RichConsoleManager (Singleton Pattern)
Manages console sharing between RichHandler and Rich features:

```python
class RichConsoleManager:
    _instance = None
    _consoles: dict[str, Console] = {}

    def register_console(self, logger_name: str, console: Console):
    def get_console(self, logger_name: str) -> Console | None:
```

## 📊 Data Flow

### Logger Creation Flow

```
User calls Log.create_logger()
         │
         ▼
Log validates parameters & creates LogConfig
         │
         ▼
LogConfigurator.configure(config)
         │
         ├─── FormatterFactory.get_formatter()
         │
         ├─── ConsoleHandlerFactory.get_handler()
         │
         ├─── FileHandlerFactory.get_handlers()
         │
         └─── Apply to logger instance
         │
         ▼
RichLogger wraps logger + Rich features
         │
         ▼
Return enhanced logger to user
```

### Rich Feature Flow

```
User calls logger.table(data)
         │
         ▼
RichLogger checks if Rich available
         │
         ├─── Yes: Get console from manager
         │    │
         │    ▼
         │    Create Rich Table
         │    │
         │    ▼
         │    console.print(table)
         │
         └─── No: Silent no-op (graceful fallback)
```

## 🔌 Extension Points

### Adding New Formatters

1. Create formatter class:
```python
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Custom formatting logic
        pass
```

2. Add to enum:
```python
class LogFormatters(Enum):
    CUSTOM = "custom"
```

3. Update factory:
```python
class FormatterFactory:
    @staticmethod
    def get_formatter(formatter_type: LogFormatters, **kwargs):
        if formatter_type == LogFormatters.CUSTOM:
            return CustomFormatter(**kwargs)
```

### Adding New Handlers

Similar pattern for handlers:

1. Create handler class or use existing
2. Add to enum if needed
3. Update appropriate factory
4. Add configuration dataclass if needed

### Adding Rich Features

1. Add method to RichLogger:
```python
def custom_feature(self, **kwargs):
    if not RICH_AVAILABLE:
        return

    console = self._get_console()
    if console:
        # Implement Rich feature
        pass
```

2. Add configuration to RichFeatureSettings if needed
3. Add fallback behavior for when Rich unavailable

## 🧪 Testing Architecture

### Unit Testing Strategy

Each component is tested in isolation:

- **Factories**: Test creation of correct instances
- **Configurator**: Test orchestration logic
- **Settings**: Test validation and defaults
- **Rich Features**: Test both Rich available and unavailable scenarios

### Integration Testing

Test complete flows:

- Logger creation with various configurations
- Rich features integration
- File handler setup and rotation
- Console sharing between components

### Mock Strategy

Use mocks for external dependencies:

- Mock Rich library for fallback testing
- Mock file system for file handler testing
- Mock console for Rich feature testing

## 🔄 Configuration Lifecycle

### Creation Phase
1. User provides parameters to `Log.create_logger()`
2. Parameters validated and merged with defaults
3. LogConfig created with complete configuration
4. LogConfigurator sets up all components
5. RichLogger wraps result with Rich features

### Update Phase
1. User calls `Log.update()` with changes
2. Existing configuration retrieved and merged
3. Logger reconfigured with new settings
4. Handlers replaced/updated as needed
5. Rich features updated with new settings

### Validation Phase
Throughout both phases:
- Type checking via dataclass annotations
- Runtime validation in `__post_init__` methods
- Factory validation of parameters
- Graceful handling of invalid configurations

## 🎨 Design Patterns Used

### Facade Pattern
- `Log` class provides simple interface to complex subsystem

### Factory Pattern
- `FormatterFactory`, `ConsoleHandlerFactory`, `FileHandlerFactory`

### Singleton Pattern
- `RichConsoleManager` ensures single console manager instance

### Wrapper Pattern
- `RichLogger` wraps `logging.Logger` with additional features

### Strategy Pattern
- Different formatters and handlers implement common interfaces

### Builder Pattern
- `LogConfig` builds complete configuration from parts

This architecture ensures the logging module is maintainable, extensible, and provides excellent developer experience while maintaining backward compatibility with standard Python logging.
