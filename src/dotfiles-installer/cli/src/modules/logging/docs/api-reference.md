# API Reference

Complete reference for all public APIs in the logging module.

## 📚 Core Classes

### Log (Facade)

The main entry point for the logging system.

#### `Log.create_logger()`

```python
@staticmethod
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
) -> RichLogger
```

**Parameters:**
- `name` (str): Logger name (required)
- `config` (LogConfig | None): Complete configuration object
- `log_level` (LogLevels | None): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `verbosity` (int): Verbosity count (0-3), overrides log_level
- `formatter_style` (LogFormatterStyleChoices): Format style (PERCENT, BRACE, DOLLAR)
- `format` (str): Log format string
- `formatter_type` (LogFormatters): Formatter type (DEFAULT, COLORED, RICH)
- `colors` (type[ColoredFormatterColors] | None): Color class for COLORED formatter
- `console_handler_type` (ConsoleHandlers): Console handler type (DEFAULT, RICH)
- `handler_config` (RichHandlerSettings | None): Rich handler configuration
- `file_handlers` (list[FileHandlerSpec] | None): File handler specifications
- `rich_features` (RichFeatureSettings | None): Rich features configuration

**Returns:** RichLogger instance

**Example:**
```python
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(show_time=True),
    rich_features=RichFeatureSettings(enabled=True)
)
```

#### `Log.update()`

```python
@staticmethod
def update(
    name: str,
    config: LogConfig | None = None,
    log_level: LogLevels | None = None,
    verbosity: int | None = None,
    formatter_style: LogFormatterStyleChoices | None = None,
    format: str | None = None,
    formatter_type: LogFormatters | None = None,
    colors: type[ColoredFormatterColors] | None = None,
    console_handler_type: ConsoleHandlers | None = None,
    handler_config: RichHandlerSettings | None = None,
    file_handlers: list[FileHandlerSpec] | None = None,
    rich_features: RichFeatureSettings | None = None,
) -> RichLogger
```

Updates existing logger configuration. Parameters same as `create_logger()` but all optional.

**Returns:** Updated RichLogger instance

### RichLogger

Enhanced logger with Rich features and standard logging compatibility.

#### Standard Logging Methods

```python
def debug(self, message: str, *args, **kwargs) -> None
def info(self, message: str, *args, **kwargs) -> None
def warning(self, message: str, *args, **kwargs) -> None
def error(self, message: str, *args, **kwargs) -> None
def critical(self, message: str, *args, **kwargs) -> None
def exception(self, message: str, *args, **kwargs) -> None
def log(self, level: int, message: str, *args, **kwargs) -> None
```

#### Rich Feature Methods

```python
def table(
    self,
    data: list[list[str]] | dict[str, list],
    *,
    title: str | None = None,
    show_header: bool | None = None,
    show_lines: bool | None = None,
    **kwargs
) -> None
```

Display a Rich table.

**Parameters:**
- `data`: Table data as list of rows or dict of columns
- `title`: Optional table title
- `show_header`: Show header row
- `show_lines`: Show lines between rows
- `**kwargs`: Additional Rich Table parameters

```python
def panel(
    self,
    content: str,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    border_style: str | None = None,
    box_style: str | None = None,
    **kwargs
) -> None
```

Display a Rich panel.

**Parameters:**
- `content`: Panel content
- `title`: Optional panel title
- `subtitle`: Optional panel subtitle
- `border_style`: Border color/style
- `box_style`: Box type (rounded, square, double, heavy, ascii)

```python
def rule(
    self,
    title: str | None = None,
    *,
    style: str | None = None,
    align: str | None = None,
    **kwargs
) -> None
```

Display a Rich rule (separator).

```python
@contextmanager
def progress(
    self,
    description: str | None = None,
    total: int | None = None,
    **kwargs
) -> Iterator[Progress]
```

Rich progress bar context manager.

```python
@contextmanager
def status(
    self,
    message: str,
    *,
    spinner: str | None = None,
    **kwargs
) -> Iterator[Status]
```

Rich status indicator context manager.

```python
def tree(
    self,
    data: dict[str, Any] | str,
    *,
    title: str | None = None,
    guide_style: str | None = None,
    expanded: bool | None = None,
    **kwargs
) -> None
```

Display hierarchical data as a tree structure.

**Parameters:**
- `data`: Tree data as nested dict or root label string
- `title`: Optional tree title (used as root if data is dict)
- `guide_style`: Style for tree guide lines
- `expanded`: Whether nodes should be expanded
- `**kwargs`: Additional Rich Tree parameters

```python
def columns(
    self,
    *renderables: Any,
    equal: bool | None = None,
    expand: bool | None = None,
    padding: tuple[int, int] | None = None,
    **kwargs
) -> None
```

