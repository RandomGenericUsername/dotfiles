"""Tests for colorscheme viewer."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
from rofi_colorscheme_viewer.viewer.colorscheme_viewer import ColorschemeViewer


class TestColorschemeViewer:
    """Test colorscheme viewer."""

    @pytest.fixture
    def viewer(self, mock_config):
        """Create a ColorschemeViewer instance."""
        return ColorschemeViewer(mock_config)

    def test_init(self, mock_config):
        """Test initialization."""
        viewer = ColorschemeViewer(mock_config)

        assert viewer.config == mock_config
        assert viewer.colorscheme is not None
        assert viewer.state_manager is not None
        assert viewer.swatch_generator is not None
        assert viewer.converter is not None
        assert viewer.formatter is not None

    def test_get_color_entries(self, viewer):
        """Test getting color entries."""
        entries = viewer.get_color_entries()

        assert len(entries) == 19  # 3 special + 16 colors

        # Check first entry (background)
        assert entries[0][0] == "Background"
        assert entries[0][1] == "#1a1b26"
        assert entries[0][2] == (26, 27, 38)

        # Check second entry (foreground)
        assert entries[1][0] == "Foreground"
        assert entries[1][1] == "#c0caf5"

        # Check color entries
        assert entries[3][0] == "Color 0"
        assert entries[4][0] == "Color 1"

    def test_get_metadata_text(self, viewer):
        """Test getting metadata text."""
        text = viewer.get_metadata_text()

        assert "mountain.png" in text
        assert "pywal" in text
        assert "2024-01-15" in text

    def test_get_format_selector_text_hex(self, viewer):
        """Test format selector text with hex selected."""
        with patch.object(viewer.state_manager, 'get_current_format', return_value='hex'):
            text = viewer.get_format_selector_text()

            assert "🎨 Format:" in text
            assert "[✓] Hex" in text
            assert "[ ] Rgb" in text
            assert "[ ] Json" in text

    def test_get_format_selector_text_rgb(self, viewer):
        """Test format selector text with rgb selected."""
        with patch.object(viewer.state_manager, 'get_current_format', return_value='rgb'):
            text = viewer.get_format_selector_text()

            assert "[✓] Rgb" in text
            assert "[ ] Hex" in text
            assert "[ ] Json" in text

    def test_get_format_selector_text_json(self, viewer):
        """Test format selector text with json selected."""
        with patch.object(viewer.state_manager, 'get_current_format', return_value='json'):
            text = viewer.get_format_selector_text()

            assert "[✓] Json" in text
            assert "[ ] Hex" in text
            assert "[ ] Rgb" in text

    @patch('sys.stdout', new_callable=StringIO)
    @patch('subprocess.run')
    def test_show_menu(self, mock_run, mock_stdout, viewer):
        """Test showing menu."""
        mock_run.return_value = MagicMock(returncode=0)

        viewer.show_menu()

        output = mock_stdout.getvalue()

        # Should contain metadata
        assert "mountain.png" in output

        # Should contain format selector
        assert "🎨 Format:" in output

        # Should contain colors
        assert "Background" in output
        assert "Foreground" in output
        assert "Color 0" in output

    @patch('sys.stdout', new_callable=StringIO)
    @patch('subprocess.run')
    def test_show_menu_with_reload(self, mock_run, mock_stdout, viewer):
        """Test showing menu with reload."""
        mock_run.return_value = MagicMock(returncode=0)

        viewer.show_menu(highlight_index=0, reload=True)

        output = mock_stdout.getvalue()

        # Should contain reload commands
        assert "\x00keep-selection\x1ftrue\n" in output
        assert "\x00new-selection\x1f0\n" in output
        assert "\x00reload\x1f1\n" in output

    @patch('sys.stdout', new_callable=StringIO)
    @patch('subprocess.run')
    def test_handle_selection_format_selector(self, mock_run, mock_stdout, viewer):
        """Test handling format selector selection."""
        mock_run.return_value = MagicMock(returncode=0)

        viewer.handle_selection("🎨 Format: [✓] Hex  [ ] Rgb  [ ] Json")

        output = mock_stdout.getvalue()

        # Should reload menu
        assert "\x00reload\x1f1\n" in output

    @patch('subprocess.run')
    def test_handle_selection_color_hex(self, mock_run, viewer):
        """Test handling color selection in hex format."""
        mock_run.return_value = MagicMock(returncode=0)

        with patch.object(viewer.state_manager, 'get_current_format', return_value='hex'):
            viewer.handle_selection("Background  #1a1b26")

            # Should call wl-copy
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "wl-copy" in args
            assert "#1a1b26" in args

    @patch('subprocess.run')
    def test_handle_selection_color_rgb(self, mock_run, viewer):
        """Test handling color selection in RGB format."""
        mock_run.return_value = MagicMock(returncode=0)

        with patch.object(viewer.state_manager, 'get_current_format', return_value='rgb'):
            viewer.handle_selection("Background  rgb(26, 27, 38)")

            # Should call wl-copy
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "wl-copy" in args
            assert "rgb(26, 27, 38)" in args

    @patch('subprocess.run')
    def test_handle_selection_color_json(self, mock_run, viewer):
        """Test handling color selection in JSON format."""
        mock_run.return_value = MagicMock(returncode=0)

        with patch.object(viewer.state_manager, 'get_current_format', return_value='json'):
            viewer.handle_selection('Background  {"r": 26, "g": 27, "b": 38}')

            # Should call wl-copy
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "wl-copy" in args
