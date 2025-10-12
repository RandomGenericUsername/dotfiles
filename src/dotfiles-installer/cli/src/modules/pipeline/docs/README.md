# Pipeline Module

A clean, type-safe pipeline execution system for orchestrating steps in serial and parallel with class-based architecture.

## Quick Start

```python
from cli.modules.pipeline import Pipeline, PipelineStep

# Define your steps
class BackupFilesStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "backup_files"

    @property
    def description(self) -> str:
        return "Backup existing files"

    def run(self, context: PipelineContext) -> PipelineContext:
        # Your backup logic
        context.results['backup_completed'] = True
        return context

# Simple serial execution
pipeline = Pipeline([BackupFilesStep(), CopyFilesStep(), VerifyStep()])
final_context = pipeline.run(context)

# Mixed serial and parallel
pipeline = Pipeline([
    BackupFilesStep(),                              # Serial
    [CopyFilesStep(), SetupSymlinksStep()],        # Parallel group
    VerifyStep(),                                   # Serial
])
final_context = pipeline.run(context)
```

## Core Features

- 🔄 **Serial & Parallel Execution** - Mix serial steps and parallel groups
- 🏗️ **Class-Based Steps** - Clean OOP design with abstract base class
- 🔄 **Context Passing** - Steps receive and return context objects
- ⚙️ **Configurable Logic** - AND/OR operators for parallel groups
- 🛡️ **Type Safety** - Abstract base class with full type hints
- 🚨 **Error Handling** - Comprehensive error collection and fail-fast options
- 🏗️ **Clean Architecture** - Separation of concerns with dedicated executors
- 🧪 **Testable** - Dependency injection for easy mocking

## Step Interface

Steps must inherit from the `PipelineStep` abstract base class:

```python
from abc import ABC, abstractmethod

class PipelineStep(ABC):
    @property
    @abstractmethod
    def step_id(self) -> str:
        """Unique identifier for this step."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this step does."""
        pass

    @abstractmethod
    def run(self, context: Any) -> Any:
        """Execute the step logic and return modified context."""
        pass

    # Optional overridable properties
    @property
    def timeout(self) -> float | None:
        return None

    @property
    def critical(self) -> bool:
        return True
```

Example task:

```python
def backup_files(context: PipelineContext) -> bool:
    """Backup existing files."""
    try:
        # Your backup logic here
        context.logger_instance.info("Files backed up successfully")
        return True
    except Exception as e:
        context.logger_instance.error(f"Backup failed: {e}")
        return False
```

## Configuration

### Pipeline Configuration

```python
from cli.modules.pipeline import PipelineConfig, ParallelConfig, LogicOperator

config = PipelineConfig(
    fail_fast=True,  # Stop on first failure
    parallel_config=ParallelConfig(
        operator=LogicOperator.AND,  # All tasks must succeed
        max_workers=4,               # Limit concurrent tasks
        timeout=30.0                 # Timeout for parallel groups
    )
)

pipeline = Pipeline(steps, config)
```

### Parallel Logic Operators

- **AND** (default): All tasks in parallel group must succeed
- **OR**: At least one task in parallel group must succeed

```python
# AND logic - all must succeed
config = ParallelConfig(operator=LogicOperator.AND)

# OR logic - any one can succeed
config = ParallelConfig(operator=LogicOperator.OR)
```

## Integration with Install Command

Replace the current pipeline in `install.py`:

```python
from cli.modules.pipeline import Pipeline

def install(...):
    # ... existing setup code ...

    context = PipelineContext(
        logger_instance=logger,
        install_directory=install_directory,
        backup_directory=backup_directory,
        # ... other args
    )

    pipeline = Pipeline([
        backup_existing_files,
        [copy_dotfiles, setup_symlinks],  # parallel
        verify_installation,
    ])

    success = pipeline.run(context)
    if not success:
        logger.error("Installation failed")
        raise SystemExit(1)
```

## Architecture

The pipeline module follows clean architecture principles:

- **Pipeline**: High-level interface (like Log class)
- **PipelineExecutor**: Orchestrates execution flow
- **ParallelTaskExecutor**: Handles parallel groups with ThreadPoolExecutor
- **TaskExecutor**: Executes individual tasks with error handling

## Error Handling

- Tasks return `bool` for success/failure
- Exceptions are caught and stored in `context.errors` (if available)
- Pipeline returns overall success status
- Configurable fail-fast behavior

## Testing

The module includes comprehensive tests demonstrating all features:

```bash
# Run tests
cd src/dotfiles-installer
uv run pytest cli/modules/pipeline/tests/
```

## Type Safety

Full type hints throughout:
- Protocol-based task interface
- Union types for mixed serial/parallel steps
- Dataclass configuration with validation
- Generic context support
