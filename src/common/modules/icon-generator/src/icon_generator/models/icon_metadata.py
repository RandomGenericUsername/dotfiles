"""Icon metadata models."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IconCategory:
    """Metadata for an icon category.

    An icon category represents a collection of related icons (e.g., battery-icons,
    network-icons). Categories can have variants (different visual styles) or be
    flat (no variants).

    Attributes:
        name: Category name (e.g., "battery-icons")
        base_path: Path to category directory
        has_variants: Whether this category has variant subdirectories
        variants: Map of variant name to variant directory path (if has_variants)
        icons: Map of icon name to icon file path (if no variants)
        icon_count: Total number of icons in this category
    """

    name: str
    base_path: Path
    has_variants: bool
    variants: dict[str, Path] = field(default_factory=dict)
    icons: dict[str, Path] = field(default_factory=dict)
    icon_count: int = 0

    def __post_init__(self) -> None:
        """Validate category metadata."""
        if self.has_variants and not self.variants:
            raise ValueError(
                f"Category '{self.name}' marked as having variants "
                f"but no variants provided"
            )
        if not self.has_variants and not self.icons:
            raise ValueError(
                f"Category '{self.name}' has no variants and no icons"
            )

    def get_variant_path(self, variant: str) -> Path:
        """Get path for a specific variant.

        Args:
            variant: Variant name

        Returns:
            Path to variant directory

        Raises:
            KeyError: If variant not found
        """
        if not self.has_variants:
            raise ValueError(
                f"Category '{self.name}' does not have variants"
            )
        return self.variants[variant]

    def list_variants(self) -> list[str]:
        """Get list of available variant names.

        Returns:
            List of variant names, or empty list if no variants
        """
        return list(self.variants.keys()) if self.has_variants else []

    def list_icons(self, variant: str | None = None) -> list[str]:
        """Get list of icon names.

        Args:
            variant: Variant name (required if category has variants)

        Returns:
            List of icon names (without .svg extension)

        Raises:
            ValueError: If variant required but not provided
            KeyError: If variant not found
        """
        if self.has_variants:
            if variant is None:
                raise ValueError(
                    f"Category '{self.name}' has variants, "
                    f"variant must be specified"
                )
            variant_path = self.get_variant_path(variant)
            return [
                f.stem for f in variant_path.glob("*.svg") if f.is_file()
            ]
        return list(self.icons.keys())

    def get_icon_path(
        self, icon_name: str, variant: str | None = None
    ) -> Path:
        """Get path to a specific icon file.

        Args:
            icon_name: Icon name (without .svg extension)
            variant: Variant name (required if category has variants)

        Returns:
            Path to icon SVG file

        Raises:
            ValueError: If variant required but not provided
            KeyError: If variant or icon not found
        """
        if self.has_variants:
            if variant is None:
                raise ValueError(
                    f"Category '{self.name}' has variants, "
                    f"variant must be specified"
                )
            variant_path = self.get_variant_path(variant)
            return variant_path / f"{icon_name}.svg"
        return self.icons[icon_name]
