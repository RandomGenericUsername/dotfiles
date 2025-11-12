"""Base classes and interfaces for manager implementations."""

from abc import ABC, abstractmethod
from typing import Any


class BaseManager(ABC):
    """Abstract base class for manager implementations.

    Provides a common interface that all manager implementations
    should follow.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the manager."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources."""
        pass

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Get current status.

        Returns:
            Dictionary containing status information.
        """
        pass
