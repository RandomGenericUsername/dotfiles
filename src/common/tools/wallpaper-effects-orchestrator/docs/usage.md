# Wallpaper Effects Orchestrator Usage Guide

## Installation

```bash
cd src/common/tools/wallpaper-effects-orchestrator
make install
```

This installs:
- container-manager module
- wallpaper-effects-processor module
- dotfiles-logging module
- wallpaper-effects-orchestrator CLI tool

## Basic Usage

### Single Image Processing

Process a single image with a preset:

```bash
wallpaper-effects-process process \
  -i ~/wallpapers/mountain.jpg \
  -o ~/processed/mountain.jpg \
  --preset dark_blur
```

Process with custom effects:

```bash
wallpaper-effects-process process \
  -i ~/wallpapers/mountain.jpg \
  -o ~/processed/mountain.jpg \
  -e blur --sigma 8 \
  -e brightness --adjustment -20
```

### Generate All Effect Variants

Generate all effect variants for a single image:

```bash
wallpaper-effects-process variants \
  -i ~/wallpapers/mountain.jpg \
  -o ~/variants/

# Creates:
# ~/variants/mountain/blur.png
# ~/variants/mountain/brightness.png
# ~/variants/mountain/saturation.png
# ~/variants/mountain/vignette.png
# ~/variants/mountain/color_overlay.png
# ~/variants/mountain/grayscale.png
# ~/variants/mountain/negate.png
```

### Batch Processing

Process all images in a directory:

```bash
wallpaper-effects-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset aesthetic
```

Parallel batch processing:

```bash
wallpaper-effects-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset lockscreen \
  --parallel 4
```

### List Available Options

List effects:

```bash
wallpaper-effects-process list
```

List presets:

```bash
wallpaper-effects-process presets
```

## Command Reference

### `process` - Process Single Image

**Required:**
- `-i, --input PATH` - Input image path
- `-o, --output PATH` - Output image path

**Effect Selection (choose one):**
- `--preset NAME` - Use preset
- `-e, --effect NAME` - Apply effect (can be specified multiple times)

**Effect Parameters:**
- `--sigma FLOAT` - Blur sigma (0-100)
- `--radius FLOAT` - Blur radius (0-50)
- `--adjustment INT` - Brightness/saturation adjustment (-100 to 100)
- `--strength INT` - Vignette strength (0-100)
- `--color HEX` - Color overlay hex code
- `--opacity FLOAT` - Color overlay opacity (0.0-1.0)

**Processing Options:**
- `--mode {memory,file}` - Processing mode (default: memory)
- `--quality INT` - Output quality 1-100 (default: 95)
- `--metadata` - Write metadata file

**Container Options:**
- `--runtime {docker,podman}` - Container runtime (default: docker)
- `--no-cache` - Don't use cached container image

**Examples:**

```bash
# Use preset
wallpaper-effects-process process -i input.jpg -o output.jpg --preset dark_blur

# Custom blur
wallpaper-effects-process process -i input.jpg -o output.jpg -e blur --sigma 10

# Multiple effects
wallpaper-effects-process process -i input.jpg -o output.jpg \
  -e blur --sigma 6 \
  -e brightness --adjustment -15 \
  -e vignette --strength 20

# With metadata
wallpaper-effects-process process -i input.jpg -o output.jpg \
  --preset lockscreen \
  --metadata

# Use podman
wallpaper-effects-process process -i input.jpg -o output.jpg \
  --preset aesthetic \
  --runtime podman
```

### `variants` - Generate All Effect Variants

Generate all effect variants for an input image.

**Required:**
- `-i, --input PATH` - Input image path
- `-o, --output-dir PATH` - Output directory

**Examples:**

```bash
# Generate all variants
wallpaper-effects-process variants \
  -i ~/wallpapers/mountain.jpg \
  -o ~/variants/

# Creates directory structure:
# ~/variants/mountain/
#   ├── blur.png
#   ├── brightness.png
#   ├── saturation.png
#   ├── vignette.png
#   ├── color_overlay.png
#   ├── grayscale.png
#   └── negate.png
```

### `batch` - Process Multiple Images

**Required:**
- `--batch-dir PATH` - Input directory
- `--output-dir PATH` - Output directory

