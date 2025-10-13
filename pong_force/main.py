#!/usr/bin/env python3
# ===== PONG FORCE - MAIN ENTRY POINT =====

import sys
import argparse
import pygame
from game.game_loop import GameLoop
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
            print("🎮 Starting Pong Force Server...")
            print(f"📍 Server running on {args.host}:{args.port}")
            print("⏳ Waiting for players to connect...")
            print("💡 Players can connect with: pong_force.exe --client --host", args.host)
            
            server = GameServer(args.host, args.port)
            server.run()
            
        elif args.client:
            print("🎮 Starting Pong Force Client...")
            print(f"🔗 Connecting to {args.host}:{args.port}")
            
            client = GameClient(args.host, args.port)
            client.run()
            
        else:
            # No arguments - show menu
            print("🎮 Pong Force - Revolutionary Pong with Force Push")
            print("=" * 50)
            print("Choose game mode:")
            print("1. Host Game (Server)")
            print("2. Join Game (Client)")
            print("3. Local Multiplayer")
            print("4. Exit")
            print("=" * 50)
            
            while True:
                try:
                    choice = input("Enter your choice (1-4): ").strip()
                    
                    if choice == "1":
                        print(f"🎮 Starting server on {args.host}:{args.port}")
                        server = GameServer(args.host, args.port)
                        server.run()
                        break
                        
                    elif choice == "2":
                        host = input(f"Enter server IP (default: {args.host}): ").strip()
                        if not host:
                            host = args.host
                        print(f"🔗 Connecting to {host}:{args.port}")
                        client = GameClient(host, args.port)
                        client.run()
                        break
                        
                    elif choice == "3":
                        print("🎮 Starting local multiplayer game...")
                        game = GameLoop()
                        game.run_local()
                        break
                        
                    elif choice == "4":
                        print("👋 Thanks for playing Pong Force!")
                        sys.exit(0)
                        
                    else:
                        print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                        
                except KeyboardInterrupt:
                    print("\n👋 Thanks for playing Pong Force!")
                    sys.exit(0)
                except Exception as e:
                    print(f"❌ Error: {e}")
                    if config.AUTO_RESTART_ON_ERROR:
                        print("🔄 Restarting...")
                        continue
                    else:
                        sys.exit(1)
    
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
