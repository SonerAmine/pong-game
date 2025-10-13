#!/usr/bin/env python3
# ===== PONG FORCE - MAIN ENTRY POINT =====

import sys
import argparse
import pygame
from game.game_loop import GameLoop
from game.menu import GameMenu, HostInputDialog, OnlineSubmenu
from network.server import GameServer
from network.client import GameClient
import config

def main():
    """Main entry point for Pong Force"""
    parser = argparse.ArgumentParser(description='Pong Force - Revolutionary Pong with Force Push')
    parser.add_argument('--server', action='store_true', help='Run as server')
    parser.add_argument('--client', action='store_true', help='Run as client')
    parser.add_argument('--host', default=config.SERVER_IP, help='Server IP address')
    parser.add_argument('--port', type=int, default=config.SERVER_PORT, help='Server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--local', action='store_true', help='Start local multiplayer directly')
    
    args = parser.parse_args()
    
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init(
        frequency=config.AUDIO_FREQUENCY,
        size=config.AUDIO_SIZE,
        channels=config.AUDIO_CHANNELS,
        buffer=config.AUDIO_BUFFER
    )
    
    # Set debug mode
    if args.debug:
        config.DEBUG_MODE = True
    
    try:
        if args.server:
            # Server mode with console output
            print("🎮 Starting Pong Force Server...")
            print(f"📍 Server running on {args.host}:{args.port}")
            print("⏳ Waiting for players to connect...")
            print("💡 Players can connect with: pong_force.exe --client --host", args.host)
            
            server = GameServer(args.host, args.port)
            server.run()
            
        elif args.client:
            # Client mode
            print("🎮 Starting Pong Force Client...")
            print(f"🔗 Connecting to {args.host}:{args.port}")
            
            client = GameClient(args.host, args.port)
            client.run()
            
        elif args.local:
            # Direct local multiplayer (no menu)
            print("🎮 Starting local multiplayer game...")
            game = GameLoop()
            game.run_local()
            
        else:
            # No arguments - show graphical menu
            menu = GameMenu()
            choice = menu.run()
            
            # Handle menu choice
            if choice == 0:  # Play with Friend (Same PC)
                game = GameLoop()
                game.run_local()
                
            elif choice == 1:  # Play vs Robot
                game = GameLoop()
                game.run_vs_ai()
                
            elif choice == 2:  # Play Online Multiplayer
                # Show submenu for Host or Join
                submenu = OnlineSubmenu()
                online_choice = submenu.run()
                
                if online_choice == 0:  # Host Game
                    server = GameServer(args.host, args.port)
                    server.run()
                elif online_choice == 1:  # Join Game
                    dialog = HostInputDialog(args.host)
                    host = dialog.run()
                    client = GameClient(host, args.port)
                    client.run()
                
            else:  # Exit or Cancel (-1)
                print("👋 Thanks for playing Pong Force!")
                sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n👋 Thanks for playing Pong Force!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if config.DEBUG_MODE:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
