# Wallpaper Orchestrator

Container-based CLI tool for applying effects to wallpapers using the wallpaper-processor module.

## Features

- **Container-Based Processing**: All effects run in isolated containers
- **Multiple Effects**: Blur, brightness, saturation, vignette, color overlay, grayscale, negate
- **Presets**: Pre-configured effect combinations
- **Batch Processing**: Process single images, batches, or parallel processing
- **Variant Generation**: Generate all effect variants automatically
- **Flexible Output**: Multiple formats (PNG, JPEG, WebP, etc.) with quality control
- **Metadata**: Optional metadata output for tracking applied effects
- **Docker/Podman Support**: Configurable container runtime

## Installation

```bash
cd src/common/tools/wallpaper-orchestrator
make install
```

This will:
1. Install container-manager module
2. Install wallpaper-processor module
3. Install dotfiles-logging module
4. Install wallpaper-orchestrator tool

## Quick Start

### Single Image Processing

```bash
# Use preset
wallpaper-process process -i wallpaper.jpg -o output.jpg --preset dark_blur

# Custom effects
wallpaper-process process -i wallpaper.jpg -o output.jpg \
  -e blur --sigma 6 \
  -e brightness --adjustment -15
```

### Generate All Variants

```bash
# Generate all effect variants
wallpaper-process variants -i wallpaper.jpg -o ~/variants/

# Creates:
# ~/variants/wallpaper/blur.png
# ~/variants/wallpaper/brightness.png
# ~/variants/wallpaper/saturation.png
# ~/variants/wallpaper/vignette.png
# ~/variants/wallpaper/color_overlay.png
# ~/variants/wallpaper/grayscale.png
# ~/variants/wallpaper/negate.png
```

### Batch Processing

```bash
# Process directory
wallpaper-process batch --batch-dir ~/wallpapers/ --output-dir ~/processed/

# Parallel processing
wallpaper-process batch --batch-dir ~/wallpapers/ --output-dir ~/processed/ --parallel 4
```

### List Available Options

```bash
# List effects
wallpaper-process list

# List presets
wallpaper-process presets
```

## Available Effects

| Effect | Description | Parameters |
|--------|-------------|------------|
| `blur` | Gaussian blur | `sigma` (0-100), `radius` (0-50) |
| `brightness` | Adjust brightness | `adjustment` (-100 to 100) |
| `saturation` | Adjust saturation | `adjustment` (-100 to 100) |
| `vignette` | Darken edges | `strength` (0-100) |
| `color_overlay` | Overlay color | `color` (hex), `opacity` (0.0-1.0) |
| `grayscale` | Convert to grayscale | `method` (average, luminosity, mean) |
| `negate` | Invert colors | - |

## Presets

### dark_blur
Blurred and darkened wallpaper (ideal for desktop backgrounds).
- Blur: sigma=6
- Brightness: adjustment=-15

### aesthetic
Aesthetic wallpaper with reduced saturation and vignette.
- Saturation: adjustment=-30
- Vignette: strength=15

### lockscreen
Heavily blurred and darkened (ideal for lock screens).
- Blur: sigma=12
- Brightness: adjustment=-30
- Color Overlay: #000000, opacity=0.2

### minimal_dark
Minimal dark theme with desaturation and darkening.
- Saturation: adjustment=-50
- Brightness: adjustment=-25

## Configuration

### Container Runtime

Set container runtime in `config/settings.toml`:

```toml
[container]
runtime = "docker"  # or "podman"
```

Or via environment variable:

```bash
export CONTAINER_RUNTIME=podman
wallpaper-process -i input.jpg -o output.jpg --preset dark_blur
```

### Processing Options

```toml
[processing]
mode = "memory"  # "memory" or "file"
output_format = "png"
quality = 95
```

### Custom Presets

Create `~/.config/wallpaper-orchestrator/presets.toml`:

```toml
[presets.my_custom]
description = "My personal preset"
effects = [
    { name = "blur", params = { sigma = 10 } },
    { name = "saturation", params = { adjustment = -50 } },
]
```

## CLI Reference

### Basic Usage

```bash
wallpaper-process [OPTIONS] COMMAND [ARGS]
```

### Commands

- `process`: Process single image
- `variants`: Generate all effect variants for an image
- `batch`: Process multiple images
- `list`: List available effects
- `presets`: List available presets
- `build`: Build container image
- `clean`: Clean container resources

### Options

**Input/Output:**
- `-i, --input PATH`: Input image path
- `-o, --output PATH`: Output image path
- `--batch-dir PATH`: Input directory for batch processing
- `--output-dir PATH`: Output directory for batch processing

**Effects:**
- `-e, --effect NAME`: Effect to apply (can be specified multiple times)
- `--preset NAME`: Use preset

**Effect Parameters:**
- `--sigma FLOAT`: Blur sigma
- `--radius FLOAT`: Blur radius
- `--adjustment INT`: Brightness/saturation adjustment
- `--strength INT`: Vignette strength
- `--color HEX`: Color overlay hex code
- `--opacity FLOAT`: Color overlay opacity

**Processing:**
- `--mode {memory,file}`: Processing mode
- `--quality INT`: Output quality (1-100)
- `--format {png,jpeg,webp}`: Output format
- `--metadata`: Write metadata file
- `--parallel INT`: Number of parallel processes (batch mode)

**Container:**
- `--runtime {docker,podman}`: Container runtime
- `--no-cache`: Don't use cached container image

**Other:**
- `--debug`: Enable debug logging
- `--help`: Show help message

## Examples

### Single Image with Custom Effects

```bash
wallpaper-process process -i wallpaper.jpg -o output.jpg \
  -e blur --sigma 8 \
  -e brightness --adjustment -20 \
  -e vignette --strength 15
```

### Generate All Effect Variants

```bash
wallpaper-process variants -i wallpaper.jpg -o ~/variants/

# Creates directory structure:
# ~/variants/wallpaper/
#   ├── blur.png
#   ├── brightness.png
#   ├── saturation.png
#   ├── vignette.png
#   ├── color_overlay.png
#   ├── grayscale.png
#   └── negate.png
```

### Batch Processing with Preset

```bash
wallpaper-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset dark_blur \
  --parallel 4
```

### Custom Output Format and Quality

```bash
wallpaper-process process -i wallpaper.jpg -o output.webp \
  --preset aesthetic \
  --format webp \
  --quality 90
```

### With Metadata

```bash
wallpaper-process process -i wallpaper.jpg -o output.jpg \
  --preset lockscreen \
  --metadata
```

This creates:
- `output.jpg` - Processed image
- `output_metadata.json` - Processing metadata

## Container Management

### Build Container Image

```bash
wallpaper-process build
```

### Clean Container Resources

```bash
wallpaper-process clean
```

## Architecture

```
wallpaper-orchestrator/
├── Container Registry    # Manages container images
├── Container Builder     # Builds wallpaper-processor container
├── Container Runner      # Executes processing in containers
├── Orchestrator          # Coordinates processing workflow
└── CLI                   # User interface
```

## Development

### Run Tests

```bash
make test
```

### Lint Code

```bash
make lint
```

### Format Code

```bash
make format
```

## License

Part of the dotfiles project.

