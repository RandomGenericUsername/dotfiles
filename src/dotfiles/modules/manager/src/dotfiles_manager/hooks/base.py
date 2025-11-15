"""Base hook interface."""

from abc import ABC, abstractmethod

from dotfiles_manager.models.hook import HookContext, HookResult


class Hook(ABC):
    """Abstract base class for hooks.

    Hooks are executed after wallpaper changes to perform
    additional actions (e.g., generate icons, reload UI components).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this hook."""
        pass

    @abstractmethod
    def execute(self, context: HookContext) -> HookResult:
        """Execute the hook logic.

        Args:
            context: Hook execution context

        Returns:
            HookResult: Result of hook execution
        """
        pass
