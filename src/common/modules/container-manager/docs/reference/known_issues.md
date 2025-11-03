# Known Issues & Patches

**Module:** `dotfiles-container-manager`
**Version:** 0.1.0

---

## Patches Applied

### 1. Missing `exit_code` field in `ContainerInfo`

**Issue**: The `ContainerInfo` dataclass was missing the `exit_code` field, making it impossible to check container execution status.

**Status**: ✅ Fixed in v0.1.0

**Changes**:
```python
# src/dotfiles_container_manager/core/types.py
@dataclass
class ContainerInfo:
    # ... existing fields ...
    exit_code: int | None = None
    """Exit code (if container has exited)"""
```

```python
# src/dotfiles_container_manager/implementations/docker/container.py
def inspect(self, container: str) -> ContainerInfo:
    # ... existing code ...
    return ContainerInfo(
        # ... existing fields ...
        exit_code=cont_data.get("State", {}).get("ExitCode"),
    )
```

**Usage**:
```python
info = engine.containers.inspect(container_id)
if info.exit_code != 0:
    raise RuntimeError(f"Container failed with exit code {info.exit_code}")
```

---

## Important Behavior Notes

### `detach` Parameter in `run()` Method

**Behavior**: The return value of `run()` depends on the `detach` parameter:
- `detach=True`: Returns container ID (12-character short ID)
- `detach=False`: Returns container stdout as string

**Recommended Pattern for Long-Running Containers**:
```python
# Use detach=True and poll for completion
config = RunConfig(image="my-image", detach=True)
container_id = engine.containers.run(config)

# Poll for completion
import time
while True:
    info = engine.containers.inspect(container_id)
    if info.state in ("exited", "dead", "stopped"):
        break
    time.sleep(0.5)

# Check exit code
if info.exit_code != 0:
    logs = engine.containers.logs(container_id)
    raise RuntimeError(f"Container failed: {logs}")
```

**Why**: Using `detach=False` blocks until completion but doesn't provide access to container ID for inspection or log retrieval if `remove=True` is set.
