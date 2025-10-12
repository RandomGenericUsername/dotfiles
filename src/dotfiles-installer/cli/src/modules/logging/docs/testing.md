# Testing Guide

Comprehensive guide to testing patterns, strategies, and examples for the logging module.

## 🧪 Testing Overview

The logging module uses pytest for testing with comprehensive coverage of:

1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Component interaction testing
3. **Rich Feature Tests** - Rich library integration testing
4. **File Handler Tests** - File logging and rotation testing
5. **Configuration Tests** - Type safety and validation testing
6. **Performance Tests** - Performance and resource usage testing

## 🛠️ Test Setup

### Dependencies

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock
```

### Test Configuration

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=cli.modules.logging
    --cov-report=term-missing
    --cov-report=html
```

### Test Fixtures

```python
# conftest.py
import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from cli.modules.logging import Log, LogLevels, ConsoleHandlers

@pytest.fixture
def temp_log_dir():
    """Provide temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def basic_logger():
    """Provide basic logger for testing."""
    return Log.create_logger("test", log_level=LogLevels.INFO)

@pytest.fixture
def rich_logger():
    """Provide Rich-enabled logger for testing."""
    return Log.create_logger(
        "test_rich",
        console_handler_type=ConsoleHandlers.RICH,
        rich_features=RichFeatureSettings(enabled=True)
    )

@pytest.fixture
def mock_rich_available():
    """Mock Rich library as available."""
    with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', True):
        yield

@pytest.fixture
def mock_rich_unavailable():
    """Mock Rich library as unavailable."""
    with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', False):
        yield

@pytest.fixture
def mock_console():
    """Provide mock Rich console."""
    console = Mock()
    with patch('cli.modules.logging.rich_console_manager.RichConsoleManager.get_console',
               return_value=console):
        yield console
```

## 🔧 Unit Testing

### Testing Logger Creation

```python
class TestLoggerCreation:
    """Test logger creation functionality."""

    def test_create_basic_logger(self):
        """Test creating a basic logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        assert logger is not None
        assert logger._logger.name == "test"
        assert logger._logger.level == LogLevels.INFO.value

    def test_create_logger_with_custom_format(self):
        """Test creating logger with custom format."""
        custom_format = "%(levelname)s: %(message)s"
        logger = Log.create_logger("test", format=custom_format)

        # Check that handler has correct formatter
        handler = logger._logger.handlers[0]
        assert custom_format in handler.formatter._fmt

    def test_create_logger_with_verbosity(self):
        """Test logger creation with verbosity override."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.WARNING,  # This should be overridden
            verbosity=2  # Should set to DEBUG
        )

        assert logger._logger.level == LogLevels.DEBUG.value

    def test_invalid_logger_name(self):
        """Test error handling for invalid logger name."""
        with pytest.raises(ValueError, match="Logger name cannot be empty"):
            Log.create_logger("")
```

### Testing Configuration Validation

```python
class TestConfigurationValidation:
    """Test configuration validation."""

    def test_rich_handler_settings_validation(self):
        """Test RichHandlerSettings validation."""
        # Valid settings
        settings = RichHandlerSettings(
            show_time=True,
            tracebacks_extra_lines=5
        )
        assert settings.show_time is True

        # Invalid tracebacks_extra_lines
        with pytest.raises(ValueError, match="tracebacks_extra_lines must be non-negative"):
            RichHandlerSettings(tracebacks_extra_lines=-1)

    def test_file_handler_settings_validation(self):
        """Test FileHandlerSettings validation."""
        # Valid settings
        settings = FileHandlerSettings(filename="test.log")
        assert settings.filename == "test.log"

        # Invalid filename
        with pytest.raises(ValueError, match="filename cannot be empty"):
            FileHandlerSettings(filename="")

        # Invalid mode
        with pytest.raises(ValueError, match="Invalid mode"):
            FileHandlerSettings(filename="test.log", mode="invalid")

    def test_rotating_file_handler_validation(self):
        """Test RotatingFileHandlerSettings validation."""
        # Valid settings
        settings = RotatingFileHandlerSettings(
            filename="test.log",
            max_bytes=1000000,
            backup_count=5
        )
        assert settings.max_bytes == 1000000

        # Invalid max_bytes
        with pytest.raises(ValueError, match="max_bytes must be positive"):
            RotatingFileHandlerSettings(filename="test.log", max_bytes=0)

        # Invalid backup_count
        with pytest.raises(ValueError, match="backup_count must be non-negative"):
            RotatingFileHandlerSettings(filename="test.log", backup_count=-1)
```

