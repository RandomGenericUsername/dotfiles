"""Result types for wallpaper orchestrator."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class WallpaperResult:
    """Result metadata from wallpaper orchestration.

    Contains all paths and metadata from the complete wallpaper setup process:
    - Original wallpaper path
    - Generated effect variants
    - Generated color scheme files
    - Wallpaper set status

    Example:
        >>> result = orchestrator.process(Path("wallpaper.png"))
        >>> print(f"Original: {result.original_wallpaper}")
        >>> print(f"Effects: {len(result.effect_variants)} variants")
        >>> print(f"Color schemes: {list(result.colorscheme_files.keys())}")
        >>> print(f"Set: {result.wallpaper_set}")
    """

    # Original wallpaper
    original_wallpaper: Path = field(
        metadata={"description": "Path to original wallpaper"}
    )

    # Output directories
    effects_output_dir: Path = field(
        metadata={"description": "Directory containing effect variants"}
    )
    colorscheme_output_dir: Path = field(
        metadata={"description": "Directory containing color scheme files"}
    )

    # Generated files
    effect_variants: dict[str, Path] = field(
        default_factory=dict,
        metadata={"description": "Mapping of effect name to output file path"},
    )
    colorscheme_files: dict[str, Path] = field(
        default_factory=dict,
        metadata={"description": "Mapping of format to output file path"},
    )

    # Wallpaper set status
    wallpaper_set: bool = field(
        default=False,
        metadata={"description": "Whether wallpaper was successfully set"},
    )
    monitor_set: str | None = field(
        default=None,
        metadata={"description": "Monitor name where wallpaper was set"},
    )

    # Metadata
    timestamp: datetime = field(
        default_factory=datetime.now,
        metadata={"description": "When the orchestration completed"},
    )
    success: bool = field(
        default=True, metadata={"description": "Overall success status"}
    )
    errors: list[str] = field(
        default_factory=list,
        metadata={"description": "List of error messages if any"},
    )

    def __deepcopy__(self, memo):
        """Return self for deep copy (result should not be copied).

        The result object is shared across parallel pipeline steps and should
        not be deep copied to preserve modifications made by each step.
        """
        return self

    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [
            "Wallpaper Orchestration Result",
            "=" * 60,
            f"Original Wallpaper: {self.original_wallpaper}",
            f"Effects Output Dir: {self.effects_output_dir}",
            f"Colorscheme Output Dir: {self.colorscheme_output_dir}",
            "",
            f"Effect Variants ({len(self.effect_variants)}):",
        ]

        for effect_name, path in sorted(self.effect_variants.items()):
            lines.append(f"  • {effect_name}: {path}")

        lines.extend(
            [
                "",
                f"Colorscheme Files ({len(self.colorscheme_files)}):",
            ]
        )

        for fmt, path in sorted(self.colorscheme_files.items()):
            lines.append(f"  • {fmt}: {path}")

        lines.extend(
            [
                "",
                f"Wallpaper Set: {self.wallpaper_set}",
                f"Monitor: {self.monitor_set or 'all'}",
                f"Success: {self.success}",
                f"Timestamp: {self.timestamp.isoformat()}",
            ]
        )

        if self.errors:
            lines.extend(["", "Errors:"])
            for error in self.errors:
                lines.append(f"  • {error}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "original_wallpaper": str(self.original_wallpaper),
            "effects_output_dir": str(self.effects_output_dir),
            "colorscheme_output_dir": str(self.colorscheme_output_dir),
            "effect_variants": {
                name: str(path) for name, path in self.effect_variants.items()
            },
            "colorscheme_files": {
                fmt: str(path) for fmt, path in self.colorscheme_files.items()
            },
            "wallpaper_set": self.wallpaper_set,
            "monitor_set": self.monitor_set,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "errors": self.errors,
        }
