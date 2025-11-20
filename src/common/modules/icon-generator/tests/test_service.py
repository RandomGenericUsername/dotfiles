"""Tests for IconService."""

import pytest
from pathlib import Path

from icon_generator import (
    IconRegistry,
    IconService,
    IconGenerationRequest,
)
from icon_generator.exceptions import IconVariantNotFoundError


def test_service_generates_icons_with_variant(
    test_icons_dir, sample_colorscheme, tmp_path
):
    """Test service generates icons with variant."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(registry=registry)

    output_dir = tmp_path / "output"
    request = IconGenerationRequest(
        category="battery-icons",
        variant="solid",
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
    )

    result = service.generate_icons(request)

    assert result.success is True
    assert len(result.generated_icons) == 3
    assert "battery-0" in result.generated_icons
    assert "battery-50" in result.generated_icons
    assert "battery-100" in result.generated_icons

    # Check files exist
    assert (output_dir / "battery-0.svg").exists()
    assert (output_dir / "battery-50.svg").exists()

    # Check content
    content = (output_dir / "battery-0.svg").read_text()
    assert "#ffffff" in content
    assert "battery-0" in content


def test_service_generates_icons_without_variant(
    test_icons_dir, sample_colorscheme, tmp_path
):
    """Test service generates icons for flat category."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(registry=registry)

    output_dir = tmp_path / "output"
    request = IconGenerationRequest(
        category="wlogout-icons",
        variant=None,
        color="#ff0000",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
    )

    result = service.generate_icons(request)

    assert result.success is True
    assert len(result.generated_icons) == 2
    assert "lock" in result.generated_icons
    assert "logout" in result.generated_icons

    # Check content
    content = (output_dir / "lock.svg").read_text()
    assert "#ff0000" in content


def test_service_generates_specific_icons(
    test_icons_dir, sample_colorscheme, tmp_path
):
    """Test service generates only specified icons."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(registry=registry)

    output_dir = tmp_path / "output"
    request = IconGenerationRequest(
        category="battery-icons",
        variant="solid",
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
        icons=["battery-0", "battery-100"],  # Only these two
    )

    result = service.generate_icons(request)

    assert result.success is True
    assert len(result.generated_icons) == 2
    assert "battery-0" in result.generated_icons
    assert "battery-100" in result.generated_icons
    assert "battery-50" not in result.generated_icons


def test_service_uses_cache(
    test_icons_dir, sample_colorscheme, mock_cache_manager, tmp_path
):
    """Test service uses cache manager."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(
        registry=registry, cache_manager=mock_cache_manager
    )

    output_dir = tmp_path / "output"
    request = IconGenerationRequest(
        category="battery-icons",
        variant="solid",
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
    )

    # First generation - cache misses
    result1 = service.generate_icons(request)
    assert result1.cache_hits == 0
    assert result1.cache_misses == 3
    assert result1.from_cache is False

    # Second generation - cache hits
    result2 = service.generate_icons(request)
    assert result2.cache_hits == 3
    assert result2.cache_misses == 0
    assert result2.from_cache is True
    assert result2.cache_hit_rate == 100.0


def test_service_cache_key_includes_variant(
    test_icons_dir, sample_colorscheme, mock_cache_manager, tmp_path
):
    """Test cache keys include variant name."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(
        registry=registry, cache_manager=mock_cache_manager
    )

    output_dir = tmp_path / "output"

    # Generate with solid variant
    request1 = IconGenerationRequest(
        category="battery-icons",
        variant="solid",
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
        icons=["battery-0"],
    )
    service.generate_icons(request1)

    # Generate with rounded variant - should be cache miss
    request2 = IconGenerationRequest(
        category="battery-icons",
        variant="rounded",
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
        icons=["battery-0"],
    )
    result2 = service.generate_icons(request2)

    # Should be cache miss because variant is different
    assert result2.cache_misses == 1


def test_service_raises_on_invalid_variant(
    test_icons_dir, sample_colorscheme, tmp_path
):
    """Test service raises error for invalid variant."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(registry=registry)

    output_dir = tmp_path / "output"
    request = IconGenerationRequest(
        category="battery-icons",
        variant="nonexistent",
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
    )

    with pytest.raises(IconVariantNotFoundError) as exc_info:
        service.generate_icons(request)

    assert "nonexistent" in str(exc_info.value)
    assert "battery-icons" in str(exc_info.value)


def test_service_creates_output_directory(
    test_icons_dir, sample_colorscheme, tmp_path
):
    """Test service creates output directory if it doesn't exist."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(registry=registry)

    output_dir = tmp_path / "nested" / "output" / "dir"
    assert not output_dir.exists()

    request = IconGenerationRequest(
        category="wlogout-icons",
        variant=None,
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
    )

    service.generate_icons(request)

    assert output_dir.exists()
    assert (output_dir / "lock.svg").exists()


def test_result_summary(test_icons_dir, sample_colorscheme, tmp_path):
    """Test result.summary() provides human-readable output."""
    registry = IconRegistry(test_icons_dir)
    service = IconService(registry=registry)

    output_dir = tmp_path / "output"
    request = IconGenerationRequest(
        category="battery-icons",
        variant="solid",
        color="#ffffff",
        colorscheme_data=sample_colorscheme,
        output_dir=output_dir,
    )

    result = service.generate_icons(request)
    summary = result.summary()

    assert "battery-icons" in summary
    assert "solid" in summary
    assert "3 icons" in summary or "3" in summary
