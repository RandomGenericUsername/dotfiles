# Extension Guide

Learn how to extend the logging module with custom formatters, handlers, and Rich features.

## 🔧 Extension Architecture

The logging module is designed for extensibility through well-defined extension points:

1. **Custom Formatters** - Add new formatting styles
2. **Custom Handlers** - Add new output destinations
3. **Custom Rich Features** - Add new Rich UI elements
4. **Custom Settings** - Add new configuration options
5. **Custom Factories** - Modify creation logic

## 🎨 Adding Custom Formatters

### Step 1: Create Formatter Class

```python
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON-structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)

class XMLFormatter(logging.Formatter):
    """Formatter that outputs XML-structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        from xml.sax.saxutils import escape

        timestamp = datetime.fromtimestamp(record.created).isoformat()
        message = escape(record.getMessage())

        xml = f"""<log>
    <timestamp>{timestamp}</timestamp>
    <level>{record.levelname}</level>
    <logger>{escape(record.name)}</logger>
    <message>{message}</message>
    <location module="{escape(record.module)}" function="{escape(record.funcName)}" line="{record.lineno}"/>
</log>"""

        return xml
```

### Step 2: Add to Enum

```python
# In log_types.py
class LogFormatters(Enum):
    DEFAULT = "default"
    COLORED = "colored"
    RICH = "rich"
    JSON = "json"        # New formatter
    XML = "xml"          # New formatter
```

### Step 3: Update Factory

```python
# In formatters/__init__.py
class FormatterFactory:
    @staticmethod
    def get_formatter(
        formatter_type: LogFormatters,
        format_string: str,
        style: LogFormatterStyleChoices,
        colors: type[ColoredFormatterColors] | None = None
    ) -> logging.Formatter:

        if formatter_type == LogFormatters.JSON:
            return JSONFormatter()
        elif formatter_type == LogFormatters.XML:
            return XMLFormatter()
        elif formatter_type == LogFormatters.COLORED:
            return ColoredFormatter(format_string, style, colors)
        elif formatter_type == LogFormatters.RICH:
            return RichFormatter(format_string, style)
        else:
            return logging.Formatter(format_string, style=style.value)
```

### Step 4: Usage

```python
# Use custom formatter
logger = Log.create_logger(
    "app",
    formatter_type=LogFormatters.JSON,
    file_handlers=[
        FileHandlerSpec(
            handler_type=FileHandlerTypes.FILE,
            config=FileHandlerSettings(filename="app.json")
        )
    ]
)

logger.info("This will be logged as JSON")
```

## 🔌 Adding Custom Handlers

### Step 1: Create Handler Class

```python
import logging
import requests
from dataclasses import dataclass

@dataclass
class WebhookHandlerSettings:
    """Settings for webhook handler."""
    url: str
    method: str = "POST"
    headers: dict[str, str] | None = None
    timeout: int = 5

    def __post_init__(self):
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        if self.method not in ['POST', 'PUT', 'PATCH']:
            raise ValueError("Method must be POST, PUT, or PATCH")

class WebhookHandler(logging.Handler):
    """Handler that sends logs to a webhook."""

    def __init__(self, settings: WebhookHandlerSettings):
        super().__init__()
        self.settings = settings
        self.session = requests.Session()

        if settings.headers:
            self.session.headers.update(settings.headers)

    def emit(self, record: logging.LogRecord):
        try:
            log_entry = {
                "timestamp": record.created,
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record)
            }

            response = self.session.request(
                method=self.settings.method,
                url=self.settings.url,
                json=log_entry,
                timeout=self.settings.timeout
            )
            response.raise_for_status()

        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)
```

### Step 2: Add to Enum and Factory

```python
# In log_types.py
class ConsoleHandlers(Enum):
    DEFAULT = "default"
    RICH = "rich"
    WEBHOOK = "webhook"  # New handler type

# Create factory for custom handlers
class CustomHandlerFactory:
    @staticmethod
    def get_webhook_handler(settings: WebhookHandlerSettings) -> WebhookHandler:
        return WebhookHandler(settings)
```

### Step 3: Integration with LogConfig

