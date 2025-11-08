# Colorscheme Orchestrator Scripts

Utility scripts for maintaining and managing the colorscheme orchestrator tool.

---

## Available Scripts

### `rebuild_backend.py`

Rebuild container images for colorscheme backends with the latest version of the colorscheme-generator module.

**Usage:**

```bash
# Via Makefile (recommended)
make rebuild-wallust        # Rebuild wallust container
make rebuild-pywal          # Rebuild pywal container
make rebuild-all-backends   # Rebuild all backend containers
make list-backends          # List available backends

# Direct script usage
python scripts/rebuild_backend.py wallust              # Rebuild wallust
python scripts/rebuild_backend.py pywal                # Rebuild pywal
python scripts/rebuild_backend.py --all                # Rebuild all backends
python scripts/rebuild_backend.py wallust --no-cache   # Force clean rebuild
python scripts/rebuild_backend.py --all --verbose      # Verbose output
```

**When to use:**

- ✅ After modifying the `colorscheme-generator` module
- ✅ After fixing bugs in backend integration
- ✅ When container is behaving unexpectedly
- ✅ After updating backend dependencies

**Options:**

- `--all` - Rebuild all backend containers
- `--no-cache` - Force clean rebuild without using Docker cache
- `-v, --verbose` - Enable verbose output with detailed progress

---

## Development Workflow

### Typical Development Cycle

1. **Make changes** to colorscheme-generator module
   ```bash
   cd src/common/modules/colorscheme-generator
   # Edit code...
   ```

2. **Test changes** locally (if possible)
   ```bash
   make test
   ```

3. **Rebuild affected containers**
   ```bash
   cd src/common/tools/colorscheme-orchestrator
   make rebuild-wallust  # Or whichever backend you're testing
   ```

4. **Test the orchestrator** with rebuilt container
   ```bash
   # Test via CLI or Python
   ```

### Clean Rebuild

If you encounter issues or want to ensure a completely fresh build:

```bash
# Clean rebuild without cache
python scripts/rebuild_backend.py wallust --no-cache

# Or via Makefile (add NO_CACHE=1)
NO_CACHE=1 make rebuild-wallust
```

---

## Container Architecture

The colorscheme orchestrator uses containerized backends for isolation and reproducibility:

```
colorscheme-orchestrator/
├── containers/
│   ├── pywal/
│   │   ├── Dockerfile
│   │   └── entrypoint.py
│   ├── wallust/
│   │   ├── Dockerfile
│   │   └── entrypoint.py
│   └── custom/
│       ├── Dockerfile
│       └── entrypoint.py
└── scripts/
    └── rebuild_backend.py  ← This script
```

Each container:
- Includes the `colorscheme-generator` module
- Has a specific backend installed (pywal, wallust, etc.)
- Runs in isolation with mounted input/output directories
- Is rebuilt when the module changes

---

## Troubleshooting

### Container build fails

**Problem:** Build fails with dependency errors

**Solution:**
```bash
# Try clean rebuild
python scripts/rebuild_backend.py wallust --no-cache --verbose

# Check Docker/Podman is running
docker ps  # or: podman ps
```

### Module not found errors

**Problem:** Container can't find colorscheme-generator module

**Solution:**
- Ensure the module exists at `src/common/modules/colorscheme-generator`
- Check the module is properly structured with `pyproject.toml`
- Rebuild with `--verbose` to see build logs

### Old container still being used

**Problem:** Changes not reflected after rebuild

**Solution:**
```bash
# Force rebuild
python scripts/rebuild_backend.py wallust --no-cache

# Or manually remove old images
docker images | grep colorscheme
docker rmi <image-id>
```

---

## Adding New Scripts

When adding new utility scripts to this directory:

1. **Follow naming convention:** `verb_noun.py` (e.g., `rebuild_backend.py`, `test_container.py`)
2. **Add shebang:** `#!/usr/bin/env python3`
3. **Add docstring:** Describe purpose and usage
4. **Add to Makefile:** Expose via make target
5. **Update this README:** Document the new script

**Example Makefile target:**

```makefile
my-target: ensure-sync ## Description of what it does
	@echo "Running my script..."
	@uv run python scripts/my_script.py
	@echo "✅ Done"
```

---

## See Also

- [Colorscheme Orchestrator README](../README.md)
- [Colorscheme Generator Module](../../../modules/colorscheme-generator/)
- [Container Manager Module](../../../modules/container-manager/)
