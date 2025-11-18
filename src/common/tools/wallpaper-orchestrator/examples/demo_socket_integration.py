#!/usr/bin/env python3
"""Demo script to show socket integration working."""

import sys
import time
from pathlib import Path

# Add socket module to path
socket_module_path = Path(__file__).parent.parent.parent / "modules" / "socket" / "src"
sys.path.insert(0, str(socket_module_path))

# Add wallpaper orchestrator to path
orchestrator_path = Path(__file__).parent / "src"
sys.path.insert(0, str(orchestrator_path))

from dotfiles_socket import create_client, SocketType, MessageType


def listen_for_progress(socket_dir: Path, event_name: str = "wallpaper_progress"):
    """Listen for progress updates from wallpaper orchestrator."""
    print(f"\n{'='*60}")
    print(f"🎧 Socket Client Listening for Progress Updates")
    print(f"{'='*60}")
    print(f"Socket: {socket_dir / f'{event_name}.sock'}")
    print(f"Event: {event_name}")
    print(f"{'='*60}\n")
    
    try:
        # Create and connect client
        client = create_client(
            SocketType.UNIX,
            event_name,
            socket_dir=socket_dir,
            auto_reconnect=True,
        )
        
        # Wait a bit for server to start
        max_retries = 10
        for i in range(max_retries):
            try:
                client.connect()
                print("✅ Connected to socket server!\n")
                break
            except Exception as e:
                if i < max_retries - 1:
                    print(f"⏳ Waiting for server... ({i+1}/{max_retries})")
                    time.sleep(0.5)
                else:
                    print(f"❌ Failed to connect: {e}")
                    return
        
        # Receive and display messages
        message_count = 0
        for message in client.receive_iter():
            message_count += 1
            
            if message.message_type == MessageType.DATA:
                data = message.data
                
                # Format progress bar
                if "progress_percent" in data:
                    progress = data["progress_percent"]
                    bar_length = 40
                    filled = int(bar_length * progress / 100)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    
                    print(f"\r[{bar}] {progress:.1f}%", end="", flush=True)
                    
                    # Show step details on new line
                    if "step_name" in data:
                        step_name = data["step_name"]
                        status = data.get("status", "processing")
                        print(f"\n📍 Step: {step_name} ({status})")
                
                # Show completion message
                if data.get("status") == "completed":
                    print(f"\n\n✅ {data.get('message', 'Processing completed!')}")
                    if "wallpaper_path" in data:
                        print(f"   Wallpaper: {data['wallpaper_path']}")
                    break
                    
            elif message.message_type == MessageType.ERROR:
                print(f"\n\n❌ Error: {message.data.get('error', 'Unknown error')}")
                break
                
            elif message.message_type == MessageType.CONTROL:
                if message.data.get("action") == "shutdown":
                    print("\n\n🛑 Server shutting down")
                    break
        
        client.disconnect()
        print(f"\n\n{'='*60}")
        print(f"📊 Received {message_count} messages")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    socket_dir = Path("/tmp/sockets")
    socket_dir.mkdir(parents=True, exist_ok=True)
    
    listen_for_progress(socket_dir)