```python
# Extend LogConfig to support custom handlers
@dataclass
class LogConfig:
    # ... existing fields ...
    webhook_handler: WebhookHandlerSettings | None = None

# Update LogConfigurator
class LogConfigurator:
    def configure(self, config: LogConfig) -> None:
        # ... existing configuration ...

        # Add webhook handler if configured
        if config.webhook_handler:
            webhook_handler = CustomHandlerFactory.get_webhook_handler(config.webhook_handler)
            webhook_handler.setFormatter(self.formatter)
            self.logger.addHandler(webhook_handler)
```

## 🎭 Adding Custom Rich Features

### Step 1: Create Rich Feature

```python
# In rich_logger.py
def chart(self, data: dict[str, float], *, title: str | None = None, **kwargs):
    """Display a simple bar chart using Rich."""
    if not RICH_AVAILABLE:
        return

    console = self._get_console()
    if not console:
        return

    from rich.table import Table
    from rich.bar import Bar

    # Create table for chart
    table = Table(title=title, show_header=True)
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Chart", style="green")

    # Find max value for scaling
    max_value = max(data.values()) if data else 1

    for item, value in data.items():
        # Create bar representation
        bar_width = int((value / max_value) * 20)  # Scale to 20 chars
        bar = "█" * bar_width

        table.add_row(
            str(item),
            f"{value:.2f}",
            bar
        )

    console.print(table)

def tree(self, data: dict, *, title: str | None = None, **kwargs):
    """Display hierarchical data as a tree."""
    if not RICH_AVAILABLE:
        return

    console = self._get_console()
    if not console:
        return

    from rich.tree import Tree

    tree = Tree(title or "Data Tree")

    def add_to_tree(node, data_dict):
        for key, value in data_dict.items():
            if isinstance(value, dict):
                branch = node.add(f"[bold blue]{key}[/bold blue]")
                add_to_tree(branch, value)
            else:
                node.add(f"{key}: [green]{value}[/green]")

    add_to_tree(tree, data)
    console.print(tree)
```

### Step 2: Add Configuration

```python
# In rich_feature_settings.py
@dataclass
class RichFeatureSettings:
    # ... existing fields ...

    # Chart defaults
    chart_max_width: int = 20
    chart_show_values: bool = True

    # Tree defaults
    tree_expand_all: bool = False
    tree_guide_style: str = "tree.line"
```

### Step 3: Usage

```python
logger = Log.create_logger(
    "app",
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)

# Use custom Rich features
logger.chart({"A": 10, "B": 20, "C": 15}, title="Sales Data")
logger.tree({"config": {"db": {"host": "localhost", "port": 5432}}})
```

## 🏗️ Creating Custom Settings Classes

### Step 1: Define Settings Class

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class DatabaseLoggerSettings:
    """Settings for database logging."""
    connection_string: str
    table_name: str = "logs"
    batch_size: int = 100
    flush_interval: int = 30  # seconds
    max_retries: int = 3

    def __post_init__(self):
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.flush_interval <= 0:
            raise ValueError("flush_interval must be positive")
        if not self.connection_string:
            raise ValueError("connection_string is required")

@dataclass
class MetricsSettings:
    """Settings for metrics collection."""
    enabled: bool = True
    endpoint: str | None = None
    tags: dict[str, str] | None = None
    sample_rate: float = 1.0

    def __post_init__(self):
        if not 0.0 <= self.sample_rate <= 1.0:
            raise ValueError("sample_rate must be between 0.0 and 1.0")
```

### Step 2: Integrate with LogConfig

```python
@dataclass
class ExtendedLogConfig(LogConfig):
    """Extended LogConfig with custom settings."""
    database_settings: DatabaseLoggerSettings | None = None
    metrics_settings: MetricsSettings | None = None
```

## 🔄 Custom Factory Patterns

### Step 1: Create Custom Factory

```python
class AdvancedFormatterFactory:
    """Factory with additional formatting options."""

    @staticmethod
    def get_formatter(
        formatter_type: LogFormatters,
        format_string: str,
        style: LogFormatterStyleChoices,
        colors: type[ColoredFormatterColors] | None = None,
        timezone: str | None = None,
        include_process_info: bool = False
    ) -> logging.Formatter:

        # Modify format string based on options
        if include_process_info:
            format_string = f"[PID:{os.getpid()}] {format_string}"

        if timezone:
            # Custom timezone handling
            formatter = TimezoneFormatter(format_string, style.value, timezone)
        else:
            formatter = FormatterFactory.get_formatter(
                formatter_type, format_string, style, colors
            )

        return formatter