### Testing Formatters

```python
class TestFormatters:
    """Test formatter functionality."""

    def test_default_formatter(self):
        """Test default formatter."""
        from cli.modules.logging.formatters import FormatterFactory

        formatter = FormatterFactory.get_formatter(
            LogFormatters.DEFAULT,
            "%(levelname)s: %(message)s",
            LogFormatterStyleChoices.PERCENT
        )

        assert isinstance(formatter, logging.Formatter)

    def test_colored_formatter(self):
        """Test colored formatter."""
        formatter = FormatterFactory.get_formatter(
            LogFormatters.COLORED,
            "%(levelname)s: %(message)s",
            LogFormatterStyleChoices.PERCENT,
            ColoredFormatterColors
        )

        # Create test record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)
        assert "Test message" in formatted

    @pytest.mark.skipif(not RICH_AVAILABLE, reason="Rich not available")
    def test_rich_formatter(self):
        """Test Rich formatter when Rich is available."""
        formatter = FormatterFactory.get_formatter(
            LogFormatters.RICH,
            "%(message)s",
            LogFormatterStyleChoices.PERCENT
        )

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)
        assert "Test message" in formatted
```

## 🎭 Rich Feature Testing

### Testing Rich Features with Mock

```python
class TestRichFeatures:
    """Test Rich feature functionality."""

    def test_table_with_rich_available(self, mock_rich_available, mock_console):
        """Test table feature when Rich is available."""
        logger = Log.create_logger(
            "test",
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        data = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        logger.table(data, title="Test Table")

        # Verify console.print was called
        mock_console.print.assert_called()

    def test_panel_with_rich_available(self, mock_rich_available, mock_console):
        """Test panel feature when Rich is available."""
        logger = Log.create_logger(
            "test",
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        logger.panel("Test content", title="Test Panel")
        mock_console.print.assert_called()

    def test_rich_features_without_rich(self, mock_rich_unavailable):
        """Test Rich features when Rich is not available."""
        logger = Log.create_logger(
            "test",
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should not raise exception
        logger.table([["A", "B"]], title="Test")
        logger.panel("Test", title="Test")
        logger.rule("Test")

    def test_progress_context_manager(self, mock_rich_available):
        """Test progress context manager."""
        with patch('cli.modules.logging.rich_logger.Progress') as mock_progress:
            mock_progress_instance = Mock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance

            logger = Log.create_logger(
                "test",
                console_handler_type=ConsoleHandlers.RICH,
                rich_features=RichFeatureSettings(enabled=True)
            )

            with logger.progress("Test") as progress:
                assert progress is mock_progress_instance

    def test_status_context_manager(self, mock_rich_available):
        """Test status context manager."""
        with patch('cli.modules.logging.rich_logger.Status') as mock_status:
            mock_status_instance = Mock()
            mock_status.return_value.__enter__.return_value = mock_status_instance

            logger = Log.create_logger(
                "test",
                console_handler_type=ConsoleHandlers.RICH,
                rich_features=RichFeatureSettings(enabled=True)
            )

            with logger.status("Test") as status:
                assert status is mock_status_instance
```

### Testing Rich Console Manager

