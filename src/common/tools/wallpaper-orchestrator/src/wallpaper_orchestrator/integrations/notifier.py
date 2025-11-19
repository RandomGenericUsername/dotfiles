#!/usr/bin/env python3
"""
Wallpaper Progress Notifier

Listens to wallpaper_progress socket and displays real-time notifications
with progress bar, wallpaper path, and current step.

Supports dunstify, mako, and GNOME Shell notification systems.

Usage:
    # Run as a module:
    uv run python -m wallpaper_orchestrator.integrations.notifier \\
        [--socket-dir /tmp/sockets]

    # Or run directly:
    uv run python src/wallpaper_orchestrator/integrations/notifier.py \\
        [--socket-dir /tmp/sockets]
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

from dotfiles_socket import SocketType, create_client

# Global notification ID tracker
_notification_id: int | None = None


# Detect notification backend
def detect_notification_backend() -> str:
    """Detect which notification system is available."""
    # Check if dunstify is available (preferred - works with any daemon)
    try:
        result = subprocess.run(
            ["which", "dunstify"],
            capture_output=True,
            timeout=2,
        )
        if result.returncode == 0:
            return "dunstify"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check if mako is running (Wayland/Hyprland)
    try:
        result = subprocess.run(
            ["pgrep", "-x", "mako"],
            capture_output=True,
            timeout=2,
        )
        if result.returncode == 0:
            return "mako"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check if GNOME Shell is running
    try:
        result = subprocess.run(
            [
                "gdbus",
                "call",
                "--session",
                "--dest",
                "org.freedesktop.Notifications",
                "--object-path",
                "/org/freedesktop/Notifications",
                "--method",
                "org.freedesktop.Notifications.GetServerInformation",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and "gnome-shell" in result.stdout.lower():
            return "gnome"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback to notify-send
    return "notify-send"


# Will be set in main()
NOTIFICATION_BACKEND: str = ""


def send_notification(
    title: str,
    message: str,
    progress: int | None = None,
    icon: str = "image-x-generic",
    urgency: str = "normal",
) -> None:
    """
    Send a notification with optional progress bar.

    Automatically uses the detected notification backend
    (mako/dunst/gnome/notify-send).

    Args:
        title: Notification title
        message: Notification message
        progress: Progress percentage (0-100), None for no progress bar
        icon: Icon name from /usr/share/icons
        urgency: Urgency level (low, normal, critical)
    """
    global _notification_id

    # Clamp progress to 0-100
    if progress is not None:
        progress = max(0, min(100, int(progress)))

    if NOTIFICATION_BACKEND == "dunstify":
        _send_dunstify_notification(title, message, progress, icon, urgency)
    elif NOTIFICATION_BACKEND == "mako":
        _send_mako_notification(title, message, progress, icon, urgency)
    elif NOTIFICATION_BACKEND == "gnome":
        _send_gnome_notification(title, message, progress, icon, urgency)
    else:
        _send_notify_send(title, message, icon, urgency)


def _send_mako_notification(
    title: str, message: str, progress: int | None, icon: str, urgency: str
) -> None:
    """Send notification using mako (makoctl)."""
    global _notification_id

    cmd = [
        "notify-send",
        "-a",
        "wallpaper-orchestrator",
        "-i",
        icon,
        "-u",
        urgency,
    ]

    # Mako supports progress hints via notify-send
    if progress is not None:
        cmd.extend(["-h", f"int:value:{progress}"])

    # Use category for grouping/replacing notifications
    cmd.extend(["-c", "wallpaper-progress"])

    cmd.extend([title, message])

    try:
        subprocess.run(cmd, check=False, capture_output=True)
    except FileNotFoundError:
        print("Error: notify-send not found.", file=sys.stderr)
        sys.exit(1)


def _send_dunstify_notification(
    title: str, message: str, progress: int | None, icon: str, urgency: str
) -> None:
    """Send notification using dunstify (works with any daemon)."""
    global _notification_id

    cmd = [
        "dunstify",
        "-a",
        "wallpaper-orchestrator",
        "-i",
        icon,
        "-u",
        urgency,
    ]

    # Use --replace if we have an ID, otherwise use --printid to get one
    if _notification_id is not None:
        cmd.extend(["-r", str(_notification_id)])
    else:
        cmd.append("-p")

    if progress is not None:
        cmd.extend(["-h", f"int:value:{progress}"])

    cmd.extend([title, message])

    try:
        result = subprocess.run(
            cmd, check=False, capture_output=True, text=True
        )

        # If this was the first notification, save the ID
        if _notification_id is None and result.stdout.strip():
            _notification_id = int(result.stdout.strip())
    except FileNotFoundError:
        print("Error: dunstify not found.", file=sys.stderr, flush=True)
        sys.exit(1)


def _send_gnome_notification(
    title: str, message: str, progress: int | None, icon: str, urgency: str
) -> None:
    """Send notification using GNOME Shell (notify-send)."""
    cmd = [
        "notify-send",
        "-a",
        "wallpaper-orchestrator",
        "-i",
        icon,
        "-u",
        urgency,
    ]

    if progress is not None:
        cmd.extend(["-h", f"int:value:{progress}"])

    cmd.extend([title, message])

    try:
        subprocess.run(cmd, check=False, capture_output=True)
    except FileNotFoundError:
        print("Error: notify-send not found.", file=sys.stderr)
        sys.exit(1)


def _send_notify_send(
    title: str, message: str, icon: str, urgency: str
) -> None:
    """Fallback: send notification using notify-send (no progress bar)."""
    cmd = ["notify-send", "-i", icon, "-u", urgency, title, message]

    try:
        subprocess.run(cmd, check=False, capture_output=True)
    except FileNotFoundError:
        print("Error: notify-send not found.", file=sys.stderr)
        sys.exit(1)


def format_wallpaper_path(wallpaper_path: str) -> str:
    """Format wallpaper path for display (show only filename)."""
    return Path(wallpaper_path).name


def main() -> None:
    """Main function to listen to socket and display notifications."""
    global NOTIFICATION_BACKEND

    import argparse

    parser = argparse.ArgumentParser(description="Wallpaper progress notifier")
    parser.add_argument(
        "--socket-dir",
        type=Path,
        default=None,
        help="Directory for socket files (default: /tmp/sockets)",
    )
    args = parser.parse_args()

    # Detect notification backend
    NOTIFICATION_BACKEND = detect_notification_backend()
    print(f"Using notification backend: {NOTIFICATION_BACKEND}", flush=True)

    # Create socket client
    try:
        client = create_client(
            SocketType.UNIX,
            event_name="wallpaper_progress",
            socket_dir=args.socket_dir,
        )
    except Exception as e:
        print(
            f"Error creating socket client: {e}", file=sys.stderr, flush=True
        )
        sys.exit(1)

    # Connect to socket with retry logic
    import time

    max_retries = 30  # 30 seconds timeout
    retry_delay = 1  # 1 second between retries

    print("Waiting for wallpaper orchestrator to start...", flush=True)
    for attempt in range(max_retries):
        try:
            client.connect()
            print(
                "Connected to wallpaper_progress socket. "
                "Listening for updates...",
                flush=True,
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print(
                    f"Error connecting to socket: {e}",
                    file=sys.stderr,
                    flush=True,
                )
                print(
                    "Timeout: wallpaper orchestrator did not start "
                    "within 30 seconds.",
                    file=sys.stderr,
                    flush=True,
                )
                sys.exit(1)

    # Listen for messages
    try:
        for message in client.receive_iter():
            data: dict[str, Any] = message.data

            # Extract progress information
            step = data.get("step", "Processing")
            progress = data.get("progress", 0)
            status = data.get("status", "processing")

            # Get wallpaper path from extra_data if available
            # (DEPRECATED - now in data directly)
            extra_data = data.get("extra_data", {})
            wallpaper_path = extra_data.get(
                "wallpaper_path", data.get("wallpaper_path", "")
            )

            # Format message
            if wallpaper_path:
                wallpaper_name = format_wallpaper_path(wallpaper_path)
                message_text = f"{step}\n{wallpaper_name}"
            else:
                message_text = step

            # Determine icon and urgency based on status
            if status == "completed":
                icon = "emblem-default"
                urgency = "normal"
                title = "Wallpaper Changed ✓"
            elif status == "error":
                icon = "dialog-error"
                urgency = "critical"
                title = "Wallpaper Error ✗"
                # Show error message if available
                error_msg = data.get("error", "Unknown error")
                message_text = (
                    f"{error_msg}\n{wallpaper_name}"
                    if wallpaper_path
                    else error_msg
                )
            else:
                icon = "image-x-generic"
                urgency = "normal"
                title = "Processing Wallpaper..."

            # Send notification
            send_notification(
                title=title,
                message=message_text,
                progress=int(progress) if status == "processing" else None,
                icon=icon,
                urgency=urgency,
            )

    except KeyboardInterrupt:
        print("\nStopping notifier...")
    except Exception as e:
        print(f"Error receiving messages: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