Display content in multiple columns.

**Parameters:**
- `*renderables`: Content to display in columns
- `equal`: Whether columns should have equal width
- `expand`: Whether columns should expand to fill width
- `padding`: Padding as (vertical, horizontal)
- `**kwargs`: Additional Rich Columns parameters

```python
def syntax(
    self,
    code: str,
    lexer: str = "python",
    *,
    theme: str | None = None,
    line_numbers: bool | None = None,
    word_wrap: bool | None = None,
    background_color: str | None = None,
    title: str | None = None,
    **kwargs
) -> None
```

Display syntax-highlighted code.

**Parameters:**
- `code`: Code string to highlight
- `lexer`: Language lexer (e.g., 'python', 'bash', 'javascript')
- `theme`: Syntax highlighting theme
- `line_numbers`: Whether to show line numbers
- `word_wrap`: Whether to enable word wrap
- `background_color`: Background color
- `title`: Optional title for the code block
- `**kwargs`: Additional Rich Syntax parameters

```python
def markdown(
    self,
    markdown_text: str,
    *,
    code_theme: str | None = None,
    hyperlinks: bool | None = None,
    inline_code_lexer: str | None = None,
    **kwargs
) -> None
```

Render markdown text with Rich formatting.

**Parameters:**
- `markdown_text`: Markdown text to render
- `code_theme`: Theme for code blocks
- `hyperlinks`: Whether to enable hyperlinks
- `inline_code_lexer`: Lexer for inline code
- `**kwargs`: Additional Rich Markdown parameters

```python
def json(
    self,
    data: dict[str, Any] | list[Any] | str,
    *,
    indent: int | None = None,
    highlight: bool | None = None,
    sort_keys: bool | None = None,
    title: str | None = None,
    **kwargs
) -> None
```

Display JSON data with syntax highlighting.

**Parameters:**
- `data`: JSON data (dict, list, or JSON string)
- `indent`: Indentation level
- `highlight`: Whether to enable syntax highlighting
- `sort_keys`: Whether to sort keys
- `title`: Optional title for the JSON display
- `**kwargs`: Additional Rich JSON parameters

```python
@contextmanager
def live(
    self,
    renderable: Any,
    *,
    refresh_per_second: int | None = None,
    vertical_overflow: str | None = None,
    auto_refresh: bool | None = None,
    **kwargs
) -> Iterator[Live | None]
```

Create a live-updating display context manager.

**Parameters:**
- `renderable`: Content to display and update
- `refresh_per_second`: Refresh rate
- `vertical_overflow`: Overflow handling ('crop', 'ellipsis', 'visible')
- `auto_refresh`: Whether to auto-refresh
- `**kwargs`: Additional Rich Live parameters

```python
def bar_chart(
    self,
    data: dict[str, int | float],
    *,
    title: str | None = None,
    width: int | None = None,
    character: str | None = None,
    show_values: bool | None = None,
    **kwargs
) -> None
```

Display a simple bar chart using table format.

**Parameters:**
- `data`: Dictionary mapping labels to values
- `title`: Optional chart title
- `width`: Width of bars in characters
- `character`: Character to use for bars
- `show_values`: Whether to show numeric values
- `**kwargs`: Additional Rich Table parameters

```python
def text(
    self,
    text: str,
    *,
    style: str | None = None,
    justify: str | None = None,
    overflow: str | None = None,
    no_wrap: bool | None = None,
    **kwargs
) -> None
```

Display styled and formatted text.

**Parameters:**
- `text`: Text to display
- `style`: Text style (e.g., "bold red", "italic blue")
- `justify`: Text justification ('left', 'center', 'right', 'full')
- `overflow`: Overflow handling ('crop', 'fold', 'ellipsis')
- `no_wrap`: Whether to disable wrapping
- `**kwargs`: Additional Rich Text parameters

```python
def align(
    self,
    renderable: Any,
    align: str = "center",
    *,
    style: str | None = None,
    vertical: str | None = None,
    **kwargs
) -> None
```

Display content with specific alignment.

**Parameters:**
- `renderable`: Content to align
- `align`: Horizontal alignment ('left', 'center', 'right')
- `style`: Optional style for the aligned content
- `vertical`: Vertical alignment ('top', 'middle', 'bottom')
- `**kwargs`: Additional Rich Align parameters

```python
def prompt(
    self,
    question: str,
    *,
    choices: list[str] | None = None,
    default: str | None = None,
    show_default: bool | None = None,
    show_choices: bool | None = None,
    **kwargs
) -> str
```

Display an interactive prompt for user input.

