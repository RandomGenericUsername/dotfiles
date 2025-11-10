"""Tests for custom exceptions."""

import pytest

from wallpaper_processor.core.exceptions import (
    EffectNotAvailableError,
    InvalidParametersError,
    PresetNotFoundError,
    ProcessingError,
    UnsupportedFormatError,
    WallpaperProcessorError,
)


class TestWallpaperProcessorError:
    """Tests for WallpaperProcessorError base exception."""

    def test_raise_base_exception(self):
        """Test raising base exception."""
        with pytest.raises(WallpaperProcessorError):
            raise WallpaperProcessorError("Test error")

    def test_exception_message(self):
        """Test exception message."""
        error = WallpaperProcessorError("Test error message")
        assert str(error) == "Test error message"

    def test_exception_inheritance(self):
        """Test that it inherits from Exception."""
        error = WallpaperProcessorError("Test")
        assert isinstance(error, Exception)


class TestEffectNotAvailableError:
    """Tests for EffectNotAvailableError."""

    def test_raise_with_effect_name_only(self):
        """Test raising with effect name only."""
        with pytest.raises(EffectNotAvailableError) as exc_info:
            raise EffectNotAvailableError("blur")

        assert exc_info.value.effect_name == "blur"
        assert str(exc_info.value) == "Effect 'blur' is not available"

    def test_raise_with_custom_message(self):
        """Test raising with custom message."""
        with pytest.raises(EffectNotAvailableError) as exc_info:
            raise EffectNotAvailableError(
                "blur", "ImageMagick not found on system"
            )

        assert exc_info.value.effect_name == "blur"
        assert str(exc_info.value) == "ImageMagick not found on system"

    def test_exception_inheritance(self):
        """Test that it inherits from WallpaperProcessorError."""
        error = EffectNotAvailableError("blur")
        assert isinstance(error, WallpaperProcessorError)
        assert isinstance(error, Exception)

    def test_effect_name_attribute(self):
        """Test that effect_name attribute is accessible."""
        error = EffectNotAvailableError("brightness")
        assert error.effect_name == "brightness"


class TestInvalidParametersError:
    """Tests for InvalidParametersError."""

    def test_raise_exception(self):
        """Test raising exception."""
        with pytest.raises(InvalidParametersError):
            raise InvalidParametersError("Invalid sigma value")

    def test_exception_message(self):
        """Test exception message."""
        error = InvalidParametersError("Sigma must be between 0 and 100")
        assert str(error) == "Sigma must be between 0 and 100"

    def test_exception_inheritance(self):
        """Test that it inherits from WallpaperProcessorError."""
        error = InvalidParametersError("Test")
        assert isinstance(error, WallpaperProcessorError)
        assert isinstance(error, Exception)


class TestPresetNotFoundError:
    """Tests for PresetNotFoundError."""

    def test_raise_with_preset_name(self):
        """Test raising with preset name."""
        with pytest.raises(PresetNotFoundError) as exc_info:
            raise PresetNotFoundError("dark_blur")

        assert exc_info.value.preset_name == "dark_blur"
        assert str(exc_info.value) == "Preset 'dark_blur' not found"

    def test_exception_inheritance(self):
        """Test that it inherits from WallpaperProcessorError."""
        error = PresetNotFoundError("test_preset")
        assert isinstance(error, WallpaperProcessorError)
        assert isinstance(error, Exception)

    def test_preset_name_attribute(self):
        """Test that preset_name attribute is accessible."""
        error = PresetNotFoundError("aesthetic")
        assert error.preset_name == "aesthetic"

    def test_different_preset_names(self):
        """Test with different preset names."""
        error1 = PresetNotFoundError("preset1")
        error2 = PresetNotFoundError("preset2")

        assert error1.preset_name == "preset1"
        assert error2.preset_name == "preset2"
        assert str(error1) == "Preset 'preset1' not found"
        assert str(error2) == "Preset 'preset2' not found"


class TestProcessingError:
    """Tests for ProcessingError."""

    def test_raise_exception(self):
        """Test raising exception."""
        with pytest.raises(ProcessingError):
            raise ProcessingError("Failed to apply blur effect")

    def test_exception_message(self):
        """Test exception message."""
        error = ProcessingError("Image processing failed")
        assert str(error) == "Image processing failed"

    def test_exception_inheritance(self):
        """Test that it inherits from WallpaperProcessorError."""
        error = ProcessingError("Test")
        assert isinstance(error, WallpaperProcessorError)
        assert isinstance(error, Exception)

    def test_with_detailed_message(self):
        """Test with detailed error message."""
        error = ProcessingError(
            "Failed to apply brightness effect: Invalid adjustment value"
        )
        assert (
            "Failed to apply brightness effect: Invalid adjustment value"
            in str(error)
        )


class TestUnsupportedFormatError:
    """Tests for UnsupportedFormatError."""

    def test_raise_with_format_name(self):
        """Test raising with format name."""
        with pytest.raises(UnsupportedFormatError) as exc_info:
            raise UnsupportedFormatError("bmp")

        assert exc_info.value.format_name == "bmp"
        assert str(exc_info.value) == "Format 'bmp' is not supported"

    def test_exception_inheritance(self):
        """Test that it inherits from WallpaperProcessorError."""
        error = UnsupportedFormatError("tiff")
        assert isinstance(error, WallpaperProcessorError)
        assert isinstance(error, Exception)

    def test_format_name_attribute(self):
        """Test that format_name attribute is accessible."""
        error = UnsupportedFormatError("gif")
        assert error.format_name == "gif"

    def test_different_format_names(self):
        """Test with different format names."""
        error1 = UnsupportedFormatError("bmp")
        error2 = UnsupportedFormatError("tiff")

        assert error1.format_name == "bmp"
        assert error2.format_name == "tiff"
        assert str(error1) == "Format 'bmp' is not supported"
        assert str(error2) == "Format 'tiff' is not supported"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_inherit_from_base(self):
        """Test that all custom exceptions inherit from base."""
        exceptions = [
            EffectNotAvailableError("test"),
            InvalidParametersError("test"),
            PresetNotFoundError("test"),
            ProcessingError("test"),
            UnsupportedFormatError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, WallpaperProcessorError)
            assert isinstance(exc, Exception)

    def test_catch_with_base_exception(self):
        """Test catching specific exceptions with base exception."""
        with pytest.raises(WallpaperProcessorError):
            raise EffectNotAvailableError("blur")

        with pytest.raises(WallpaperProcessorError):
            raise InvalidParametersError("test")

        with pytest.raises(WallpaperProcessorError):
            raise PresetNotFoundError("test")

        with pytest.raises(WallpaperProcessorError):
            raise ProcessingError("test")

        with pytest.raises(WallpaperProcessorError):
            raise UnsupportedFormatError("test")

    def test_catch_specific_exception(self):
        """Test catching specific exception types."""
        try:
            raise EffectNotAvailableError("blur")
        except EffectNotAvailableError as e:
            assert e.effect_name == "blur"
        except WallpaperProcessorError:
            pytest.fail("Should have caught EffectNotAvailableError")

        try:
            raise PresetNotFoundError("test")
        except PresetNotFoundError as e:
            assert e.preset_name == "test"
        except WallpaperProcessorError:
            pytest.fail("Should have caught PresetNotFoundError")

