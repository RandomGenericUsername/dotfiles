# Rich Integration Guide

Deep dive into how Rich features integrate with the logging system.

## 🎨 Integration Architecture

### Console Sharing Strategy

The logging module uses a sophisticated console sharing mechanism to ensure Rich features and logging output work together seamlessly:

```
┌─────────────────────────────────────────────────────────────┐
│                    RichHandler                              │
├─────────────────────────────────────────────────────────────┤
│  Creates Rich Console instance                              │
│  Registers with RichConsoleManager                         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│               RichConsoleManager (Singleton)               │
├─────────────────────────────────────────────────────────────┤
│  Stores console references by logger name                  │
│  Provides thread-safe access                               │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    RichLogger                              │
├─────────────────────────────────────────────────────────────┤
│  Retrieves shared console for Rich features                │
│  Ensures consistent output formatting                      │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Details

#### RichConsoleManager

```python
class RichConsoleManager:
    _instance = None
    _lock = threading.Lock()
    _consoles: dict[str, Console] = {}

    def register_console(self, logger_name: str, console: Console) -> None:
        """Register a console for a logger."""
        with self._lock:
            self._consoles[logger_name] = console

    def get_console(self, logger_name: str) -> Console | None:
        """Get the console for a logger."""
        with self._lock:
            return self._consoles.get(logger_name)
```

#### Console Registration

When a RichHandler is created, it automatically registers its console:

```python
class RichHandlerConfig:
    def create_handler(self) -> logging.Handler:
        handler = RichHandler(...)

        # Register console with manager
        if self.logger_name and hasattr(handler, 'console'):
            console_manager = RichConsoleManager()
            console_manager.register_console(self.logger_name, handler.console)

        return handler
```

#### Rich Feature Access

RichLogger methods retrieve the shared console:

```python
class RichLogger:
    def _get_console(self) -> Console | None:
        """Get the shared console for this logger."""
        console_manager = RichConsoleManager()
        return console_manager.get_console(self._logger.name)

    def table(self, data, **kwargs):
        if not RICH_AVAILABLE:
            return

        console = self._get_console()
        if console:
            table = Table(...)
            console.print(table)
```

## 🔧 Rich Feature Implementation

### Graceful Fallback Pattern

All Rich features use a consistent fallback pattern:

```python
def rich_feature(self, *args, **kwargs):
    # Check 1: Is Rich available?
    if not RICH_AVAILABLE:
        return  # Silent no-op

    # Check 2: Do we have a console?
    console = self._get_console()
    if not console:
        return  # Silent no-op

    # Check 3: Are Rich features enabled?
    if not self._rich_settings.enabled:
        return  # Silent no-op

    # Implement Rich feature
    rich_object = create_rich_object(*args, **kwargs)
    console.print(rich_object)
```

### Feature-Specific Implementations

#### Table Implementation

```python
def table(self, data, *, title=None, show_header=None, show_lines=None, **kwargs):
    if not RICH_AVAILABLE:
        return

    console = self._get_console()
    if not console:
        return

    # Apply settings defaults
    if show_header is None:
        show_header = self._rich_settings.table_show_header
    if show_lines is None:
        show_lines = self._rich_settings.table_show_lines

    # Create table
    table = Table(
        title=title,
        show_header=show_header,
        show_lines=show_lines,
        expand=self._rich_settings.table_expand,
        **kwargs
    )

    # Handle different data formats
    if isinstance(data, dict):
        # Dictionary format: {column: [values]}
        for column, values in data.items():
            table.add_column(str(column))

        max_rows = max(len(values) for values in data.values())
        for i in range(max_rows):
            row = [str(values[i] if i < len(values) else "")
                   for values in data.values()]
            table.add_row(*row)

    elif isinstance(data, list) and data:
        # List format: [[row1], [row2], ...]
        if show_header and data:
            # First row as headers
            for header in data[0]:
                table.add_column(str(header))

            # Remaining rows as data
            for row in data[1:]:
                table.add_row(*[str(cell) for cell in row])
        else:
            # All rows as data
            for row in data:
                table.add_row(*[str(cell) for cell in row])

    console.print(table)
```

#### Progress Implementation

```python
@contextmanager
def progress(self, description=None, total=None, **kwargs):
    if not RICH_AVAILABLE:
        yield _DummyProgress()
        return

    console = self._get_console()
    if not console:
        yield _DummyProgress()
        return

    # Create Rich Progress
    progress = Progress(
        auto_refresh=self._rich_settings.progress_auto_refresh,
        console=console,
        **kwargs
    )

    try:
        progress.start()
        if description and total:
            progress.add_task(description, total=total)
        yield progress
    finally:
        progress.stop()

