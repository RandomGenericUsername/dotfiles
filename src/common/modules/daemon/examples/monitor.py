#!/usr/bin/env python3
"""Real-world demo using actual WallpaperService."""
import asyncio
import json
from pathlib import Path


async def monitor_wallpaper_events():
    """Monitor real wallpaper events from WallpaperService."""
    socket_path = Path.home() / ".cache/dotfiles/sockets/wallpaper_events.sock"
    
    print("📡 Waiting for wallpaper events...")
    print("   (Run: dotfiles-manager wallpaper change <path> in another terminal)\n")
    
    # Wait for socket
    for _ in range(60):
        if socket_path.exists():
            break
        await asyncio.sleep(1)
    
    if not socket_path.exists():
        print("❌ No wallpaper events socket found")
        return
    
    reader, writer = await asyncio.open_unix_connection(socket_path)
    print("✅ Connected to wallpaper events!\n")
    print("=" * 70)
    
    while True:
        try:
            length_bytes = await reader.read(4)
            if not length_bytes:
                break
            
            message_length = int.from_bytes(length_bytes, "big")
            data = await reader.read(message_length)
            msg = json.loads(data.decode("utf-8"))
            
            payload_type = msg["payload"].get("type")
            timestamp = msg["timestamp"]
            
            if payload_type == "operation_started":
                print(f"\n🚀 Wallpaper Change Started [{timestamp}]")
                print(f"   Wallpaper: {msg['payload']['wallpaper_path']}")
                print(f"   Monitor: {msg['payload'].get('monitor', 'all')}")
                print(f"   Operation ID: {msg['payload']['operation_id']}\n")
            
            elif payload_type == "operation_progress":
                progress = msg['payload']['overall_progress']
                step = msg['payload']['step_id']
                bar_length = 40
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"⏳ [{bar}] {progress:5.1f}% - {step}")
            
            elif payload_type == "operation_completed":
                success = msg['payload']['success']
                if success:
                    print(f"\n✅ Wallpaper Changed Successfully! [{timestamp}]")
                else:
                    print(f"\n❌ Wallpaper Change Failed [{timestamp}]")
                print("=" * 70)
            
            elif payload_type == "operation_failed":
                error = msg['payload']['error']
                print(f"\n❌ Operation Failed: {error} [{timestamp}]")
                print("=" * 70)
        
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    print("=" * 70)
    print("🎯 Real-World Event Monitor")
    print("=" * 70)
    print()
    
    try:
        asyncio.run(monitor_wallpaper_events())
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped")