```python
class TestRichConsoleManager:
    """Test Rich console manager."""

    def test_singleton_behavior(self):
        """Test that RichConsoleManager is a singleton."""
        from cli.modules.logging.rich_console_manager import RichConsoleManager

        manager1 = RichConsoleManager()
        manager2 = RichConsoleManager()

        assert manager1 is manager2

    def test_console_registration(self):
        """Test console registration and retrieval."""
        from cli.modules.logging.rich_console_manager import RichConsoleManager

        manager = RichConsoleManager()

        # Initially no console
        assert manager.get_console("test") is None

        # Register console
        mock_console = Mock()
        manager.register_console("test", mock_console)

        # Should return registered console
        assert manager.get_console("test") is mock_console

    def test_console_cleanup(self):
        """Test console cleanup."""
        from cli.modules.logging.rich_console_manager import RichConsoleManager

        manager = RichConsoleManager()
        mock_console = Mock()

        manager.register_console("test", mock_console)
        assert manager.get_console("test") is mock_console

        manager.cleanup_console("test")
        assert manager.get_console("test") is None
```

## 📁 File Handler Testing

### Testing File Logging

```python
class TestFileHandlers:
    """Test file handler functionality."""

    def test_basic_file_logging(self, temp_log_dir):
        """Test basic file logging."""
        log_file = os.path.join(temp_log_dir, "test.log")

        logger = Log.create_logger(
            "test",
            file_handlers=[
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.FILE,
                    config=FileHandlerSettings(filename=log_file)
                )
            ]
        )

        test_message = "Test log message"
        logger.info(test_message)

        # Verify file was created and contains message
        assert os.path.exists(log_file)
        with open(log_file, 'r') as f:
            content = f.read()
            assert test_message in content

    def test_rotating_file_handler(self, temp_log_dir):
        """Test rotating file handler."""
        log_file = os.path.join(temp_log_dir, "rotating.log")

        logger = Log.create_logger(
            "test",
            file_handlers=[
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.ROTATING_FILE,
                    config=RotatingFileHandlerSettings(
                        filename=log_file,
                        max_bytes=100,  # Small size for testing
                        backup_count=2
                    )
                )
            ]
        )

        # Write enough data to trigger rotation
        for i in range(10):
            logger.info(f"Test message {i} with enough content to trigger rotation")

        # Check that rotation occurred
        assert os.path.exists(log_file)
        # Backup files should exist
        backup_files = [f for f in os.listdir(temp_log_dir) if f.startswith("rotating.log.")]
        assert len(backup_files) > 0

    def test_timed_rotating_file_handler(self, temp_log_dir):
        """Test timed rotating file handler."""
        log_file = os.path.join(temp_log_dir, "timed.log")

        logger = Log.create_logger(
            "test",
            file_handlers=[
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.TIMED_ROTATING_FILE,
                    config=TimedRotatingFileHandlerSettings(
                        filename=log_file,
                        when='S',  # Every second for testing
                        interval=1,
                        backup_count=3
                    )
                )
            ]
        )

        logger.info("Test message")

        # Verify file was created
        assert os.path.exists(log_file)
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Test message" in content

    def test_multiple_file_handlers(self, temp_log_dir):
        """Test multiple file handlers."""
        info_file = os.path.join(temp_log_dir, "info.log")
        error_file = os.path.join(temp_log_dir, "error.log")

        logger = Log.create_logger(
            "test",
            file_handlers=[
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.FILE,
                    config=FileHandlerSettings(filename=info_file)
                ),
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.FILE,
                    config=FileHandlerSettings(filename=error_file)
                )
            ]
        )

        logger.info("Info message")
        logger.error("Error message")

        # Both files should exist and contain messages
        assert os.path.exists(info_file)
        assert os.path.exists(error_file)

        with open(info_file, 'r') as f:
            content = f.read()
            assert "Info message" in content
            assert "Error message" in content

        with open(error_file, 'r') as f:
            content = f.read()
            assert "Info message" in content
            assert "Error message" in content
```

### Testing File Permissions

```python
class TestFilePermissions:
    """Test file permission handling."""

    def test_permission_error_handling(self, temp_log_dir):
        """Test handling of permission errors."""
        # Create read-only directory
        readonly_dir = os.path.join(temp_log_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only

        log_file = os.path.join(readonly_dir, "test.log")

        # Should handle permission error gracefully
        try:
            logger = Log.create_logger(
                "test",
                file_handlers=[
                    FileHandlerSpec(
                        handler_type=FileHandlerTypes.FILE,
                        config=FileHandlerSettings(filename=log_file)
                    )
                ]
            )

            # This might raise PermissionError or be handled gracefully
            logger.info("Test message")

        except PermissionError:
            # Expected behavior
            pass
        finally:
            # Cleanup
            os.chmod(readonly_dir, 0o755)
```

