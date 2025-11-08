# Wallpaper Cache Manager Tool - Design Concern

**Date:** 2025-11-08
**Project:** Dotfiles System
**Concern Type:** New Tool Implementation
**Layer:** Tools (Upper Layer)

---

## Executive Summary

This document outlines the design concern for implementing a **Wallpaper Cache Manager Tool** that optimizes the wallpaper orchestration workflow by caching previously processed wallpapers. The tool will check if a wallpaper has already been processed (variants generated and color scheme extracted) before invoking the expensive wallpaper orchestrator pipeline.

---

## Problem Statement

### Current Workflow

The current `wallpaper-orchestrator` tool performs three operations sequentially:

1. **Generate Effect Variants** - Creates multiple effect variants (blur, grayscale, negate, etc.) via containerized image processing
2. **Generate Color Scheme** - Extracts color palette from the original wallpaper via containerized backends (pywal/wallust)
3. **Set Wallpaper** - Applies the wallpaper using hyprpaper manager

### Pain Point

**First-time wallpaper processing is extremely slow** due to:
- Container image building/pulling (if not cached)
- Multiple effect variant generation (CPU/GPU intensive)
- Color scheme extraction (image analysis)
- File I/O operations

**Subsequent calls with the same wallpaper repeat all operations unnecessarily**, even though:
- Effect variants already exist on disk
- Color scheme files already exist on disk
- Only the wallpaper setting step is actually needed

### User Need

Users need a **smart caching layer** that:
1. Detects if a wallpaper has been previously processed
2. Skips expensive regeneration if cache is valid
3. Only performs the wallpaper setting operation for cached wallpapers
4. Provides clear feedback about cache hits/misses

---

## Current Architecture Context

### Project Structure

```
src/common/
├── modules/           # Lowest layer - reusable components
│   ├── colorscheme-generator/
│   ├── hyprpaper-manager/
│   ├── wallpaper-effects-processor/
│   ├── pipeline/
│   └── ...
└── tools/            # Upper layer - orchestration tools
    ├── colorscheme-orchestrator/
    ├── wallpaper-effects-orchestrator/
    ├── wallpaper-orchestrator/
    └── [NEW] wallpaper-cache-manager/  ← Proposed tool
```

### Existing Components

#### 1. Wallpaper Orchestrator Tool
- **Location:** `src/common/tools/wallpaper-orchestrator/`
- **Purpose:** Coordinates complete wallpaper setup pipeline
- **Interface:**
  ```python
  class WallpaperOrchestrator:
      def process(
          self,
          wallpaper_path: Path,
          effects_output_dir: Path | None = None,
          colorscheme_output_dir: Path | None = None,
          monitor: str | None = None,
      ) -> WallpaperResult
  ```
- **Returns:** `WallpaperResult` with paths to all generated files

#### 2. WallpaperResult Type
- **Location:** `src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/types.py`
- **Contains:**
  ```python
  @dataclass
  class WallpaperResult:
      original_wallpaper: Path
      effects_output_dir: Path
      colorscheme_output_dir: Path
      effect_variants: dict[str, Path]  # effect_name -> path
      colorscheme_files: dict[str, Path]  # format -> path
      wallpaper_set: bool
      monitor_set: str | None
      timestamp: datetime
      success: bool
      errors: list[str]
  ```

#### 3. Hyprpaper Manager Module
- **Location:** `src/common/modules/hyprpaper-manager/`
- **Purpose:** Manages wallpaper setting via hyprpaper IPC
- **Key Method:**
  ```python
  def set(
      self,
      wallpaper: Path | str,
      monitor: str | MonitorSelector = MonitorSelector.ALL,
      mode: WallpaperMode = WallpaperMode.COVER,
  ) -> None
  ```

#### 4. Current Output Directories
From `wallpaper-orchestrator/config/settings.toml`:
```toml
[orchestrator]
effects_output_dir = "~/.cache/wallpaper/effects"
colorscheme_output_dir = "~/.cache/colorscheme"
```

---

## Proposed Solution

### High-Level Design

Create a new **Wallpaper Cache Manager Tool** that:

1. **Receives:** Wallpaper path (same input as wallpaper-orchestrator)
2. **Checks:** If wallpaper is cached (variants + color scheme exist)
3. **Branches:**
   - **Cache Hit:** Skip orchestration, only set wallpaper, inform user
   - **Cache Miss:** Call wallpaper-orchestrator, cache results

### Cache Detection Strategy

#### Option A: File-Based Detection (Recommended)
Check for existence of expected output files:

```python
def is_cached(wallpaper_path: Path) -> bool:
    """Check if wallpaper has been processed."""
    # 1. Check effect variants exist
    effects_dir = get_effects_dir(wallpaper_path)
    expected_effects = ["blur", "grayscale", "negate", ...]  # From config

    for effect in expected_effects:
        if not (effects_dir / f"{effect}.png").exists():
            return False

    # 2. Check color scheme files exist
    colorscheme_dir = get_colorscheme_dir()
    expected_formats = ["json", "css", "yaml", "sh"]  # From config

    for fmt in expected_formats:
        if not (colorscheme_dir / f"colors.{fmt}").exists():
            return False

    return True
```

