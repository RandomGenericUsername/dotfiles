# Architecture

## Overview

The rofi-colorscheme-viewer is a rofi script mode application that displays colorschemes with visual swatches and supports multiple output formats.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Rofi UI                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Format: [✓] Hex  [ ] RGB  [ ] JSON                   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ [■] Background    #1a1b26                            │   │
│  │ [■] Foreground    #c0caf5                            │   │
│  │ [■] Color 0       #15161e                            │   │
│  │ ...                                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      CLI Entry Point                        │
│                      (cli.py)                               │
│  • Checks ROFI_RETV environment variable                    │
│  • Routes to list mode or selection mode                    │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│     List Mode            │  │   Selection Mode         │
│   (ROFI_RETV=0)          │  │   (ROFI_RETV=1)          │
│  • Show menu             │  │  • Handle selection      │
│  • Display colors        │  │  • Copy to clipboard     │
│  • Format selector       │  │  • Or cycle format       │
└──────────────────────────┘  └──────────────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  ColorschemeViewer                          │
│                  (viewer/colorscheme_viewer.py)             │
│  • show_menu() - Emit rofi items                            │
│  • handle_selection() - Process user selection              │
│  • get_color_entries() - Extract colors from colorscheme    │
│  • get_metadata_text() - Format metadata header             │
│  • get_format_selector_text() - Format selector display     │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│StateManager  │  │SwatchGenerator   │  │FormatConverter   │
│(state_       │  │(swatch_          │  │(format_          │
│manager.py)   │  │generator.py)     │  │converter.py)     │
│              │  │                  │  │                  │
│• Persist     │  │• Generate color  │  │• Convert colors  │
│  format      │  │  swatches with   │  │  to hex/rgb/json │
│  selection   │  │  ImageMagick     │  │                  │
│• Cycle       │  │• Cache in temp   │  │                  │
│  formats     │  │  directory       │  │                  │
└──────────────┘  └──────────────────┘  └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │RofiFormatter     │
                  │(rofi_            │
                  │formatter.py)     │
                  │                  │
                  │• Format items    │
                  │• Escape sequences│
                  │• Reload commands │
                  └──────────────────┘
```

## Data Flow

### List Mode (ROFI_RETV=0)

```
User launches rofi
    ↓
CLI checks ROFI_RETV=0
    ↓
ColorschemeViewer.show_menu()
    ↓
Load colorscheme from JSON file
    ↓
Get current format from StateManager
    ↓
Generate format selector text
    ↓
For each color:
    ├─ Generate swatch with SwatchGenerator
    ├─ Convert to current format with FormatConverter
    └─ Format as rofi item with RofiFormatter
    ↓
Emit all items to stdout
    ↓
Rofi displays items
```

### Selection Mode (ROFI_RETV=1)

```
User clicks item in rofi
    ↓
CLI checks ROFI_RETV=1
    ↓
Read selected item from $1 argument
    ↓
ColorschemeViewer.handle_selection(selected)
    ↓
Is format selector?
    ├─ Yes: StateManager.cycle_format()
    │       ↓
    │   show_menu(reload=True)
    │       ↓
    │   Emit reload commands
    │       ↓
    │   Rofi refreshes without closing
    │
    └─ No: Extract color value
            ↓
        Copy to clipboard with wl-copy
            ↓
        Exit (rofi closes)
```

## Key Design Patterns

### Rofi Reload Mechanism

The module uses rofi's reload mechanism for seamless format switching:

```python
# Emit reload commands
sys.stdout.write("\x00keep-selection\x1ftrue\n")
sys.stdout.write("\x00new-selection\x1f0\n")  # Highlight format selector
sys.stdout.write("\x00reload\x1f1\n")
```

This allows the UI to update without closing and reopening rofi.

### State Persistence

Format selection is persisted to a state file so it's remembered across invocations:

```python
# State file: /tmp/rofi-colorscheme-viewer/state.json
{
  "current_format": "rgb"
}
```

### On-the-Fly Swatch Generation

Color swatches are generated dynamically using ImageMagick:

```bash
convert -size 100x100 xc:#1a1b26 /tmp/rofi-colorscheme-viewer/swatch_1a1b26.png
```

Swatches are cached in the temp directory and reused if they already exist.

## Module Structure

```
src/rofi_colorscheme_viewer/
├── cli.py                      # Entry point
├── config/
│   ├── config.py               # Pydantic models
│   └── __init__.py
├── utils/
│   ├── format_converter.py    # Color format conversion
│   ├── rofi_formatter.py      # Rofi output formatting
│   ├── swatch_generator.py    # ImageMagick swatch generation
│   └── __init__.py
└── viewer/
    ├── colorscheme_viewer.py  # Main viewer class
    ├── state_manager.py       # Format state persistence
    └── __init__.py
```

## Configuration System

Uses Dynaconf for configuration management:

```
config/settings.toml → Dynaconf → Pydantic Models → Application
```

Configuration can be overridden via environment variables:

```bash
ROFI_COLORSCHEME_VIEWER_PATHS__COLORSCHEME_FILE=/path/to/colors.json rofi-colorscheme-viewer
```

## Dependencies

- **colorscheme-generator**: Provides `ColorScheme` data structure
- **ImageMagick**: Generates color swatches
- **wl-clipboard**: Copies colors to clipboard
- **rofi**: Provides the UI framework
