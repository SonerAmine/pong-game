#!/usr/bin/env python3
# ===== PONG FORCE - MAIN ENTRY POINT =====

import sys
import argparse
import pygame
import traceback
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
    
    # Set debug mode
    if args.debug:
        config.DEBUG_MODE = True
    
    # Initialize Pygame ONCE
    pygame.init()
    pygame.mixer.init(
        frequency=config.AUDIO_FREQUENCY,
        size=config.AUDIO_SIZE,
        channels=config.AUDIO_CHANNELS,
        buffer=config.AUDIO_BUFFER
    )
    
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
            try:
                menu = GameMenu()
                choice = menu.run()
                
                # Handle menu choice
                if choice == 0:  # Play with Friend (Same PC)
                    try:
                        print("🎮 Starting local multiplayer...")
                        game = GameLoop()
                        game.run_local()
                    except Exception as e:
                        print(f"❌ Error in local multiplayer: {e}")
                        if config.DEBUG_MODE:
                            traceback.print_exc()
                        input("Press Enter to exit...")
                    
                elif choice == 1:  # Play vs Robot
                    try:
                        print("🤖 Starting vs AI...")
                        game = GameLoop()
                        game.run_vs_ai()
                    except Exception as e:
                        print(f"❌ Error in AI mode: {e}")
                        if config.DEBUG_MODE:
                            traceback.print_exc()
                        input("Press Enter to exit...")
                    
                elif choice == 2:  # Play Online Multiplayer
                    try:
                        # Show submenu for Host or Join
                        submenu = OnlineSubmenu()
                        online_choice = submenu.run()
                        
                        if online_choice == 0:  # Host Game
                            print("🌐 Starting server...")
                            print(f"📍 Server will listen on all interfaces (0.0.0.0):{args.port}")
                            print("💡 Share your PUBLIC IP address with other players!")
                            print("💡 To find your public IP, visit: https://www.whatismyip.com/")
                            server = GameServer(config.SERVER_IP, args.port)
                            server.run()
                        elif online_choice == 1:  # Join Game
                            dialog = HostInputDialog()
                            host = dialog.run()
                            if host:  # Only connect if user entered an IP
                                print(f"🔗 Connecting to {host}:{args.port}...")
                                client = GameClient(host, args.port)
                                client.run()
                            else:
                                print("❌ Connection cancelled")
                    except Exception as e:
                        print(f"❌ Error in online mode: {e}")
                        if config.DEBUG_MODE:
                            traceback.print_exc()
                        input("Press Enter to exit...")
                    
                else:  # Exit or Cancel (-1)
                    print("👋 Thanks for playing Pong Force!")
                    
            except Exception as e:
                print(f"❌ Menu error: {e}")
                if config.DEBUG_MODE:
                    traceback.print_exc()
                input("Press Enter to exit...")
    
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
