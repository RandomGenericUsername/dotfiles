"""Pytest configuration and fixtures for icon generator tests."""

import pytest
from pathlib import Path


@pytest.fixture
def test_icons_dir(tmp_path):
    """Create test icon directory structure."""
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()

    # Category with variants
    battery_dir = icons_dir / "battery-icons"
    battery_dir.mkdir()

    solid_dir = battery_dir / "solid"
    solid_dir.mkdir()
    (solid_dir / "battery-0.svg").write_text(
        '<svg>{{CURRENT_COLOR}} battery-0</svg>'
    )
    (solid_dir / "battery-50.svg").write_text(
        '<svg>{{CURRENT_COLOR}} battery-50</svg>'
    )
    (solid_dir / "battery-100.svg").write_text(
        '<svg>{{CURRENT_COLOR}} battery-100</svg>'
    )

    rounded_dir = battery_dir / "rounded"
    rounded_dir.mkdir()
    (rounded_dir / "battery-0.svg").write_text(
        '<svg>{{CURRENT_COLOR}} battery-0 rounded</svg>'
    )

    # Empty variant directory
    sharp_dir = battery_dir / "sharp"
    sharp_dir.mkdir()

    # Category without variants (flat)
    wlogout_dir = icons_dir / "wlogout-icons"
    wlogout_dir.mkdir()
    (wlogout_dir / "lock.svg").write_text(
        '<svg>{{CURRENT_COLOR}} lock</svg>'
    )
    (wlogout_dir / "logout.svg").write_text(
        '<svg>{{CURRENT_COLOR}} logout</svg>'
    )

    # Empty category
    empty_dir = icons_dir / "empty-category"
    empty_dir.mkdir()

    return icons_dir


@pytest.fixture
def mock_cache_manager():
    """Create mock SVG cache manager."""

    class MockCacheManager:
        def __init__(self):
            self.cache = {}
            self.hits = 0
            self.misses = 0

        def compute_colorscheme_hash(self, colorscheme_data):
            import hashlib
            import json

            data_str = json.dumps(colorscheme_data, sort_keys=True)
            return hashlib.sha256(data_str.encode()).hexdigest()

        def get_cached_svg(self, colorscheme_hash, template_name):
            key = f"{colorscheme_hash}:{template_name}"
            if key in self.cache:
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

        def cache_svg(self, colorscheme_hash, template_name, svg_content):
            key = f"{colorscheme_hash}:{template_name}"
            self.cache[key] = svg_content

    return MockCacheManager()


@pytest.fixture
def sample_colorscheme():
    """Sample colorscheme data."""
    return {
        "color0": "#000000",
        "color1": "#ff0000",
        "color2": "#00ff00",
        "color3": "#0000ff",
        "color4": "#ffff00",
        "color5": "#ff00ff",
        "color6": "#00ffff",
        "color7": "#ffffff",
        "color8": "#808080",
        "color9": "#ff8080",
        "color10": "#80ff80",
        "color11": "#8080ff",
        "color12": "#ffff80",
        "color13": "#ff80ff",
        "color14": "#80ffff",
        "color15": "#f0f0f0",
        "background": "#1a1a1a",
        "foreground": "#ffffff",
        "cursor": "#ff0000",
    }
