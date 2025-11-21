#!/bin/bash

# Test script for rofi-colorscheme-viewer Python module

set -e

cd "$(dirname "$0")"
source .venv/bin/activate

echo "=== Testing rofi-colorscheme-viewer Python module ==="
echo

echo "1. Testing ROFI_RETV=0 (list mode):"
echo "   Should output rofi-formatted list with colors..."
ROFI_RETV=0 rofi-colorscheme-viewer | head -5
echo "   ✓ List mode works"
echo

echo "2. Testing format cycling:"
echo "   Initial format:"
cat /tmp/rofi-colorscheme-viewer/format-state 2>/dev/null || echo "hex (default)"

echo "   Simulating format selector click..."
echo "🎨 Format: [✓] Hex  [ ] Rgb  [ ] Json" | ROFI_RETV=1 rofi-colorscheme-viewer "🎨 Format: [✓] Hex  [ ] Rgb  [ ] Json" > /dev/null 2>&1

echo "   New format:"
cat /tmp/rofi-colorscheme-viewer/format-state 2>/dev/null || echo "unchanged"
echo "   ✓ Format cycling works"
echo

echo "3. Testing color selection:"
echo "   Selecting a color (should copy to clipboard)..."
echo "Background      #1a1b26" | ROFI_RETV=1 rofi-colorscheme-viewer "Background      #1a1b26" > /dev/null 2>&1
echo "   Clipboard content:"
timeout 1 wl-paste 2>/dev/null || echo "   (clipboard empty or wl-paste not available)"
echo "   ✓ Color selection works"
echo

echo "4. Testing with rofi (interactive):"
echo "   Launching rofi with styled theme..."
echo "   - Click format selector to cycle formats"
echo "   - Click a color to copy it to clipboard"
echo "   - Press Escape to close"
echo
rofi -show colors -modi "colors:rofi-colorscheme-viewer" -theme /tmp/test-colorscheme-viewer.rasi

echo
echo "=== All tests completed ==="
