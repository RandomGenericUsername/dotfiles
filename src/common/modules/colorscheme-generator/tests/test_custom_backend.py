"""Tests for CustomGenerator backend."""

from pathlib import Path

import pytest

from colorscheme_generator.backends.custom import CustomGenerator
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.types import GeneratorConfig


@pytest.fixture
def settings():
    """Get settings for tests."""
    return Settings.get()


@pytest.fixture
def generator(settings):
    """Create CustomGenerator instance."""
    return CustomGenerator(settings)


def test_backend_name(generator):
    """Test backend name."""
    assert generator.backend_name == "custom"


def test_is_available(generator):
    """Test custom backend is always available."""
    assert generator.is_available() is True


def test_generate_requires_valid_image(generator, settings):
    """Test that generate requires a valid image."""
    from colorscheme_generator.core.exceptions import InvalidImageError

    config = GeneratorConfig.from_settings(settings)
    invalid_path = Path("/nonexistent/image.png")

    with pytest.raises(InvalidImageError):
        generator.generate(invalid_path, config)
