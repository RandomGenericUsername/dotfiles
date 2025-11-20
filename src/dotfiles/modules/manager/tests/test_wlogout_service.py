"""Tests for WlogoutService."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from icon_generator.models.requests import (
    IconGenerationRequest,
    IconGenerationResult,
)

from dotfiles_manager.services.wlogout_service import WlogoutService


@pytest.fixture
def mock_icon_registry():
    """Create mock icon registry."""
    registry = Mock()
    return registry


@pytest.fixture
def mock_icon_service():
    """Create mock icon service."""
    service = Mock()
    # Mock generate_icons to return IconGenerationResult
    service.generate_icons.return_value = IconGenerationResult(
        category="wlogout-icons",
        variant=None,
        generated_icons={
            "lock": Path("/tmp/lock.svg"),
            "logout": Path("/tmp/logout.svg"),
            "shutdown": Path("/tmp/shutdown.svg"),
        },
        from_cache=False,
        cache_hits=0,
        cache_misses=3,
    )
    return service


@pytest.fixture
def style_template_path(tmp_path):
    """Create temporary style template."""
    template = tmp_path / "style.css.tpl"
    template.write_text("""
/* Wlogout Style */
@import url("{{ COLORS_FILE_PATH }}");

* {
    font-family: {{ SYSTEM_FONT_FAMILY }};
    font-size: {{ FONT_SIZE_PX }}px;
    background-image: url("{{ BACKGROUND_IMAGE }}");
}
""")
    return template


@pytest.fixture
def icons_output_dir(tmp_path):
    """Create temporary icons output directory."""
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    return icons_dir


@pytest.fixture
def wlogout_service(
    mock_icon_registry,
    mock_icon_service,
    style_template_path,
    icons_output_dir,
):
    """Create WlogoutService instance."""
    return WlogoutService(
        icon_registry=mock_icon_registry,
        icon_service=mock_icon_service,
        style_template_path=style_template_path,
        icons_output_dir=icons_output_dir,
        color_key="color15",
    )


@pytest.fixture
def colorscheme():
    """Create test colorscheme."""
    return {
        "color0": "#000000",
        "color1": "#ff0000",
        "color15": "#ffffff",
        "background": "#1a1a1a",
        "foreground": "#e0e0e0",
    }


def test_service_initialization(wlogout_service, icons_output_dir):
    """Test service initializes with correct attributes."""
    assert wlogout_service._color_key == "color15"
    assert wlogout_service._icons_output_dir == icons_output_dir


def test_generate_icons_creates_request_with_correct_color(
    wlogout_service, mock_icon_service, colorscheme, icons_output_dir
):
    """Test generate_icons creates IconGenerationRequest with correct color."""
    # Act
    result = wlogout_service.generate_icons(colorscheme, icons_output_dir)

    # Assert
    mock_icon_service.generate_icons.assert_called_once()
    call_args = mock_icon_service.generate_icons.call_args
    request: IconGenerationRequest = call_args[0][0]

    assert isinstance(request, IconGenerationRequest)
    assert request.category == "wlogout-icons"
    assert request.variant is None
    assert request.color == "#ffffff"  # color15 value
    assert request.colorscheme_data == colorscheme
    assert request.output_dir == icons_output_dir


def test_generate_icons_uses_custom_color_key(
    mock_icon_registry,
    mock_icon_service,
    style_template_path,
    icons_output_dir,
    colorscheme,
):
    """Test generate_icons uses custom color key."""
    # Arrange - create service with custom color key
    service = WlogoutService(
        icon_registry=mock_icon_registry,
        icon_service=mock_icon_service,
        style_template_path=style_template_path,
        icons_output_dir=icons_output_dir,
        color_key="color1",  # Custom key
    )

    # Act
    service.generate_icons(colorscheme, icons_output_dir)

    # Assert
    call_args = mock_icon_service.generate_icons.call_args
    request: IconGenerationRequest = call_args[0][0]
    assert request.color == "#ff0000"  # color1 value


def test_generate_icons_returns_generated_icons_dict(
    wlogout_service, colorscheme, icons_output_dir
):
    """Test generate_icons returns dict of generated icons."""
    # Act
    result = wlogout_service.generate_icons(colorscheme, icons_output_dir)

    # Assert
    assert isinstance(result, dict)
    assert "lock" in result
    assert "logout" in result
    assert "shutdown" in result
    assert result["lock"] == Path("/tmp/lock.svg")


def test_generate_icons_uses_fallback_color_when_key_missing(
    wlogout_service, mock_icon_service, icons_output_dir
):
    """Test generate_icons uses fallback color when color key is missing."""
    # Arrange - colorscheme without color15
    colorscheme = {"color0": "#000000"}

    # Act
    wlogout_service.generate_icons(colorscheme, icons_output_dir)

    # Assert
    call_args = mock_icon_service.generate_icons.call_args
    request: IconGenerationRequest = call_args[0][0]
    assert request.color == "#ffffff"  # Fallback color


def test_generate_style_creates_output_directory(wlogout_service, tmp_path):
    """Test generate_style creates output directory if it doesn't exist."""
    # Arrange
    output_path = tmp_path / "nested" / "dir" / "style.css"
    colors_css = tmp_path / "colors.css"
    colors_css.write_text("/* colors */")
    wallpaper = tmp_path / "wallpaper.png"
    wallpaper.touch()

    # Act
    wlogout_service.generate_style(
        font_family="JetBrains Mono",
        font_size=14,
        colors_css_path=colors_css,
        background_image=wallpaper,
        icons_dir=tmp_path / "icons",
        output_path=output_path,
    )

    # Assert
    assert output_path.parent.exists()
    assert output_path.exists()


