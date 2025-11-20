"""Request and result models for icon generation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class IconGenerationRequest:
    """Request for generating icons.

    Attributes:
        category: Icon category name (e.g., "battery-icons")
        variant: Variant name (e.g., "solid", "rounded") or None if no variants
        color: Primary color for template rendering (hex format)
        colorscheme_data: Full colorscheme dict for cache hashing
        output_dir: Directory to write generated icon files
        icons: Specific icon names to generate, or None for all icons
        context: Additional template context variables
    """

    category: str
    variant: str | None
    color: str
    colorscheme_data: dict[str, Any]
    output_dir: Path
    icons: list[str] | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate request."""
        if not self.color.startswith("#"):
            raise ValueError(
                f"Color must be in hex format (e.g., '#ffffff'), "
                f"got: {self.color}"
            )
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)


@dataclass
class IconGenerationResult:
    """Result of icon generation.

    Attributes:
        category: Icon category name
        variant: Variant name or None
        generated_icons: Map of icon name to output file path
        from_cache: Whether any icons were loaded from cache
        cache_hits: Number of icons loaded from cache
        cache_misses: Number of icons rendered (not cached)
        total_icons: Total number of icons generated
        errors: Map of icon name to error message for failed icons
    """

    category: str
    variant: str | None
    generated_icons: dict[str, Path]
    from_cache: bool
    cache_hits: int
    cache_misses: int
    total_icons: int = 0
    errors: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Calculate derived fields."""
        if self.total_icons == 0:
            self.total_icons = len(self.generated_icons) + len(self.errors)

    @property
    def success(self) -> bool:
        """Whether all icons generated successfully."""
        return len(self.errors) == 0

    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate as percentage (0-100)."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100

    def summary(self) -> str:
        """Get human-readable summary."""
        parts = [
            f"Generated {len(self.generated_icons)} icons",
            f"for category '{self.category}'",
        ]
        if self.variant:
            parts.append(f"(variant: {self.variant})")

        if self.cache_hits > 0 or self.cache_misses > 0:
            parts.append(
                f"- Cache: {self.cache_hits} hits, "
                f"{self.cache_misses} misses "
                f"({self.cache_hit_rate:.1f}% hit rate)"
            )

        if self.errors:
            parts.append(f"- {len(self.errors)} errors")

        return " ".join(parts)
