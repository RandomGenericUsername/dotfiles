"""Core pipeline types and configuration classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from src.config.enums import InstallType
from src.modules.logging.rich.rich_logger import RichLogger


@dataclass
class PipelineContext:
    """Centralized pipeline context for dotfiles installer."""

    logger_instance: RichLogger
    install_directory: Path
    backup_directory: Path
    install_type: InstallType

    dependencies_directory: Path
    scripts_directory: Path
    config_directory: Path
    # Runtime state
    results: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)


class LogicOperator(Enum):
    """Logic operators for parallel task execution."""

    AND = "and"
    OR = "or"


class PipelineStep(ABC):
    """Abstract base class for pipeline steps."""

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
    def run(self, context: PipelineContext) -> PipelineContext:
        """
        Execute the step logic.

        Args:
            context: Pipeline context object

        Returns:
            PipelineContext: The context object (potentially modified)
        """
        pass

    # Optional overridable properties
    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return None

    @property
    def retries(self) -> int:
        """Number of retries on failure."""
        return 0

    @property
    def critical(self) -> bool:
        """Whether step failure should stop the pipeline."""
        return True


@dataclass
class ParallelConfig:
    """Configuration for parallel task execution."""

    operator: LogicOperator = LogicOperator.AND
    max_workers: int | None = None
    timeout: float | None = None


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""

    fail_fast: bool = True
    parallel_config: ParallelConfig = field(default_factory=ParallelConfig)


# Type alias for pipeline steps
TaskStep = PipelineStep | list[PipelineStep]
