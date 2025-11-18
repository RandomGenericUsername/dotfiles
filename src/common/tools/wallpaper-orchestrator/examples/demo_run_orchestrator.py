#!/usr/bin/env python3
"""Demo script to run wallpaper orchestrator with socket enabled."""

import sys
import time
from pathlib import Path

# Add modules to path
orchestrator_path = Path(__file__).parent / "src"
sys.path.insert(0, str(orchestrator_path))

# Add dependencies to path
for module_name in ["socket", "pipeline", "logging", "state-manager"]:
    module_path = Path(__file__).parent.parent.parent / "modules" / module_name / "src"
    if module_path.exists():
        sys.path.insert(0, str(module_path))

from wallpaper_orchestrator.orchestrator import WallpaperOrchestrator
from wallpaper_orchestrator.config import WallpaperOrchestratorConfig


def run_with_socket(wallpaper_path: Path, socket_dir: Path):
    """Run wallpaper orchestrator with socket enabled."""
    print(f"\n{'='*60}")
    print(f"🚀 Starting Wallpaper Orchestrator with Socket Integration")
    print(f"{'='*60}")
    print(f"Wallpaper: {wallpaper_path}")
    print(f"Socket Dir: {socket_dir}")
    print(f"{'='*60}\n")
    
    try:
        # Create config
        config = WallpaperOrchestratorConfig()
        
        # Create orchestrator with socket enabled
        orchestrator = WallpaperOrchestrator(
            config=config,
            socket_dir=socket_dir
        )
        
        print("⏳ Processing wallpaper (this will send progress updates via socket)...\n")
        
        # Process wallpaper
        result = orchestrator.process(
            wallpaper_path=wallpaper_path,
            force_regenerate=False,
            skip_cache=False,
        )
        
        if result:
            print("\n✅ Wallpaper processing completed successfully!")
            print(f"   Result: {result}")
        else:
            print("\n❌ Wallpaper processing failed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Use first available wallpaper
    wallpaper = Path("/home/inumaki/Pictures/screenshot_1746113584.png")
    
    if not wallpaper.exists():
        print(f"❌ Wallpaper not found: {wallpaper}")
        sys.exit(1)
    
    socket_dir = Path("/tmp/sockets")
    socket_dir.mkdir(parents=True, exist_ok=True)
    
    # Give client time to start
    print("⏳ Waiting 2 seconds for client to connect...")
    time.sleep(2)
    
    run_with_socket(wallpaper, socket_dir)

