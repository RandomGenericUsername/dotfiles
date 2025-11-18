#!/usr/bin/env python3
"""Test the socket manager directly."""

import sys
import time
from pathlib import Path

# Add socket module to path
socket_module_path = (
    Path(__file__).parent.parent.parent / "modules" / "socket" / "src"
)
sys.path.insert(0, str(socket_module_path))

# Import socket_manager module directly without going through __init__
socket_manager_file = (
    Path(__file__).parent
    / "src"
    / "wallpaper_orchestrator"
    / "socket_manager.py"
)
import importlib.util

spec = importlib.util.spec_from_file_location(
    "socket_manager", socket_manager_file
)
socket_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(socket_manager)

WallpaperProgressSocketManager = socket_manager.WallpaperProgressSocketManager


def test_socket_manager():
    """Test socket manager basic functionality."""
    print("\n" + "=" * 60)
    print("Testing WallpaperProgressSocketManager")
    print("=" * 60 + "\n")

    socket_dir = Path("/tmp/sockets")
    socket_dir.mkdir(parents=True, exist_ok=True)

    # Create socket manager
    print("1. Creating socket manager...")
    manager = WallpaperProgressSocketManager(
        event_name="test_progress", socket_dir=socket_dir
    )
    print("   ✅ Socket manager created\n")

    # Test context manager
    print("2. Testing context manager (start/stop)...")
    with manager:
        print("   ✅ Socket server started")
        print(f"   📍 Socket path: {socket_dir / 'test_progress.sock'}")

        # Send some test progress updates
        print("\n3. Sending test progress updates...")
        for i in range(5):
            progress = (i + 1) * 20
            manager.send_progress(
                step_name=f"Step {i + 1}",
                progress_percent=progress,
                status="processing",
                extra_data={"step_index": i, "total_steps": 5},
            )
            print(f"   📤 Sent: Step {i + 1} - {progress}%")
            time.sleep(0.2)

        print("\n4. Sending completion message...")
        manager.send_progress(
            step_name="Complete",
            progress_percent=100.0,
            status="completed",
            extra_data={"message": "All steps completed!"},
        )
        print("   ✅ Completion message sent")

        time.sleep(0.5)

    print("\n   ✅ Socket server stopped\n")

    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60 + "\n")

    print("Note: No clients were connected, but the socket manager")
    print("      successfully started, sent messages, and stopped.")
    print("      Messages are queued for when clients connect.\n")


if __name__ == "__main__":
    try:
        test_socket_manager()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
