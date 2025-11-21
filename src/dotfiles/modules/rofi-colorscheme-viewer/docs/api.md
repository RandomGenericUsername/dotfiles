# API Reference

## CLI Entry Point

### `main()`

Main entry point for the rofi-colorscheme-viewer command.

**Environment Variables:**
- `ROFI_RETV`: Rofi return value (0 = list mode, 1 = selection mode)

**Arguments:**
- `$1`: Selected item (only in selection mode)

**Example:**
```bash
# List mode
ROFI_RETV=0 rofi-colorscheme-viewer

# Selection mode
echo "Background  #1a1b26" | ROFI_RETV=1 rofi-colorscheme-viewer
```

## ColorschemeViewer

Main viewer class that handles colorscheme display and interaction.

### `__init__(config: ViewerConfig)`

Initialize the viewer with configuration.

**Parameters:**
- `config`: ViewerConfig object with paths and settings

### `show_menu(highlight_index: int = 0, reload: bool = False) -> None`

Display the colorscheme menu in rofi.

**Parameters:**
- `highlight_index`: Index of item to highlight (0-based)
- `reload`: Whether this is a reload operation (emits reload commands)

**Behavior:**
- Emits metadata header
- Emits format selector
- Emits color entries with swatches
- If reload=True, emits reload commands to refresh rofi without closing

**Example:**
```python
viewer = ColorschemeViewer(config)
viewer.show_menu()  # Initial display
viewer.show_menu(highlight_index=0, reload=True)  # Reload with format selector highlighted
```

### `handle_selection(selected: str) -> None`

Handle user selection from rofi.

**Parameters:**
- `selected`: The selected item text

**Behavior:**
- If format selector: cycles format and reloads menu
- If color: extracts color value and copies to clipboard

**Example:**
```python
viewer.handle_selection("🎨 Format: [✓] Hex  [ ] RGB  [ ] JSON")  # Cycles format
viewer.handle_selection("Background  #1a1b26")  # Copies #1a1b26 to clipboard
```

### `get_color_entries() -> list[tuple[str, str, tuple[int, int, int]]]`

Get list of color entries from the colorscheme.

**Returns:**
- List of tuples: (name, hex_value, rgb_value)

**Example:**
```python
entries = viewer.get_color_entries()
# [
#   ("Background", "#1a1b26", (26, 27, 38)),
#   ("Foreground", "#c0caf5", (192, 202, 245)),
#   ...
# ]
```

### `get_metadata_text() -> str`

Get formatted metadata text for the header.

**Returns:**
- Formatted string with source image, backend, and generation time

**Example:**
```python
text = viewer.get_metadata_text()
# "Source: mountain.png | Backend: pywal | Generated: 2024-01-15 14:30:22"
```

### `get_format_selector_text() -> str`

Get formatted format selector text with checkboxes.

**Returns:**
- Formatted string showing current format selection

**Example:**
```python
text = viewer.get_format_selector_text()
# "🎨 Format: [✓] Hex  [ ] Rgb  [ ] Json"
```

## StateManager

Manages format selection state persistence.

### `__init__(state_file: Path)`

Initialize state manager with state file path.

**Parameters:**
- `state_file`: Path to JSON state file

### `get_current_format() -> str`

Get the currently selected format.

**Returns:**
- Format name ("hex", "rgb", or "json")

**Example:**
```python
manager = StateManager(Path("/tmp/state.json"))
format = manager.get_current_format()  # "hex"
```

### `set_format(format_name: str) -> None`

Set the current format.

**Parameters:**
- `format_name`: Format to set ("hex", "rgb", or "json")

**Example:**
```python
manager.set_format("rgb")
```

### `cycle_format() -> str`

Cycle to the next format.

**Returns:**
- New format name

**Example:**
```python
current = manager.cycle_format()  # "hex" -> "rgb" -> "json" -> "hex"
```

## SwatchGenerator

Generates color swatch images using ImageMagick.

### `__init__(temp_dir: Path, swatch_size: int = 100)`

Initialize swatch generator.

**Parameters:**
- `temp_dir`: Directory for swatch images
- `swatch_size`: Size of swatches in pixels

### `generate(hex_color: str) -> Path`

Generate a swatch for the given color.

**Parameters:**
- `hex_color`: Hex color value (e.g., "#1a1b26")

**Returns:**
- Path to generated swatch image

**Example:**
```python
generator = SwatchGenerator(Path("/tmp/swatches"))
swatch_path = generator.generate("#1a1b26")
# /tmp/swatches/swatch_1a1b26.png
```

## FormatConverter

Converts colors between different formats.

### `format_color(hex_value: str, rgb_value: tuple[int, int, int], format_name: str) -> str`

Format a color in the specified format.

**Parameters:**
- `hex_value`: Hex color value
- `rgb_value`: RGB tuple (r, g, b)
- `format_name`: Target format ("hex", "rgb", or "json")

**Returns:**
- Formatted color string

**Example:**
```python
converter = FormatConverter()
hex_str = converter.format_color("#1a1b26", (26, 27, 38), "hex")     # "#1a1b26"
rgb_str = converter.format_color("#1a1b26", (26, 27, 38), "rgb")     # "rgb(26, 27, 38)"
json_str = converter.format_color("#1a1b26", (26, 27, 38), "json")   # '{"r": 26, "g": 27, "b": 38}'
```

## RofiFormatter

Formats output for rofi script mode.

### `item(label: str, icon_path: str | None = None) -> str`

Format an item for rofi.

**Parameters:**
- `label`: Item label text
- `icon_path`: Optional path to icon image

**Returns:**
- Formatted rofi item string

**Example:**
```python
formatter = RofiFormatter()
item = formatter.item("Background  #1a1b26", icon_path="/tmp/swatch.png")
```

### `message(text: str) -> str`

Format a message for rofi header.

**Parameters:**
- `text`: Message text

**Returns:**
- Formatted rofi message string

### `keep_selection() -> str`

Emit command to keep current selection during reload.

### `new_selection(index: int) -> str`

Emit command to set highlighted item during reload.

**Parameters:**
- `index`: 0-based index of item to highlight

### `reload() -> str`

Emit command to reload rofi menu.
