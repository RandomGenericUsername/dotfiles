"""Pytest configuration and fixtures."""

import json
import pytest
from pathlib import Path
from datetime import datetime


@pytest.fixture
def mock_colorscheme_file(tmp_path):
    """Create a mock colorscheme JSON file."""
    colorscheme_file = tmp_path / "colors.json"

    colorscheme_data = {
        "metadata": {
            "source_image": "/path/to/mountain.png",
            "backend": "pywal",
            "generated_at": "2024-01-15T14:30:22"
        },
        "special": {
            "background": {
                "hex": "#1a1b26",
                "rgb": [26, 27, 38]
            },
            "foreground": {
                "hex": "#c0caf5",
                "rgb": [192, 202, 245]
            },
            "cursor": {
                "hex": "#c0caf5",
                "rgb": [192, 202, 245]
            }
        },
        "colors": [
            {"hex": "#15161e", "rgb": [21, 22, 30]},
            {"hex": "#f7768e", "rgb": [247, 118, 142]},
            {"hex": "#9ece6a", "rgb": [158, 206, 106]},
            {"hex": "#e0af68", "rgb": [224, 175, 104]},
            {"hex": "#7aa2f7", "rgb": [122, 162, 247]},
            {"hex": "#bb9af7", "rgb": [187, 154, 247]},
            {"hex": "#7dcfff", "rgb": [125, 207, 255]},
            {"hex": "#c0caf5", "rgb": [192, 202, 245]},
            {"hex": "#414868", "rgb": [65, 72, 104]},
            {"hex": "#f7768e", "rgb": [247, 118, 142]},
            {"hex": "#9ece6a", "rgb": [158, 206, 106]},
            {"hex": "#e0af68", "rgb": [224, 175, 104]},
            {"hex": "#7aa2f7", "rgb": [122, 162, 247]},
            {"hex": "#bb9af7", "rgb": [187, 154, 247]},
            {"hex": "#7dcfff", "rgb": [125, 207, 255]},
            {"hex": "#c0caf5", "rgb": [192, 202, 245]}
        ]
    }

    colorscheme_file.write_text(json.dumps(colorscheme_data, indent=2))
    return colorscheme_file


@pytest.fixture
def mock_temp_dir(tmp_path):
    """Create a mock temp directory for swatches."""
    temp_dir = tmp_path / "swatches"
    temp_dir.mkdir()
    return temp_dir


@pytest.fixture
def mock_state_file(tmp_path):
    """Create a mock state file."""
    state_file = tmp_path / "state.json"
    state_data = {"current_format": "hex"}
    state_file.write_text(json.dumps(state_data))
    return state_file


@pytest.fixture
def mock_config(mock_colorscheme_file, mock_temp_dir):
    """Create a mock ViewerConfig."""
    from rofi_colorscheme_viewer.config.config import ViewerConfig

    return ViewerConfig(
        colorscheme_file=mock_colorscheme_file,
        temp_dir=mock_temp_dir,
        show_icons=True,
        swatch_size=100,
        available_formats=["hex", "rgb", "json"],
        default_format="hex"
    )


@pytest.fixture
def sample_colorscheme():
    """Return a sample ColorScheme object."""
    from colorscheme_generator.core.types import ColorScheme, Color

    return ColorScheme(
        background=Color(hex="#1a1b26", rgb=(26, 27, 38)),
        foreground=Color(hex="#c0caf5", rgb=(192, 202, 245)),
        cursor=Color(hex="#c0caf5", rgb=(192, 202, 245)),
        colors=[
            Color(hex="#15161e", rgb=(21, 22, 30)),
            Color(hex="#f7768e", rgb=(247, 118, 142)),
            Color(hex="#9ece6a", rgb=(158, 206, 106)),
            Color(hex="#e0af68", rgb=(224, 175, 104)),
            Color(hex="#7aa2f7", rgb=(122, 162, 247)),
            Color(hex="#bb9af7", rgb=(187, 154, 247)),
            Color(hex="#7dcfff", rgb=(125, 207, 255)),
            Color(hex="#c0caf5", rgb=(192, 202, 245)),
            Color(hex="#414868", rgb=(65, 72, 104)),
            Color(hex="#f7768e", rgb=(247, 118, 142)),
            Color(hex="#9ece6a", rgb=(158, 206, 106)),
            Color(hex="#e0af68", rgb=(224, 175, 104)),
            Color(hex="#7aa2f7", rgb=(122, 162, 247)),
            Color(hex="#bb9af7", rgb=(187, 154, 247)),
            Color(hex="#7dcfff", rgb=(125, 207, 255)),
            Color(hex="#c0caf5", rgb=(192, 202, 245))
        ],
        metadata={
            "source_image": "/path/to/mountain.png",
            "backend": "pywal",
            "generated_at": datetime(2024, 1, 15, 14, 30, 22)
        }
    )
