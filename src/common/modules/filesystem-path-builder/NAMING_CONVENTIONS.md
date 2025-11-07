# Naming Conventions and Key Storage

**Module:** `filesystem-path-builder`
**Version:** 0.1.0
**Last Updated:** 2025-11-07

---

## Overview

The `filesystem-path-builder` module stores path keys **exactly as registered** without any automatic sanitization or normalization. This design provides explicit control over path naming while maintaining Python compatibility through different access methods.

---

## Key Principles

### 1. **No Automatic Sanitization**

Keys are stored exactly as provided to `add_path()`:

```python
builder.add_path("my-config")      # Stored as: "my-config"
builder.add_path("my_config")      # Stored as: "my_config"
builder.add_path("My Config")      # Stored as: "My Config"
```

These are **three separate paths** - no collision, no conversion.

### 2. **Access Method Determines Syntax**

- **Attribute access**: Requires Python-friendly names (lowercase, underscores, no spaces)
- **Bracket notation**: Works with any name (hyphens, spaces, mixed case)

```python
# Attribute access (Python syntax rules apply)
paths.my_config.path              # ✅ Works if registered as "my_config"
paths.my-config.path              # ❌ SyntaxError (invalid Python)

# Bracket notation (any name works)
paths["my-config"].path           # ✅ Works if registered as "my-config"
paths["my_config"].path           # ✅ Works if registered as "my_config"
paths["My Config"].path           # ✅ Works if registered as "My Config"
```

### 3. **Directory Names Match Keys**

The filesystem directory name matches the registered key:

```python
builder.add_path("oh-my-zsh")     # Creates: oh-my-zsh/
builder.add_path("oh_my_zsh")     # Creates: oh_my_zsh/
```

---

## Recommended Patterns

### Pattern 1: Underscores for Attribute Access (Recommended)

**Use when:** You want clean attribute-based navigation

```python
# Registration
builder.add_path("dotfiles.oh_my_zsh", hidden=True)
builder.add_path("dotfiles.my_scripts", hidden=False)

# Access
paths.dotfiles.oh_my_zsh.path     # → ~/.oh_my_zsh
paths.dotfiles.my_scripts.path    # → /dotfiles/my_scripts
```

**Pros:**
- ✅ Clean attribute access
- ✅ IDE autocomplete works
- ✅ Type hints work

**Cons:**
- ❌ Directory names have underscores (less conventional)

### Pattern 2: Hyphens with Bracket Notation

**Use when:** You want conventional directory names (hyphens)

```python
# Registration
builder.add_path("dotfiles.oh-my-zsh", hidden=True)
builder.add_path("dotfiles.my-scripts", hidden=False)

# Access
paths.dotfiles["oh-my-zsh"].path  # → ~/.oh-my-zsh
paths.dotfiles["my-scripts"].path # → /dotfiles/my-scripts
```

**Pros:**
- ✅ Conventional directory names (hyphens)
- ✅ Matches common naming conventions

**Cons:**
- ❌ Requires bracket notation
- ❌ More verbose

### Pattern 3: Mixed Approach

**Use when:** You have both types of paths

```python
# Registration
builder.add_path("dotfiles.oh-my-zsh", hidden=True)    # Hyphen
builder.add_path("dotfiles.my_scripts", hidden=False)  # Underscore

# Access
paths.dotfiles["oh-my-zsh"].path  # Bracket for hyphens
paths.dotfiles.my_scripts.path    # Attribute for underscores
```

---

## Common Use Cases

### Dotfiles Installation

```python
from filesystem_path_builder import PathsBuilder
from pathlib import Path

builder = PathsBuilder(Path.home())

# Use underscores for attribute access
builder.add_path("dotfiles", hidden=True)
builder.add_path("dotfiles.config", hidden=False)
builder.add_path("dotfiles.scripts", hidden=False)

# Build and use
paths = builder.build()
paths.dotfiles.config.ensure_dir()   # Creates ~/.dotfiles/config
paths.dotfiles.scripts.ensure_dir()  # Creates ~/.dotfiles/scripts
```

### Project Structure

```python
builder = PathsBuilder(Path.cwd())

# Use underscores for clean attribute access
builder.add_path("src")
builder.add_path("src.common")
builder.add_path("src.common.modules")
builder.add_path("tests")

paths = builder.build()
paths.src.common.modules.ensure_dir()
```

