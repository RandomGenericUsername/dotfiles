"""Tests for type definitions and Pydantic models."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from wallpaper_processor.config.enums import OutputFormat, ProcessingMode
from wallpaper_processor.core.types import (
    BlurParams,
    BrightnessParams,
    ColorOverlayParams,
    EffectMetadata,
    EffectParams,
    GrayscaleParams,
    NegateParams,
    ProcessingMetadata,
    ProcessorConfig,
    SaturationParams,
    VignetteParams,
)


class TestEffectParams:
    """Tests for EffectParams base class."""

    def test_create_base_params(self):
        """Test creating base EffectParams."""
        params = EffectParams()
        assert isinstance(params, EffectParams)


class TestBlurParams:
    """Tests for BlurParams."""

    def test_create_with_defaults(self):
        """Test creating BlurParams with default values."""
        params = BlurParams()
        assert params.sigma == 8
        assert params.radius == 0

    def test_create_with_custom_values(self):
        """Test creating BlurParams with custom values."""
        params = BlurParams(sigma=10, radius=5)
        assert params.sigma == 10
        assert params.radius == 5

    def test_sigma_validation_min(self):
        """Test sigma minimum validation."""
        with pytest.raises(ValidationError):
            BlurParams(sigma=-1)

    def test_sigma_validation_max(self):
        """Test sigma maximum validation."""
        with pytest.raises(ValidationError):
            BlurParams(sigma=101)

    def test_radius_validation_min(self):
        """Test radius minimum validation."""
        with pytest.raises(ValidationError):
            BlurParams(radius=-1)

    def test_radius_validation_max(self):
        """Test radius maximum validation."""
        with pytest.raises(ValidationError):
            BlurParams(radius=51)

    def test_valid_edge_values(self):
        """Test valid edge values."""
        params = BlurParams(sigma=0, radius=0)
        assert params.sigma == 0
        assert params.radius == 0

        params = BlurParams(sigma=100, radius=50)
        assert params.sigma == 100
        assert params.radius == 50


class TestBrightnessParams:
    """Tests for BrightnessParams."""

    def test_create_with_defaults(self):
        """Test creating BrightnessParams with default values."""
        params = BrightnessParams()
        assert params.adjustment == -20

    def test_create_with_custom_values(self):
        """Test creating BrightnessParams with custom values."""
        params = BrightnessParams(adjustment=50)
        assert params.adjustment == 50

    def test_adjustment_validation_min(self):
        """Test adjustment minimum validation."""
        with pytest.raises(ValidationError):
            BrightnessParams(adjustment=-101)

    def test_adjustment_validation_max(self):
        """Test adjustment maximum validation."""
        with pytest.raises(ValidationError):
            BrightnessParams(adjustment=101)

    def test_valid_edge_values(self):
        """Test valid edge values."""
        params = BrightnessParams(adjustment=-100)
        assert params.adjustment == -100

        params = BrightnessParams(adjustment=100)
        assert params.adjustment == 100


class TestSaturationParams:
    """Tests for SaturationParams."""

    def test_create_with_defaults(self):
        """Test creating SaturationParams with default values."""
        params = SaturationParams()
        assert params.adjustment == 0

    def test_create_with_custom_values(self):
        """Test creating SaturationParams with custom values."""
        params = SaturationParams(adjustment=50)
        assert params.adjustment == 50

    def test_adjustment_validation_min(self):
        """Test adjustment minimum validation."""
        with pytest.raises(ValidationError):
            SaturationParams(adjustment=-101)

    def test_adjustment_validation_max(self):
        """Test adjustment maximum validation."""
        with pytest.raises(ValidationError):
            SaturationParams(adjustment=101)


class TestVignetteParams:
    """Tests for VignetteParams."""

    def test_create_with_defaults(self):
        """Test creating VignetteParams with default values."""
        params = VignetteParams()
        assert params.strength == 20

    def test_create_with_custom_values(self):
        """Test creating VignetteParams with custom values."""
        params = VignetteParams(strength=50)
        assert params.strength == 50

    def test_strength_validation_min(self):
        """Test strength minimum validation."""
        with pytest.raises(ValidationError):
            VignetteParams(strength=-1)

    def test_strength_validation_max(self):
        """Test strength maximum validation."""
        with pytest.raises(ValidationError):
            VignetteParams(strength=101)


class TestColorOverlayParams:
    """Tests for ColorOverlayParams."""

    def test_create_with_defaults(self):
        """Test creating ColorOverlayParams with default values."""
        params = ColorOverlayParams()
        assert params.color == "#000000"
        assert params.opacity == 0.3

    def test_create_with_custom_values(self):
        """Test creating ColorOverlayParams with custom values."""
        params = ColorOverlayParams(color="#ff00ff", opacity=0.5)
        assert params.color == "#ff00ff"
        assert params.opacity == 0.5

    def test_opacity_validation_min(self):
        """Test opacity minimum validation."""
        with pytest.raises(ValidationError):
            ColorOverlayParams(opacity=-0.1)

    def test_opacity_validation_max(self):
        """Test opacity maximum validation."""
        with pytest.raises(ValidationError):
            ColorOverlayParams(opacity=1.1)

    def test_valid_edge_values(self):
        """Test valid edge values."""
        params = ColorOverlayParams(opacity=0.0)
        assert params.opacity == 0.0

        params = ColorOverlayParams(opacity=1.0)
        assert params.opacity == 1.0


class TestGrayscaleParams:
    """Tests for GrayscaleParams."""

    def test_create_with_defaults(self):
        """Test creating GrayscaleParams with default values."""
        params = GrayscaleParams()
        assert params.method == "average"

    def test_create_with_custom_method(self):
        """Test creating GrayscaleParams with custom method."""
        params = GrayscaleParams(method="luminosity")
        assert params.method == "luminosity"


class TestNegateParams:
    """Tests for NegateParams."""

    def test_create_negate_params(self):
        """Test creating NegateParams."""
        params = NegateParams()
        assert isinstance(params, NegateParams)
        assert isinstance(params, EffectParams)


class TestProcessorConfig:
    """Tests for ProcessorConfig."""

    def test_create_with_defaults(self):
        """Test creating ProcessorConfig with default values."""
        config = ProcessorConfig()
        assert config.processing_mode == ProcessingMode.MEMORY
        assert config.output_format == OutputFormat.PNG
        assert config.quality == 95
        assert config.write_metadata is False

    def test_create_with_custom_values(self):
        """Test creating ProcessorConfig with custom values."""
        config = ProcessorConfig(
            processing_mode=ProcessingMode.FILE,
            output_format=OutputFormat.JPEG,
            quality=85,
            write_metadata=True,
        )
        assert config.processing_mode == ProcessingMode.FILE
        assert config.output_format == OutputFormat.JPEG
        assert config.quality == 85
        assert config.write_metadata is True

    def test_quality_validation_min(self):
        """Test quality minimum validation."""
        with pytest.raises(ValidationError):
            ProcessorConfig(quality=0)

    def test_quality_validation_max(self):
        """Test quality maximum validation."""
        with pytest.raises(ValidationError):
            ProcessorConfig(quality=101)

    def test_valid_edge_values(self):
        """Test valid edge values."""
        config = ProcessorConfig(quality=1)
        assert config.quality == 1

        config = ProcessorConfig(quality=100)
        assert config.quality == 100


class TestEffectMetadata:
    """Tests for EffectMetadata."""

    def test_create_effect_metadata(self):
        """Test creating EffectMetadata."""
        metadata = EffectMetadata(
            name="blur", backend="pil", params={"sigma": 8, "radius": 0}
        )
        assert metadata.name == "blur"
        assert metadata.backend == "pil"
        assert metadata.params == {"sigma": 8, "radius": 0}

    def test_params_with_mixed_types(self):
        """Test params with mixed types."""
        metadata = EffectMetadata(
            name="color_overlay",
            backend="pil",
            params={"color": "#ff00ff", "opacity": 0.5},
        )
        assert metadata.params["color"] == "#ff00ff"
        assert metadata.params["opacity"] == 0.5


class TestProcessingMetadata:
    """Tests for ProcessingMetadata."""

    def test_create_processing_metadata(self):
        """Test creating ProcessingMetadata."""
        metadata = ProcessingMetadata(
            input_path=Path("/input.jpg"),
            output_path=Path("/output.png"),
            effects_applied=[
                EffectMetadata(name="blur", backend="pil", params={"sigma": 8})
            ],
            processing_mode=ProcessingMode.MEMORY,
            output_format=OutputFormat.PNG,
            quality=95,
        )
        assert metadata.input_path == Path("/input.jpg")
        assert metadata.output_path == Path("/output.png")
        assert len(metadata.effects_applied) == 1
        assert metadata.processing_mode == ProcessingMode.MEMORY
        assert metadata.output_format == OutputFormat.PNG
        assert metadata.quality == 95

    def test_multiple_effects(self):
        """Test metadata with multiple effects."""
        metadata = ProcessingMetadata(
            input_path=Path("/input.jpg"),
            output_path=Path("/output.png"),
            effects_applied=[
                EffectMetadata(name="blur", backend="pil", params={"sigma": 8}),
                EffectMetadata(
                    name="brightness", backend="pil", params={"adjustment": -20}
                ),
            ],
            processing_mode=ProcessingMode.MEMORY,
            output_format=OutputFormat.PNG,
            quality=95,
        )
        assert len(metadata.effects_applied) == 2
        assert metadata.effects_applied[0].name == "blur"
        assert metadata.effects_applied[1].name == "brightness"

