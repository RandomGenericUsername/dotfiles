"""Preset manager for loading and managing effect presets."""

from wallpaper_processor.config import AppConfig, Preset
from wallpaper_processor.core.exceptions import PresetNotFoundError


class PresetManager:
    """Manages effect presets."""

    def __init__(self, settings: AppConfig):
        """Initialize preset manager.

        Args:
            settings: Application configuration
        """
        self.settings = settings

    def get_preset(self, preset_name: str) -> Preset:
        """Get preset by name.

        Args:
            preset_name: Preset identifier

        Returns:
            Preset instance

        Raises:
            PresetNotFoundError: If preset doesn't exist
        """
        if preset_name not in self.settings.presets:
            raise PresetNotFoundError(preset_name)

        return self.settings.presets[preset_name]

    def list_presets(self) -> dict[str, str]:
        """List all available presets.

        Returns:
            Dict mapping preset names to descriptions
        """
        return {
            name: preset.description
            for name, preset in self.settings.presets.items()
        }

    def preset_exists(self, preset_name: str) -> bool:
        """Check if preset exists.

        Args:
            preset_name: Preset identifier

        Returns:
            True if preset exists, False otherwise
        """
        return preset_name in self.settings.presets