**Parameters:**
- `question`: Question to ask the user
- `choices`: List of valid choices (None for free text input)
- `default`: Default value if user presses Enter
- `show_default`: Whether to show default value
- `show_choices`: Whether to show available choices
- `**kwargs`: Additional Rich Prompt parameters

```python
def confirm(
    self,
    question: str,
    *,
    default: bool = False,
    **kwargs
) -> bool
```

Display a yes/no confirmation prompt.

**Parameters:**
- `question`: Question to ask the user
- `default`: Default value if user presses Enter
- `**kwargs`: Additional Rich Confirm parameters

```python
def inspect(
    self,
    obj: Any,
    *,
    title: str | None = None,
    methods: bool | None = None,
    help: bool | None = None,
    private: bool | None = None,
    dunder: bool | None = None,
    sort: bool | None = None,
    **kwargs
) -> None
```

Inspect and display detailed information about an object.

**Parameters:**
- `obj`: Object to inspect
- `title`: Optional title for the inspection
- `methods`: Whether to show methods
- `help`: Whether to show help text
- `private`: Whether to show private attributes
- `dunder`: Whether to show dunder methods
- `sort`: Whether to sort attributes
- `**kwargs`: Additional Rich inspect parameters

```python
def pretty(
    self,
    obj: Any,
    *,
    indent_guides: bool | None = None,
    max_length: int | None = None,
    max_string: int | None = None,
    max_depth: int | None = None,
    **kwargs
) -> None
```

Pretty print Python objects with Rich formatting.

**Parameters:**
- `obj`: Object to pretty print
- `indent_guides`: Whether to show indent guides
- `max_length`: Maximum length for sequences
- `max_string`: Maximum string length
- `max_depth`: Maximum depth for nested objects
- `**kwargs`: Additional Rich Pretty parameters

## 📋 Configuration Classes

### LogConfig

Complete logger configuration.

```python
@dataclass
class LogConfig:
    name: str
    log_level: LogLevels
    verbosity: int
    formatter_style: LogFormatterStyleChoices
    format: str
    formatter_type: LogFormatters
    console_handler: ConsoleHandlers = ConsoleHandlers.DEFAULT
    handler_config: RichHandlerSettings | None = None
    file_handlers: list[FileHandlerSpec] | None = None
    colors: type[ColoredFormatterColors] | None = None
    rich_features: RichFeatureSettings | None = None
```

### RichHandlerSettings

Configuration for Rich console handler.

```python
@dataclass
class RichHandlerSettings:
    show_time: bool = True
    show_level: bool = True
    show_path: bool = True
    markup: bool = False
    omit_repeated_times: bool = True
    log_time_format: str = "[%x %X]"
    enable_link_path: bool = True
    keywords: list[str] | None = None
    rich_tracebacks: bool = False
    tracebacks_show_locals: bool = False
    tracebacks_extra_lines: int = 3
    tracebacks_theme: str | None = None
    tracebacks_width: int | None = None
    locals_max_length: int = 10
    locals_max_string: int = 80
```

### RichFeatureSettings

Configuration for Rich features.

```python
@dataclass
class RichFeatureSettings:
    # Global Rich features control
    enabled: bool = True

    # Table settings
    table_show_header: bool = True
    table_show_lines: bool = False
    table_show_edge: bool = True
    table_expand: bool = False

    # Panel settings
    panel_border_style: str = "blue"
    panel_box_style: str = "rounded"
    panel_expand: bool = True
    panel_padding: tuple[int, int] = (0, 1)

    # Rule settings
    rule_style: str = "rule.line"
    rule_align: str = "center"

    # Progress settings
    progress_auto_refresh: bool = True
    progress_refresh_per_second: int = 10
    progress_speed_estimate_period: float = 30.0

    # Status settings
    status_spinner: str = "dots"
    status_refresh_per_second: int = 12.5

    # Console settings
    console_width: int | None = None
    console_height: int | None = None

    # Tree settings
    tree_guide_style: str = "tree.line"
    tree_expanded: bool = True

    # Columns settings
    columns_equal: bool = False
    columns_expand: bool = False
    columns_padding: tuple[int, int] = (0, 1)

    # Syntax highlighting settings
    syntax_theme: str = "monokai"
    syntax_line_numbers: bool = False
    syntax_word_wrap: bool = False
    syntax_background_color: str | None = None

    # Markdown settings
    markdown_code_theme: str = "monokai"
    markdown_hyperlinks: bool = True
    markdown_inline_code_lexer: str | None = None

    # JSON settings
    json_indent: int = 2
    json_highlight: bool = True
    json_sort_keys: bool = False

    # Live display settings
    live_refresh_per_second: int = 4
    live_vertical_overflow: str = "ellipsis"
    live_auto_refresh: bool = True

    # Bar chart settings
    bar_chart_width: int = 20
    bar_chart_character: str = "█"
    bar_chart_show_values: bool = True

    # Text and alignment settings
    text_justify: str = "left"
    text_overflow: str = "fold"
    text_no_wrap: bool = False

    # Prompt settings
    prompt_show_default: bool = True
    prompt_show_choices: bool = True

    # Inspection settings
    inspect_methods: bool = False
    inspect_help: bool = False
    inspect_private: bool = False
    inspect_dunder: bool = False
    inspect_sort: bool = True

    # Pretty printing settings
    pretty_indent_guides: bool = True
    pretty_max_length: int | None = None
    pretty_max_string: int | None = None
    pretty_max_depth: int | None = None
```