### Mixed Naming

```python
builder = PathsBuilder(Path.home() / ".config")

# Some paths use hyphens (conventional names)
builder.add_path("oh-my-zsh", hidden=True)

# Some paths use underscores (attribute access)
builder.add_path("my_scripts", hidden=False)

paths = builder.build()
paths["oh-my-zsh"].ensure_dir()  # Bracket notation
paths.my_scripts.ensure_dir()    # Attribute access
```

---

## Migration from Previous Versions

### If You Were Using Hyphens

**Before (with sanitization):**
```python
builder.add_path("oh-my-zsh")     # Stored as "oh_my_zsh"
paths.oh_my_zsh.path              # Worked (sanitized lookup)
# Created: oh-my-zsh/ (original name preserved)
```

**After (no sanitization):**
```python
# Option 1: Use underscores
builder.add_path("oh_my_zsh")     # Stored as "oh_my_zsh"
paths.oh_my_zsh.path              # Works
# Creates: oh_my_zsh/

# Option 2: Use hyphens with brackets
builder.add_path("oh-my-zsh")     # Stored as "oh-my-zsh"
paths["oh-my-zsh"].path           # Works
# Creates: oh-my-zsh/
```

### Update Checklist

1. **Review all `add_path()` calls**
   - Decide: underscores or hyphens?
   - Update registration to match

2. **Review all path access**
   - If using hyphens: switch to bracket notation
   - If using underscores: attribute access works

3. **Test directory creation**
   - Verify directories are created with expected names
   - Check hidden status is applied correctly

---

## Best Practices

### ✅ DO

- **Be consistent** within a project (all underscores OR all hyphens)
- **Use underscores** if you want attribute access
- **Use hyphens** if you want conventional directory names
- **Document your choice** in project README

### ❌ DON'T

- **Mix hyphens and underscores** for the same logical path
- **Assume sanitization** - keys are stored exactly as provided
- **Use spaces** unless you're okay with bracket notation only

---

## Examples

### Good: Consistent Underscores

```python
builder.add_path("my_app")
builder.add_path("my_app.src")
builder.add_path("my_app.tests")

paths.my_app.src.ensure_dir()
paths.my_app.tests.ensure_dir()
```

### Good: Consistent Hyphens

```python
builder.add_path("my-app")
builder.add_path("my-app.src")
builder.add_path("my-app.tests")

paths["my-app"]["src"].ensure_dir()
paths["my-app"]["tests"].ensure_dir()
```

### Avoid: Inconsistent Mixing

```python
# Confusing - don't do this
builder.add_path("my-app")        # Hyphen
builder.add_path("my-app.src_code")  # Mixed

# Now you need to remember which is which
paths["my-app"]["src_code"]  # Works but confusing
```

---

## Technical Details

### Registry Storage

```python
# Internal registry structure
{
    "my-config": PathDefinition(key="my-config", original_key="my-config", hidden=False),
    "my_config": PathDefinition(key="my_config", original_key="my_config", hidden=False),
}
```

Both keys exist independently - no collision, no conversion.

### Lookup Behavior

```python
# Attribute access
paths.my_config  # Looks up "my_config" in registry

# Bracket access
paths["my-config"]  # Looks up "my-config" in registry
paths["my_config"]  # Looks up "my_config" in registry
```

### Directory Creation

```python
builder.add_path("my-config")
builder.create()
# Creates: /base/my-config/

builder.add_path("my_config")
builder.create()
# Creates: /base/my_config/
```

---

## FAQ

**Q: Can I use both `"my-config"` and `"my_config"` in the same builder?**

A: Yes, they are separate paths. But this is confusing and not recommended.

**Q: What if I need to access a hyphenated path via attribute?**

A: You can't. Use bracket notation or register with underscores.

**Q: Will my old code break?**

A: If you were using hyphens in registration and underscores in access, yes. Update your registration to use underscores.

**Q: Which should I choose: hyphens or underscores?**

A: Underscores for attribute access, hyphens for conventional names. Choose based on your priority.

---

## See Also

- [README.md](README.md) - Module overview and quick start
- [docs/api/](docs/api/) - Complete API documentation
- [docs/guides/](docs/guides/) - Usage guides and examples
