# Type Safety Guide

Comprehensive guide to the type-safe configuration system in the logging module.

## 🎯 Type Safety Overview

The logging module uses Python's type system extensively to provide:

1. **Compile-time validation** through type checkers (mypy, pyright)
2. **Runtime validation** through dataclass `__post_init__` methods
3. **IDE support** with autocomplete and error detection
4. **Self-documenting code** through type annotations

## 📋 Dataclass-Based Configuration

### Why Dataclasses?

The module uses dataclasses instead of dictionaries for configuration:

```python
# ❌ Old approach - No type safety
config = {
    'show_time': True,
    'show_levl': True,    # Typo - silently ignored!
    'invalid_key': 123,   # Invalid - silently ignored!
}

# ✅ New approach - Type-safe
@dataclass
class RichHandlerSettings:
    show_time: bool = True
    show_level: bool = True  # IDE catches typos immediately!
    # invalid_key: int     # IDE shows error immediately!
```

### Benefits of Type Safety

1. **Early Error Detection** - Catch errors before runtime
2. **IDE Support** - Autocomplete, refactoring, navigation
3. **Self-Documentation** - Types serve as documentation
4. **Refactoring Safety** - IDE tools work correctly
5. **No Silent Failures** - Invalid configurations cause immediate errors

## 🔧 Configuration Classes

### RichHandlerSettings

```python
@dataclass
class RichHandlerSettings:
    # Core display options
    show_time: bool = True
    show_level: bool = True
    show_path: bool = True
    markup: bool = False

    # Time formatting
    omit_repeated_times: bool = True
    log_time_format: str = "[%x %X]"

    # Path options
    enable_link_path: bool = True

    # Highlighting
    keywords: list[str] | None = None

    # Traceback configuration
    rich_tracebacks: bool = False
    tracebacks_show_locals: bool = False
    tracebacks_extra_lines: int = 3
    tracebacks_theme: str | None = None
    tracebacks_width: int | None = None

    # Local variable display
    locals_max_length: int = 10
    locals_max_string: int = 80

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.tracebacks_extra_lines < 0:
            raise ValueError("tracebacks_extra_lines must be non-negative")

        if self.locals_max_length < 1:
            raise ValueError("locals_max_length must be positive")

        if self.locals_max_string < 1:
            raise ValueError("locals_max_string must be positive")

        if self.tracebacks_width is not None and self.tracebacks_width < 1:
            raise ValueError("tracebacks_width must be positive")
```

### RichFeatureSettings

```python
@dataclass
class RichFeatureSettings:
    enabled: bool = True

    # Table defaults
    table_show_header: bool = True
    table_show_lines: bool = False
    table_expand: bool = False

    # Panel defaults
    panel_border_style: str = "blue"
    panel_box_style: str = "rounded"
    panel_expand: bool = True

    # Rule defaults
    rule_style: str = "rule.line"
    rule_align: str = "center"

    # Progress defaults
    progress_auto_refresh: bool = True

    # Status defaults
    status_spinner: str = "dots"

    def __post_init__(self):
        """Validate Rich feature settings."""
        # Validate box styles
        valid_box_styles = ["rounded", "square", "double", "heavy", "ascii"]
        if self.panel_box_style not in valid_box_styles:
            raise ValueError(
                f"Invalid panel_box_style '{self.panel_box_style}'. "
                f"Must be one of: {', '.join(valid_box_styles)}"
            )

        # Validate alignment
        valid_alignments = ["left", "center", "right"]
        if self.rule_align not in valid_alignments:
            raise ValueError(
                f"Invalid rule_align '{self.rule_align}'. "
                f"Must be one of: {', '.join(valid_alignments)}"
            )

        # Validate border styles (basic validation)
        if not isinstance(self.panel_border_style, str):
            raise TypeError("panel_border_style must be a string")
```

### File Handler Settings

