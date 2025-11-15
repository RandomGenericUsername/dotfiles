# Hook System

## Overview

The hook system provides an extensible plugin architecture for executing actions after wallpaper changes. Hooks are executed using the dotfiles-pipeline module for consistent error handling and logging.

## Built-in Hooks

### WlogoutIconsHook

Generates wlogout icons and styles after wallpaper change.

**Configuration:**
```toml
[hooks]
enabled = ["wlogout_icons"]

[hooks.wlogout_icons]
color_key = "foreground"  # Color to extract from colorscheme
```

**What it does:**
1. Extracts specified color from colorscheme JSON
2. Renders 6 SVG icon templates with the color:
   - shutdown.svg
   - reboot.svg
   - logout.svg
   - lock.svg
   - suspend.svg
   - hibernate.svg
3. Renders style.css template with:
   - Colors CSS file path
   - Font family and size
   - Background image (wallpaper)
   - Icons directory

**Output:**
- `{install_root}/dotfiles/wlogout/icons/*.svg` - 6 icon files
- `{install_root}/dotfiles/wlogout/style.css` - Style file

## Creating Custom Hooks

### Step 1: Implement HookBase

```python
from pathlib import Path
from dotfiles_manager.hooks.base import HookBase, HookContext, HookResult

class NotificationHook(HookBase):
    """Send notification when wallpaper changes."""

    def __init__(self, config, logger):
        self._config = config
        self._logger = logger

    @property
    def name(self) -> str:
        return "notification"

    def execute(self, context: HookContext) -> HookResult:
        """Send desktop notification."""
        try:
            import subprocess

            message = f"Wallpaper changed to {context.wallpaper_path.name}"
            subprocess.run([
                "notify-send",
                "Dotfiles Manager",
                message,
                "-i", str(context.wallpaper_path)
            ])

            return HookResult(
                success=True,
                message=f"Notification sent: {message}"
            )
        except Exception as e:
            return HookResult(
                success=False,
                message=f"Failed to send notification: {e}"
            )
```

### Step 2: Register Hook

Add to `hooks/registry.py`:

```python
def _create_hooks(self) -> list[HookBase]:
    """Create hook instances from configuration."""
    hooks = []
    enabled_hooks = self._config.hooks.enabled

    if "wlogout_icons" in enabled_hooks:
        hooks.append(self._create_wlogout_hook())

    if "notification" in enabled_hooks:
        hooks.append(NotificationHook(self._config, self._logger))

    return hooks
```

### Step 3: Configure

Add to `config/settings.toml`:

```toml
[hooks]
enabled = ["wlogout_icons", "notification"]
```

## Hook Context

The `HookContext` provides all necessary information to hooks:

```python
@dataclass
class HookContext:
    wallpaper_path: Path          # Original wallpaper path
    monitor: str                  # Monitor name (e.g., "eDP-2")
    colorscheme_json_path: Path   # Path to colors.json
    colorscheme_css_path: Path    # Path to colors.css
    font_family: str              # System font family
    font_size: int                # System font size
```

## Hook Result

Hooks return a `HookResult`:

```python
@dataclass
class HookResult:
    success: bool    # Whether hook executed successfully
    message: str     # Human-readable result message
```

## Hook Execution

Hooks are executed using the pipeline module:

1. **Serial Execution**: Hooks run one after another
2. **Error Handling**: Failures are logged but don't stop other hooks
3. **Result Collection**: All results are collected and returned
4. **Logging**: Each hook execution is logged with timing

### Execution Flow

```python
# In WallpaperService
hook_results = self._hook_registry.execute_all(hook_context)

# Results format:
{
    "wlogout_icons": HookResult(success=True, message="Generated 6 icons and style.css"),
    "notification": HookResult(success=True, message="Notification sent: ...")
}
```

## Best Practices

### 1. Keep Hooks Focused

Each hook should do one thing well:
- ✅ Good: Generate wlogout icons
- ❌ Bad: Generate icons, update configs, restart services

### 2. Handle Errors Gracefully

Always catch exceptions and return appropriate results:

```python
def execute(self, context: HookContext) -> HookResult:
    try:
        # Hook logic
        return HookResult(success=True, message="Success")
    except Exception as e:
        self._logger.error(f"Hook failed: {e}")
        return HookResult(success=False, message=str(e))
```

### 3. Use Configuration

Make hooks configurable via settings.toml:

```python
def __init__(self, config, logger):
    self._config = config
    self._logger = logger
    self._timeout = config.hooks.notification.timeout
```

### 4. Log Appropriately

Use the provided logger for debugging:

```python
self._logger.debug(f"Processing {context.wallpaper_path}")
self._logger.info("Hook completed successfully")
self._logger.error(f"Hook failed: {error}")
```

### 5. Test Hooks

Write tests for your hooks:

```python
def test_notification_hook():
    config = create_test_config()
    logger = create_test_logger()
    hook = NotificationHook(config, logger)

    context = HookContext(
        wallpaper_path=Path("/test/wallpaper.jpg"),
        monitor="eDP-2",
        # ... other fields
    )

    result = hook.execute(context)
    assert result.success
```
