"""Dependency injection container for dotfiles manager."""

from dependency_injector import containers, providers
from dotfiles_state_manager import SQLiteBackend, StateManager
from icon_generator import IconRegistry, IconService  # noqa: F401
from wallpaper_orchestrator import WallpaperOrchestrator, load_settings

from dotfiles_manager.config.settings import load_config
from dotfiles_manager.hooks.registry import HookRegistry
from dotfiles_manager.hooks.status_bar_icons_hook import (  # noqa: F401
    StatusBarIconsHook,
)
from dotfiles_manager.hooks.wlogout_hook import WlogoutIconsHook
from dotfiles_manager.repositories.system_attributes import (
    SystemAttributesRepository,
)
from dotfiles_manager.repositories.wallpaper_state import (
    WallpaperStateRepository,
)
from dotfiles_manager.services.svg_template_cache_manager import (
    SVGTemplateCacheManager,
)
from dotfiles_manager.services.wallpaper_service import WallpaperService
from dotfiles_manager.services.wlogout_service import WlogoutService


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    config = providers.Singleton(load_config)

    # System state manager (SQLite backend)
    system_state_backend = providers.Singleton(
        SQLiteBackend,
        db_path=config.provided.manager.state_db_path,
    )

    system_state = providers.Singleton(
        StateManager,
        backend=system_state_backend,
    )

    # Wallpaper orchestrator (with its own cache)
    # Load orchestrator config from its default location
    orchestrator_config = providers.Singleton(load_settings)

    wallpaper_orchestrator = providers.Singleton(
        WallpaperOrchestrator,
        config=orchestrator_config,
    )

    # Repositories
    system_attributes_repo = providers.Singleton(
        SystemAttributesRepository,
        state=system_state,
    )

    wallpaper_state_repo = providers.Singleton(
        WallpaperStateRepository,
        system_state=system_state,
        orchestrator_cache=None,  # Cache manager deprecated
        orchestrator_config=orchestrator_config,
    )

    # SVG template cache
    svg_cache_manager = providers.Singleton(
        SVGTemplateCacheManager,
        state=system_state,
        max_cache_size_mb=config.provided.svg_cache.max_cache_size_mb,
        enable_lru=config.provided.svg_cache.enable_lru,
    )

    # Icon generator
    icon_registry = providers.Singleton(
        IconRegistry,
        base_path=config.provided.paths.status_bar_icons_base_dir,
    )

    icon_service = providers.Singleton(
        IconService,
        registry=icon_registry,
        cache_manager=svg_cache_manager,
    )

    # Wlogout icon registry (separate from status bar icons)
    wlogout_icon_registry = providers.Singleton(
        IconRegistry,
        base_path=config.provided.paths.wlogout_icons_templates_dir,
    )

    wlogout_icon_service = providers.Singleton(
        IconService,
        registry=wlogout_icon_registry,
        cache_manager=svg_cache_manager,
    )

    # Services
    wlogout_service = providers.Singleton(
        WlogoutService,
        icon_registry=wlogout_icon_registry,
        icon_service=wlogout_icon_service,
        style_template_path=config.provided.paths.wlogout_style_template_path,
        icons_output_dir=config.provided.paths.wlogout_icons_output_dir,
        color_key=providers.Callable(
            lambda cfg: cfg.hooks.model_dump()
            .get("wlogout_icons", {})
            .get("colorscheme_color_key", "color15"),
            cfg=config,
        ),
    )

    # Hook registry - convert HooksConfig to dict
    hook_registry = providers.Singleton(
        HookRegistry,
        config=providers.Callable(
            lambda cfg: cfg.model_dump(),
            cfg=config.provided.hooks,
        ),
    )

    # Hooks
    status_bar_icons_hook = providers.Singleton(
        StatusBarIconsHook,
        icon_registry=icon_registry,
        icon_service=icon_service,
        icons_output_dir=config.provided.paths.status_bar_icons_output_dir,
        default_variant=config.provided.manager.icon_variant,
        variant_overrides=config.provided.manager.icon_variant_overrides,
    )

    wlogout_hook = providers.Singleton(
        WlogoutIconsHook,
        wlogout_service=wlogout_service,
        style_output_path=config.provided.paths.wlogout_style_output_path,
    )

    # Wallpaper service
    wallpaper_service = providers.Singleton(
        WallpaperService,
        orchestrator=wallpaper_orchestrator,
        wallpaper_state_repo=wallpaper_state_repo,
        system_attributes_repo=system_attributes_repo,
        hook_registry=hook_registry,
    )

    @classmethod
    def initialize(cls) -> "Container":
        """Initialize container and register hooks.

        Returns:
            Initialized container
        """
        container = cls()

        # Register hooks
        registry: HookRegistry = container.hook_registry()

        status_bar_icons_hook_instance: StatusBarIconsHook = (
            container.status_bar_icons_hook()
        )
        registry.register(status_bar_icons_hook_instance)

        wlogout_hook_instance: WlogoutIconsHook = container.wlogout_hook()
        registry.register(wlogout_hook_instance)

        return container
