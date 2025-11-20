"""Icon registry for dynamic category and variant discovery."""

import logging
from pathlib import Path

from icon_generator.exceptions import (
    IconCategoryNotFoundError,
    IconVariantNotFoundError,
)
from icon_generator.models.icon_metadata import IconCategory

logger = logging.getLogger(__name__)


class IconRegistry:
    """Registry for discovering and managing icon categories and variants.

    The registry scans a base directory to discover icon categories and their
    variants. It supports two structures:

    1. Categories with variants:
       base_path/
         category-name/
           variant1/
             icon1.svg
             icon2.svg
           variant2/
             icon1.svg

    2. Categories without variants (flat):
       base_path/
         category-name/
           icon1.svg
           icon2.svg

    The registry automatically detects which structure is used based on the
    presence of subdirectories containing SVG files.
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize registry and discover categories.

        Args:
            base_path: Base directory containing icon categories
        """
        self._base_path = Path(base_path)
        self._categories: dict[str, IconCategory] = {}

        if not self._base_path.exists():
            logger.warning(
                f"Icon base path does not exist: {self._base_path}"
            )
        else:
            self._discover_categories()

    def _discover_categories(self) -> None:
        """Discover all icon categories from filesystem."""
        logger.debug(f"Discovering icon categories in: {self._base_path}")

        for category_dir in self._base_path.iterdir():
            if not category_dir.is_dir():
                continue

            category_name = category_dir.name
            logger.debug(f"  Examining category: {category_name}")

            # Check if this category has variants or is flat
            has_variants, variants, icons = self._analyze_category(
                category_dir
            )

            if not has_variants and not icons:
                logger.debug(
                    f"    Skipping '{category_name}' - no icons found"
                )
                continue

            icon_count = (
                sum(
                    len(list(v.glob("*.svg"))) for v in variants.values()
                )
                if has_variants
                else len(icons)
            )

            category = IconCategory(
                name=category_name,
                base_path=category_dir,
                has_variants=has_variants,
                variants=variants,
                icons=icons,
                icon_count=icon_count,
            )

            self._categories[category_name] = category

            if has_variants:
                logger.debug(
                    f"    Registered category with {len(variants)} "
                    f"variants: {', '.join(variants.keys())}"
                )
            else:
                logger.debug(
                    f"    Registered flat category with {len(icons)} icons"
                )

        logger.info(
            f"Discovered {len(self._categories)} icon categories: "
            f"{', '.join(self._categories.keys())}"
        )

    def _analyze_category(
        self, category_dir: Path
    ) -> tuple[bool, dict[str, Path], dict[str, Path]]:
        """Analyze category structure to determine if it has variants.

        Args:
            category_dir: Path to category directory

        Returns:
            Tuple of (has_variants, variants_dict, icons_dict)
        """
        # Check for SVG files directly in category directory
        direct_svgs = list(category_dir.glob("*.svg"))

        # Check for subdirectories containing SVG files
        variant_dirs = {}
        for subdir in category_dir.iterdir():
            if not subdir.is_dir():
                continue
            svg_files = list(subdir.glob("*.svg"))
            if svg_files:
                variant_dirs[subdir.name] = subdir

        # Determine structure
        if variant_dirs and not direct_svgs:
            # Has variants (subdirectories with SVGs, no direct SVGs)
            return True, variant_dirs, {}
        elif direct_svgs and not variant_dirs:
            # Flat structure (direct SVGs, no variant subdirectories)
            icons = {svg.stem: svg for svg in direct_svgs}
            return False, {}, icons
        elif direct_svgs and variant_dirs:
            # Mixed structure - treat as flat and warn
            logger.warning(
                f"Category '{category_dir.name}' has both direct SVG files "
                f"and variant subdirectories. Treating as flat structure."
            )
            icons = {svg.stem: svg for svg in direct_svgs}
            return False, {}, icons
        else:
            # Empty category
            return False, {}, {}

    def get_category(self, name: str) -> IconCategory:
        """Get category by name.

        Args:
            name: Category name

        Returns:
            IconCategory instance

        Raises:
            IconCategoryNotFoundError: If category not found
        """
        if name not in self._categories:
            raise IconCategoryNotFoundError(
                name, list(self._categories.keys())
            )
        return self._categories[name]

    def list_categories(self) -> list[str]:
        """Get list of all category names.

        Returns:
            List of category names
        """
        return list(self._categories.keys())

    def get_variants(self, category: str) -> list[str]:
        """Get list of variants for a category.

        Args:
            category: Category name

        Returns:
            List of variant names, or empty list if category has no variants

        Raises:
            IconCategoryNotFoundError: If category not found
        """
        cat = self.get_category(category)
        return cat.list_variants()