## 🔄 Integration Testing

### Testing Logger Updates

```python
class TestLoggerUpdates:
    """Test logger update functionality."""

    def test_update_log_level(self):
        """Test updating log level."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        # Initial level
        assert logger._logger.level == LogLevels.INFO.value

        # Update level
        Log.update("test", log_level=LogLevels.DEBUG)

        # Verify update
        assert logger._logger.level == LogLevels.DEBUG.value

    def test_update_with_config(self):
        """Test updating with LogConfig."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        new_config = LogConfig(
            name="test",
            log_level=LogLevels.WARNING,
            verbosity=0,
            formatter_style=LogFormatterStyleChoices.PERCENT,
            format="%(message)s",
            formatter_type=LogFormatters.DEFAULT
        )

        Log.update("test", config=new_config)

        # Verify update
        assert logger._logger.level == LogLevels.WARNING.value
```

### Testing Component Integration

```python
class TestComponentIntegration:
    """Test integration between components."""

    def test_rich_handler_with_rich_features(self, mock_rich_available):
        """Test Rich handler integration with Rich features."""
        with patch('cli.modules.logging.rich_console_manager.Console') as mock_console_class:
            mock_console = Mock()
            mock_console_class.return_value = mock_console

            logger = Log.create_logger(
                "test",
                console_handler_type=ConsoleHandlers.RICH,
                rich_features=RichFeatureSettings(enabled=True)
            )

            # Both handler and features should use same console
            logger.info("Regular log message")
            logger.table([["A", "B"]], title="Test Table")

            # Console should be used for both
            assert mock_console.print.call_count >= 2
```

## 📊 Performance Testing

### Testing Performance

```python
import time
import pytest

class TestPerformance:
    """Test performance characteristics."""

    def test_logger_creation_performance(self):
        """Test logger creation performance."""
        start_time = time.time()

        for i in range(100):
            logger = Log.create_logger(f"test_{i}")

        end_time = time.time()
        duration = end_time - start_time

        # Should create 100 loggers in reasonable time
        assert duration < 1.0  # Less than 1 second

    def test_logging_performance(self, basic_logger):
        """Test logging performance."""
        start_time = time.time()

        for i in range(1000):
            basic_logger.info(f"Test message {i}")

        end_time = time.time()
        duration = end_time - start_time

        # Should log 1000 messages in reasonable time
        assert duration < 1.0  # Less than 1 second

    @pytest.mark.skipif(not RICH_AVAILABLE, reason="Rich not available")
    def test_rich_feature_performance(self, rich_logger):
        """Test Rich feature performance."""
        start_time = time.time()

        for i in range(100):
            rich_logger.table([["A", "B"], ["1", "2"]], title=f"Table {i}")

        end_time = time.time()
        duration = end_time - start_time

        # Should create 100 tables in reasonable time
        assert duration < 5.0  # Less than 5 seconds
```

## 🎯 Test Coverage

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=cli.modules.logging --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Coverage Goals

- **Overall Coverage**: > 90%
- **Critical Components**: > 95%
- **New Features**: 100%

### Coverage Exclusions

```python
# pragma: no cover for defensive code
if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

# pragma: no cover for fallback imports
try:
    from rich import Console
except ImportError:  # pragma: no cover
    Console = None
```

## 📝 Testing Best Practices

1. **Test Isolation** - Each test should be independent
2. **Use Fixtures** - Reuse common setup code
3. **Mock External Dependencies** - Don't rely on external services
4. **Test Edge Cases** - Include boundary conditions and error cases
5. **Clear Test Names** - Describe what is being tested
6. **Arrange-Act-Assert** - Structure tests clearly
7. **Test Documentation** - Include docstrings for complex tests
8. **Performance Awareness** - Don't let tests become too slow
9. **Cleanup Resources** - Use temporary files and directories
10. **Continuous Integration** - Run tests automatically

This comprehensive testing approach ensures the logging module is reliable, performant, and maintainable across all its features and use cases.
