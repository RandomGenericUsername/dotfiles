"""Shared fixtures for wallpaper processor tests."""

from pathlib import Path
from unittest.mock import MagicMock, Mock
import tempfile

import pytest
from PIL import Image

from wallpaper_processor.config import AppConfig, get_default_config
from wallpaper_processor.config.config import (
    BackendConfig,
    EffectDefaults,
    Preset,
    PresetEffect,
    ProcessingConfig,
)
from wallpaper_processor.config.enums import OutputFormat, ProcessingMode
from wallpaper_processor.core.types import (
    BlurParams,
    BrightnessParams,
    ColorOverlayParams,
    ProcessorConfig,
    SaturationParams,
    VignetteParams,
)


@pytest.fixture
def test_image():
    """Create a test PIL Image."""
    return Image.new("RGB", (100, 100), color=(128, 128, 128))


@pytest.fixture
def test_image_file(tmp_path):
    """Create a test image file."""
    image_path = tmp_path / "test_image.png"
    image = Image.new("RGB", (100, 100), color=(128, 128, 128))
    image.save(image_path)
    return image_path


@pytest.fixture
def test_image_large():
    """Create a larger test PIL Image."""
    return Image.new("RGB", (1920, 1080), color=(64, 64, 64))


@pytest.fixture
def test_image_large_file(tmp_path):
    """Create a larger test image file."""
    image_path = tmp_path / "test_image_large.png"
    image = Image.new("RGB", (1920, 1080), color=(64, 64, 64))
    image.save(image_path)
    return image_path


@pytest.fixture
def colorful_test_image():
    """Create a colorful test image with multiple colors."""
    image = Image.new("RGB", (100, 100))
    pixels = image.load()
    
    # Create a gradient
    for y in range(100):
        for x in range(100):
            r = int(255 * x / 100)
            g = int(255 * y / 100)
            b = 128
            pixels[x, y] = (r, g, b)
    
    return image


@pytest.fixture
def mock_app_config():
    """Create a mock AppConfig with default values."""
    return AppConfig(
        processing=ProcessingConfig(
            mode=ProcessingMode.MEMORY,
            output_format=OutputFormat.PNG,
            quality=95,
            write_metadata=False,
        ),
        backend=BackendConfig(
            prefer_imagemagick=False,  # Use PIL for tests
            imagemagick_binary="convert",
            strict_mode=False,
            fallback_enabled=True,
        ),
        defaults=EffectDefaults(),
        presets={},
    )


@pytest.fixture
def mock_app_config_with_presets():
    """Create a mock AppConfig with sample presets."""
    return AppConfig(
        processing=ProcessingConfig(),
        backend=BackendConfig(prefer_imagemagick=False),
        defaults=EffectDefaults(),
        presets={
            "test_preset": Preset(
                description="Test preset",
                effects=[
                    PresetEffect(name="blur", params={"sigma": 5}),
                    PresetEffect(name="brightness", params={"adjustment": -10}),
                ],
            )
        },
    )


@pytest.fixture
def default_config():
    """Get default configuration from settings.toml."""
    return get_default_config()


@pytest.fixture
def processor_config_memory():
    """Create a ProcessorConfig for memory mode."""
    return ProcessorConfig(
        processing_mode=ProcessingMode.MEMORY,
        output_format=OutputFormat.PNG,
        quality=95,
        write_metadata=False,
    )


@pytest.fixture
def processor_config_file():
    """Create a ProcessorConfig for file mode."""
    return ProcessorConfig(
        processing_mode=ProcessingMode.FILE,
        output_format=OutputFormat.PNG,
        quality=95,
        write_metadata=False,
    )


@pytest.fixture
def blur_params():
    """Create default blur parameters."""
    return BlurParams(radius=0, sigma=8)


@pytest.fixture
def brightness_params():
    """Create default brightness parameters."""
    return BrightnessParams(adjustment=-20)


@pytest.fixture
def saturation_params():
    """Create default saturation parameters."""
    return SaturationParams(adjustment=0)


@pytest.fixture
def vignette_params():
    """Create default vignette parameters."""
    return VignetteParams(strength=20)


@pytest.fixture
def color_overlay_params():
    """Create default color overlay parameters."""
    return ColorOverlayParams(color="#000000", opacity=0.3)


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for ImageMagick tests."""
    mock = Mock()
    mock.return_value = Mock(returncode=0, stdout="", stderr="")
    return mock


@pytest.fixture
def mock_shutil_which():
    """Mock shutil.which for availability checks."""
    mock = Mock()
    mock.return_value = "/usr/bin/convert"  # Simulate ImageMagick available
    return mock


@pytest.fixture
def mock_shutil_which_not_found():
    """Mock shutil.which returning None (not found)."""
    mock = Mock()
    mock.return_value = None
    return mock


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_metadata():
    """Create sample processing metadata."""
    from wallpaper_processor.core.types import EffectMetadata, ProcessingMetadata
    
    return ProcessingMetadata(
        input_path=Path("/path/to/input.jpg"),
        output_path=Path("/path/to/output.png"),
        effects=[
            EffectMetadata(
                name="blur",
                backend="pil",
                params={"sigma": 8, "radius": 0},
            ),
            EffectMetadata(
                name="brightness",
                backend="pil",
                params={"adjustment": -20},
            ),
        ],
        processing_mode="memory",
        output_format="png",
    )


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test."""
    yield
    # Cleanup happens automatically with tmp_path fixture

