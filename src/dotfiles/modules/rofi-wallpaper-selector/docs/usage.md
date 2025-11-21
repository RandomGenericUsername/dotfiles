# Usage Guide

## Basic Usage

### Opening the Wallpaper Selector

Use rofi with the provided configuration:

```bash
rofi -show wallpapers -config ~/.local/share/dotfiles/dotfiles/config/rofi/wallpapers-and-effects-mode.rasi
```

This opens rofi with two modes:
- **wallpapers**: Browse and select wallpapers
- **effects**: Apply effects to current wallpaper

### Selecting a Wallpaper

1. Open rofi with the wallpapers mode
2. Browse wallpapers with thumbnail previews
3. Use arrow keys or type to search
4. Press Enter to select

When you select a wallpaper:
- The wallpaper is set on the focused monitor
- A colorscheme is generated from the wallpaper
- All effect variants are generated and cached

### Applying Effects

1. Switch to the effects mode (sidebar button)
2. Browse available effects with previews
3. Select an effect to apply

When you select an effect:
- The effect is applied to the current wallpaper
- A new colorscheme is generated from the effect
- No new effects are generated (they already exist)

### Reverting to Original

In the effects mode, select "off" to revert to the original wallpaper without effects.

## Advanced Usage

### Custom Monitor

Specify a monitor when calling the selector:

```bash
# For wallpapers
ROFI_RETV=0 rofi-wallpaper-selector wallpapers --monitor DP-1

# For effects
ROFI_RETV=0 rofi-wallpaper-selector effects --monitor HDMI-1
```

### Custom Configuration

Use a custom settings file:

```bash
rofi-wallpaper-selector wallpapers --config /path/to/settings.toml
```

### Keyboard Shortcuts

In rofi:
- **Arrow keys**: Navigate
- **Enter**: Select item
- **Esc**: Close
- **Tab**: Switch between modes (wallpapers/effects)
- **Type**: Search/filter items

## Configuration

### Module Configuration

Edit `~/.local/share/dotfiles/.dependencies/modules/rofi-wallpaper-selector/config/settings.toml`:

```toml
[paths]
wallpapers_dir = "~/.local/share/dotfiles/dotfiles/wallpapers"
effects_cache_dir = "~/.cache/wallpaper/effects"
dotfiles_manager_path = "~/.local/share/dotfiles/.dependencies/modules/manager"

[rofi]
show_icons = true
icon_size = 100
wallpaper_mode_name = "wallpapers"
effect_mode_name = "effects"

[wallpaper]
default_monitor = "focused"
auto_generate_effects = true
auto_generate_colorscheme = true
```

### Rofi Configuration

Edit `~/.local/share/dotfiles/dotfiles/config/rofi/wallpapers-and-effects-mode.rasi`:

- Adjust window size, position, colors
- Modify grid layout (columns, lines)
- Change icon size
- Customize styling

## Integration with Dotfiles Manager

The rofi-wallpaper-selector integrates with dotfiles-manager for state management:

- **Current wallpaper tracking**: Manager tracks which wallpaper is set on each monitor
- **Effect caching**: Effects are cached in the manager's cache directory
- **Colorscheme generation**: Manager coordinates colorscheme generation
- **State persistence**: Wallpaper state persists across sessions

## Troubleshooting

### No wallpapers shown

Check that wallpapers exist in the wallpapers directory:

```bash
ls ~/.local/share/dotfiles/dotfiles/wallpapers/
```

### No effects available

Effects are generated when you first select a wallpaper. If no effects are shown:

1. Select a wallpaper first
2. Wait for effects to generate
3. Switch to effects mode

### Icons not showing

Check rofi configuration:

```toml
[rofi]
show_icons = true
```

And ensure rofi is configured to show icons:

```rasi
configuration {
    show-icons: true;
}
```

### Manager not found

Check that dotfiles-manager is installed:

```bash
ls ~/.local/share/dotfiles/.dependencies/modules/manager/
```

If not installed, run the dotfiles installer.

## Tips

- **Performance**: Effects generation can take time. Be patient on first wallpaper selection.
- **Cache**: Effects are cached, so switching between effects is instant after first generation.
- **Search**: Type to filter wallpapers/effects by name in rofi.
- **Preview**: Hover over items to see larger previews (if rofi supports it).
