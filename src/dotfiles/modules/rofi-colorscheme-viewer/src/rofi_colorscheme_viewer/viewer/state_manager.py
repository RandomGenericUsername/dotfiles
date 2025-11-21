"""State management for format selection."""

from pathlib import Path


class StateManager:
    """Manages persistent state for format selection.

    Stores the current format selection in a file so it persists
    across rofi reloads when cycling formats.

    Attributes:
        state_file: Path to the state file
        available_formats: List of available formats

    Example:
        >>> manager = StateManager(
        ...     state_file=Path("/tmp/format-state"),
        ...     available_formats=["hex", "rgb", "json"]
        ... )
        >>> manager.get_current_format()
        'hex'
        >>> manager.cycle_format()
        >>> manager.get_current_format()
        'rgb'
    """

    def __init__(self, state_file: Path, available_formats: list[str]):
        """Initialize state manager.

        Args:
            state_file: Path to the state file
            available_formats: List of available formats
        """
        self.state_file = state_file
        self.available_formats = available_formats

        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def get_current_format(self) -> str:
        """Get the current format from state file.

        Returns:
            Current format string (defaults to first available format)

        Example:
            >>> manager.get_current_format()
            'hex'
        """
        if not self.state_file.exists():
            # Default to first available format
            return self.available_formats[0]

        current_format = self.state_file.read_text().strip()

        # Validate format
        if current_format not in self.available_formats:
            return self.available_formats[0]

        return current_format

    def set_format(self, format_type: str) -> None:
        """Set the current format in state file.

        Args:
            format_type: Format to set

        Raises:
            ValueError: If format_type is not in available_formats

        Example:
            >>> manager.set_format("rgb")
        """
        if format_type not in self.available_formats:
            raise ValueError(
                f"Invalid format: {format_type}. "
                f"Available: {', '.join(self.available_formats)}"
            )

        self.state_file.write_text(format_type)

    def cycle_format(self) -> str:
        """Cycle to the next format.

        Returns:
            The new current format

        Example:
            >>> manager.cycle_format()
            'rgb'
            >>> manager.cycle_format()
            'json'
            >>> manager.cycle_format()
            'hex'
        """
        current = self.get_current_format()

        # Find current index
        try:
            current_index = self.available_formats.index(current)
        except ValueError:
            # Current format not in list, default to first
            current_index = -1

        # Cycle to next (wrap around)
        next_index = (current_index + 1) % len(self.available_formats)
        next_format = self.available_formats[next_index]

        # Save new format
        self.set_format(next_format)

        return next_format
