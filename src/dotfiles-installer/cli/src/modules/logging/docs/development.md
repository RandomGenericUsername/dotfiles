# Development Guide

Guide for contributing to and developing the logging module.

## 🛠️ Development Setup

### Prerequisites

- Python 3.12+
- Git
- Virtual environment tool (venv, conda, etc.)

### Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd dotfiles-installer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
mypy>=1.0.0
black>=22.0.0
isort>=5.0.0
flake8>=5.0.0
pre-commit>=2.0.0
rich>=13.0.0  # For Rich features
```

## 🏗️ Project Structure

```
cli/modules/logging/
├── __init__.py              # Public API exports
├── log.py                   # Main Log facade
├── configurator.py          # LogConfigurator
├── log_types.py            # Type definitions and enums
├── utils.py                # Utility functions
├── rich_logger.py          # RichLogger wrapper
├── rich_console_manager.py # Console sharing
├── rich_feature_settings.py # Rich configuration
├── formatters/             # Formatter implementations
│   ├── __init__.py
│   ├── base.py
│   ├── colored.py
│   └── rich.py
├── handlers/               # Handler implementations
│   ├── __init__.py
│   ├── base.py
│   ├── console.py
│   ├── file.py
│   ├── file_settings.py
│   └── rich_settings.py
├── docs/                   # Documentation
│   ├── README.md
│   ├── architecture.md
│   ├── api-reference.md
│   ├── usage-guide.md
│   ├── configuration.md
│   ├── rich-features.md
│   ├── rich-integration.md
│   ├── extension-guide.md
│   ├── file-handling.md
│   ├── type-safety.md
│   ├── migration.md
│   ├── development.md
│   ├── testing.md
│   └── troubleshooting.md
└── tests/                  # Test files
    ├── __init__.py
    ├── test_log.py
    ├── test_configurator.py
    ├── test_formatters.py
    ├── test_handlers.py
    ├── test_rich_features.py
    └── conftest.py
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cli.modules.logging

# Run specific test file
pytest tests/test_log.py

# Run specific test
pytest tests/test_log.py::test_create_logger

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_rich"
```

### Test Categories

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **Rich Feature Tests** - Test Rich integration with/without Rich available
4. **File Handler Tests** - Test file logging and rotation
5. **Configuration Tests** - Test type safety and validation

### Writing Tests

#### Basic Test Structure

```python
import pytest
from cli.modules.logging import Log, LogLevels, ConsoleHandlers

class TestLogCreation:
    """Test logger creation functionality."""

    def test_create_basic_logger(self):
        """Test creating a basic logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        assert logger is not None
        assert logger._logger.name == "test"
        assert logger._logger.level == LogLevels.INFO.value

    def test_create_logger_with_rich(self):
        """Test creating logger with Rich features."""
        logger = Log.create_logger(
            "test",
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        assert logger is not None
        assert hasattr(logger, 'table')
        assert hasattr(logger, 'panel')
```

#### Testing Rich Features

```python
from unittest.mock import patch, Mock

class TestRichFeatures:
    """Test Rich feature functionality."""

    def test_rich_features_with_rich_available(self):
        """Test Rich features when Rich is available."""
        with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', True):
            with patch('cli.modules.logging.rich_logger.Table') as mock_table:
                logger = Log.create_logger(
                    "test",
                    console_handler_type=ConsoleHandlers.RICH,
                    rich_features=RichFeatureSettings(enabled=True)
                )

                logger.table([["A", "B"], ["1", "2"]], title="Test")
                mock_table.assert_called_once()

    def test_rich_features_without_rich(self):
        """Test Rich features when Rich is not available."""
        with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', False):
            logger = Log.create_logger(
                "test",
                rich_features=RichFeatureSettings(enabled=True)
            )

            # Should not raise exception
            logger.table([["A", "B"], ["1", "2"]], title="Test")
            logger.panel("Test content", title="Test")
```

#### Testing File Handlers

```python
import tempfile
import os

class TestFileHandlers:
    """Test file handler functionality."""

    def test_file_logging(self):
        """Test basic file logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            logger = Log.create_logger(
                "test",
                file_handlers=[
                    FileHandlerSpec(
                        handler_type=FileHandlerTypes.FILE,
                        config=FileHandlerSettings(filename=log_file)
                    )
                ]
            )

            logger.info("Test message")

            # Verify file content
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
```

### Test Configuration

```python
# conftest.py
import pytest
import tempfile
import os

