"""Configuration models for colorscheme orchestrator."""

from pathlib import Path
from typing import Literal

from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class OrchestratorSettings(BaseModel):
    """Main orchestrator configuration."""

    default_backend: str = Field(
        default="pywal",
        description="Default backend to use if not specified",
    )
    default_output_dir: Path = Field(
        default=Path.home() / ".cache/colorscheme",
        description="Default output directory for generated colorschemes",
    )
    default_formats: list[str] = Field(
        default_factory=lambda: ["json", "css", "yaml", "sh"],
        description="Default output formats",
    )
    default_color_count: int = Field(
        default=16,
        description="Default number of colors to extract",
    )
    container_runtime: Literal["docker", "podman"] = Field(
        default="docker",
        description="Container runtime to use",
    )
    container_prefix: str = Field(
        default="colorscheme",
        description="Prefix for container names",
    )
    auto_cleanup: bool = Field(
        default=True,
        description="Automatically cleanup containers after execution",
    )
    keep_images: bool = Field(
        default=True,
        description="Keep container images after building",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose logging",
    )


class BackendImageSettings(BaseModel):
    """Container image settings for a backend."""

    image_name: str = Field(
        description="Container image name",
    )
    image_tag: str = Field(
        default="latest",
        description="Container image tag",
    )


class PywalBackendSettings(BackendImageSettings):
    """Pywal backend settings."""

    use_library: bool = Field(
        default=True,
        description="Use pywal as Python library instead of CLI",
    )


class WallustBackendSettings(BackendImageSettings):
    """Wallust backend settings."""

    output_format: str = Field(
        default="json",
        description="Wallust output format",
    )
    backend_type: str = Field(
        default="resized",
        description="Wallust backend type",
    )


class CustomBackendSettings(BackendImageSettings):
    """Custom backend settings."""

    algorithm: str = Field(
        default="kmeans",
        description="Color extraction algorithm",
    )
    n_clusters: int = Field(
        default=16,
        description="Number of color clusters",
    )


class BackendSettings(BaseModel):
    """Backend-specific settings."""

    pywal: PywalBackendSettings
    wallust: WallustBackendSettings
    custom: CustomBackendSettings


class OrchestratorConfig(BaseModel):
    """Complete orchestrator configuration."""

    orchestrator: OrchestratorSettings
    backends: BackendSettings


def load_settings() -> OrchestratorConfig:
    """Load settings from settings.toml.

    Returns:
        OrchestratorConfig: Loaded configuration
    """
    # Get the directory where this file is located
    config_dir = Path(__file__).parent

    # Load settings using Dynaconf
    settings = Dynaconf(
        settings_files=[str(config_dir / "settings.toml")],
        environments=False,
        load_dotenv=False,
    )

    # Convert to Pydantic models
    orchestrator_settings = OrchestratorSettings(
        default_backend=settings.orchestrator.default_backend,
        default_output_dir=Path(settings.orchestrator.default_output_dir).expanduser(),
        default_formats=settings.orchestrator.default_formats,
        default_color_count=settings.orchestrator.default_color_count,
        container_runtime=settings.orchestrator.container_runtime,
        container_prefix=settings.orchestrator.container_prefix,
        auto_cleanup=settings.orchestrator.auto_cleanup,
        keep_images=settings.orchestrator.keep_images,
        log_level=settings.orchestrator.log_level,
        verbose=settings.orchestrator.verbose,
    )

    backend_settings = BackendSettings(
        pywal=PywalBackendSettings(
            image_name=settings.backends.pywal.image_name,
            image_tag=settings.backends.pywal.image_tag,
            use_library=settings.backends.pywal.use_library,
        ),
        wallust=WallustBackendSettings(
            image_name=settings.backends.wallust.image_name,
            image_tag=settings.backends.wallust.image_tag,
            output_format=settings.backends.wallust.output_format,
            backend_type=settings.backends.wallust.backend_type,
        ),
        custom=CustomBackendSettings(
            image_name=settings.backends.custom.image_name,
            image_tag=settings.backends.custom.image_tag,
            algorithm=settings.backends.custom.algorithm,
            n_clusters=settings.backends.custom.n_clusters,
        ),
    )

    return OrchestratorConfig(
        orchestrator=orchestrator_settings,
        backends=backend_settings,
    )

