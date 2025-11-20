"""Icon Generator - Dynamic icon generation with variant support and caching.

This module provides a flexible system for generating icons from SVG templates
with support for:
- Dynamic category and variant discovery
- SVG template caching for performance
- Full colorscheme-aware generation
- Clean API for integration

Main components:
- IconRegistry: Discovers icon categories and variants from filesystem
- IconService: Generates icons with template rendering and caching
- Models: Data structures for requests, results, and metadata
"""

from icon_generator.core.registry import IconRegistry
from icon_generator.core.service import IconService
from icon_generator.exceptions import (
    IconCategoryNotFoundError,
    IconGenerationError,
    IconVariantNotFoundError,
)
from icon_generator.models.icon_metadata import IconCategory
from icon_generator.models.requests import (
    IconGenerationRequest,
    IconGenerationResult,
)

__version__ = "0.1.0"

__all__ = [
    "IconRegistry",
    "IconService",
    "IconCategory",
    "IconGenerationRequest",
    "IconGenerationResult",
    "IconCategoryNotFoundError",
    "IconVariantNotFoundError",
    "IconGenerationError",
]