class TimezoneFormatter(logging.Formatter):
    """Formatter with timezone support."""

    def __init__(self, fmt: str, style: str, timezone: str):
        super().__init__(fmt, style=style)
        self.timezone = timezone

    def formatTime(self, record, datefmt=None):
        import pytz
        dt = datetime.fromtimestamp(record.created, tz=pytz.timezone(self.timezone))
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S %Z")
```

## 🧪 Testing Extensions

### Unit Testing Custom Components

```python
import unittest
from unittest.mock import Mock, patch

class TestCustomFormatter(unittest.TestCase):
    def test_json_formatter(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        import json
        parsed = json.loads(result)

        self.assertEqual(parsed["level"], "INFO")
        self.assertEqual(parsed["message"], "Test message")
        self.assertIn("timestamp", parsed)

class TestWebhookHandler(unittest.TestCase):
    @patch('requests.Session.request')
    def test_webhook_handler_success(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        settings = WebhookHandlerSettings(url="https://example.com/webhook")
        handler = WebhookHandler(settings)

        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="Test", args=(), exc_info=None
        )

        handler.emit(record)
        mock_request.assert_called_once()
```

### Integration Testing

```python
def test_custom_formatter_integration():
    logger = Log.create_logger(
        "test_app",
        formatter_type=LogFormatters.JSON,
        file_handlers=[
            FileHandlerSpec(
                handler_type=FileHandlerTypes.FILE,
                config=FileHandlerSettings(filename="test.json")
            )
        ]
    )

    logger.info("Test message")

    # Verify JSON output
    with open("test.json", "r") as f:
        content = f.read()
        import json
        log_entry = json.loads(content.strip())
        assert log_entry["message"] == "Test message"
```

## 📦 Packaging Extensions

### Step 1: Create Extension Module

```python
# extensions/database_logging.py
from cli.modules.logging import LogConfig
from .handlers import DatabaseHandler
from .settings import DatabaseLoggerSettings

class DatabaseLoggingExtension:
    """Extension for database logging."""

    @staticmethod
    def extend_config(config: LogConfig, db_settings: DatabaseLoggerSettings) -> LogConfig:
        """Add database logging to existing config."""
        # Implementation here
        pass

    @staticmethod
    def create_database_logger(name: str, db_settings: DatabaseLoggerSettings):
        """Create logger with database handler."""
        # Implementation here
        pass
```

### Step 2: Plugin Registration

```python
# extensions/__init__.py
from .database_logging import DatabaseLoggingExtension
from .metrics_logging import MetricsLoggingExtension

__all__ = [
    "DatabaseLoggingExtension",
    "MetricsLoggingExtension"
]

# Register extensions
AVAILABLE_EXTENSIONS = {
    "database": DatabaseLoggingExtension,
    "metrics": MetricsLoggingExtension
}
```

### Step 3: Usage

```python
from cli.modules.logging.extensions import AVAILABLE_EXTENSIONS

# Use extension
db_extension = AVAILABLE_EXTENSIONS["database"]
db_settings = DatabaseLoggerSettings(connection_string="postgresql://...")
logger = db_extension.create_database_logger("app", db_settings)
```

## 🔍 Best Practices for Extensions

1. **Follow Existing Patterns** - Use the same patterns as built-in components
2. **Comprehensive Validation** - Validate all configuration in `__post_init__`
3. **Graceful Fallbacks** - Handle missing dependencies gracefully
4. **Thread Safety** - Ensure extensions work in multi-threaded environments
5. **Documentation** - Document all extension points and usage
6. **Testing** - Provide comprehensive tests for all extensions
7. **Backward Compatibility** - Don't break existing functionality
8. **Performance** - Consider performance impact of extensions

This extension system allows the logging module to grow and adapt to new requirements while maintaining its clean architecture and ease of use.
