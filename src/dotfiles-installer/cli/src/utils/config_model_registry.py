"""Registry of Pydantic config models for installed components.

Maps component names to their configuration model classes for validation.
This allows install_component() to automatically validate settings overrides.
"""

from typing import Literal

from pydantic import BaseModel

ComponentType = Literal["module", "tool"]


class ConfigModelRegistry:
    """Registry for component configuration models.

    This registry maps component names to their Pydantic config models,
    enabling automatic validation when applying settings overrides.

    Example:
        >>> # Register a module
        >>> ConfigModelRegistry.register_module("hyprpaper-manager", HyprpaperConfig)
        >>>
        >>> # Get the model later
        >>> model = ConfigModelRegistry.get_model("hyprpaper-manager", "module")
        >>> # Use it for validation
        >>> model(**settings_dict)
    """

    _MODULE_MODELS: dict[str, type[BaseModel]] = {}
    _TOOL_MODELS: dict[str, type[BaseModel]] = {}

    @classmethod
    def register_module(cls, name: str, model: type[BaseModel]) -> None:
        """Register a module's config model.

        Args:
            name: Module name (e.g., "hyprpaper-manager")
            model: Pydantic model class (e.g., AppConfig)
        """
        cls._MODULE_MODELS[name] = model

    @classmethod
    def register_tool(cls, name: str, model: type[BaseModel]) -> None:
        """Register a tool's config model.

        Args:
            name: Tool name (e.g., "colorscheme-orchestrator")
            model: Pydantic model class (e.g., OrchestratorConfig)
        """
        cls._TOOL_MODELS[name] = model

    @classmethod
    def get_model(
        cls,
        name: str,
        component: ComponentType,
    ) -> type[BaseModel] | None:
        """Get config model for a component.

        Args:
            name: Component name
            component: Component type ("module" or "tool")

        Returns:
            Pydantic model class or None if not registered
        """
        if component == "module":
            return cls._MODULE_MODELS.get(name)
        else:
            return cls._TOOL_MODELS.get(name)

    @classmethod
    def is_registered(cls, name: str, component: ComponentType) -> bool:
        """Check if a component has a registered model.

        Args:
            name: Component name
            component: Component type

        Returns:
            True if registered, False otherwise
        """
        return cls.get_model(name, component) is not None


# ============================================================================
# Auto-register known modules
# ============================================================================


def _register_known_modules():
    """Register all known module config models.

    This function attempts to import and register config models for all
    known modules. Import failures are silently ignored (module not installed).
    """

    # Hyprpaper Manager
    try:
        from hyprpaper_manager.config.config import (
            AppConfig as HyprpaperConfig,
        )

        ConfigModelRegistry.register_module(
            "hyprpaper-manager", HyprpaperConfig
        )
    except ImportError:
        pass

    # Colorscheme Generator
    try:
        from colorscheme_generator.config import AppConfig as ColorschemeConfig

        ConfigModelRegistry.register_module(
            "colorscheme-generator", ColorschemeConfig
        )
    except ImportError:
        pass

    # Wallpaper Effects Processor
    try:
        from wallpaper_processor.config.config import (
            AppConfig as WallpaperConfig,
        )

        ConfigModelRegistry.register_module(
            "wallpaper-effects-processor", WallpaperConfig
        )
    except ImportError:
        pass

    # Logging
    try:
        from dotfiles_logging.core import LogConfig

        ConfigModelRegistry.register_module("logging", LogConfig)
    except ImportError:
        pass

    # Pipeline
    try:
        from dotfiles_pipeline.core import PipelineConfig

        ConfigModelRegistry.register_module("pipeline", PipelineConfig)
    except ImportError:
        pass


def _register_known_tools():
    """Register all known tool config models.

    This function attempts to import and register config models for all
    known tools. Import failures are silently ignored (tool not installed).
    """

    # Colorscheme Orchestrator
    try:
        from colorscheme_orchestrator.config.settings import (
            OrchestratorConfig,
        )

        ConfigModelRegistry.register_tool(
            "colorscheme-orchestrator", OrchestratorConfig
        )
    except ImportError:
        pass

    # Wallpaper Effects Orchestrator
    try:
        from wallpaper_orchestrator.config import (
            OrchestratorConfig as WallpaperOrchestratorConfig,
        )

        ConfigModelRegistry.register_tool(
            "wallpaper-effects-orchestrator", WallpaperOrchestratorConfig
        )
    except ImportError:
        pass


# Initialize registry on module import
_register_known_modules()
_register_known_tools()