@pytest.fixture
def temp_log_dir():
    """Provide temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_rich_available():
    """Mock Rich availability."""
    with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', True):
        yield

@pytest.fixture
def mock_rich_unavailable():
    """Mock Rich unavailability."""
    with patch('cli.modules.logging.rich_logger.RICH_AVAILABLE', False):
        yield
```

## 🎨 Code Style

### Formatting Tools

```bash
# Format code with black
black cli/modules/logging/

# Sort imports with isort
isort cli/modules/logging/

# Check style with flake8
flake8 cli/modules/logging/

# Type checking with mypy
mypy cli/modules/logging/
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Style Guidelines

1. **Follow PEP 8** - Standard Python style guide
2. **Use type hints** - All functions should have type annotations
3. **Document with docstrings** - Use Google-style docstrings
4. **Keep functions small** - Single responsibility principle
5. **Use descriptive names** - Clear, self-documenting code
6. **Validate inputs** - Use `__post_init__` for dataclass validation

### Example Code Style

```python
from typing import Any
from dataclasses import dataclass

@dataclass
class ExampleSettings:
    """Example settings class with proper style.

    Args:
        name: The name of the setting
        value: The value of the setting
        enabled: Whether the setting is enabled
    """
    name: str
    value: int
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.value < 0:
            raise ValueError("value must be non-negative")

def create_example(
    name: str,
    settings: ExampleSettings | None = None,
    **kwargs: Any
) -> "ExampleClass":
    """Create an example instance.

    Args:
        name: The name for the example
        settings: Optional settings configuration
        **kwargs: Additional keyword arguments

    Returns:
        Configured example instance

    Raises:
        ValueError: If name is empty
    """
    if not name:
        raise ValueError("name is required")

    if settings is None:
        settings = ExampleSettings(name=name, value=0)

    return ExampleClass(name, settings)
```

## 🔧 Adding New Features

### Feature Development Process

1. **Design** - Plan the feature and its integration points
2. **Types** - Add necessary enums and dataclasses
3. **Implementation** - Implement core functionality
4. **Factory Integration** - Add to appropriate factories
5. **Configuration** - Add configuration options
6. **Testing** - Write comprehensive tests
7. **Documentation** - Update relevant documentation

### Example: Adding New Formatter

```python
# 1. Create formatter class
class CustomFormatter(logging.Formatter):
    """Custom formatter implementation."""

    def format(self, record: logging.LogRecord) -> str:
        # Implementation here
        pass

# 2. Add to enum
class LogFormatters(Enum):
    CUSTOM = "custom"

# 3. Update factory
class FormatterFactory:
    @staticmethod
    def get_formatter(formatter_type: LogFormatters, **kwargs):
        if formatter_type == LogFormatters.CUSTOM:
            return CustomFormatter(**kwargs)
        # ... existing code

# 4. Add tests
class TestCustomFormatter:
    def test_custom_formatter(self):
        formatter = CustomFormatter()
        # Test implementation

# 5. Update documentation
```

## 📚 Documentation

### Documentation Standards

1. **API Documentation** - Docstrings for all public functions
2. **User Guides** - Practical examples and tutorials
3. **Architecture Documentation** - Design decisions and patterns
4. **Migration Guides** - Help users upgrade
5. **Troubleshooting** - Common issues and solutions

### Writing Documentation

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """Example function with proper documentation.

    This function demonstrates the documentation style used
    throughout the logging module.

    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not an integer

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    if not param1:
        raise ValueError("param1 cannot be empty")

    return True
```

## 🚀 Release Process

### Version Management

```python
# In __init__.py
__version__ = "1.0.0"
```

### Release Checklist

- [ ] **Update version number** - Increment version in `__init__.py`
- [ ] **Update CHANGELOG** - Document changes and new features
- [ ] **Run full test suite** - Ensure all tests pass
- [ ] **Update documentation** - Reflect any API changes
- [ ] **Type checking** - Run mypy with no errors
- [ ] **Code formatting** - Run black and isort
- [ ] **Performance testing** - Check for regressions
- [ ] **Create release notes** - Summarize changes for users

### Semantic Versioning

- **Major (X.0.0)** - Breaking changes
- **Minor (0.X.0)** - New features, backward compatible
- **Patch (0.0.X)** - Bug fixes, backward compatible

## 🤝 Contributing Guidelines

### Pull Request Process

1. **Fork the repository** - Create your own fork
2. **Create feature branch** - `git checkout -b feature/new-feature`
3. **Make changes** - Implement your feature or fix
4. **Add tests** - Ensure good test coverage
5. **Update documentation** - Document any changes
6. **Run tests** - Ensure all tests pass
7. **Submit PR** - Create pull request with clear description

### Code Review Criteria

- **Functionality** - Does it work as intended?
- **Tests** - Are there adequate tests?
- **Documentation** - Is it properly documented?
- **Style** - Does it follow style guidelines?
- **Performance** - Any performance implications?
- **Backward Compatibility** - Does it break existing code?

### Issue Reporting

When reporting issues:

1. **Clear title** - Summarize the problem
2. **Reproduction steps** - How to reproduce the issue
3. **Expected behavior** - What should happen
4. **Actual behavior** - What actually happens
5. **Environment** - Python version, OS, dependencies
6. **Code example** - Minimal example demonstrating issue

## 🔍 Debugging

### Debug Mode

```python
# Enable debug logging for development
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use the logging module's debug features
logger = Log.create_logger(
    "debug",
    log_level=LogLevels.DEBUG,
    console_handler_type=ConsoleHandlers.RICH,
    handler_config=RichHandlerSettings(
        show_path=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True
    )
)
```

### Common Development Issues

1. **Import Errors** - Check Python path and dependencies
2. **Type Errors** - Run mypy to catch type issues
3. **Test Failures** - Use pytest's verbose mode for details
4. **Rich Features Not Working** - Check Rich availability
5. **File Permission Errors** - Ensure write permissions for log files

This development guide provides the foundation for contributing to and extending the logging module while maintaining code quality and consistency.
