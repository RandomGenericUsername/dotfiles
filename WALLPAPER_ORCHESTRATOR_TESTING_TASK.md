# Wallpaper Orchestrator Testing Task - In Progress

## Current Status: BLOCKED - Configuration Error

The wallpaper-orchestrator tool has been successfully installed via the dotfiles installer, but testing revealed a configuration mismatch error that needs to be fixed before the complete flow can be tested.

## Error Details

**Error Message:**
```
AttributeError: 'Settings' object has no attribute 'CONTAINER'
```

**Error Location:**
- File: `src/wallpaper_orchestrator/steps/effects_step.py`, line 46
- Code: `effects_config.container.runtime = ...`

**Root Cause:**
The wallpaper-effects-orchestrator's settings structure doesn't have a `CONTAINER` section. The code is trying to access `effects_config.container.runtime` but the config uses a different structure.

## What Was Completed

### 1. Added Missing Modules to Installer ✅

Added the following modules to both `directories.py` and `install.py`:
- `pipeline` - Pipeline execution framework
- `package-manager` - Package management utilities
- `container-manager` - Docker container management
- `wallpaper-effects-processor` - Image effects processing

**Files Modified:**
- `src/dotfiles-installer/cli/config/directories.py` (lines 80-85)
- `src/dotfiles-installer/cli/src/commands/install.py` (lines 207-213)

### 2. Successfully Ran Dotfiles Installer ✅

The installer successfully:
- Installed all modules to `/home/inumaki/.tmp/inumaki-dotfiles/modules/`
- Installed wallpaper-orchestrator to `/home/inumaki/.tmp/inumaki-dotfiles/tools/wallpaper-orchestrator/`
- Applied settings overrides correctly in `config/settings.toml`
- Created virtual environment with all dependencies

**Verified Installations:**
```bash
/home/inumaki/.tmp/inumaki-dotfiles/
├── modules/
│   ├── container-manager/
│   ├── hyprpaper-manager/
│   ├── logging/
│   ├── pipeline/
│   ├── package-manager/
│   └── wallpaper-effects-processor/
└── tools/
    ├── colorscheme-orchestrator/
    ├── wallpaper-effects-orchestrator/
    └── wallpaper-orchestrator/
```

### 3. Verified Settings Overrides ✅

The installed `config/settings.toml` has correct overrides:
```toml
[orchestrator]
effects_output_dir = "/home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/wallpaper-effects"
colorscheme_output_dir = "/home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/colorschemes"
log_level = "INFO"
verbose = false

[colorscheme]
backend = "pywal"
# ... other settings

[hyprpaper]
monitor = "all"
# ... other settings
```

### 4. Successfully Installed Dependencies ✅

Ran `uv sync` in the installed directory, which successfully installed 45 packages including:
- All local editable dependencies (modules and tools)
- All third-party dependencies (Pillow, Typer, Pydantic, etc.)

### 5. Verified CLI Works ✅

```bash
cd /home/inumaki/.tmp/inumaki-dotfiles/tools/wallpaper-orchestrator
uv run wallpaper-orchestrator --help
# ✅ Shows help with 'process' and 'batch' commands
```

## What Needs to Be Fixed

### Issue: Configuration Structure Mismatch

**Problem:**
The `effects_step.py` is trying to access configuration attributes that don't exist in the wallpaper-effects-orchestrator's settings structure.

**File to Fix:** `src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/steps/effects_step.py`

**Current Code (line 46):**
```python
effects_config.container.runtime = (
    self.config.wallpaper_effects.container_runtime
)
```

**Investigation Needed:**
1. Check the actual structure of wallpaper-effects-orchestrator's settings:
   - File: `src/common/tools/wallpaper-effects-orchestrator/config/settings.toml`
   - File: `src/common/tools/wallpaper-effects-orchestrator/src/wallpaper_effects_orchestrator/config/settings.py`

2. Determine the correct way to pass container runtime settings to the effects orchestrator

3. Check if similar issues exist in other steps:
   - `colorscheme_step.py` (line ~40-50)
   - `wallpaper_step.py` (line ~40-50)

**Possible Solutions:**

**Option A:** The wallpaper-effects-orchestrator doesn't need container runtime to be set dynamically
- Remove the lines that try to set `effects_config.container.runtime`
- The effects orchestrator should use its own config defaults

**Option B:** The settings structure is different
- Check if it's `effects_config.processing.container_runtime` or similar
- Update the code to match the actual structure

**Option C:** Need to create a new config object
- Instead of modifying the loaded config, create a new config object with the desired values
- Pass it to the WallpaperOrchestrator constructor

## Complete Testing Procedure

### Prerequisites Before Testing

