#!/usr/bin/env python3
"""Real-time wallpaper status viewer - socket listener."""

import sys
import time
from pathlib import Path

from dotfiles_socket import SocketType, create_client


def main() -> None:
    """Listen to wallpaper progress socket and display real-time updates."""
    print("🔌 Connecting to wallpaper_progress socket...", flush=True)

    client = create_client(SocketType.UNIX, event_name="wallpaper_progress")

    # Retry connection
    for i in range(30):
        try:
            client.connect()
            print(
                "✓ Connected! Listening for wallpaper status updates...",
                flush=True,
            )
            print("=" * 70, flush=True)
            break
        except Exception:  # noqa: S110
            if i == 0:
                print("⏳ Waiting for orchestrator to start...", flush=True)
            time.sleep(1)
    else:
        print(
            "✗ Timeout: orchestrator not started within 30 seconds",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    try:
        for message in client.receive_iter():
            data = message.data
            step = data.get("step", "Unknown")
            progress = data.get("progress", 0)
            status = data.get("status", "unknown")
            wallpaper = data.get("wallpaper_path", "")
            step_details = data.get("step_details", {})

            # Extract wallpaper filename
            if wallpaper:
                wallpaper = Path(wallpaper).name

            # Format output based on status
            if status == "completed":
                print(f"✓ {step} [{progress:.0f}%] - {wallpaper}", flush=True)
            elif status == "error":
                print(f"✗ ERROR: {step} - {wallpaper}", flush=True)
            else:
                # Processing status - show overall progress
                bar_width = 40
                filled = int(bar_width * progress / 100)
                progress_bar = "█" * filled + "░" * (bar_width - filled)
                print(
                    f"⟳ [{progress_bar}] {progress:.1f}% - {step}", flush=True
                )

                if wallpaper:
                    print(f"   📄 {wallpaper}", flush=True)

                # Show step-level details if available
                if step_details:
                    for step_id, details in step_details.items():
                        internal_progress = details.get("internal_progress", 0)
                        if internal_progress > 0:
                            step_bar_width = 30
                            step_filled = int(
                                step_bar_width * internal_progress / 100
                            )
                            step_bar = "▓" * step_filled + "░" * (
                                step_bar_width - step_filled
                            )
                            progress_str = f"{internal_progress:.1f}%"
                            print(
                                f"      └─ {step_id}: [{step_bar}] "
                                f"{progress_str}",
                                flush=True,
                            )

    except KeyboardInterrupt:
        print("\n\n✓ Stopped listening.", flush=True)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