```python
@dataclass
class FileHandlerSettings:
    filename: str
    mode: str = 'a'
    encoding: str = 'utf-8'
    delay: bool = False

    def __post_init__(self):
        """Validate file handler settings."""
        if not self.filename:
            raise ValueError("filename cannot be empty")

        valid_modes = ['a', 'w', 'x']
        if self.mode not in valid_modes:
            raise ValueError(
                f"Invalid mode '{self.mode}'. "
                f"Must be one of: {', '.join(valid_modes)}"
            )

        # Validate encoding
        try:
            "test".encode(self.encoding)
        except LookupError:
            raise ValueError(f"Invalid encoding: {self.encoding}")

@dataclass
class RotatingFileHandlerSettings:
    filename: str
    max_bytes: int = 10_485_760  # 10MB
    backup_count: int = 5
    mode: str = 'a'
    encoding: str = 'utf-8'
    delay: bool = False

    def __post_init__(self):
        """Validate rotating file handler settings."""
        # Validate inherited settings
        FileHandlerSettings.__post_init__(self)

        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")

        if self.backup_count < 0:
            raise ValueError("backup_count must be non-negative")

@dataclass
class TimedRotatingFileHandlerSettings:
    filename: str
    when: str = 'midnight'
    interval: int = 1
    backup_count: int = 7
    encoding: str = 'utf-8'
    delay: bool = False
    utc: bool = False

    def __post_init__(self):
        """Validate timed rotating file handler settings."""
        if not self.filename:
            raise ValueError("filename cannot be empty")

        valid_when_values = ['S', 'M', 'H', 'D', 'midnight'] + [f'W{i}' for i in range(7)]
        if self.when not in valid_when_values:
            raise ValueError(
                f"Invalid when value '{self.when}'. "
                f"Must be one of: {', '.join(valid_when_values)}"
            )

        if self.interval <= 0:
            raise ValueError("interval must be positive")

        if self.backup_count < 0:
            raise ValueError("backup_count must be non-negative")
```

## 🔍 Type Annotations

### Function Signatures

All public functions use comprehensive type annotations:

```python
def create_logger(
    name: str,
    config: LogConfig | None = None,
    log_level: LogLevels | None = None,
    verbosity: int = 0,
    formatter_style: LogFormatterStyleChoices = LogFormatterStyleChoices.PERCENT,
    format: str = "%(asctime)s | %(levelname)-8s | %(message)s",
    formatter_type: LogFormatters = LogFormatters.DEFAULT,
    colors: type[ColoredFormatterColors] | None = None,
    console_handler_type: ConsoleHandlers = ConsoleHandlers.DEFAULT,
    handler_config: RichHandlerSettings | None = None,
    file_handlers: list[FileHandlerSpec] | None = None,
    rich_features: RichFeatureSettings | None = None,
) -> RichLogger:
```

### Union Types

The module uses union types for flexibility:

```python
# Optional configuration
handler_config: RichHandlerSettings | None = None

# Multiple possible types
config: FileHandlerSettings | RotatingFileHandlerSettings | TimedRotatingFileHandlerSettings

# Enum or None
log_level: LogLevels | None = None
```

### Generic Types

For collections and complex types:

```python
from typing import Iterator, Any, Callable

# List of specific types
file_handlers: list[FileHandlerSpec] | None = None

# Dictionary with typed keys and values
colors: type[ColoredFormatterColors] | None = None

# Context manager return type
@contextmanager
def progress(self, **kwargs) -> Iterator[Progress]:
```

## ✅ Validation Patterns

### Runtime Validation

All configuration classes validate their data:

```python
def __post_init__(self):
    """Validate configuration after initialization."""
    # Type validation
    if not isinstance(self.max_bytes, int):
        raise TypeError("max_bytes must be an integer")

    # Range validation
    if self.max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    # Choice validation
    valid_choices = ["option1", "option2", "option3"]
    if self.choice not in valid_choices:
        raise ValueError(f"choice must be one of: {valid_choices}")

    # Complex validation
    if self.start_time >= self.end_time:
        raise ValueError("start_time must be before end_time")
```

### Custom Validators

For complex validation logic:

```python
@dataclass
class AdvancedSettings:
    url: str
    timeout: int = 30
    retries: int = 3

    def __post_init__(self):
        self._validate_url()
        self._validate_timeout()
        self._validate_retries()

    def _validate_url(self):
        """Validate URL format."""
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")

    def _validate_timeout(self):
        """Validate timeout value."""
        if not 1 <= self.timeout <= 300:
            raise ValueError("timeout must be between 1 and 300 seconds")

    def _validate_retries(self):
        """Validate retry count."""
        if not 0 <= self.retries <= 10:
            raise ValueError("retries must be between 0 and 10")
```

## 🔧 Type Checking Tools

### mypy Configuration

```ini
# mypy.ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

### Running Type Checks

```bash
# Check specific module
mypy src/dotfiles-installer/cli/modules/logging/

# Check with strict mode
mypy --strict src/dotfiles-installer/cli/modules/logging/

