"""System attributes repository."""

from dotfiles_manager.models.system_attributes import SystemAttributes
from dotfiles_state_manager import StateManager


class SystemAttributesRepository:
    """Repository for system attributes (font, monitors, etc.)."""

    def __init__(self, state: StateManager):
        """Initialize repository.

        Args:
            state: State manager instance
        """
        self._state = state

    def get_attributes(self) -> SystemAttributes:
        """Get current system attributes.

        Returns:
            SystemAttributes: Current system attributes
        """
        font_family = self._state.get("system:font_family") or "JetBrains Mono"
        font_size_str = self._state.get("system:font_size") or "14"
        font_size = int(font_size_str)

        # Get monitors list
        monitors_count_str = self._state.get("system:monitors:count") or "0"
        monitors_count = int(monitors_count_str)
        monitors = []
        for i in range(monitors_count):
            monitor = self._state.get(f"system:monitors:{i}")
            if monitor:
                monitors.append(monitor)

        return SystemAttributes(
            font_family=font_family,
            font_size=font_size,
            monitors=monitors,
        )

    def set_font_family(self, font_family: str) -> None:
        """Set system font family.

        Args:
            font_family: Font family to set
        """
        self._state.set("system:font_family", font_family)

    def set_font_size(self, font_size: int) -> None:
        """Set system font size.

        Args:
            font_size: Font size in pixels
        """
        self._state.set("system:font_size", str(font_size))

    def set_monitors(self, monitors: list[str]) -> None:
        """Set monitors list.

        Args:
            monitors: List of monitor names
        """
        # Clear existing monitors
        monitors_count_str = self._state.get("system:monitors:count") or "0"
        monitors_count = int(monitors_count_str)
        for i in range(monitors_count):
            self._state.delete(f"system:monitors:{i}")

        # Set new monitors
        self._state.set("system:monitors:count", str(len(monitors)))
        for i, monitor in enumerate(monitors):
            self._state.set(f"system:monitors:{i}", monitor)

    def update_attributes(self, attributes: SystemAttributes) -> None:
        """Update system attributes.

        Args:
            attributes: System attributes to set
        """
        self.set_font_family(attributes.font_family)
        self.set_font_size(attributes.font_size)
        self.set_monitors(attributes.monitors)