1. **Fix the configuration error** (see "What Needs to Be Fixed" section above)

2. **Re-deploy the fix** by running the installer:
   ```bash
   cd /home/inumaki/Development/new/src/dotfiles-installer/cli

   # Enter the CLI development environment
   make dev-shell

   # Inside the dev shell, run the installer
   dotfiles-installer install

   # Or exit the shell and run directly with uv
   exit
   uv run python main.py install -i /tmp/test-dotfiles-install -b /tmp/test-dotfiles-backup -v -L /tmp/test-logs
   ```

3. **Navigate to installed tool**:
   ```bash
   cd /home/inumaki/.tmp/inumaki-dotfiles/tools/wallpaper-orchestrator
   ```

### Step 1: Verify CLI is Working

```bash
# Check help output
uv run wallpaper-orchestrator --help

# Check process command help
uv run wallpaper-orchestrator process --help
```

**Expected Output:**
- Should show commands: `process` and `batch`
- No import errors
- No missing module errors

### Step 2: Test Single Wallpaper Processing

```bash
# Test with verbose output to see detailed logs
uv run wallpaper-orchestrator process \
  -i /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/abstract.jpg \
  -v
```

**Expected Output:**
```
Processing wallpaper: abstract.jpg

INFO     ============================================================
INFO     Wallpaper Orchestration
INFO     ============================================================
INFO     Wallpaper: /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/abstract.jpg
INFO     Effects output: /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/wallpaper-effects
INFO     Colorscheme output: /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/colorschemes
INFO     ============================================================
INFO     Generating effect variants for: ...
INFO     Processing effect: blur
INFO     Processing effect: darken
INFO     Processing effect: lighten
... (more effects)
INFO     Generating color scheme from: ...
INFO     Using backend: pywal
INFO     Setting wallpaper: ...
INFO     Monitor: all

✓ Success: Wallpaper processing complete
```

**What Should Happen:**
1. ✅ **Effects Generation** - Creates multiple effect variants (blur, darken, lighten, etc.)
2. ✅ **Colorscheme Generation** - Extracts colors and creates scheme files
3. ✅ **Wallpaper Setting** - Sets the wallpaper via hyprpaper (if Hyprland is running)
4. ✅ **No Errors** - Process completes without exceptions

### Step 3: Verify Generated Files

```bash
# Check effects directory was created
ls -lh /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/wallpaper-effects/

# Should show multiple effect variants like:
# abstract_blur.png
# abstract_darken.png
# abstract_lighten.png
# abstract_grayscale.png
# etc.

# Check colorscheme directory was created
ls -lh /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/colorschemes/

# Should show colorscheme files like:
# colors.json
# colors.css
# colors.yaml
# colors.sh

# Verify colorscheme content
cat /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/colorschemes/colors.json

# Should show JSON with color palette extracted from wallpaper
```

**Expected File Structure:**
```
/home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/
├── wallpaper-effects/
│   ├── abstract_blur.png
│   ├── abstract_darken.png
│   ├── abstract_lighten.png
│   ├── abstract_grayscale.png
│   ├── abstract_sepia.png
│   └── ... (more effects)
└── colorschemes/
    ├── colors.json
    ├── colors.css
    ├── colors.yaml
    └── colors.sh
```

### Step 4: Test with Different Options

```bash
# Test with custom output directories
uv run wallpaper-orchestrator process \
  -i /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/abstract.jpg \
  --effects-output /tmp/test-effects \
  --colorscheme-output /tmp/test-colors \
  -v

# Verify custom directories were used
ls -lh /tmp/test-effects/
ls -lh /tmp/test-colors/

# Test with different backend (if wallust is installed)
uv run wallpaper-orchestrator process \
  -i /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/abstract.jpg \
  --backend wallust \
  -v

# Test with specific monitor
uv run wallpaper-orchestrator process \
  -i /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/abstract.jpg \
  --monitor DP-1 \
  -v
```

### Step 5: Test Batch Processing (Optional)

```bash
# Process all wallpapers in directory
uv run wallpaper-orchestrator batch \
  -i /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/ \
  -v

# Check that effects were generated for all wallpapers
ls -lh /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/.cache/wallpaper-effects/
```

### Step 6: Test Error Handling

```bash
# Test with non-existent file
uv run wallpaper-orchestrator process -i /tmp/nonexistent.jpg

# Expected: Clear error message about file not found

# Test with invalid file format
echo "not an image" > /tmp/test.txt
uv run wallpaper-orchestrator process -i /tmp/test.txt

# Expected: Clear error message about invalid image format

# Test with missing required argument
uv run wallpaper-orchestrator process

# Expected: Error message about missing --input option
```

### Step 7: Verify Integration with Dependencies