**Effect Selection (choose one):**
- `--preset NAME` - Use preset
- `-e, --effect NAME` - Apply effect

**Batch Options:**
- `--parallel INT` - Number of parallel processes (default: 1)
- `--skip-existing` - Skip existing output files
- `--continue-on-error` - Continue on processing errors (default: true)

**Processing Options:**
- `--mode {memory,file}` - Processing mode
- `--quality INT` - Output quality

**Container Options:**
- `--runtime {docker,podman}` - Container runtime

**Examples:**

```bash
# Basic batch
wallpaper-effects-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset dark_blur

# Parallel processing
wallpaper-effects-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset aesthetic \
  --parallel 4

# Skip existing files
wallpaper-effects-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset lockscreen \
  --skip-existing
```

### `list` - List Available Effects

Shows all available effects with descriptions and parameters.

```bash
wallpaper-effects-process list
```

### `presets` - List Available Presets

Shows all available presets with descriptions.

```bash
wallpaper-effects-process presets
```

### `build` - Build Container Image

Builds the wallpaper-effects-processor container image.

**Options:**
- `--no-cache` - Build without cache
- `--runtime {docker,podman}` - Container runtime

**Examples:**

```bash
# Build image
wallpaper-effects-process build

# Build without cache
wallpaper-effects-process build --no-cache

# Build with podman
wallpaper-effects-process build --runtime podman
```

### `clean` - Clean Container Resources

Removes wallpaper-effects-processor container images.

**Options:**
- `--runtime {docker,podman}` - Container runtime

**Examples:**

```bash
# Clean resources
wallpaper-effects-process clean

# Clean with podman
wallpaper-effects-process clean --runtime podman
```

## Configuration

### Settings File

Edit `config/settings.toml`:

```toml
[container]
runtime = "docker"  # or "podman"
image_name = "wallpaper-effects-processor"
image_tag = "latest"

[processing]
mode = "memory"  # or "file"
output_format = "png"
quality = 95

[batch]
parallel = 0  # 0 = auto-detect CPU count
skip_existing = false
continue_on_error = true
```

### Custom Presets

Create `~/.config/wallpaper-effects-orchestrator/presets.toml`:

```toml
[presets.my_custom]
description = "My personal preset"
effects = [
    { name = "blur", params = { sigma = 10, radius = 0 } },
    { name = "saturation", params = { adjustment = -50 } },
    { name = "brightness", params = { adjustment = -25 } },
]
```

### Environment Variables

Override settings with environment variables:

```bash
# Set container runtime
export WALLPAPER_CONTAINER__RUNTIME=podman

# Set processing mode
export WALLPAPER_PROCESSING__MODE=file

# Set quality
export WALLPAPER_PROCESSING__QUALITY=90

wallpaper-effects-process process -i input.jpg -o output.jpg --preset dark_blur
```

## Troubleshooting

### Container Runtime Not Found

If you get "runtime not available" error:

```bash
# Check if Docker is installed
docker --version

# Or check if Podman is installed
podman --version

# Specify runtime explicitly
wallpaper-effects-process process -i input.jpg -o output.jpg \
  --preset dark_blur \
  --runtime podman
```

### Image Build Fails

Rebuild without cache:

```bash
wallpaper-effects-process build --no-cache
```

### Permission Errors

Ensure output directory is writable:

```bash
mkdir -p ~/processed
chmod 755 ~/processed
```

### Slow Processing

Use parallel processing for batches:

```bash
wallpaper-effects-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset dark_blur \
  --parallel 4  # Use 4 parallel processes
```

## Advanced Usage

### Custom Output Format

```bash
wallpaper-effects-process process -i input.jpg -o output.webp \
  --preset aesthetic \
  --quality 90
```

### File-Based Processing (Memory Efficient)

```bash
wallpaper-effects-process process -i large-image.jpg -o output.jpg \
  --preset lockscreen \
  --mode file
```

### Combining with Other Tools

```bash
# Process all wallpapers and set as background
for img in ~/wallpapers/*.jpg; do
  wallpaper-effects-process process -i "$img" -o ~/processed/$(basename "$img") \
    --preset dark_blur
done

# Set processed wallpaper as background
feh --bg-fill ~/processed/mountain.jpg
```
