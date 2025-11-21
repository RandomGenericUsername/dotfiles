#!/usr/bin/env bash
# Test rofi colorscheme viewer with proper mode switching
# This demonstrates the correct UX using rofi's mode-switcher

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create three separate scripts for each mode
HEX_SCRIPT="$SCRIPT_DIR/mode-hex.sh"
RGB_SCRIPT="$SCRIPT_DIR/mode-rgb.sh"
JSON_SCRIPT="$SCRIPT_DIR/mode-json.sh"

# Launch rofi with three modes
rofi -show hex \
    -modi "hex:$HEX_SCRIPT,rgb:$RGB_SCRIPT,json:$JSON_SCRIPT" \
    -show-icons