class _DummyProgress:
    """Fallback progress object when Rich unavailable."""
    def add_task(self, *args, **kwargs): return 0
    def update(self, *args, **kwargs): pass
    def start(self): pass
    def stop(self): pass
```

## 🎛️ Configuration Integration

### RichFeatureSettings

Rich features are configured through `RichFeatureSettings`:

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
        # Validate box styles
        valid_box_styles = ["rounded", "square", "double", "heavy", "ascii"]
        if self.panel_box_style not in valid_box_styles:
            raise ValueError(f"Invalid box style: {self.panel_box_style}")

        # Validate alignment
        valid_alignments = ["left", "center", "right"]
        if self.rule_align not in valid_alignments:
            raise ValueError(f"Invalid alignment: {self.rule_align}")
```

### Settings Application

Settings are applied consistently across all Rich features:

```python
def panel(self, content, *, title=None, border_style=None, box_style=None, **kwargs):
    # Apply defaults from settings
    if border_style is None:
        border_style = self._rich_settings.panel_border_style
    if box_style is None:
        box_style = self._rich_settings.panel_box_style

    # Map box_style to Rich Box objects
    box_mapping = {
        "rounded": box.ROUNDED,
        "square": box.SQUARE,
        "double": box.DOUBLE,
        "heavy": box.HEAVY,
        "ascii": box.ASCII
    }

    panel = Panel(
        content,
        title=title,
        border_style=border_style,
        box=box_mapping.get(box_style, box.ROUNDED),
        expand=self._rich_settings.panel_expand,
        **kwargs
    )

    console.print(panel)
```

## 🔄 Lifecycle Management

### Logger Creation

1. User calls `Log.create_logger()` with Rich configuration
2. LogConfigurator creates RichHandler with console
3. Console is registered with RichConsoleManager
4. RichLogger is created with RichFeatureSettings
5. Rich features can now access the shared console

### Logger Updates

1. User calls `Log.update()` with new Rich settings
2. Existing handlers are removed
3. New RichHandler created with updated console
4. Console re-registered with manager
5. RichLogger updated with new settings

### Console Cleanup

The manager automatically handles console lifecycle:

```python
def register_console(self, logger_name: str, console: Console) -> None:
    with self._lock:
        # Replace existing console if present
        self._consoles[logger_name] = console
```

## 🧪 Testing Rich Integration

### Mock Strategy

Testing uses mocks to simulate Rich availability:

```python
def test_rich_features_with_rich_available():
    with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', True):
        with patch('cli.modules.logging.rich_logger.Table') as mock_table:
            logger = create_test_logger()
            logger.table([["A", "B"], ["1", "2"]])
            mock_table.assert_called_once()

def test_rich_features_without_rich():
    with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', False):
        logger = create_test_logger()
        # Should not raise exception
        logger.table([["A", "B"], ["1", "2"]])
```

### Console Manager Testing

```python
def test_console_sharing():
    manager = RichConsoleManager()
    console = Mock()

    # Register console
    manager.register_console("test_logger", console)

    # Retrieve console
    retrieved = manager.get_console("test_logger")
    assert retrieved is console

    # Non-existent logger
    assert manager.get_console("nonexistent") is None
```

## 🔍 Debugging Rich Integration

### Console Availability

Check if console is available for Rich features:

```python
def debug_console_availability(logger_name: str):
    manager = RichConsoleManager()
    console = manager.get_console(logger_name)

    if console:
        print(f"Console available for {logger_name}")
        print(f"Console type: {type(console)}")
        print(f"Console size: {console.size}")
    else:
        print(f"No console registered for {logger_name}")
```

### Rich Feature Status

Check Rich feature configuration:

```python
def debug_rich_features(logger: RichLogger):
    print(f"Rich available: {RICH_AVAILABLE}")
    print(f"Rich features enabled: {logger._rich_settings.enabled}")
    print(f"Console available: {logger._get_console() is not None}")
    print(f"Settings: {logger._rich_settings}")
```

## 🚀 Performance Considerations

### Console Reuse

Console sharing provides performance benefits:
- Single console instance per logger
- Consistent formatting and styling
- Reduced memory usage
- Thread-safe access

### Lazy Evaluation

Rich features use lazy evaluation:
- No Rich objects created when Rich unavailable
- Console retrieved only when needed
- Settings applied at render time

### Fallback Performance

Fallback implementations are lightweight:
- Immediate returns for unavailable features
- No object creation overhead
- Minimal memory footprint

This integration design ensures Rich features enhance the logging experience when available while maintaining full compatibility and performance when Rich is not present.
