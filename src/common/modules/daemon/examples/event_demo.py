#!/usr/bin/env python3
"""Better demo with proper timing."""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


async def monitor():
    """Monitor wallpaper events."""
    socket_path = Path.home() / ".cache/dotfiles/sockets/wallpaper_events.sock"
    
    # Wait for socket
    for _ in range(20):
        if socket_path.exists():
            break
        await asyncio.sleep(0.1)
    
    reader, writer = await asyncio.open_unix_connection(socket_path)
    print("✅ Monitor: Connected and listening...\n")
    
    while True:
        length_bytes = await reader.read(4)
        if not length_bytes:
            break
        
        message_length = int.from_bytes(length_bytes, "big")
        data = await reader.read(message_length)
        msg = json.loads(data.decode("utf-8"))
        
        payload_type = msg["payload"].get("type")
        
        if payload_type == "operation_started":
            print(f"🚀 Operation Started:")
            print(f"   Wallpaper: {msg['payload']['wallpaper_path']}")
            print(f"   Monitor: {msg['payload']['monitor']}\n")
        
        elif payload_type == "operation_progress":
            progress = msg['payload']['overall_progress']
            step = msg['payload']['step_id']
            bar_length = 30
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"⏳ [{bar}] {progress:5.1f}% - {step}")
        
        elif payload_type == "operation_completed":
            print(f"\n✅ Operation Completed Successfully!\n")
            break
        
        elif payload_type == "operation_failed":
            print(f"\n❌ Operation Failed: {msg['payload']['error']}\n")
            break


async def publisher():
    """Publish test events."""
    # Give monitor time to connect first
    await asyncio.sleep(0.5)
    
    command_socket = Path.home() / ".cache/dotfiles/sockets/command.sock"
    reader, writer = await asyncio.open_unix_connection(command_socket)
    
    operation_id = str(uuid4())
    
    async def send(msg_dict):
        data = json.dumps(msg_dict).encode("utf-8")
        writer.write(len(data).to_bytes(4, "big"))
        writer.write(data)
        await writer.drain()
    
    # Operation started
    await send({
        "message_id": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "event_type": "wallpaper",
        "payload": {
            "type": "operation_started",
            "operation_id": operation_id,
            "wallpaper_path": "/home/user/Pictures/Wallpapers/mountain-sunset.jpg",
            "monitor": "DP-1"
        }
    })
    await asyncio.sleep(0.5)
    
    # Simulate realistic progress
    steps = [
        ("validate_wallpaper", 5.0),
        ("load_image", 10.0),
        ("generate_blur_effect", 20.0),
        ("generate_dim_effect", 30.0),
        ("generate_grayscale_effect", 40.0),
        ("generate_pixelate_effect", 50.0),
        ("extract_colors", 60.0),
        ("generate_colorscheme_json", 70.0),
        ("generate_colorscheme_css", 80.0),
        ("generate_colorscheme_yaml", 90.0),
        ("set_wallpaper", 100.0),
    ]
    
    for step_id, progress in steps:
        await send({
            "message_id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": "wallpaper",
            "payload": {
                "type": "operation_progress",
                "operation_id": operation_id,
                "step_id": step_id,
                "step_progress": 100.0,
                "overall_progress": progress
            }
        })
        await asyncio.sleep(0.3)
    
    # Completed
    await send({
        "message_id": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "event_type": "wallpaper",
        "payload": {
            "type": "operation_completed",
            "operation_id": operation_id,
            "success": True
        }
    })
    
    writer.close()
    await writer.wait_closed()


async def main():
    print("=" * 70)
    print("🎯 Dotfiles Event System - Live Demo")
    print("=" * 70)
    print()
    
    await asyncio.gather(monitor(), publisher())
    
    print("=" * 70)
    print("✅ Demo Complete - Event system working perfectly!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
