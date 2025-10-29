"""Custom backend for color scheme generation.

This backend uses PIL/Pillow and various algorithms (K-means, median cut, octree)
to extract colors from images. Pure Python implementation with no external dependencies.
"""

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.config.enums import ColorAlgorithm
from colorscheme_generator.core.base import ColorSchemeGenerator
from colorscheme_generator.core.exceptions import (
    ColorExtractionError,
    InvalidImageError,
)
from colorscheme_generator.core.types import Color, ColorScheme, GeneratorConfig


class CustomGenerator(ColorSchemeGenerator):
    """Custom backend for color extraction using PIL.
    
    Uses various algorithms to extract colors:
    - K-means clustering
    - Median cut
    - Octree quantization
    
    Attributes:
        settings: Application configuration
        algorithm: Color extraction algorithm to use
        n_clusters: Number of color clusters
    """

    def __init__(self, settings: AppConfig):
        """Initialize CustomGenerator.
        
        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.algorithm = ColorAlgorithm(settings.backends.custom.algorithm)
        self.n_clusters = settings.backends.custom.n_clusters

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "custom"

    def is_available(self) -> bool:
        """Check if custom backend is available.
        
        Returns:
            Always True (PIL is a required dependency)
        """
        return True

    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        """Generate color scheme using custom algorithm.
        
        Args:
            image_path: Path to source image
            config: Runtime configuration
            
        Returns:
            ColorScheme object with extracted colors
            
        Raises:
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
        """
        # Validate image
        image_path = image_path.expanduser().resolve()
        if not image_path.exists():
            raise InvalidImageError(image_path, "File does not exist")
        if not image_path.is_file():
            raise InvalidImageError(image_path, "Not a file")

        # Load image
        try:
            img = Image.open(image_path)
            img = img.convert("RGB")
        except Exception as e:
            raise InvalidImageError(image_path, f"Failed to load image: {e}") from e

        # Get algorithm from config or use default
        algorithm = config.backend_options.get("algorithm", self.algorithm.value)
        n_clusters = config.backend_options.get("n_clusters", self.n_clusters)

        # Extract colors using selected algorithm
        try:
            if algorithm == ColorAlgorithm.KMEANS.value:
                colors = self._extract_kmeans(img, n_clusters)
            elif algorithm == ColorAlgorithm.MEDIAN_CUT.value:
                colors = self._extract_median_cut(img, n_clusters)
            elif algorithm == ColorAlgorithm.OCTREE.value:
                colors = self._extract_octree(img, n_clusters)
            else:
                raise ColorExtractionError(
                    f"Unknown algorithm: {algorithm}",
                    backend=self.backend_name,
                    image_path=image_path,
                )
        except Exception as e:
            raise ColorExtractionError(
                f"Color extraction failed: {e}",
                backend=self.backend_name,
                image_path=image_path,
            ) from e

        # Convert to ColorScheme
        return self._create_color_scheme(colors, image_path)

    def _extract_kmeans(self, img: Image.Image, n_clusters: int) -> list[tuple[int, int, int]]:
        """Extract colors using K-means clustering.
        
        Args:
            img: PIL Image
            n_clusters: Number of clusters
            
        Returns:
            List of RGB tuples
        """
        # Resize for performance
        img = img.resize((150, 150))
        
        # Convert to numpy array
        pixels = np.array(img).reshape(-1, 3)
        
        # Run K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get cluster centers as colors
        colors = kmeans.cluster_centers_.astype(int)
        
        # Sort by brightness (darkest first)
        colors = sorted(colors, key=lambda c: sum(c))
        
        return [tuple(c) for c in colors]

    def _extract_median_cut(self, img: Image.Image, n_colors: int) -> list[tuple[int, int, int]]:
        """Extract colors using median cut algorithm.
        
        Args:
            img: PIL Image
            n_colors: Number of colors
            
        Returns:
            List of RGB tuples
        """
        # Use PIL's quantize method (implements median cut)
        img = img.quantize(colors=n_colors, method=2)  # method=2 is median cut
        palette = img.getpalette()
        
        # Extract RGB colors from palette
        colors = []
        for i in range(n_colors):
            r = palette[i * 3]
            g = palette[i * 3 + 1]
            b = palette[i * 3 + 2]
            colors.append((r, g, b))
        
        # Sort by brightness
        colors = sorted(colors, key=lambda c: sum(c))
        
        return colors

    def _extract_octree(self, img: Image.Image, n_colors: int) -> list[tuple[int, int, int]]:
        """Extract colors using octree quantization.
        
        Args:
            img: PIL Image
            n_colors: Number of colors
            
        Returns:
            List of RGB tuples
        """
        # Use PIL's quantize method (octree is default)
        img = img.quantize(colors=n_colors, method=0)  # method=0 is octree
        palette = img.getpalette()
        
        # Extract RGB colors from palette
        colors = []
        for i in range(n_colors):
            r = palette[i * 3]
            g = palette[i * 3 + 1]
            b = palette[i * 3 + 2]
            colors.append((r, g, b))
        
        # Sort by brightness
        colors = sorted(colors, key=lambda c: sum(c))
        
        return colors

    def _create_color_scheme(
        self, colors: list[tuple[int, int, int]], image_path: Path
    ) -> ColorScheme:
        """Create ColorScheme from extracted colors.
        
        Args:
            colors: List of RGB tuples
            image_path: Source image path
            
        Returns:
            ColorScheme object
        """
        # Ensure we have at least 16 colors
        while len(colors) < 16:
            colors.append((0, 0, 0))
        
        # Take first 16 colors
        colors = colors[:16]
        
        # Convert to Color objects
        color_objects = [
            Color(hex=self._rgb_to_hex(r, g, b), rgb=(r, g, b))
            for r, g, b in colors
        ]
        
        # Assign special colors
        # Background: darkest color
        background = color_objects[0]
        
        # Foreground: brightest color
        foreground = color_objects[-1]
        
        # Cursor: a bright accent color (use color 1 or 9)
        cursor = color_objects[9] if len(color_objects) > 9 else foreground
        
        return ColorScheme(
            background=background,
            foreground=foreground,
            cursor=cursor,
            colors=color_objects,
            source_image=str(image_path),
            backend=self.backend_name,
        )

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB to hex color string.
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            
        Returns:
            Hex color string (e.g., "#1a1a1a")
        """
        return f"#{r:02x}{g:02x}{b:02x}"