```bash
# Test that all three orchestrators work together:

# 1. Check wallpaper-effects-orchestrator is accessible
cd /home/inumaki/.tmp/inumaki-dotfiles/tools/wallpaper-effects-orchestrator
uv run wallpaper-effects-process --help

# 2. Check colorscheme-orchestrator is accessible
cd /home/inumaki/.tmp/inumaki-dotfiles/tools/colorscheme-orchestrator
uv run colorscheme-orchestrator --help

# 3. Check hyprpaper-manager module is importable
cd /home/inumaki/.tmp/inumaki-dotfiles/modules/hyprpaper-manager
uv run python -c "from hyprpaper_manager import HyprpaperManager; print('✓ Import successful')"
```

### Success Criteria

The testing is successful if:

1. ✅ **CLI works** - All commands show help without errors
2. ✅ **Single wallpaper processing works** - Completes without errors
3. ✅ **Effect variants are generated** - Multiple PNG files created in effects directory
4. ✅ **Colorscheme is generated** - JSON/CSS/YAML/SH files created in colorscheme directory
5. ✅ **Colorscheme contains valid colors** - JSON file has color palette with hex codes
6. ✅ **Custom options work** - Can specify custom output directories
7. ✅ **Error handling works** - Clear error messages for invalid inputs
8. ✅ **All dependencies are accessible** - Can import and run all three orchestrators

### Troubleshooting Common Issues

**Issue: "Module not found" errors**
- Solution: Run `uv sync` in the installed directory to reinstall dependencies

**Issue: "Docker not found" errors**
- Solution: Ensure Docker is installed and running, or check container runtime settings

**Issue: "Hyprpaper IPC connection failed"**
- Solution: This is expected if not running Hyprland. The wallpaper setting step will fail gracefully

**Issue: "Permission denied" errors**
- Solution: Check that output directories are writable

**Issue: Settings not applied**
- Solution: Re-run the installer to ensure settings overrides are applied correctly

## Key Files Reference

### Source Files (Development)
- **Orchestrator:** `src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/orchestrator.py`
- **Effects Step:** `src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/steps/effects_step.py`
- **Colorscheme Step:** `src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/steps/colorscheme_step.py`
- **Wallpaper Step:** `src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/steps/wallpaper_step.py`
- **CLI:** `src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/cli.py`

### Configuration Files
- **Wallpaper Orchestrator Config:** `src/common/tools/wallpaper-orchestrator/config/settings.toml`
- **Effects Orchestrator Config:** `src/common/tools/wallpaper-effects-orchestrator/config/settings.toml`
- **Colorscheme Orchestrator Config:** `src/common/tools/colorscheme-orchestrator/config/settings.toml`

### Installed Files (Testing)
- **Installed Tool:** `/home/inumaki/.tmp/inumaki-dotfiles/tools/wallpaper-orchestrator/`
- **Installed Config:** `/home/inumaki/.tmp/inumaki-dotfiles/tools/wallpaper-orchestrator/config/settings.toml`

### Installer Files
- **Directories Config:** `src/dotfiles-installer/cli/config/directories.py`
- **Install Command:** `src/dotfiles-installer/cli/src/commands/install.py`

## Important Notes

1. **Don't modify installed files** - Always fix issues in the source files (`src/common/tools/wallpaper-orchestrator/`), then re-run the installer

2. **Re-running installer** - To test fixes:
   ```bash
   cd src/dotfiles-installer/cli
   uv run python main.py install -i /tmp/test-dotfiles-install -b /tmp/test-dotfiles-backup -v -L /tmp/test-logs
   ```

3. **Wallpaper location** - Test wallpapers are at: `/home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/`

4. **Dependencies** - The wallpaper-orchestrator depends on:
   - `wallpaper-effects-orchestrator` (generates effect variants)
   - `colorscheme-orchestrator` (generates color schemes)
   - `hyprpaper-manager` (sets wallpapers)
   - All three must be installed for the orchestrator to work

5. **Virtual environment warning** - The warning about `VIRTUAL_ENV` mismatch is harmless and can be ignored

## Next Immediate Action

**Fix the configuration access in `effects_step.py`:**

1. View the wallpaper-effects-orchestrator settings structure:
   ```bash
   cat src/common/tools/wallpaper-effects-orchestrator/config/settings.toml
   ```

2. Check the Pydantic model:
   ```bash
   cat src/common/tools/wallpaper-effects-orchestrator/src/wallpaper_effects_orchestrator/config/settings.py
   ```

3. Update `effects_step.py` to correctly access or not access the container settings

4. Check and fix similar issues in `colorscheme_step.py` and `wallpaper_step.py`

5. Re-run the installer to deploy the fix

6. Test the complete flow again