def test_generate_style_renders_template_with_context(
    wlogout_service, tmp_path
):
    """Test generate_style renders template with correct context."""
    # Arrange
    output_path = tmp_path / "style.css"
    colors_css = tmp_path / "colors.css"
    colors_css.write_text("/* colors */")
    wallpaper = tmp_path / "wallpaper.png"
    wallpaper.touch()
    icons_dir = tmp_path / "icons"

    # Act
    wlogout_service.generate_style(
        font_family="JetBrains Mono",
        font_size=14,
        colors_css_path=colors_css,
        background_image=wallpaper,
        icons_dir=icons_dir,
        output_path=output_path,
    )

    # Assert
    content = output_path.read_text()
    assert "JetBrains Mono" in content
    assert "14px" in content
    assert str(colors_css) in content
    assert str(wallpaper) in content


def test_generate_all_generates_both_icons_and_style(
    wlogout_service, colorscheme, tmp_path
):
    """Test generate_all generates both icons and style."""
    # Arrange
    style_output = tmp_path / "style.css"
    colors_css = tmp_path / "colors.css"
    colors_css.write_text("/* colors */")
    wallpaper = tmp_path / "wallpaper.png"
    wallpaper.touch()

    # Act
    result = wlogout_service.generate_all(
        colorscheme=colorscheme,
        font_family="JetBrains Mono",
        font_size=14,
        colors_css_path=colors_css,
        background_image=wallpaper,
        style_output_path=style_output,
    )

    # Assert
    assert "icons" in result
    assert "style" in result
    assert isinstance(result["icons"], dict)
    assert result["style"] == style_output
    assert style_output.exists()


def test_generate_all_passes_colorscheme_to_icon_generation(
    wlogout_service, mock_icon_service, colorscheme, tmp_path
):
    """Test generate_all passes full colorscheme to icon generation."""
    # Arrange
    style_output = tmp_path / "style.css"
    colors_css = tmp_path / "colors.css"
    colors_css.write_text("/* colors */")
    wallpaper = tmp_path / "wallpaper.png"
    wallpaper.touch()

    # Act
    wlogout_service.generate_all(
        colorscheme=colorscheme,
        font_family="JetBrains Mono",
        font_size=14,
        colors_css_path=colors_css,
        background_image=wallpaper,
        style_output_path=style_output,
    )

    # Assert
    call_args = mock_icon_service.generate_icons.call_args
    request: IconGenerationRequest = call_args[0][0]
    assert request.colorscheme_data == colorscheme
