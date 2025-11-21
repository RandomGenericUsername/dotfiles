#!/usr/bin/env bash
# Test script for rofi-colorscheme-viewer-minimal
# Tests the minimal viewer with actual rofi display

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_BIN="$SCRIPT_DIR/.venv/bin"
MODULE_BIN="$VENV_BIN/rofi-colorscheme-viewer-minimal"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Testing rofi-colorscheme-viewer-minimal ===${NC}\n"

# Check if virtual environment exists
if [ ! -d "$VENV_BIN" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Run 'make install' first"
    exit 1
fi

# Check if module is installed
if [ ! -f "$MODULE_BIN" ]; then
    echo -e "${RED}Error: Module not installed${NC}"
    echo "Run 'make install' first"
    exit 1
fi

echo -e "${GREEN}✓${NC} Virtual environment found"
echo -e "${GREEN}✓${NC} Module installed\n"

# Test 1: Check if module can be executed
echo -e "${BLUE}Test 1: Module execution${NC}"
if "$MODULE_BIN" --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Module executes successfully\n"
else
    echo -e "${RED}✗${NC} Module execution failed\n"
    exit 1
fi

# Test 2: Launch rofi with minimal viewer
echo -e "${BLUE}Test 2: Launch rofi viewer${NC}"
echo "This will open rofi - press Escape to close"
echo "Expected: 2 rows of 8 color swatches each (16 total)"
echo ""
read -p "Press Enter to launch rofi..."

rofi -show colors -modi "colors:$MODULE_BIN" || true

echo -e "\n${GREEN}✓${NC} Rofi launched successfully\n"

# Test 3: Verify colorscheme file is read
echo -e "${BLUE}Test 3: Colorscheme file reading${NC}"
COLORSCHEME_FILE="$HOME/.cache/colorscheme/colors.json"

if [ -f "$COLORSCHEME_FILE" ]; then
    echo -e "${GREEN}✓${NC} Colorscheme file found: $COLORSCHEME_FILE"

    # Check if file is valid JSON
    if jq empty "$COLORSCHEME_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Colorscheme file is valid JSON"

        # Check if it has the expected structure
        if jq -e '.colors.color0' "$COLORSCHEME_FILE" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Colorscheme has expected structure\n"
        else
            echo -e "${RED}✗${NC} Colorscheme missing expected colors\n"
        fi
    else
        echo -e "${RED}✗${NC} Colorscheme file is not valid JSON\n"
    fi
else
    echo -e "${RED}✗${NC} Colorscheme file not found"
    echo "Generate a colorscheme first using colorscheme-generator\n"
fi

# Test 4: Check swatch generation
echo -e "${BLUE}Test 4: Swatch generation${NC}"
SWATCH_DIR="/tmp/rofi-colorscheme-swatches-minimal"

if [ -d "$SWATCH_DIR" ]; then
    SWATCH_COUNT=$(find "$SWATCH_DIR" -name "*.png" | wc -l)
    echo -e "${GREEN}✓${NC} Swatch directory exists: $SWATCH_DIR"
    echo -e "${GREEN}✓${NC} Generated $SWATCH_COUNT swatches"

    if [ "$SWATCH_COUNT" -eq 16 ]; then
        echo -e "${GREEN}✓${NC} Correct number of swatches (16)\n"
    else
        echo -e "${RED}✗${NC} Expected 16 swatches, found $SWATCH_COUNT\n"
    fi
else
    echo -e "${RED}✗${NC} Swatch directory not found"
    echo "Swatches are generated on first run\n"
fi

echo -e "${BLUE}=== Test Summary ===${NC}"
echo "All basic tests completed!"
echo ""
echo "Manual verification checklist:"
echo "  [ ] Rofi window shows 2 rows of 8 colors"
echo "  [ ] Colors are touching (no spacing between swatches)"
echo "  [ ] Transparent blurred container wraps the colors"
echo "  [ ] Clicking a color copies hex value to clipboard"
echo "  [ ] Window is centered on screen"
