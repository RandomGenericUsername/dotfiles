"""Custom exceptions for icon generator."""


class IconGeneratorError(Exception):
    """Base exception for icon generator errors."""


class IconCategoryNotFoundError(IconGeneratorError):
    """Raised when requested icon category is not found."""

    def __init__(self, category: str, available: list[str]) -> None:
        """Initialize exception.

        Args:
            category: The category that was not found
            available: List of available categories
        """
        self.category = category
        self.available = available
        super().__init__(
            f"Icon category '{category}' not found. "
            f"Available categories: {', '.join(available)}"
        )


class IconVariantNotFoundError(IconGeneratorError):
    """Raised when requested icon variant is not found."""

    def __init__(
        self, category: str, variant: str, available: list[str]
    ) -> None:
        """Initialize exception.

        Args:
            category: The category name
            variant: The variant that was not found
            available: List of available variants for this category
        """
        self.category = category
        self.variant = variant
        self.available = available
        super().__init__(
            f"Icon variant '{variant}' not found in category '{category}'. "
            f"Available variants: {', '.join(available)}"
        )


class IconGenerationError(IconGeneratorError):
    """Raised when icon generation fails."""

    def __init__(self, message: str, category: str, icon: str) -> None:
        """Initialize exception.

        Args:
            message: Error message
            category: The category being generated
            icon: The icon that failed to generate
        """
        self.category = category
        self.icon = icon
        super().__init__(
            f"Failed to generate icon '{icon}' in category '{category}': "
            f"{message}"
        )
