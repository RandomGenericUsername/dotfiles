#!/usr/bin/env bash
# Test script for rofi colorscheme viewer layout
# This validates the UX before implementing the full Python module
#
# Usage with custom keybindings:
# rofi -show colors -modi "colors:$0" \
#   -kb-custom-1 "Alt+h" \
#   -kb-custom-2 "Alt+r" \
#   -kb-custom-3 "Alt+j"

set -e

# Configuration
SWATCH_SIZE=100
TMP_DIR="/tmp/rofi-colorscheme-test"
STATE_FILE="$TMP_DIR/format-state"
SWATCH_DIR="$TMP_DIR/swatches"

# Create temp directories
mkdir -p "$SWATCH_DIR"

# Initialize state file with default format if it doesn't exist
if [[ ! -f "$STATE_FILE" ]]; then
    echo "hex" > "$STATE_FILE"
fi

# Read current format
CURRENT_FORMAT=$(cat "$STATE_FILE")

# Function to generate color swatch
generate_swatch() {
    local hex_color="$1"
    local output_path="$2"

    # Remove # from hex color for filename
    local clean_hex="${hex_color#\#}"

    # Generate swatch using ImageMagick
    convert -size "${SWATCH_SIZE}x${SWATCH_SIZE}" "xc:${hex_color}" "$output_path" 2>/dev/null
}

# Function to cycle format
cycle_format() {
    case "$CURRENT_FORMAT" in
        hex) echo "rgb" > "$STATE_FILE" ;;
        rgb) echo "json" > "$STATE_FILE" ;;
        json) echo "hex" > "$STATE_FILE" ;;
    esac
}

# Test colors (simulating colorscheme data)
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

declare -A RGB_VALUES=(
    ["Background"]="26, 27, 38"
    ["Foreground"]="192, 202, 245"
    ["Cursor"]="192, 202, 245"
    ["Color 0"]="21, 22, 30"
    ["Color 1"]="247, 118, 142"
    ["Color 2"]="158, 206, 106"
    ["Color 3"]="224, 175, 104"
    ["Color 4"]="122, 162, 247"
    ["Color 5"]="187, 154, 247"
    ["Color 6"]="125, 207, 255"
    ["Color 7"]="169, 177, 214"
)

# Function to show the menu (called on initial load and after format change)
show_menu() {
    local highlight_index="${1:-0}"  # Default to format selector

    # Show metadata in message area
    printf "\x00message\x1fSource: mountain.png | Backend: pywal | Generated: 2024-01-15 14:30:22\n"

    # Keep selection state and set highlight position
    printf "\x00keep-selection\x1ftrue\n"
    printf "\x00new-selection\x1f%s\n" "$highlight_index"

    # Format selectors (clickable to change format)
    if [[ "$CURRENT_FORMAT" == "hex" ]]; then
        echo "🎨 Format: [✓] Hex  [ ] RGB  [ ] JSON"
    elif [[ "$CURRENT_FORMAT" == "rgb" ]]; then
        echo "🎨 Format: [ ] Hex  [✓] RGB  [ ] JSON"
    else
        echo "🎨 Format: [ ] Hex  [ ] RGB  [✓] JSON"
    fi

    # Separator
    echo "─────────────────────────────────────────"

    # List all colors with swatches
    for color_name in "Background" "Foreground" "Cursor" "Color 0" "Color 1" "Color 2" "Color 3" "Color 4" "Color 5" "Color 6" "Color 7"; do
        hex="${COLORS[$color_name]}"
        rgb="${RGB_VALUES[$color_name]}"

        # Generate swatch
        swatch_path="$SWATCH_DIR/${hex#\#}.png"
        generate_swatch "$hex" "$swatch_path"

        # Format label based on current format
        if [[ "$CURRENT_FORMAT" == "hex" ]]; then
            label=$(printf "%-15s %s" "$color_name" "$hex")
        elif [[ "$CURRENT_FORMAT" == "rgb" ]]; then
            label=$(printf "%-15s rgb(%s)" "$color_name" "$rgb")
        else
            # JSON format
            label=$(printf "%-15s {\"hex\":\"%s\",\"rgb\":\"%s\"}" "$color_name" "$hex" "$rgb")
        fi

        # Output rofi item with icon
        printf "%s\x00icon\x1f%s\n" "$label" "$swatch_path"
    done

    # Trigger reload if this is being called from selection handler
    if [[ -n "$RELOAD_MENU" ]]; then
        printf "\x00reload\x1f1\n"
    fi
}

# Handle rofi script mode
ROFI_RETV="${ROFI_RETV:-0}"

if [[ "$ROFI_RETV" == "0" ]]; then
    # Initial load - show menu
    show_menu "0"

elif [[ "$ROFI_RETV" == "1" ]]; then
    # Selection mode - handle user selection (Enter pressed)

    # Rofi passes the selected line as the first argument when using -format
    # But in script mode, it's passed via stdin
    # Try multiple methods to get the selection
    if [[ -n "$1" ]]; then
        selected="$1"
    else
        # Read from stdin with timeout
        IFS= read -r -t 0.1 selected || selected=""
    fi

    # Debug logging
    echo "Selected: [$selected]" >> /tmp/rofi-colorscheme-test/debug.log
    echo "Args: $@" >> /tmp/rofi-colorscheme-test/debug.log
    echo "ROFI_INFO: [$ROFI_INFO]" >> /tmp/rofi-colorscheme-test/debug.log

    # Check if separator was selected - ignore
    if [[ "$selected" == "─"* ]]; then
        exit 0
    fi

    # Check if format selector was clicked - cycle format and reload menu
    if [[ "$selected" == "🎨 Format:"* ]]; then
        echo "Format selector clicked!" >> /tmp/rofi-colorscheme-test/debug.log
        cycle_format
        # Re-read the updated format
        CURRENT_FORMAT=$(cat "$STATE_FILE")
        echo "New format: $CURRENT_FORMAT" >> /tmp/rofi-colorscheme-test/debug.log
        # Reload menu with format selector highlighted (position 0)
        RELOAD_MENU=1 show_menu "0"
        exit 0
    fi

    # Color was selected - copy to clipboard

    # Parse color name and values from selected line
    color_name=$(echo "$selected" | awk '{print $1, $2}' | xargs)
    hex="${COLORS[$color_name]}"
    rgb="${RGB_VALUES[$color_name]}"

    # Format based on current format
    case "$CURRENT_FORMAT" in
        hex)
            output="$hex"
            ;;
        rgb)
            output="rgb($rgb)"
            ;;
        json)
            # Convert RGB string to array format
            IFS=', ' read -r r g b <<< "$rgb"
            output=$(cat <<EOF
{
  "hex": "$hex",
  "rgb": [$r, $g, $b]
}
EOF
)
            ;;
    esac

    # Copy to clipboard
    echo -n "$output" | wl-copy

    # Show notification (optional - for testing)
    echo "Copied: $output"
fi