**Pros:**
- Simple implementation
- No additional dependencies
- Works with existing file structure
- Stateless (no database needed)

**Cons:**
- Doesn't track metadata (when cached, which backend used, etc.)
- Can't detect partial/corrupted caches easily
- No cache invalidation mechanism

#### Option B: Metadata-Based Detection
Store cache metadata in a lightweight database/file:

```python
# Cache metadata structure
{
    "wallpaper_hash": "sha256_of_file",
    "wallpaper_path": "/path/to/wallpaper.png",
    "cached_at": "2025-11-08T10:30:00",
    "effects_dir": "~/.cache/wallpaper/effects/wallpaper",
    "colorscheme_dir": "~/.cache/colorscheme",
    "effect_variants": ["blur", "grayscale", ...],
    "colorscheme_formats": ["json", "css", ...],
    "backend": "pywal",
    "valid": true
}
```

**Pros:**
- Rich metadata tracking
- Easy cache invalidation
- Can detect file changes via hash
- Better debugging/introspection

**Cons:**
- Requires state management (see Concern #2)
- More complex implementation
- Needs cache consistency management

---

## Key Design Questions

### 1. Cache Key Strategy

**Question:** How do we uniquely identify a cached wallpaper?

**Options:**

**A. File Path (Simple)**
```python
cache_key = str(wallpaper_path.resolve())
```
- ✅ Simple
- ❌ Breaks if file moves
- ❌ Doesn't detect file content changes

**B. File Hash (Robust)**
```python
cache_key = hashlib.sha256(wallpaper_path.read_bytes()).hexdigest()
```
- ✅ Content-based (detects changes)
- ✅ Survives file moves
- ❌ Slower (needs to read entire file)
- ❌ Same image with different paths creates duplicate caches

**C. Hybrid (Path + Modification Time)**
```python
cache_key = f"{wallpaper_path.resolve()}_{wallpaper_path.stat().st_mtime}"
```
- ✅ Fast
- ✅ Detects file changes
- ❌ Breaks if file moves
- ❌ Modification time can change without content change

**Recommendation:** Start with **Option A (File Path)** for simplicity, add Option B later if needed.

### 2. Cache Validation

**Question:** How do we ensure cached files are still valid?

**Scenarios to Handle:**
- User manually deletes some effect variants
- User changes colorscheme backend (pywal → wallust)
- User changes effect configuration
- Disk corruption

**Proposed Validation:**
```python
def validate_cache(wallpaper_path: Path) -> bool:
    """Validate that all expected cache files exist and are readable."""
    try:
        # Check all expected files exist
        if not is_cached(wallpaper_path):
            return False

        # Optional: Check file integrity (can read, not empty)
        for file in get_cached_files(wallpaper_path):
            if file.stat().st_size == 0:
                return False

        return True
    except Exception:
        return False
```

### 3. Cache Invalidation

**Question:** When should we invalidate/rebuild cache?

**Triggers:**
- User explicitly requests rebuild (CLI flag: `--force-rebuild`)
- Configuration changes (different effects, different backend)
- Cached files are missing/corrupted
- Wallpaper file content changed (if using hash-based keys)

**Proposed Interface:**
```python
def process(
    wallpaper_path: Path,
    force_rebuild: bool = False,
    validate_cache: bool = True,
) -> WallpaperResult:
    """Process wallpaper with caching."""
    if force_rebuild:
        return _rebuild_cache(wallpaper_path)

    if validate_cache and not _validate_cache(wallpaper_path):
        return _rebuild_cache(wallpaper_path)

    if is_cached(wallpaper_path):
        return _use_cache(wallpaper_path)

    return _rebuild_cache(wallpaper_path)
```

### 4. Output Directory Structure

**Question:** How should cached files be organized?

**Current Structure:**
```
~/.cache/
├── wallpaper/effects/
│   └── [all effect variants mixed together]
└── colorscheme/
    └── [all colorscheme files]
```

**Problem:** Multiple wallpapers overwrite each other's files!

**Proposed Structure:**
```
~/.cache/
├── wallpaper/effects/
│   ├── wallpaper1/
│   │   ├── blur.png
│   │   ├── grayscale.png
│   │   └── ...
│   └── wallpaper2/
│       ├── blur.png
│       └── ...
└── colorscheme/
    ├── wallpaper1/
    │   ├── colors.json
    │   ├── colors.css
    │   └── ...
    └── wallpaper2/
        └── ...
```

**Naming Strategy:**
```python
def get_cache_subdir(wallpaper_path: Path) -> str:
    """Get subdirectory name for wallpaper cache."""
    # Option 1: Use wallpaper filename (without extension)
    return wallpaper_path.stem

    # Option 2: Use hash (if multiple wallpapers have same name)
    # return hashlib.sha256(str(wallpaper_path).encode()).hexdigest()[:8]
```

---

## Integration Points

### 1. With Wallpaper Orchestrator
```python
# Cache manager wraps orchestrator
from wallpaper_orchestrator import WallpaperOrchestrator

class WallpaperCacheManager:
    def __init__(self):
        self.orchestrator = WallpaperOrchestrator()

    def process(self, wallpaper_path: Path) -> WallpaperResult:
        if self.is_cached(wallpaper_path):
            return self._load_from_cache(wallpaper_path)
        else:
            return self.orchestrator.process(wallpaper_path)
```

### 2. With Hyprpaper Manager
```python
# For cache hits, only set wallpaper
from hyprpaper_manager import HyprpaperManager

def _load_from_cache(self, wallpaper_path: Path) -> WallpaperResult:
    """Load cached result and set wallpaper."""
    # Reconstruct WallpaperResult from cached files
    result = self._build_result_from_cache(wallpaper_path)

    # Only set wallpaper (skip regeneration)
    manager = HyprpaperManager()
    manager.set(wallpaper_path)

    result.wallpaper_set = True
    return result
```

---

## Implementation Considerations

### 1. Tool Structure

Follow existing tool patterns:
```
src/common/tools/wallpaper-cache-manager/
├── config/
│   └── settings.toml
├── src/
│   └── wallpaper_cache_manager/
│       ├── __init__.py
│       ├── manager.py          # Main WallpaperCacheManager class
│       ├── cache.py            # Cache detection/validation logic
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       └── types.py            # CacheStatus, CacheMetadata types
├── pyproject.toml
├── Makefile
└── README.md
```

### 2. Configuration

Add to `config/settings.toml`:
```toml
[cache]
# Enable caching (can disable for debugging)
enabled = true

# Validate cache before using
validate_before_use = true

# Cache directory structure
use_subdirectories = true  # wallpaper1/, wallpaper2/ vs flat

# Cache key strategy
key_strategy = "path"  # "path", "hash", or "hybrid"

[orchestrator]
# Inherit from wallpaper-orchestrator
effects_output_dir = "~/.cache/wallpaper/effects"
colorscheme_output_dir = "~/.cache/colorscheme"
```

### 3. Logging and User Feedback

```python
# Cache hit
logger.info("✓ Wallpaper already cached, skipping regeneration")
logger.info(f"  Effects: {len(cached_effects)} variants")
logger.info(f"  Color schemes: {len(cached_schemes)} formats")
logger.info(f"  Setting wallpaper...")

# Cache miss
logger.info("✗ Wallpaper not cached, processing...")
logger.info("  This may take a while on first run...")
```

---

## Relationship to Concern #2 (State Management)

This concern is **related but separable** from the broader state management concern:

### Can Be Implemented Without State Management
- Use **file-based detection** (Option A)
- Check for file existence on each call
- Stateless operation

### Would Benefit From State Management
- Store cache metadata (when cached, which backend, etc.)
- Track cache statistics (hit rate, last used, etc.)
- Enable advanced features (cache expiration, LRU eviction, etc.)

**Recommendation:** Implement basic file-based caching first, then enhance with state management later if needed.

---

## Success Criteria

### Functional Requirements
- ✅ Detects if wallpaper has been previously processed
- ✅ Skips expensive regeneration for cached wallpapers
- ✅ Sets wallpaper correctly for both cached and uncached cases
- ✅ Provides clear feedback about cache status
- ✅ Supports force rebuild flag

### Performance Requirements
- ✅ Cache detection completes in <100ms
- ✅ Cached wallpaper setting completes in <2s (vs 30-60s for full processing)

### User Experience Requirements
- ✅ Transparent caching (works automatically)
- ✅ Clear logging (user knows what's happening)
- ✅ Reliable (doesn't use stale/corrupted cache)

---

## Open Questions for Refinement

1. **Should cache manager be a wrapper or a replacement?**
   - Wrapper: `wallpaper-cache-manager` calls `wallpaper-orchestrator`
   - Replacement: Merge caching logic into `wallpaper-orchestrator`

2. **How to handle configuration changes?**
   - If user changes effect list, should cache be invalidated?
   - If user changes colorscheme backend, should cache be invalidated?

3. **Should we support partial cache hits?**
   - E.g., effects cached but color scheme missing
   - Regenerate only missing parts vs regenerate everything?

4. **Cache cleanup strategy?**
   - Manual cleanup only?
   - Automatic LRU eviction when cache size exceeds limit?
   - TTL-based expiration?

5. **Multi-wallpaper support?**
   - Current design assumes one wallpaper at a time
   - Should we support caching multiple wallpapers simultaneously?

---

## Next Steps

1. **Decide on cache detection strategy** (file-based vs metadata-based)
2. **Decide on cache key strategy** (path vs hash vs hybrid)
3. **Design output directory structure** (subdirectories per wallpaper)
4. **Implement basic file-based cache manager**
5. **Add CLI interface** (following existing tool patterns)
6. **Test with real wallpapers** (measure performance improvement)
7. **Consider integration with state management** (if Concern #2 is implemented)

---

## References

- Existing wallpaper orchestrator: `src/common/tools/wallpaper-orchestrator/`
- Hyprpaper manager module: `src/common/modules/hyprpaper-manager/`
- Pipeline module: `src/common/modules/pipeline/`
- Project architecture: `dev/scripts/README.md`
