# Wallpaper Orchestrator Step Reordering

## Current Problem

When changing a wallpaper for the first time (not cached), the user waits **~90-150 seconds** before seeing any visual change:

```
Current Order:
1. GenerateEffectsStep()        → 60-90 seconds (Docker container)
2. GenerateColorSchemeStep()    → 30-60 seconds (Docker container)
3. SetWallpaperStep()           → 1-2 seconds (IPC call)

Total wait time: ~90-150 seconds before wallpaper changes
```

This creates a **bad user experience** - the user thinks nothing is happening.

## Solution: Parallel Execution + Wallpaper First

### New Order (Requested)

```python
# File: src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/orchestrator.py
# Lines 177-181

steps = [
    [GenerateColorSchemeStep(), GenerateEffectsStep()],  # Parallel group
    SetWallpaperStep(),                                   # Serial after parallel
]
```

### Execution Flow

```
Step 1 (Parallel): GenerateColorSchemeStep() + GenerateEffectsStep()
├─ GenerateColorSchemeStep()  → 30-60 seconds (runs in parallel)
└─ GenerateEffectsStep()      → 60-90 seconds (runs in parallel)

   Total parallel time: ~60-90 seconds (limited by slowest step)

Step 2 (Serial): SetWallpaperStep()
└─ SetWallpaperStep()         → 1-2 seconds

Total wait time: ~60-92 seconds (40% faster!)
```

## Why This Works

### 1. **Steps are Independent**
- All three steps work on `result.original_wallpaper`
- No data dependencies between steps
- Colorscheme uses original wallpaper (not effect variants)
- Wallpaper setting uses original wallpaper (not effect variants)

### 2. **Pipeline Module Supports Parallel Execution**
- `TaskStep = PipelineStep | list[PipelineStep]` (line 96 in types.py)
- List of steps = parallel group
- Uses `ThreadPoolExecutor` for parallel execution
- Automatically merges contexts from parallel steps

### 3. **Benefits**
- ✅ **40% faster** - Both containers run simultaneously
- ✅ **Better resource usage** - Utilizes multiple CPU cores
- ✅ **Wallpaper + colors change together** - After ~60-90s, both are ready
- ✅ **Cache still works** - Subsequent changes are instant
- ✅ **No code changes to steps** - Just reorder in orchestrator

## Implementation

### File to Modify
`src/common/tools/wallpaper-orchestrator/src/wallpaper_orchestrator/orchestrator.py`

### Change Required

**Before (Lines 177-181):**
```python
# Define pipeline steps (all serial)
steps = [
    GenerateEffectsStep(),
    GenerateColorSchemeStep(),
    SetWallpaperStep(),
]
```

**After:**
```python
# Define pipeline steps (parallel + serial)
steps = [
    [GenerateColorSchemeStep(), GenerateEffectsStep()],  # Parallel group
    SetWallpaperStep(),                                   # Serial
]
```

### Update Comment (Line 176)
```python
# Before:
# Define pipeline steps (all serial)

# After:
# Define pipeline steps (parallel generation, then set wallpaper)
```

## Testing

After making the change:

1. **Clear cache** (to test first-time experience):
   ```bash
   rm -rf ~/.cache/wallpaper/
   ```

2. **Test wallpaper change**:
   ```bash
   dotfiles-manager change-wallpaper /path/to/wallpaper.png
   ```

3. **Expected behavior**:
   - Wait ~60-90 seconds (instead of ~90-150s)
   - Wallpaper changes
   - Colors are already applied
   - Effects are already generated

4. **Test cached wallpaper** (should still be instant):
   ```bash
   dotfiles-manager change-wallpaper /path/to/same-wallpaper.png
   ```
   - Should complete in ~1-2 seconds (from cache)

## Notes

- **Resource usage**: Two Docker containers will run simultaneously (higher CPU/memory usage during generation)
- **Cache behavior**: Unchanged - cache still works perfectly
- **Error handling**: Pipeline handles parallel errors correctly (AND logic by default)
- **Context merging**: Pipeline automatically merges results from both parallel steps
