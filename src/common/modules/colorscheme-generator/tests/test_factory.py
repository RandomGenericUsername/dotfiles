"""Tests for ColorSchemeGeneratorFactory."""

import pytest

from colorscheme_generator.backends import (
    CustomGenerator,
    PywalGenerator,
    WallustGenerator,
)
from colorscheme_generator.config.enums import Backend
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.factory import ColorSchemeGeneratorFactory


@pytest.fixture
def settings():
    """Get settings for tests."""
    return Settings.get()


def test_create_pywal(settings):
    """Test creating pywal backend."""
    generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
    assert isinstance(generator, PywalGenerator)
    assert generator.backend_name == "pywal"


def test_create_wallust(settings):
    """Test creating wallust backend."""
    generator = ColorSchemeGeneratorFactory.create(Backend.WALLUST, settings)
    assert isinstance(generator, WallustGenerator)
    assert generator.backend_name == "wallust"


def test_create_custom(settings):
    """Test creating custom backend."""
    generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
    assert isinstance(generator, CustomGenerator)
    assert generator.backend_name == "custom"


def test_create_auto(settings):
    """Test auto-detecting backend."""
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    # Should return one of the backends
    assert generator.backend_name in ["pywal", "wallust", "custom"]
    # Custom should always be available
    assert generator.is_available()


def test_list_available(settings):
    """Test listing available backends."""
    available = ColorSchemeGeneratorFactory.list_available(settings)
    # Custom should always be available
    assert "custom" in available
    # Should be a list of strings
    assert all(isinstance(b, str) for b in available)


def test_create_invalid_backend(settings):
    """Test creating invalid backend raises error."""
    with pytest.raises(ValueError, match="Unknown backend"):
        ColorSchemeGeneratorFactory.create("invalid", settings)  # type: ignore
