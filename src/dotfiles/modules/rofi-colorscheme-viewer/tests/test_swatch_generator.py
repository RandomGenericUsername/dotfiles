"""Tests for swatch generator."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from rofi_colorscheme_viewer.utils.swatch_generator import SwatchGenerator


class TestSwatchGenerator:
    """Test swatch generator."""

    @pytest.fixture
    def generator(self, mock_temp_dir):
        """Create a SwatchGenerator instance."""
        return SwatchGenerator(mock_temp_dir, swatch_size=100)

    def test_init(self, mock_temp_dir):
        """Test initialization."""
        generator = SwatchGenerator(mock_temp_dir, swatch_size=100)

        assert generator.temp_dir == mock_temp_dir
        assert generator.swatch_size == 100
        assert mock_temp_dir.exists()

    def test_init_creates_temp_dir(self, tmp_path):
        """Test that initialization creates temp directory."""
        temp_dir = tmp_path / "new_swatches"
        assert not temp_dir.exists()

        generator = SwatchGenerator(temp_dir, swatch_size=100)
        assert temp_dir.exists()

    @patch('subprocess.run')
    def test_generate_creates_swatch(self, mock_run, generator, mock_temp_dir):
        """Test that generate creates a swatch."""
        mock_run.return_value = MagicMock(returncode=0)

        result = generator.generate("#1a1b26")

        expected_path = mock_temp_dir / "swatch_1a1b26.png"
        assert result == expected_path

        # Verify ImageMagick was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "convert"
        assert "-size" in args
        assert "100x100" in args
        assert "xc:#1a1b26" in args
        assert str(expected_path) in args

    @patch('subprocess.run')
    def test_generate_uses_cache(self, mock_run, generator, mock_temp_dir):
        """Test that generate uses cached swatches."""
        # Create a cached swatch
        cached_swatch = mock_temp_dir / "swatch_1a1b26.png"
        cached_swatch.touch()

        result = generator.generate("#1a1b26")

        assert result == cached_swatch
        # Should not call ImageMagick
        mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_generate_different_colors(self, mock_run, generator, mock_temp_dir):
        """Test generating swatches for different colors."""
        mock_run.return_value = MagicMock(returncode=0)

        colors = ["#ff0000", "#00ff00", "#0000ff"]
        results = [generator.generate(color) for color in colors]

        assert len(results) == 3
        assert results[0] == mock_temp_dir / "swatch_ff0000.png"
        assert results[1] == mock_temp_dir / "swatch_00ff00.png"
        assert results[2] == mock_temp_dir / "swatch_0000ff.png"

        # Should have called ImageMagick 3 times
        assert mock_run.call_count == 3

    @patch('subprocess.run')
    def test_generate_strips_hash(self, mock_run, generator, mock_temp_dir):
        """Test that generate strips # from color."""
        mock_run.return_value = MagicMock(returncode=0)

        result = generator.generate("#1a1b26")

        # Filename should not have #
        assert result.name == "swatch_1a1b26.png"

    @patch('subprocess.run')
    def test_generate_custom_size(self, mock_temp_dir):
        """Test generating with custom size."""
        generator = SwatchGenerator(mock_temp_dir, swatch_size=50)

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            generator.generate("#1a1b26")

            args = mock_run.call_args[0][0]
            assert "50x50" in args

    @patch('subprocess.run')
    def test_generate_imagemagick_error(self, mock_run, generator):
        """Test handling ImageMagick errors."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error")

        with pytest.raises(RuntimeError, match="Failed to generate swatch"):
            generator.generate("#1a1b26")

    @patch('subprocess.run')
    def test_generate_uppercase_hex(self, mock_run, generator, mock_temp_dir):
        """Test generating with uppercase hex."""
        mock_run.return_value = MagicMock(returncode=0)

        result = generator.generate("#1A1B26")

        # Should normalize to lowercase
        assert result == mock_temp_dir / "swatch_1a1b26.png"
