# test_game.py - Safe way to run Pong Force
import pygame
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import game modules
from game import GameLoop, GameMenu, GoalSelectionMenu, ControlsMenu, RoomCodeMenu

def main():
    """Main entry point for testing the game"""
    print("Starting Pong Force Test...")
    
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create and run the menu first
    try:
        menu = GameMenu()
        menu_choice = menu.run()
        
        # Handle menu choice
        if menu_choice == 0:  # Play vs Robot
            print("Starting AI game...")
            # Show goal selection menu
            goal_menu = GoalSelectionMenu()
            win_score = goal_menu.run()
            
            if win_score > 0:  # User didn't cancel
                game = GameLoop(fullscreen=False)
                game.run_vs_ai_with_goals(win_score)
            else:
                print("Returning to main menu...")
        elif menu_choice == 1:  # Play 2-Player Local
            print("Starting 2-player local game...")
            # Show goal selection menu
            goal_menu = GoalSelectionMenu()
            win_score = goal_menu.run()
            
            if win_score > 0:  # User didn't cancel
                game = GameLoop(fullscreen=False)
                game.run_two_player_local(win_score)
            else:
                print("Returning to main menu...")
        elif menu_choice == 2:  # Configure Controls
            print("Opening controls configuration...")
            controls_menu = ControlsMenu()
            controls_menu.run()
            # Return to main menu after controls
            main()  # Restart to show main menu again
            return
        elif menu_choice == 3:  # Multiplayer Room
            print("Opening multiplayer room system...")
            room_menu = RoomCodeMenu()
            room_result = room_menu.run()
            
            if room_result["mode"] != "back":
                if room_result["mode"] == "host":
                    print(f"Hosting room with code: {room_result['code']}")
                    # In real implementation, this would start server
                    game = GameLoop(fullscreen=False)
                    game.run_server()  # For now, use existing server mode
                elif room_result["mode"] == "join":
                    print(f"Joining room with code: {room_result['code']}")
                    # In real implementation, this would connect to server
                    game = GameLoop(fullscreen=False)
                    game.run_client()  # For now, use existing client mode
            else:
                print("Returning to main menu...")
        elif menu_choice == -1:  # Exit/Cancel
            print("Exiting game...")
        else:
            print("Unknown menu choice, exiting...")
            
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()
        sys.exit(1)
    
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
