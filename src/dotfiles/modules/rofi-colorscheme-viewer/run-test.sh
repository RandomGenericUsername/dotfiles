#!/usr/bin/env bash
# Launcher script for testing the rofi layout

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_SCRIPT="$SCRIPT_DIR/test-rofi-layout.sh"

echo "🧪 Testing Rofi Colorscheme Viewer Layout"
echo "=========================================="
echo ""
echo "This will open rofi with a test colorscheme layout."
echo ""
echo "Features to test:"
echo "  1. Format selectors at the top with keyboard shortcuts"
echo "  2. Color swatches displayed as icons"
echo "  3. Metadata shown in header"
echo "  4. Press Alt+h (Hex), Alt+r (RGB), or Alt+j (JSON) to change format"
echo "  5. Rofi stays open when changing format!"
echo "  6. Press Enter on a color to copy it in current format"
echo ""
echo "Keyboard shortcuts:"
echo "  Alt+h = Hex format"
echo "  Alt+r = RGB format"
echo "  Alt+j = JSON format"
echo "  Enter = Copy selected color"
echo ""
echo "Press Enter to launch rofi..."
read -r

# Launch rofi with custom keybindings and focus flags
rofi -show colors -modi "colors:$TEST_SCRIPT" \
    -kb-custom-1 "Alt+h" \
    -kb-custom-2 "Alt+r" \
    -kb-custom-3 "Alt+j" \
    -steal-focus \
    -no-lazy-grab

echo ""
echo "✅ Test complete!"
echo ""
echo "Check your clipboard - it should contain the selected color."
echo "Run 'wl-paste' to see what was copied."
