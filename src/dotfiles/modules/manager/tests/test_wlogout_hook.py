"""Tests for WlogoutIconsHook."""

import json
from unittest.mock import Mock

import pytest

from dotfiles_manager.hooks.wlogout_hook import WlogoutIconsHook
from dotfiles_manager.models.hook import HookContext


@pytest.fixture
def mock_wlogout_service():
    """Create mock wlogout service."""
    service = Mock()
    service.generate_all.return_value = {
        "icons": {"lock": "lock.svg", "logout": "logout.svg"},
        "style": "style.css",
    }
    return service


@pytest.fixture
def style_output_path(tmp_path):
    """Create temporary style output path."""
    return tmp_path / "style.css"


@pytest.fixture
def wlogout_hook(mock_wlogout_service, style_output_path):
    """Create WlogoutIconsHook instance."""
    return WlogoutIconsHook(
        wlogout_service=mock_wlogout_service,
        style_output_path=style_output_path,
    )


@pytest.fixture
def colorscheme_files(tmp_path):
    """Create temporary colorscheme files."""
    colorscheme_dir = tmp_path / "colorscheme"
    colorscheme_dir.mkdir()

    # Create JSON file
    json_path = colorscheme_dir / "colors.json"
    json_path.write_text(
        json.dumps(
            {
                "colors": {
                    "color0": "#000000",
                    "color15": "#ffffff",
                }
            }
        )
    )

    # Create GTK CSS file
    gtk_css_path = colorscheme_dir / "colors.gtk.css"
    gtk_css_path.write_text("/* GTK CSS */")

    return {
        "json": json_path,
        "gtk.css": gtk_css_path,
    }


@pytest.fixture
def wallpaper_path(tmp_path):
    """Create temporary wallpaper file."""
    wallpaper = tmp_path / "wallpaper.png"
    wallpaper.touch()
    return wallpaper


def test_hook_name(wlogout_hook):
    """Test hook name property."""
    assert wlogout_hook.name == "wlogout_icons"


def test_hook_skips_when_colorscheme_not_generated(
    wlogout_hook, wallpaper_path, mock_wlogout_service
):
    """Test hook skips execution when colorscheme was not generated."""
    # Arrange
    context = HookContext(
        wallpaper_path=wallpaper_path,
        colorscheme_files={},  # Empty - no colorscheme generated
        font_family="JetBrains Mono",
        font_size=12,
        monitor="eDP-2",
        from_cache=False,
        colorscheme_generated=False,  # Not generated
        effects_generated=True,
        config={},
    )

    # Act
    result = wlogout_hook.execute(context)

    # Assert
    assert result.success is True
    assert result.message == "Skipped (no colorscheme generated)"
    # Verify service was not called
    mock_wlogout_service.generate_all.assert_not_called()


def test_hook_executes_when_colorscheme_generated(
    wlogout_hook, wallpaper_path, colorscheme_files, mock_wlogout_service
):
    """Test hook executes when colorscheme was generated."""
    # Arrange
    context = HookContext(
        wallpaper_path=wallpaper_path,
        colorscheme_files=colorscheme_files,
        font_family="JetBrains Mono",
        font_size=12,
        monitor="eDP-2",
        from_cache=False,
        colorscheme_generated=True,  # Generated
        effects_generated=True,
        config={},
    )

    # Act
    result = wlogout_hook.execute(context)

    # Assert
    assert result.success is True
    assert "Generated" in result.message
    # Verify service was called
    mock_wlogout_service.generate_all.assert_called_once()


def test_hook_fails_when_json_missing(wlogout_hook, wallpaper_path, tmp_path):
    """Test hook fails when colorscheme JSON file is missing."""
    # Arrange
    context = HookContext(
        wallpaper_path=wallpaper_path,
        colorscheme_files={"json": tmp_path / "nonexistent.json"},
        font_family="JetBrains Mono",
        font_size=12,
        monitor="eDP-2",
        from_cache=False,
        colorscheme_generated=True,
        effects_generated=True,
        config={},
    )

    # Act
    result = wlogout_hook.execute(context)

    # Assert
    assert result.success is False
    assert "Colorscheme JSON file not found" in result.message


