#!/usr/bin/env python3
"""Demo showing socket manager with connected client."""

import sys
import threading
import time
from pathlib import Path

# Add socket module to path
socket_module_path = (
    Path(__file__).parent.parent.parent / "modules" / "socket" / "src"
)
sys.path.insert(0, str(socket_module_path))

# Import socket_manager module directly
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

from dotfiles_socket import MessageType, SocketType, create_client

WallpaperProgressSocketManager = socket_manager.WallpaperProgressSocketManager


def run_client(socket_dir, event_name="demo_progress"):
    """Run socket client to receive progress updates."""
    print("\n" + "=" * 60)
    print("🎧 SOCKET CLIENT - Listening for Progress Updates")
    print("=" * 60 + "\n")

    try:
        client = create_client(
            SocketType.UNIX, event_name, socket_dir=socket_dir
        )

        # Wait for server to start
        for i in range(10):
            try:
                client.connect()
                print("✅ Connected to socket server!\n")
                break
            except:
                time.sleep(0.3)

        # Receive messages
        for message in client.receive_iter():
            if message.message_type == MessageType.DATA:
                data = message.data
                progress = data.get(
                    "progress", 0
                )  # Note: socket_manager sends "progress"
                step_name = data.get(
                    "step", "Unknown"
                )  # Note: socket_manager sends "step"
                status = data.get("status", "processing")

                # Progress bar
                bar_length = 40
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)

                print(f"[{bar}] {progress:5.1f}% | {step_name} ({status})")

                if status == "completed":
                    print("\n✅ Processing completed!")
                    break

        client.disconnect()
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print(f"❌ Client error: {e}")


def run_server(socket_dir, event_name="demo_progress"):
    """Run socket server and send progress updates."""
    print("\n" + "=" * 60)
    print("📡 SOCKET SERVER - Sending Progress Updates")
    print("=" * 60 + "\n")

    # Give client time to connect
    time.sleep(1)

    manager = WallpaperProgressSocketManager(
        event_name=event_name, socket_dir=socket_dir
    )

    with manager:
        print("✅ Socket server started\n")
        print("📤 Simulating wallpaper processing pipeline...\n")

        steps = [
            ("Generating color scheme", 0, 33.3),
            ("Creating wallpaper effects", 33.3, 66.6),
            ("Applying wallpaper via hyprpaper", 66.6, 100.0),
        ]

        for step_name, start_progress, end_progress in steps:
            # Simulate step processing with incremental progress
            for progress in range(
                int(start_progress), int(end_progress) + 1, 5
            ):
                manager.send_progress(
                    step_name=step_name,
                    progress_percent=float(progress),
                    status="processing",
                    extra_data={"step": step_name},
                )
                time.sleep(0.1)

        # Send completion
        manager.send_progress(
            step_name="Complete",
            progress_percent=100.0,
            status="completed",
            extra_data={"message": "Wallpaper change completed!"},
        )

        time.sleep(0.5)
        print("\n✅ Socket server stopped\n")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    socket_dir = Path("/tmp/sockets")
    socket_dir.mkdir(parents=True, exist_ok=True)
    event_name = "demo_progress"

    print("\n" + "=" * 60)
    print("🚀 Socket Integration Demo - Client + Server")
    print("=" * 60)

    # Start client in background thread
    client_thread = threading.Thread(
        target=run_client, args=(socket_dir, event_name)
    )
    client_thread.start()

    # Run server in main thread
    run_server(socket_dir, event_name)

    # Wait for client to finish
    client_thread.join()

    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60 + "\n")
