# Wallust Backend Implementation Fix

## Problem Summary

The wallust backend implementation in `src/common/modules/colorscheme-generator/src/colorscheme_generator/backends/wallust.py` was fundamentally broken and could never work.

## Root Cause

The implementation assumed wallust outputs JSON to stdout with a `--json` flag:

```python
# BROKEN CODE (lines 129-139)
cmd = [
    "wallust",
    "run",
    str(image_path),
    "--backend",
    self.backend_type,
    "--json",  # ❌ THIS FLAG DOESN'T EXIST!
]

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    check=True,
)
return result.stdout  # ❌ This would always be empty
```

**The problem:** Wallust doesn't have a `--json` flag and doesn't output JSON to stdout. Instead, it writes JSON files to a cache directory, just like pywal does.

## How Pywal Works (The Correct Pattern)

Looking at `src/common/modules/colorscheme-generator/src/colorscheme_generator/backends/pywal.py`:

1. **Run the CLI command** (line 98): `_run_pywal_cli()` runs `wal` command
2. **Read from cache file** (line 105): Reads from `~/.cache/wal/colors.json`
3. **Parse the JSON** (line 115): Parses the JSON from the file
4. **Return ColorScheme** (line 120): Converts to ColorScheme object

Pywal writes to a **fixed location**: `~/.cache/wal/colors.json`

## How Wallust Actually Works

Through Docker container testing, I discovered:

1. **Wallust writes to cache directory**: `~/.cache/wallust/<hash>_<version>/`
2. **Hash is consistent per image**: Same image always produces same hash (e.g., `1wmeif9_1.7` for aurora.jpg)
3. **Filename pattern**: `<Backend>_<Colorspace>_<Threshold>_<Palette>`
   - Example: `Resized_Lch_auto_Dark`
4. **JSON format**: Same format as pywal's `colors.json`

Example cache structure:
```
~/.cache/wallust/
└── 1wmeif9_1.7/
    ├── Resized                      # Raw image data
    ├── Resized_Lch_auto             # Intermediate colors
    └── Resized_Lch_auto_Dark        # Final JSON palette (THIS IS WHAT WE NEED)
```

## The Fix

The wallust backend needs to follow the **exact same pattern as pywal**:

### 1. Run wallust command (writes to cache)

```python
def _run_wallust(self, image_path: Path, config: GeneratorConfig) -> None:
    """Run wallust command to generate colors (writes to cache)."""
    cmd = [
        "wallust",
        "run",
        str(image_path),
        "--backend",
        self.backend_type,
        "-s",  # Skip terminal sequences
        "-T",  # Skip templates
        "-N",  # No config file
        "-q",  # Quiet mode
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
```

### 2. Find the cache file

```python
def _find_cache_file(self, image_path: Path, config: GeneratorConfig) -> Path:
    """Find the wallust cache file for the given image."""
    if not self.cache_dir.exists():
        raise FileNotFoundError(f"Wallust cache directory not found: {self.cache_dir}")

    # Get all cache directories
    cache_dirs = [d for d in self.cache_dir.iterdir() if d.is_dir()]
    if not cache_dirs:
        raise FileNotFoundError(f"No cache directories found in {self.cache_dir}")

    # Get the most recently modified directory (handles the hash)
    latest_cache_dir = max(cache_dirs, key=lambda d: d.stat().st_mtime)

    # Build expected filename: <Backend>_<Colorspace>_<Threshold>_<Palette>
    backend = self.backend_type.capitalize()
    colorspace = "Lch"      # Default colorspace
    threshold = "auto"      # Default threshold
    palette = "Dark"        # Default palette

    filename = f"{backend}_{colorspace}_{threshold}_{palette}"
    cache_file = latest_cache_dir / filename

    # Fallback: if exact filename doesn't exist, try to find any Dark palette file
    if not cache_file.exists():
        dark_files = list(latest_cache_dir.glob("*_Dark"))
        if dark_files:
            cache_file = dark_files[0]
        else:
            raise FileNotFoundError(f"No cache file found in {latest_cache_dir}")

    return cache_file
```

### 3. Read and parse the JSON (same as pywal)

```python
def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
    """Generate color scheme from image using wallust."""
    # ... validation ...

    # Run wallust (writes to cache)
    self._run_wallust(image_path, config)

    # Find and read the cache file
    cache_file = self._find_cache_file(image_path, config)

    if not cache_file.exists():
        raise ColorExtractionError(f"Wallust cache file not found: {cache_file}")

    # Parse JSON from cache file (SAME AS PYWAL)
    with cache_file.open() as f:
        wallust_colors = json.load(f)

    # Convert to ColorScheme
    return self._parse_wallust_output(wallust_colors, image_path)
```

## Key Changes Made

1. ✅ **Added `cache_dir` attribute** (line 48): Points to `~/.cache/wallust/`
2. ✅ **Rewrote `generate()` method** (lines 63-127): Changed from parsing stdout to reading cache files
3. ✅ **Rewrote `_run_wallust()` method** (lines 129-168): Removed `--json` flag, added proper flags
4. ✅ **Added `_find_cache_file()` method** (lines 170-217): Locates the cache file using the hash/version directory structure
5. ✅ **Fixed `ColorExtractionError` calls**: Removed keyword arguments (exception doesn't accept them)

## Testing Commands

To test the fixed implementation:

```bash
# 1. Reinstall dotfiles to copy updated code
cd /home/inumaki/Development/new/src/dotfiles-installer/cli
make dev-shell
dotfiles install

# 2. Test wallust backend
cd /home/inumaki/.tmp/inumaki-dotfiles/tools/colorscheme-orchestrator
uv run colorscheme-gen process \
  -i /home/inumaki/.tmp/inumaki-dotfiles/dotfiles/wallpapers/aurora.jpg \
  --backend wallust \
  --verbose
```

## Expected Performance

Based on Docker testing:
- **Pywal**: ~10-20 seconds per image
- **Wallust**: ~0.15-0.9 seconds per image (10-100x faster!)

## Summary

The original implementation tried to read JSON from stdout (which doesn't exist), when it should have been reading from cache files (just like pywal does). The fix makes wallust follow the exact same pattern as pywal: run the command → read from cache → parse JSON → return ColorScheme.