def test_hook_fails_when_gtk_css_missing(
    wlogout_hook, wallpaper_path, tmp_path
):
    """Test hook fails when GTK CSS file is missing."""
    # Arrange
    colorscheme_dir = tmp_path / "colorscheme"
    colorscheme_dir.mkdir()

    # Create only JSON file
    json_path = colorscheme_dir / "colors.json"
    json_path.write_text(
        json.dumps(
            {
                "colors": {
                    "color15": "#ffffff",
                }
            }
        )
    )

    context = HookContext(
        wallpaper_path=wallpaper_path,
        colorscheme_files={
            "json": json_path,
            "gtk.css": tmp_path / "nonexistent.css",
        },
        font_family="JetBrains Mono",
        font_size=12,
        monitor="eDP-2",
        from_cache=False,
        colorscheme_generated=True,
        effects_generated=True,
        config={},
    )

    # Act
    result = wlogout_hook.execute(context)

    # Assert
    assert result.success is False
    assert "Colorscheme GTK CSS file not found" in result.message


def test_hook_passes_full_colorscheme_to_service(
    wlogout_hook, wallpaper_path, colorscheme_files, mock_wlogout_service
):
    """Test hook passes full colorscheme dict to service."""
    # Arrange
    context = HookContext(
        wallpaper_path=wallpaper_path,
        colorscheme_files=colorscheme_files,
        font_family="JetBrains Mono",
        font_size=12,
        monitor="eDP-2",
        from_cache=False,
        colorscheme_generated=True,
        effects_generated=True,
        config={},
    )

    # Act
    result = wlogout_hook.execute(context)

    # Assert
    assert result.success is True
    # Verify service was called with full colorscheme dict
    call_args = mock_wlogout_service.generate_all.call_args
    colorscheme = call_args.kwargs["colorscheme"]
    assert isinstance(colorscheme, dict)
    assert "color0" in colorscheme
    assert "color15" in colorscheme
    assert colorscheme["color0"] == "#000000"
    assert colorscheme["color15"] == "#ffffff"


def test_hook_handles_service_exception(
    wlogout_hook, wallpaper_path, colorscheme_files, mock_wlogout_service
):
    """Test hook handles exceptions from wlogout service."""
    # Arrange
    mock_wlogout_service.generate_all.side_effect = Exception("Service error")

    context = HookContext(
        wallpaper_path=wallpaper_path,
        colorscheme_files=colorscheme_files,
        font_family="JetBrains Mono",
        font_size=12,
        monitor="eDP-2",
        from_cache=False,
        colorscheme_generated=True,
        effects_generated=True,
        config={},
    )

    # Act
    result = wlogout_hook.execute(context)

    # Assert
    assert result.success is False
    assert "Failed to generate wlogout icons" in result.message
    assert "Service error" in result.message


def test_hook_with_effects_not_generated(
    wlogout_hook, wallpaper_path, colorscheme_files, mock_wlogout_service
):
    """Test hook executes when colorscheme generated but effects not generated."""
    # Arrange
    context = HookContext(
        wallpaper_path=wallpaper_path,
        colorscheme_files=colorscheme_files,
        font_family="JetBrains Mono",
        font_size=12,
        monitor="eDP-2",
        from_cache=False,
        colorscheme_generated=True,  # Generated
        effects_generated=False,  # Not generated
        config={},
    )

    # Act
    result = wlogout_hook.execute(context)

    # Assert
    assert result.success is True
    assert "Generated" in result.message
    # Hook should still execute since it only depends on colorscheme
    mock_wlogout_service.generate_all.assert_called_once()
