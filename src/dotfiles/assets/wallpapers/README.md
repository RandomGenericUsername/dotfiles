# Wallpaper Management

This directory contains a collection of wallpapers stored in `wallpapers.tar.gz` and a helper script to manage them.

## Usage

The `manage_wallpapers.sh` bash script provides three commands:

### List wallpapers

View all wallpapers currently in the archive:

```bash
./manage_wallpapers.sh list
```

This will display:
- Wallpaper filename
- Total count

### Add a wallpaper

Add a new wallpaper to the archive:

```bash
./manage_wallpapers.sh add /path/to/your/wallpaper.jpg
```

Features:
- Validates that the file exists and is an image
- Warns if a wallpaper with the same name already exists (prompts for overwrite)
- Supports common image formats: jpg, jpeg, png, gif, bmp, webp, tiff, tif
- Preserves all existing wallpapers in the archive

### Extract wallpapers

Extract all wallpapers from the archive to a directory:

```bash
./manage_wallpapers.sh extract /path/to/output/directory
```

Features:
- Creates the output directory if it doesn't exist
- Extracts all wallpapers with their original filenames
- Shows progress and file sizes

## Examples

```bash
# List all wallpapers
./manage_wallpapers.sh list

# Add a new wallpaper
./manage_wallpapers.sh add ~/Pictures/sunset.jpg

# Extract all wallpapers to ~/wallpapers
./manage_wallpapers.sh extract ~/wallpapers

# Get help
./manage_wallpapers.sh help
```

## Notes

- The script automatically locates the `wallpapers.tar.gz` file in the same directory
- When adding wallpapers, the original filename is preserved in the archive
- The archive uses gzip compression to save space
- All operations are safe and will prompt before overwriting existing files
