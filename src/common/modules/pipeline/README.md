# Dotfiles Pipeline

Flexible pipeline execution framework with support for serial and parallel task execution.

## Features

- Serial and parallel task execution
- Type-safe pipeline context
- Configurable execution strategies
- Clean separation of concerns
- Reusable across different applications

## Installation

This module is part of the dotfiles monorepo and uses UV for dependency management.

## Usage

```python
from dotfiles_pipeline import Pipeline, PipelineStep, PipelineContext

# Define your steps
class MyStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "my_step"
    
    @property
    def description(self) -> str:
        return "My custom step"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        # Your logic here
        return context

# Create and run pipeline
pipeline = Pipeline([MyStep()])
result = pipeline.run(context)
```

## Dependencies

- `dotfiles-logging` - Logging infrastructure
- `dotfiles-package-manager` - Package management (used in PipelineContext)

