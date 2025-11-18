#!/usr/bin/env python3
"""Visual demo of socket integration with colors and formatting."""

import sys
import time
import threading
from pathlib import Path

# Add socket module to path
socket_module_path = Path(__file__).parent.parent.parent / "modules" / "socket" / "src"
sys.path.insert(0, str(socket_module_path))

# Import socket_manager module directly
socket_manager_file = Path(__file__).parent / "src" / "wallpaper_orchestrator" / "socket_manager.py"
import importlib.util
spec = importlib.util.spec_from_file_location("socket_manager", socket_manager_file)
socket_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(socket_manager)

from dotfiles_socket import create_client, SocketType, MessageType

WallpaperProgressSocketManager = socket_manager.WallpaperProgressSocketManager

# ANSI colors
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'


def run_client(socket_dir, event_name="visual_demo"):
    """Run socket client with visual output."""
    time.sleep(0.5)  # Let server start first
    
    try:
        client = create_client(SocketType.UNIX, event_name, socket_dir=socket_dir)
        
        # Connect
        for _ in range(10):
            try:
                client.connect()
                break
            except:
                time.sleep(0.2)
        
        print(f"\n{CYAN}{'='*70}{RESET}")
        print(f"{CYAN}{BOLD}  📱 CLIENT: Receiving Real-Time Progress Updates{RESET}")
        print(f"{CYAN}{'='*70}{RESET}\n")
        
        # Receive messages
        for message in client.receive_iter():
            if message.message_type == MessageType.DATA:
                data = message.data
                progress = data.get("progress", 0)
                step_name = data.get("step", "Unknown")
                status = data.get("status", "processing")
                
                # Progress bar with colors
                bar_length = 50
                filled = int(bar_length * progress / 100)
                bar = f"{GREEN}{'█' * filled}{RESET}{'░' * (bar_length - filled)}"
                
                # Status emoji
                emoji = "⚙️ " if status == "processing" else "✅"
                
                print(f"  {emoji} [{bar}] {YELLOW}{progress:5.1f}%{RESET}")
                print(f"     {BLUE}└─ {step_name}{RESET}\n")
                
                if status == "completed":
                    print(f"{GREEN}{BOLD}  🎉 Processing Complete!{RESET}\n")
                    break
        
        client.disconnect()
        print(f"{CYAN}{'='*70}{RESET}\n")
        
    except Exception as e:
        print(f"❌ Client error: {e}")


def run_server(socket_dir, event_name="visual_demo"):
    """Run socket server with visual output."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}  📡 SERVER: Wallpaper Orchestrator Pipeline{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    manager = WallpaperProgressSocketManager(event_name=event_name, socket_dir=socket_dir)
    
    with manager:
        print(f"  {GREEN}✓{RESET} Socket server started")
        print(f"  {GREEN}✓{RESET} Socket: {socket_dir / f'{event_name}.sock'}")
        print(f"  {GREEN}✓{RESET} Event: {event_name}\n")
        print(f"  {YELLOW}Starting 3-step pipeline...{RESET}\n")
        
        steps = [
            ("Step 1: Generate color scheme", 0, 33),
            ("Step 2: Create wallpaper effects", 33, 66),
            ("Step 3: Apply via hyprpaper", 66, 100),
        ]
        
        for step_name, start, end in steps:
            print(f"  {CYAN}▶{RESET} {step_name}")
            for progress in range(start, end + 1, 3):
                manager.send_progress(
                    step_name=step_name,
                    progress_percent=float(progress),
                    status="processing"
                )
                time.sleep(0.05)
            print(f"  {GREEN}✓{RESET} {step_name} complete\n")
        
        # Send completion
        manager.send_progress(
            step_name="All steps complete",
            progress_percent=100.0,
            status="completed"
        )
        
        time.sleep(0.3)
        print(f"  {GREEN}✓{RESET} Socket server stopped\n")
        print(f"{BLUE}{'='*70}{RESET}\n")


if __name__ == "__main__":
    socket_dir = Path("/tmp/sockets")
    socket_dir.mkdir(parents=True, exist_ok=True)
    event_name = "visual_demo"
    
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  🚀 Wallpaper Orchestrator Socket Integration Demo{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    
    # Start client in background
    client_thread = threading.Thread(target=run_client, args=(socket_dir, event_name))
    client_thread.start()
    
    # Run server
    run_server(socket_dir, event_name)
    
    # Wait for client
    client_thread.join()
    
    print(f"{GREEN}{BOLD}{'='*70}{RESET}")
    print(f"{GREEN}{BOLD}  ✅ Demo Complete - Socket Integration Working!{RESET}")
    print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")

