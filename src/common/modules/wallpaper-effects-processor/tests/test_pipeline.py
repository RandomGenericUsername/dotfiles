"""Tests for effect pipeline."""

import pytest
from PIL import Image

from wallpaper_processor.backends import PILBlur, PILBrightness
from wallpaper_processor.core.types import (
    BlurParams,
    BrightnessParams,
    ProcessorConfig,
)
from wallpaper_processor.pipeline import EffectPipeline


@pytest.fixture
def test_image_file(tmp_path):
    """Create a test image file."""
    image_path = tmp_path / "test.png"
    image = Image.new("RGB", (100, 100), color=(128, 128, 128))
    image.save(image_path)
    return image_path


class TestEffectPipeline:
    """Tests for EffectPipeline."""

    def test_single_effect(self, test_image_file, tmp_path):
        """Test pipeline with single effect."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        params = BlurParams(sigma=5)

        pipeline = EffectPipeline([(blur, params)])
        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_multiple_effects(self, test_image_file, tmp_path):
        """Test pipeline with multiple effects."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        brightness = PILBrightness()

        pipeline = EffectPipeline(
            [
                (blur, BlurParams(sigma=5)),
                (brightness, BrightnessParams(adjustment=-20)),
            ]
        )

        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_memory_mode(self, test_image_file, tmp_path):
        """Test memory processing mode."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        config = ProcessorConfig(processing_mode="memory")

        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))], config)
        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_file_mode(self, test_image_file, tmp_path):
        """Test file processing mode."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        config = ProcessorConfig(processing_mode="file")

        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))], config)
        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_metadata_generation(self, test_image_file, tmp_path):
        """Test metadata generation."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        config = ProcessorConfig(write_metadata=True)

        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))], config)
        pipeline.apply(test_image_file, output_path)

        # Check metadata file exists
        metadata_path = tmp_path / "output_metadata.json"
        assert metadata_path.exists()

        # Check metadata content
        import json

        with open(metadata_path) as f:
            metadata = json.load(f)

        assert "effects_applied" in metadata
        assert len(metadata["effects_applied"]) == 1
        assert metadata["effects_applied"][0]["name"] == "blur"
        assert metadata["effects_applied"][0]["backend"] == "pil"

    def test_get_metadata(self, test_image_file, tmp_path):
        """Test getting metadata."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))])

        # Before apply, metadata should be None
        assert pipeline.get_metadata() is None

        # After apply, metadata should exist
        pipeline.apply(test_image_file, output_path)
        metadata = pipeline.get_metadata()

        assert metadata is not None
        assert len(metadata.effects_applied) == 1
        assert metadata.effects_applied[0].name == "blur"

    def test_file_not_found(self, tmp_path):
        """Test error when input file doesn't exist."""
        input_path = tmp_path / "nonexistent.png"
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))])

        with pytest.raises(FileNotFoundError):
            pipeline.apply(input_path, output_path)

    def test_empty_pipeline(self, test_image_file, tmp_path):
        """Test pipeline with no effects."""
        output_path = tmp_path / "output.png"

        pipeline = EffectPipeline([])
        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_multiple_effects_memory_mode(self, test_image_file, tmp_path):
        """Test multiple effects in memory mode."""
        from wallpaper_processor.config.enums import ProcessingMode

        output_path = tmp_path / "output.png"

        blur = PILBlur()
        brightness = PILBrightness()

        config = ProcessorConfig(processing_mode=ProcessingMode.MEMORY)
        pipeline = EffectPipeline(
            [
                (blur, BlurParams(sigma=5)),
                (brightness, BrightnessParams(adjustment=-20)),
            ],
            config,
        )

        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_multiple_effects_file_mode(self, test_image_file, tmp_path):
        """Test multiple effects in file mode."""
        from wallpaper_processor.config.enums import ProcessingMode

        output_path = tmp_path / "output.png"

        blur = PILBlur()
        brightness = PILBrightness()

        config = ProcessorConfig(processing_mode=ProcessingMode.FILE)
        pipeline = EffectPipeline(
            [
                (blur, BlurParams(sigma=5)),
                (brightness, BrightnessParams(adjustment=-20)),
            ],
            config,
        )

        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_output_format_jpeg(self, test_image_file, tmp_path):
        """Test output format JPEG."""
        from wallpaper_processor.config.enums import OutputFormat

        output_path = tmp_path / "output.jpg"

        blur = PILBlur()
        config = ProcessorConfig(output_format=OutputFormat.JPEG, quality=85)

        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))], config)
        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_output_format_webp(self, test_image_file, tmp_path):
        """Test output format WEBP."""
        from wallpaper_processor.config.enums import OutputFormat

        output_path = tmp_path / "output.webp"

        blur = PILBlur()
        config = ProcessorConfig(output_format=OutputFormat.WEBP, quality=90)

        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))], config)
        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_metadata_multiple_effects(self, test_image_file, tmp_path):
        """Test metadata with multiple effects."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        brightness = PILBrightness()
        config = ProcessorConfig(write_metadata=True)

        pipeline = EffectPipeline(
            [
                (blur, BlurParams(sigma=5)),
                (brightness, BrightnessParams(adjustment=-20)),
            ],
            config,
        )
        pipeline.apply(test_image_file, output_path)

        # Check metadata file exists
        metadata_path = tmp_path / "output_metadata.json"
        assert metadata_path.exists()

        # Check metadata content
        import json

        with open(metadata_path) as f:
            metadata = json.load(f)

        assert "effects_applied" in metadata
        assert len(metadata["effects_applied"]) == 2
        assert metadata["effects_applied"][0]["name"] == "blur"
        assert metadata["effects_applied"][1]["name"] == "brightness"

    def test_metadata_contains_all_fields(self, test_image_file, tmp_path):
        """Test that metadata contains all expected fields."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        config = ProcessorConfig(write_metadata=True)

        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))], config)
        pipeline.apply(test_image_file, output_path)

        metadata = pipeline.get_metadata()

        assert metadata is not None
        assert metadata.input_path == test_image_file
        assert metadata.output_path == output_path
        assert len(metadata.effects_applied) == 1
        assert metadata.processing_mode is not None
        assert metadata.output_format is not None
        assert metadata.quality is not None

    def test_get_metadata_before_apply(self):
        """Test getting metadata before applying pipeline."""
        blur = PILBlur()
        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))])

        assert pipeline.get_metadata() is None

    def test_config_defaults(self, test_image_file, tmp_path):
        """Test that pipeline uses default config when none provided."""
        output_path = tmp_path / "output.png"

        blur = PILBlur()
        pipeline = EffectPipeline([(blur, BlurParams(sigma=5))])

        result = pipeline.apply(test_image_file, output_path)

        assert result == output_path
        assert output_path.exists()
        assert pipeline.config is not None
