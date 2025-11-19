# Daemon Examples

This directory contains example scripts demonstrating the dotfiles daemon event system.

## Examples

### `event_demo.py`
Complete demonstration of the event system with simulated wallpaper change operation.

**Usage:**
```bash
# Make sure daemon is running first
python -m dotfiles_daemon

# In another terminal, run the demo
.venv/bin/python examples/event_demo.py
```

**Shows:**
- Event publishing to daemon
- Real-time event monitoring
- Progress tracking with visual progress bar
- All event types (operation_started, operation_progress, operation_completed)

---

### `monitor.py`
Real-world event monitor that listens for actual wallpaper change events from the WallpaperService.

**Usage:**
```bash
# Make sure daemon is running
python -m dotfiles_daemon

# In another terminal, start the monitor
.venv/bin/python examples/monitor.py

# In a third terminal, trigger a wallpaper change
cd ../../../dotfiles/modules/manager
.venv/bin/dotfiles-manager wallpaper change /path/to/wallpaper.jpg
```

**Shows:**
- Monitoring live events from production code
- Real wallpaper change progress
- Event timestamps and operation IDs

---

## Quick Start

1. **Start the daemon:**
   ```bash
   cd src/common/modules/daemon
   .venv/bin/python -m dotfiles_daemon
   ```

2. **Run the demo:**
   ```bash
   .venv/bin/python examples/event_demo.py
   ```

3. **Monitor real events:**
   ```bash
   .venv/bin/python examples/monitor.py
   ```

