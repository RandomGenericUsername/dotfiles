"""Tests for IconRegistry."""

import pytest
from icon_generator import IconRegistry
from icon_generator.exceptions import IconCategoryNotFoundError


def test_registry_discovers_categories_with_variants(test_icons_dir):
    """Test registry discovers categories with variants."""
    registry = IconRegistry(test_icons_dir)

    categories = registry.list_categories()
    assert "battery-icons" in categories
    assert "wlogout-icons" in categories


def test_registry_discovers_variants(test_icons_dir):
    """Test registry discovers variants within categories."""
    registry = IconRegistry(test_icons_dir)

    category = registry.get_category("battery-icons")
    assert category.has_variants is True
    assert "solid" in category.variants
    assert "rounded" in category.variants
    # Note: Empty variant directories are NOT discovered (no SVG files)


def test_registry_discovers_flat_category(test_icons_dir):
    """Test registry discovers flat categories without variants."""
    registry = IconRegistry(test_icons_dir)

    category = registry.get_category("wlogout-icons")
    assert category.has_variants is False
    assert len(category.icons) == 2
    assert "lock" in category.icons
    assert "logout" in category.icons


def test_registry_skips_empty_category(test_icons_dir):
    """Test registry skips empty categories."""
    registry = IconRegistry(test_icons_dir)

    categories = registry.list_categories()
    assert "empty-category" not in categories


def test_get_category_raises_if_not_found(test_icons_dir):
    """Test get_category raises error if category not found."""
    registry = IconRegistry(test_icons_dir)

    with pytest.raises(IconCategoryNotFoundError) as exc_info:
        registry.get_category("nonexistent")

    assert "nonexistent" in str(exc_info.value)
    assert "battery-icons" in str(exc_info.value)


def test_get_variants(test_icons_dir):
    """Test get_variants returns variant list."""
    registry = IconRegistry(test_icons_dir)

    variants = registry.get_variants("battery-icons")
    assert "solid" in variants
    assert "rounded" in variants


def test_get_variants_empty_for_flat_category(test_icons_dir):
    """Test get_variants returns empty list for flat categories."""
    registry = IconRegistry(test_icons_dir)

    variants = registry.get_variants("wlogout-icons")
    assert variants == []


def test_category_list_icons_with_variant(test_icons_dir):
    """Test category.list_icons() with variant."""
    registry = IconRegistry(test_icons_dir)
    category = registry.get_category("battery-icons")

    icons = category.list_icons(variant="solid")
    assert "battery-0" in icons
    assert "battery-50" in icons
    assert "battery-100" in icons


def test_category_list_icons_without_variant(test_icons_dir):
    """Test category.list_icons() for flat category."""
    registry = IconRegistry(test_icons_dir)
    category = registry.get_category("wlogout-icons")

    icons = category.list_icons()
    assert "lock" in icons
    assert "logout" in icons


def test_category_get_icon_path_with_variant(test_icons_dir):
    """Test category.get_icon_path() with variant."""
    registry = IconRegistry(test_icons_dir)
    category = registry.get_category("battery-icons")

    path = category.get_icon_path("battery-0", variant="solid")
    assert path.exists()
    assert path.name == "battery-0.svg"
    assert "solid" in str(path)


def test_category_get_icon_path_without_variant(test_icons_dir):
    """Test category.get_icon_path() for flat category."""
    registry = IconRegistry(test_icons_dir)
    category = registry.get_category("wlogout-icons")

    path = category.get_icon_path("lock")
    assert path.exists()
    assert path.name == "lock.svg"


def test_registry_handles_nonexistent_base_path(tmp_path):
    """Test registry handles nonexistent base path gracefully."""
    nonexistent = tmp_path / "nonexistent"
    registry = IconRegistry(nonexistent)

    assert registry.list_categories() == []


def test_category_icon_count(test_icons_dir):
    """Test category tracks icon count."""
    registry = IconRegistry(test_icons_dir)

    battery_category = registry.get_category("battery-icons")
    assert battery_category.icon_count == 4  # 3 in solid + 1 in rounded

    wlogout_category = registry.get_category("wlogout-icons")
    assert wlogout_category.icon_count == 2