### FileHandlerSpec

Specification for file handlers.

```python
@dataclass
class FileHandlerSpec:
    handler_type: FileHandlerTypes
    config: FileHandlerSettings | RotatingFileHandlerSettings | TimedRotatingFileHandlerSettings
    formatter_override: LogFormatters | None = None
    format_override: str | None = None
```

### File Handler Settings

#### FileHandlerSettings
```python
@dataclass
class FileHandlerSettings:
    filename: str
    mode: str = 'a'
    encoding: str = 'utf-8'
    delay: bool = False
```

#### RotatingFileHandlerSettings
```python
@dataclass
class RotatingFileHandlerSettings:
    filename: str
    max_bytes: int = 10_485_760  # 10MB
    backup_count: int = 5
    mode: str = 'a'
    encoding: str = 'utf-8'
    delay: bool = False
```

#### TimedRotatingFileHandlerSettings
```python
@dataclass
class TimedRotatingFileHandlerSettings:
    filename: str
    when: str = 'midnight'
    interval: int = 1
    backup_count: int = 7
    encoding: str = 'utf-8'
    delay: bool = False
    utc: bool = False
```

## 🔢 Enums

### LogLevels
```python
class LogLevels(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
```

### LogFormatters
```python
class LogFormatters(Enum):
    DEFAULT = "default"
    COLORED = "colored"
    RICH = "rich"
```

### ConsoleHandlers
```python
class ConsoleHandlers(Enum):
    DEFAULT = "default"
    RICH = "rich"
```

### FileHandlerTypes
```python
class FileHandlerTypes(Enum):
    FILE = "file"
    ROTATING_FILE = "rotating_file"
    TIMED_ROTATING_FILE = "timed_rotating_file"
```

### LogFormatterStyleChoices
```python
class LogFormatterStyleChoices(Enum):
    PERCENT = "%"
    BRACE = "{"
    DOLLAR = "$"
```

## 🎨 Color Classes

### ColoredFormatterColors

Base class for colored formatter colors.

```python
class ColoredFormatterColors:
    DEBUG: str = "\033[36m"      # Cyan
    INFO: str = "\033[32m"       # Green
    WARNING: str = "\033[33m"    # Yellow
    ERROR: str = "\033[31m"      # Red
    CRITICAL: str = "\033[35m"   # Magenta
    RESET: str = "\033[0m"       # Reset
```

**Custom Colors Example:**
```python
class CustomColors(ColoredFormatterColors):
    DEBUG = "\033[94m"    # Light Blue
    INFO = "\033[92m"     # Light Green
    WARNING = "\033[93m"  # Light Yellow
    ERROR = "\033[91m"    # Light Red
    CRITICAL = "\033[95m" # Light Magenta

logger = Log.create_logger("app", colors=CustomColors)
```

## 🔧 Utility Functions

### get_log_level_from_verbosity()
```python
def get_log_level_from_verbosity(verbosity: int) -> LogLevels
```

Convert verbosity count to log level.

**Mapping:**
- 0: WARNING
- 1: INFO
- 2: DEBUG
- 3+: DEBUG

### validate_log_level_string()
```python
def validate_log_level_string(level_str: str) -> LogLevels
```

Validate and convert string to LogLevels enum.

### get_log_level_typer_option()
```python
def get_log_level_typer_option() -> Annotated[str | None, Option(...)]
```

Returns Typer option annotation for log level CLI parameter.

## 🚨 Error Handling

### Common Exceptions

- `ValueError`: Invalid configuration values
- `TypeError`: Wrong parameter types
- `ImportError`: Rich library not available (handled gracefully)
- `FileNotFoundError`: Log file path issues

### Validation

All configuration classes perform validation in `__post_init__`:

```python
def __post_init__(self):
    if self.max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    if self.backup_count < 0:
        raise ValueError("backup_count must be non-negative")
```

## 📝 Type Annotations

The module uses comprehensive type annotations:

```python
from typing import Iterator, Any, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
```

All public APIs include complete type information for IDE support and runtime validation.
