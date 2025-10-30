# Patch: Hyphen-to-Underscore Normalization in PathsBuilder

**Date:** 2025-10-29  
**Module:** `filesystem-path-builder`  
**Version:** Post-normalization patch

## Problem Statement

### The Issue

The PathsBuilder module had a critical mismatch between:
1. **Registry keys** defined with hyphens (e.g., `"dotfiles.oh-my-zsh"`)
2. **Python attribute access** which requires underscores (e.g., `dotfiles.oh_my_zsh`)

This caused:
- Registry lookups to fail when accessing paths via attributes
- Incorrect path resolution (missing hidden status, wrong directory names)
- Duplicate directories being created (one from `create()`, one from actual usage)
- Installation checks failing because code looked in the wrong directory

### Real-World Example

In the dotfiles installer, Oh My Zsh was configured as:
```python
_install_builder.add_path("dotfiles.oh-my-zsh", hidden=True)
```

But accessed as:
```python
oh_my_zsh_dir = context.app_config.project.paths.install.dotfiles.oh_my_zsh.path
```

**Result:**
- `create()` created: `.oh-my-zsh/` (empty, from registry)
- Path resolution returned: `oh_my_zsh` (wrong path, registry lookup failed)
- Installer installed to: `oh_my_zsh/` (wrong directory)
- Installation check looked in: `oh_my_zsh/` (failed to find existing installation)
- **Consequence:** Oh My Zsh was reinstalled every time, never detecting existing installations

## Solution

### Design

Normalize registry keys to use underscores while preserving original component names for directory creation:

1. **Registry keys** are normalized (hyphens → underscores) for Python attribute compatibility
2. **Original keys** are preserved to maintain the actual directory names
3. **Lookups** use normalized keys
4. **Directory creation** uses original component names

### Implementation

#### 1. Updated `PathDefinition`

```python
@dataclass
class PathDefinition:
    key: str              # Normalized key: "dotfiles.oh_my_zsh"
    original_key: str     # Original key: "dotfiles.oh-my-zsh"
    hidden: bool = False

    def get_parts(self) -> list[str]:
        """Get path components from original key (preserves hyphens)."""
        return self.original_key.split(".")
```

#### 2. Updated `add_path()`

```python
def add_path(self, key: str, hidden: bool = False) -> "PathsBuilder":
    # Normalize key for registry lookups (hyphens → underscores)
    normalized_key = key.replace("-", "_")
    self.definitions[normalized_key] = PathDefinition(
        key=normalized_key,
        original_key=key,
        hidden=hidden
    )
    return self
```

#### 3. Updated `ManagedPathTree.path` Property

```python
@property
def path(self) -> Path:
    parts = self.rel.parts  # From attribute access: ["dotfiles", "oh_my_zsh"]
    path_components = []
    
    for i in range(len(parts)):
        level_key = ".".join(parts[: i + 1])  # "dotfiles.oh_my_zsh"
        
        if level_key in self._registry:
            definition = self._registry[level_key]
            # Use original component name (preserves hyphens)
            original_parts = definition.get_parts()
            component = original_parts[-1]  # "oh-my-zsh"
            
            if definition.hidden:
                component = f".{component}"
        else:
            component = parts[i]
        
        path_components.append(component)
    
    return self.base / Path(*path_components)
```

#### 4. Updated `create()` Methods

Both `PathsBuilder.create()` and `ManagedPathTree.create()` were updated to normalize the level key before registry lookup:

```python
for key, definition in self.definitions.items():
    parts = definition.get_parts()  # Original parts: ["dotfiles", "oh-my-zsh"]
    
    for i in range(len(parts)):
        level_key_original = ".".join(parts[: i + 1])  # "dotfiles.oh-my-zsh"
        level_key = level_key_original.replace("-", "_")  # "dotfiles.oh_my_zsh"
        component = parts[i]  # "oh-my-zsh"
        
        if level_key in self.definitions and self.definitions[level_key].hidden:
            component = f".{component}"
        
        path_components.append(component)
```

## Usage

### Before the Patch

```python
# Configuration
builder.add_path("dotfiles.oh-my-zsh", hidden=True)

# Access
paths.dotfiles.oh_my_zsh.path
# Returns: /home/user/dotfiles/oh_my_zsh (WRONG!)
# Expected: /home/user/dotfiles/.oh-my-zsh
```

### After the Patch

```python
# Configuration (unchanged - keep hyphens!)
builder.add_path("dotfiles.oh-my-zsh", hidden=True)

# Access (unchanged - use underscores!)
paths.dotfiles.oh_my_zsh.path
# Returns: /home/user/dotfiles/.oh-my-zsh (CORRECT!)
```

## Benefits

1. **Backward Compatible:** Existing code using underscores in attributes continues to work
2. **Preserves Intent:** Directory names maintain their original form (with hyphens)
3. **Fixes Bugs:** Resolves the Oh My Zsh installation check issue and similar problems
4. **Intuitive:** Developers can use natural naming (hyphens) in configuration while using Python-compatible names (underscores) in code

## Migration Guide

### For Existing Code

**No changes required!** The patch is designed to be backward compatible.

If you were working around the issue by using underscores in configuration:
```python
# Old workaround
builder.add_path("dotfiles.oh_my_zsh", hidden=True)
```

You can now use the more natural hyphenated form:
```python
# New recommended approach
builder.add_path("dotfiles.oh-my-zsh", hidden=True)
```

Both will work, but hyphens are more conventional for directory names.

### For New Code

**Recommended pattern:**
- Use hyphens in `add_path()` configuration
- Use underscores in Python attribute access
- The module handles the conversion automatically

```python
# Configuration
builder.add_path("dotfiles.oh-my-zsh", hidden=True)
builder.add_path("dotfiles.my-custom-dir", hidden=False)

# Access
paths.dotfiles.oh_my_zsh.path        # → .oh-my-zsh
paths.dotfiles.my_custom_dir.path    # → my-custom-dir
```

## Testing Recommendations

When updating to this patched version:

1. **Verify directory creation:** Ensure `create()` creates directories with expected names
2. **Verify path resolution:** Ensure `.path` property returns correct paths
3. **Verify hidden status:** Ensure hidden directories get the dot prefix
4. **Test installation checks:** Ensure existing installations are detected correctly

## Related Issues

- **Oh My Zsh Installation Check:** Fixed - installer now correctly detects existing installations
- **Duplicate Directories:** Fixed - only one directory is created with the correct name
- **Path Resolution:** Fixed - paths resolve to the correct directory names

## Files Modified

- `src/common/modules/filesystem-path-builder/src/filesystem_path_builder/builder.py`
  - `PathDefinition` dataclass (lines 28-46)
  - `PathsBuilder.add_path()` method (lines 77-106)
  - `PathsBuilder.create()` method (lines 133-179)
  - `ManagedPathTree.path` property (lines 307-358)
  - `ManagedPathTree.create()` method (lines 225-273)

## Documentation Updates Needed

The following documentation should be updated to reflect this patch:

1. **Module README:** Update examples to show hyphen-to-underscore pattern
2. **API Documentation:** Document the normalization behavior
3. **Migration Guide:** Add to module changelog
4. **User Guide:** Update best practices for naming paths

## Notes

- The normalization is **one-way:** hyphens are converted to underscores for lookups, but original names are preserved
- Only hyphens are normalized; other special characters are not affected
- The patch maintains full backward compatibility with existing code

