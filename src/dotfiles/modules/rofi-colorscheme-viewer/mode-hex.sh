#!/usr/bin/env bash
# Rofi mode script - HEX format

set -e

# Configuration
SWATCH_SIZE=100
TMP_DIR="/tmp/rofi-colorscheme-test"
SWATCH_DIR="$TMP_DIR/swatches"

# Create temp directories
mkdir -p "$SWATCH_DIR"

# Sample colorscheme data
declare -A COLORS=(
    ["Background"]="#1a1b26"
    ["Foreground"]="#c0caf5"
    ["Cursor"]="#c0caf5"
    ["Color 0"]="#15161e"
    ["Color 1"]="#f7768e"
    ["Color 2"]="#9ece6a"
    ["Color 3"]="#e0af68"
    ["Color 4"]="#7aa2f7"
    ["Color 5"]="#bb9af7"
    ["Color 6"]="#7dcfff"
    ["Color 7"]="#a9b1d6"
)

# Function to generate color swatch
generate_swatch() {
    local hex_color="$1"
    local output_path="$2"
    convert -size "${SWATCH_SIZE}x${SWATCH_SIZE}" "xc:${hex_color}" "$output_path" 2>/dev/null
}

# Handle rofi script mode
ROFI_RETV="${ROFI_RETV:-0}"

if [[ "$ROFI_RETV" == "0" ]]; then
    # List mode - show colors in HEX format

    # Show metadata in message area
    printf "\x00message\x1fSource: mountain.png | Backend: pywal | Generated: 2024-01-15 14:30:22\n"

    # List all colors with swatches
    for color_name in "Background" "Foreground" "Cursor" "Color 0" "Color 1" "Color 2" "Color 3" "Color 4" "Color 5" "Color 6" "Color 7"; do
        hex="${COLORS[$color_name]}"

        # Generate swatch
        swatch_path="$SWATCH_DIR/${hex#\#}.png"
        generate_swatch "$hex" "$swatch_path"

        # Format label: "Color Name    #hexvalue"
        label=$(printf "%-15s %s" "$color_name" "$hex")

        # Output rofi item with icon
        printf "%s\x00icon\x1f%s\n" "$label" "$swatch_path"
    done

elif [[ "$ROFI_RETV" == "1" ]]; then
    # Selection mode - copy hex value to clipboard
    read -r selected

    # Extract hex value
    if [[ "$selected" =~ (#[0-9a-fA-F]{6}) ]]; then
        hex_value="${BASH_REMATCH[1]}"
        echo -n "$hex_value" | wl-copy
    fi
fi