# Check specific file
mypy src/dotfiles-installer/cli/modules/logging/log.py
```

### IDE Integration

Most IDEs support type checking:

- **VS Code**: Python extension with Pylance
- **PyCharm**: Built-in type checking
- **Vim/Neovim**: With appropriate plugins

## 🧪 Testing Type Safety

### Type Validation Tests

```python
import pytest
from cli.modules.logging import RichHandlerSettings, RotatingFileHandlerSettings

def test_rich_handler_settings_validation():
    """Test RichHandlerSettings validation."""
    # Valid settings
    settings = RichHandlerSettings(
        show_time=True,
        tracebacks_extra_lines=5,
        locals_max_length=10
    )
    assert settings.show_time is True

    # Invalid tracebacks_extra_lines
    with pytest.raises(ValueError, match="tracebacks_extra_lines must be non-negative"):
        RichHandlerSettings(tracebacks_extra_lines=-1)

    # Invalid locals_max_length
    with pytest.raises(ValueError, match="locals_max_length must be positive"):
        RichHandlerSettings(locals_max_length=0)

def test_rotating_file_handler_validation():
    """Test RotatingFileHandlerSettings validation."""
    # Valid settings
    settings = RotatingFileHandlerSettings(
        filename="test.log",
        max_bytes=1000000,
        backup_count=5
    )
    assert settings.filename == "test.log"

    # Invalid max_bytes
    with pytest.raises(ValueError, match="max_bytes must be positive"):
        RotatingFileHandlerSettings(filename="test.log", max_bytes=0)

    # Invalid backup_count
    with pytest.raises(ValueError, match="backup_count must be non-negative"):
        RotatingFileHandlerSettings(filename="test.log", backup_count=-1)
```

### Type Annotation Tests

```python
def test_function_type_annotations():
    """Test that functions have correct type annotations."""
    from cli.modules.logging import Log
    import inspect

    # Get function signature
    sig = inspect.signature(Log.create_logger)

    # Check parameter types
    assert sig.parameters['name'].annotation == str
    assert sig.parameters['verbosity'].annotation == int

    # Check return type
    assert sig.return_annotation.__name__ == 'RichLogger'
```

## 🔍 Common Type Issues

### Issue 1: Wrong Parameter Types

```python
# ❌ Wrong - passing instance instead of class
colors = ColoredFormatterColors()  # Instance
logger = Log.create_logger("app", colors=colors)  # TypeError

# ✅ Correct - passing class
logger = Log.create_logger("app", colors=ColoredFormatterColors)  # Class
```

### Issue 2: Missing Required Fields

```python
# ❌ Wrong - missing required fields
config = LogConfig(name="app")  # Missing required fields

# ✅ Correct - all required fields
config = LogConfig(
    name="app",
    log_level=LogLevels.INFO,
    verbosity=0,
    formatter_style=LogFormatterStyleChoices.PERCENT,
    format="%(message)s",
    formatter_type=LogFormatters.DEFAULT
)
```

### Issue 3: Invalid Enum Values

```python
# ❌ Wrong - string instead of enum
logger = Log.create_logger("app", log_level="INFO")  # String

# ✅ Correct - enum value
logger = Log.create_logger("app", log_level=LogLevels.INFO)  # Enum
```

## 📝 Best Practices

1. **Use Type Hints Everywhere** - Annotate all functions and variables
2. **Validate in __post_init__** - Catch configuration errors early
3. **Use Enums for Choices** - Better than string constants
4. **Prefer Union Types** - More flexible than overloads
5. **Document Type Requirements** - Clear error messages
6. **Test Type Validation** - Ensure validation works correctly
7. **Run Type Checkers** - Use mypy or similar tools
8. **IDE Integration** - Configure IDE for type checking

## 🔄 Migration to Type Safety

### From Dict to Dataclass

```python
# Old approach
config = {
    'show_time': True,
    'show_level': True,
    'markup': False
}

# New approach
config = RichHandlerSettings(
    show_time=True,
    show_level=True,
    markup=False
)
```

### From Strings to Enums

```python
# Old approach
formatter_type = "rich"
log_level = "INFO"

# New approach
formatter_type = LogFormatters.RICH
log_level = LogLevels.INFO
```

### From Any to Specific Types

```python
# Old approach
def create_logger(name, **kwargs):  # No type hints

# New approach
def create_logger(
    name: str,
    log_level: LogLevels | None = None,
    **kwargs
) -> RichLogger:
```

This type safety system ensures configuration errors are caught early, provides excellent IDE support, and makes the logging module more maintainable and reliable.
