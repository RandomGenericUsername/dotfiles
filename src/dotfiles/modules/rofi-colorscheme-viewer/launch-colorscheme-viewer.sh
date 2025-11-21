#!/usr/bin/env bash
# Wrapper script to launch rofi colorscheme viewer
# This handles relaunching rofi when format changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROFI_SCRIPT="$SCRIPT_DIR/test-rofi-layout.sh"
STATE_FILE="/tmp/rofi-colorscheme-test/format-state"

# Launch rofi in a loop - it will exit when format changes or color is selected
while true; do
    # Store the current format before launching
    BEFORE_FORMAT=$(cat "$STATE_FILE" 2>/dev/null || echo "hex")

    # Launch rofi
    rofi -show colors -modi "colors:$ROFI_SCRIPT" || true

    # Check if format changed
    AFTER_FORMAT=$(cat "$STATE_FILE" 2>/dev/null || echo "hex")

    # If format didn't change, user selected a color or cancelled - exit
    if [[ "$BEFORE_FORMAT" == "$AFTER_FORMAT" ]]; then
        break
    fi

    # Format changed - loop will relaunch rofi with new format
done
