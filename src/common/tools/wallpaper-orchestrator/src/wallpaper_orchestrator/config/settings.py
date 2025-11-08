"""Configuration settings for wallpaper orchestrator."""

from pathlib import Path
from typing import Literal

from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class OrchestratorSettings(BaseModel):
    """Main orchestrator configuration."""

    effects_output_dir: Path = Field(
        default=Path.home() / ".cache/wallpaper/effects",
        description="Output directory for effect variants",
    )
    colorscheme_output_dir: Path = Field(
        default=Path.home() / ".cache/colorscheme",
        description="Output directory for color scheme files",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose output",
    )


class ColorSchemeSettings(BaseModel):
    """Color scheme generation settings."""

    backend: str = Field(
        default="pywal",
        description="Color scheme backend (pywal, wallust, custom)",
    )
    formats: list[str] = Field(
        default_factory=lambda: ["json", "css", "yaml", "sh"],
        description="Output formats for color schemes",
    )
    color_count: int = Field(
        default=16,
        description="Number of colors to extract",
    )
    container_runtime: Literal["docker", "podman"] = Field(
        default="docker",
        description="Container runtime for colorscheme generation",
    )
    container_prefix: str = Field(
        default="colorscheme",
        description="Prefix for container names",
    )
    auto_cleanup: bool = Field(
        default=True,
        description="Automatically cleanup containers after use",
    )


class WallpaperEffectsSettings(BaseModel):
    """Wallpaper effects processing settings."""

    container_runtime: Literal["docker", "podman"] = Field(
        default="docker",
        description="Container runtime",
    )
    image_name: str = Field(
        default="wallpaper-effects-processor",
        description="Container image name",
    )
    image_tag: str = Field(
        default="latest",
        description="Container image tag",
    )
    processing_mode: Literal["memory", "file"] = Field(
        default="memory",
        description="Processing mode",
    )
    output_format: str = Field(
        default="png",
        description="Output format for processed images",
    )
    quality: int = Field(
        default=95,
        description="Quality for lossy formats (1-100)",
        ge=1,
        le=100,
    )


class HyprpaperSettings(BaseModel):
    """Hyprpaper wallpaper manager settings."""

    monitor: str = Field(
        default="all",
        description="Monitor to set wallpaper on (all, focused, or monitor name)",
    )
    mode: Literal["cover", "contain", "tile"] = Field(
        default="cover",
        description="Wallpaper display mode",
    )
    autostart: bool = Field(
        default=True,
        description="Automatically start hyprpaper if not running",
    )
    max_preload_pool_mb: int = Field(
        default=100,
        description="Maximum memory (MB) for preloaded wallpapers pool",
        gt=0,
    )
    max_wallpaper_size_multiplier: float = Field(
        default=2.0,
        description="Max single wallpaper size = pool_size * multiplier",
        gt=0,
    )
    ipc_timeout: int = Field(
        default=5,
        description="IPC command timeout in seconds",
        gt=0,
    )
    ipc_retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for IPC failures",
        ge=1,
    )
    ipc_retry_delay: float = Field(
        default=0.5,
        description="Delay between retries in seconds",
        gt=0,
    )
    ipc_startup_wait: float = Field(
        default=2.0,
        description="Maximum time to wait for hyprpaper socket on startup",
        gt=0,
    )


class PipelineSettings(BaseModel):
    """Pipeline execution settings."""

    fail_fast: bool = Field(
        default=True,
        description="Stop pipeline on first failure",
    )
    parallel_enabled: bool = Field(
        default=False,
        description="Enable parallel execution (currently not used)",
    )


class AppConfig(BaseModel):
    """Complete application configuration."""

    orchestrator: OrchestratorSettings
    colorscheme: ColorSchemeSettings
    wallpaper_effects: WallpaperEffectsSettings
    hyprpaper: HyprpaperSettings
    pipeline: PipelineSettings


def load_settings() -> AppConfig:
    """Load settings from settings.toml.

    Returns:
        AppConfig: Loaded configuration
    """
    # Get the directory where this file is located
    config_dir = Path(__file__).parent.parent.parent.parent / "config"

    # Load settings using Dynaconf
    settings = Dynaconf(
        settings_files=[str(config_dir / "settings.toml")],
        environments=False,
        load_dotenv=False,
    )

    # Convert to Pydantic models
    orchestrator_settings = OrchestratorSettings(
        effects_output_dir=Path(
            settings.orchestrator.effects_output_dir
        ).expanduser(),
        colorscheme_output_dir=Path(
            settings.orchestrator.colorscheme_output_dir
        ).expanduser(),
        log_level=settings.orchestrator.log_level,
        verbose=settings.orchestrator.verbose,
    )

    colorscheme_settings = ColorSchemeSettings(
        backend=settings.colorscheme.backend,
        formats=settings.colorscheme.formats,
        color_count=settings.colorscheme.color_count,
        container_runtime=settings.colorscheme.container_runtime,
        container_prefix=settings.colorscheme.container_prefix,
        auto_cleanup=settings.colorscheme.auto_cleanup,
    )

    wallpaper_effects_settings = WallpaperEffectsSettings(
        container_runtime=settings.wallpaper_effects.container_runtime,
        image_name=settings.wallpaper_effects.image_name,
        image_tag=settings.wallpaper_effects.image_tag,
        processing_mode=settings.wallpaper_effects.processing_mode,
        output_format=settings.wallpaper_effects.output_format,
        quality=settings.wallpaper_effects.quality,
    )

    hyprpaper_settings = HyprpaperSettings(
        monitor=settings.hyprpaper.monitor,
        mode=settings.hyprpaper.mode,
        autostart=settings.hyprpaper.autostart,
        max_preload_pool_mb=settings.hyprpaper.max_preload_pool_mb,
        max_wallpaper_size_multiplier=settings.hyprpaper.max_wallpaper_size_multiplier,
        ipc_timeout=settings.hyprpaper.ipc_timeout,
        ipc_retry_attempts=settings.hyprpaper.ipc_retry_attempts,
        ipc_retry_delay=settings.hyprpaper.ipc_retry_delay,
        ipc_startup_wait=settings.hyprpaper.ipc_startup_wait,
    )

    pipeline_settings = PipelineSettings(
        fail_fast=settings.pipeline.fail_fast,
        parallel_enabled=settings.pipeline.parallel_enabled,
    )

    return AppConfig(
        orchestrator=orchestrator_settings,
        colorscheme=colorscheme_settings,
        wallpaper_effects=wallpaper_effects_settings,
        hyprpaper=hyprpaper_settings,
        pipeline=pipeline_settings,
    )
