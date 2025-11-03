"""Abstract base class for wallpaper effects."""

from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image
from wallpaper_processor.core.exceptions import EffectNotAvailableError
from wallpaper_processor.core.types import EffectParams


class WallpaperEffect(ABC):
    """Abstract base class for wallpaper effects.

    All effect implementations must inherit from this class and implement
    the abstract methods.
    """

    @abstractmethod
    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply effect to PIL Image.

        Args:
            image: PIL Image object to process
            params: Effect parameters (Pydantic model)

        Returns:
            Modified PIL Image object

        Raises:
            ProcessingError: If effect application fails
        """
        pass

    def apply_to_file(
        self, input_path: Path, output_path: Path, params: EffectParams
    ) -> Path:
        """Apply effect to image file.

        This is a convenience method that loads an image from a file,
        applies the effect, and saves the result.

        Args:
            input_path: Path to input image file
            output_path: Path to output image file
            params: Effect parameters

        Returns:
            Path to output file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ProcessingError: If effect application fails
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        image = Image.open(input_path)
        result = self.apply(image, params)
        result.save(output_path)
        return output_path

    @abstractmethod
    def is_available(self) -> bool:
        """Check if effect dependencies are available.

        Returns:
            True if effect can be used, False otherwise
        """
        pass

    @property
    @abstractmethod
    def effect_name(self) -> str:
        """Get effect identifier.

        Returns:
            Effect name (e.g., "blur", "brightness")
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Get backend identifier.

        Returns:
            Backend name (e.g., "imagemagick", "pil")
        """
        pass

    @abstractmethod
    def get_default_params(self) -> EffectParams:
        """Get default parameters for this effect.

        Returns:
            EffectParams instance with default values
        """
        pass

    def ensure_available(self) -> None:
        """Ensure effect is available, raise if not.

        Raises:
            EffectNotAvailableError: If effect dependencies are not available
        """
        if not self.is_available():
            msg = (
                f"{self.effect_name} ({self.backend_name}) "
                "dependencies not available"
            )
            raise EffectNotAvailableError(self.effect_name, msg)
