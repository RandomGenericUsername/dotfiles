# Migration Guide: Replacing Current Pipeline

This guide shows how to migrate from the current pipeline implementation to the new pipeline module.

## Current Implementation (Before)

```python
# In install.py
@dataclass
class PipelineContext(ABC):
    logger_instance: logging.Logger

class Pipeline:
    def __init__(self, steps: list[callable]):
        self.steps = steps

    def run(self, context: PipelineContext):
        [step(context) if isinstance(step, callable) else () for step in self.steps]

# Usage
pipeline = Pipeline([print_installation_message])
pipeline.run(install_args)  # No return value, no error handling
```

## New Implementation (After)

```python
# In install.py
from cli.modules.pipeline import Pipeline, PipelineConfig

@dataclass
class PipelineContext:
    logger_instance: logging.Logger
    install_directory: Path
    backup_directory: Path
    install_type: InstallType
    # Runtime state
    results: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)

# Usage
pipeline = Pipeline([print_installation_message])
success = pipeline.run(context)  # Returns bool, proper error handling
if not success:
    logger.error("Installation failed")
    raise SystemExit(1)
```

## Step-by-Step Migration

### 1. Update Imports

**Before:**
```python
# No imports needed (pipeline was defined locally)
```

**After:**
```python
from cli.modules.pipeline import Pipeline, PipelineConfig, LogicOperator, ParallelConfig
```

### 2. Enhance PipelineContext

**Before:**
```python
@dataclass
class PipelineContext(ABC):
    logger_instance: logging.Logger
```

**After:**
```python
@dataclass
class PipelineContext:
    logger_instance: logging.Logger
    install_directory: Path
    backup_directory: Path
    install_type: InstallType
    # Runtime state for error tracking
    results: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)
```

### 3. Update Task Functions

**Before:**
```python
def print_installation_message(data: InstallArgs):
    logger: logging.Logger = data.logger_instance
    starting_installation_message: str = data.starting_installation_message
    logger.info(starting_installation_message)
    return data  # Return value ignored
```

**After:**
```python
def print_installation_message(context: PipelineContext) -> bool:
    """Print installation message."""
    try:
        logger = context.logger_instance
        logger.info("Starting installation...")
        return True  # Indicate success
    except Exception as e:
        context.logger_instance.error(f"Failed to print message: {e}")
        return False  # Indicate failure
```

### 4. Update Pipeline Usage

**Before:**
```python
install_args = InstallArgs(
    logger_instance=logger,
    starting_installation_message="Starting installation...",
)
pipeline = Pipeline([print_installation_message])
pipeline.run(install_args)  # No error handling
```

**After:**
```python
context = PipelineContext(
    logger_instance=logger,
    install_directory=install_directory,
    backup_directory=backup_directory,
    install_type=install_type,
)

pipeline = Pipeline([print_installation_message])
success = pipeline.run(context)

if not success:
    logger.error("Installation failed")
    if context.errors:
        for error in context.errors:
            logger.error(f"Error: {error}")
    raise SystemExit(1)
```

## Advanced Usage Examples

### Serial + Parallel Execution

```python
# Define tasks
def backup_files(context: PipelineContext) -> bool:
    # Your backup logic
    return True

def copy_dotfiles(context: PipelineContext) -> bool:
    # Your copy logic
    return True

def setup_symlinks(context: PipelineContext) -> bool:
    # Your symlink logic
    return True

def verify_installation(context: PipelineContext) -> bool:
    # Your verification logic
    return True

# Create pipeline with mixed execution
pipeline = Pipeline([
    backup_files,                    # Serial: backup first
    [copy_dotfiles, setup_symlinks], # Parallel: copy and symlink simultaneously
    verify_installation,             # Serial: verify everything worked
])

success = pipeline.run(context)
```

### Custom Configuration

```python
# Configure parallel execution
config = PipelineConfig(
    fail_fast=True,  # Stop on first failure
    parallel_config=ParallelConfig(
        operator=LogicOperator.AND,  # All parallel tasks must succeed
        max_workers=4,               # Limit concurrent tasks
        timeout=30.0                 # Timeout for parallel groups
    )
)

pipeline = Pipeline(steps, config)
success = pipeline.run(context)
```

## Benefits of Migration

1. **Return Values**: Know if pipeline succeeded or failed
2. **Error Handling**: Proper exception catching and reporting
3. **Parallel Execution**: Run tasks concurrently when possible
4. **Type Safety**: Full type hints and Protocol-based task interface
5. **Configurability**: Control execution behavior
6. **Testability**: Easy to mock and test individual components

## Backward Compatibility

The new pipeline is designed to be a drop-in replacement for simple use cases:

```python
# This still works
pipeline = Pipeline([task1, task2, task3])
success = pipeline.run(context)
```

The main changes are:
- Tasks must return `bool` instead of arbitrary values
- Pipeline returns `bool` instead of `None`
- Context should include error tracking fields
