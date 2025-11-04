#!/usr/bin/env bash
# Helper script for managing wallpapers in wallpapers.tar.gz archive

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE_PATH="${SCRIPT_DIR}/wallpapers.tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored message
print_error() {
    echo -e "${RED}Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}Warning: $1${NC}"
}

print_info() {
    echo -e "${CYAN}$1${NC}"
}

# Show usage information
show_usage() {
    cat << EOF
Usage: $(basename "$0") <command> [arguments]

Commands:
    add <wallpaper_path>     Add a wallpaper to the archive
    extract <output_path>    Extract wallpapers to a directory
    list                     List wallpapers in the archive
    help                     Show this help message

Examples:
    $(basename "$0") add ~/Pictures/mountain.jpg
    $(basename "$0") extract ~/wallpapers
    $(basename "$0") list

EOF
}

# List wallpapers in the archive
list_wallpapers() {
    if [[ ! -f "$ARCHIVE_PATH" ]]; then
        print_error "Archive not found: $ARCHIVE_PATH"
        return 1
    fi

    print_info "Wallpapers in $ARCHIVE_PATH:"
    echo ""

    # List contents with details
    tar -tzf "$ARCHIVE_PATH" | while read -r file; do
        echo "  • $file"
    done

    echo ""
    local count=$(tar -tzf "$ARCHIVE_PATH" | wc -l)
    print_success "Total: $count wallpaper(s)"
}

# Add a wallpaper to the archive
add_wallpaper() {
    local wallpaper_path="$1"

    # Validate input
    if [[ -z "$wallpaper_path" ]]; then
        print_error "No wallpaper path provided"
        echo "Usage: $(basename "$0") add <wallpaper_path>"
        return 1
    fi

    if [[ ! -f "$wallpaper_path" ]]; then
        print_error "Wallpaper file not found: $wallpaper_path"
        return 1
    fi

    # Get the filename
    local filename=$(basename "$wallpaper_path")

    # Check if it's an image file (basic check by extension)
    local extension="${filename##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')

    case "$extension" in
        jpg|jpeg|png|gif|bmp|webp|tiff|tif)
            # Valid image extension
            ;;
        *)
            print_warning "File does not have a common image extension: .$extension"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Aborted."
                return 1
            fi
            ;;
    esac

    # Check if file already exists in archive
    if [[ -f "$ARCHIVE_PATH" ]]; then
        if tar -tzf "$ARCHIVE_PATH" | grep -q "^${filename}$"; then
            print_warning "'$filename' already exists in the archive."
            read -p "Overwrite? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Aborted."
                return 1
            fi

            # Create temporary directory
            local temp_dir=$(mktemp -d)
            trap "rm -rf '$temp_dir'" EXIT

            # Extract all files except the one we're replacing
            print_info "Extracting existing wallpapers..."
            tar -xzf "$ARCHIVE_PATH" -C "$temp_dir"

            # Remove the old file
            rm -f "$temp_dir/$filename"

            # Copy the new file
            cp "$wallpaper_path" "$temp_dir/$filename"

            # Create new archive
            print_info "Creating updated archive..."
            tar -czf "$ARCHIVE_PATH" -C "$temp_dir" .

            print_success "Successfully updated '$filename' in $ARCHIVE_PATH"
        else
            # File doesn't exist, just append it
            print_info "Adding '$filename' to archive..."

            # Create temporary directory
            local temp_dir=$(mktemp -d)
            trap "rm -rf '$temp_dir'" EXIT

            # Extract existing files
            tar -xzf "$ARCHIVE_PATH" -C "$temp_dir"

            # Copy the new file
            cp "$wallpaper_path" "$temp_dir/$filename"

            # Create new archive
            tar -czf "$ARCHIVE_PATH" -C "$temp_dir" .

            print_success "Successfully added '$filename' to $ARCHIVE_PATH"
        fi
    else
        # Archive doesn't exist, create it
        print_info "Creating new archive with '$filename'..."
        tar -czf "$ARCHIVE_PATH" -C "$(dirname "$wallpaper_path")" "$filename"
        print_success "Successfully created archive with '$filename'"
    fi
}

# Extract wallpapers from the archive
extract_wallpapers() {
    local output_path="$1"

    # Validate input
    if [[ -z "$output_path" ]]; then
        print_error "No output path provided"
        echo "Usage: $(basename "$0") extract <output_path>"
        return 1
    fi

    if [[ ! -f "$ARCHIVE_PATH" ]]; then
        print_error "Archive not found: $ARCHIVE_PATH"
        return 1
    fi

    # Create output directory if it doesn't exist
    if [[ ! -d "$output_path" ]]; then
        print_info "Creating output directory: $output_path"
        mkdir -p "$output_path"
    fi

    # Count files
    local count=$(tar -tzf "$ARCHIVE_PATH" | wc -l)

    if [[ $count -eq 0 ]]; then
        print_warning "Archive is empty"
        return 0
    fi

    print_info "Extracting $count wallpaper(s) to $output_path..."

    # Extract files
    tar -xzf "$ARCHIVE_PATH" -C "$output_path"

    print_success "Successfully extracted wallpapers:"
    tar -tzf "$ARCHIVE_PATH" | while read -r file; do
        echo "  • $file -> $output_path/$file"
    done
}

# Main script logic
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi

    local command="$1"
    shift

    case "$command" in
        add)
            add_wallpaper "$@"
            ;;
        extract)
            extract_wallpapers "$@"
            ;;
        list)
            list_wallpapers
            ;;
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
