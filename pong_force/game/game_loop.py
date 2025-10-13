# ===== PONG FORCE - MAIN GAME LOOP =====

import pygame
import sys
import time
from .paddle import Paddle
from .ball import Ball
from .power import ForcePush
from .scoreboard import Scoreboard
from .effects import EffectsManager
import config

class GameLoop:
    def __init__(self, fullscreen=False):
        """Initialize the game loop
        
        Args:
            fullscreen (bool): Start in fullscreen mode
        """
        # Pygame should already be initialized by main.py
        # Just ensure it's initialized
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Screen settings
        self.fullscreen = fullscreen
        self.windowed_size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Get existing display or create new one
        try:
            self.screen = pygame.display.get_surface()
            if self.screen is None:
                # No existing surface, create new one
                if self.fullscreen:
                    self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            else:
                # Resize existing surface if needed
                current_size = self.screen.get_size()
                if current_size != self.windowed_size and not self.fullscreen:
                    self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        except:
            # Fallback: create new surface
            if self.fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        
        pygame.display.set_caption(config.TITLE)
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = config.STATE_PLAYING
        
        # Game objects
        self.paddle1 = Paddle(
            config.PADDLE_MARGIN, 
            config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2,
            1, 
            config.NEON_BLUE
        )
        
        self.paddle2 = Paddle(
            config.WINDOW_WIDTH - config.PADDLE_MARGIN - config.PADDLE_WIDTH,
            config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2,
            2,
            config.NEON_PINK
        )
        
        self.ball = Ball(
            config.WINDOW_WIDTH // 2 - config.BALL_SIZE // 2,
            config.WINDOW_HEIGHT // 2 - config.BALL_SIZE // 2
        )
        
        self.force_push = ForcePush()
        self.scoreboard = Scoreboard()
        self.effects = EffectsManager()
        
        # Input handling
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_timer = 0
        self.current_fps = 0
        
        # Network state (for multiplayer)
        self.is_server = False
        self.is_client = False
        self.network_connected = False
        
        # AI state
        self.ai_enabled = False
        self.ai_difficulty = 0.85  # 0.0 to 1.0 (higher = smarter AI)
        
    def run_local(self):
        """Run local multiplayer game"""
        print("🎮 Starting local multiplayer game...")
        self.is_server = True
        self.game_state = config.STATE_PLAYING
        self.main_loop()
    
    def run_vs_ai(self):
        """Run game against AI"""
        print("🤖 Starting game vs AI...")
        self.ai_enabled = True
        self.game_state = config.STATE_PLAYING
        self.main_loop()
    
    def run_server(self):
        """Run as server"""
        print("🎮 Starting server game...")
        self.is_server = True
        self.game_state = config.STATE_WAITING
        self.main_loop()
    
    def run_client(self):
        """Run as client"""
        print("🎮 Starting client game...")
        self.is_client = True
        self.game_state = config.STATE_CONNECTING
        self.main_loop()
    
    def main_loop(self):
        """Main game loop"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
            
            # Update display
            pygame.display.flip()
            
            # Cap frame rate
            self.clock.tick(config.FPS)
            
            # Update FPS counter
            self.update_fps_counter(dt)
    
    def handle_events(self):
        """Handle pygame events"""
        self.keys_just_pressed.clear()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_just_pressed.add(event.key)
                self.keys_pressed.add(event.key)
                
                # Handle key presses
                self.handle_key_press(event.key)
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
    
    def handle_key_press(self, key):
        """Handle individual key presses
        
        Args:
            key (int): Pygame key constant
        """
        if key == pygame.K_ESCAPE:
            if self.game_state == config.STATE_PLAYING:
                self.game_state = config.STATE_PAUSED
            elif self.game_state == config.STATE_PAUSED:
                self.game_state = config.STATE_PLAYING
        
        elif key == pygame.K_F11 or key == pygame.K_f:
            # Toggle fullscreen
            self.toggle_fullscreen()
        
        elif key == pygame.K_r:
            if self.game_state == config.STATE_GAME_OVER:
                self.restart_game()
        
        elif key == pygame.K_SPACE:
            if self.game_state == config.STATE_PLAYING:
                # Player 1 force push
                if self.paddle1.try_force_push(self.ball):
                    self.effects.create_force_effect(
                        self.ball.x + self.ball.size // 2,
                        self.ball.y + self.ball.size // 2,
                        1
                    )
        
        elif key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
            if self.game_state == config.STATE_PLAYING:
                # Player 2 force push
                if self.paddle2.try_force_push(self.ball):
                    self.effects.create_force_effect(
                        self.ball.x + self.ball.size // 2,
                        self.ball.y + self.ball.size // 2,
                        2
                    )
    
    def update(self, dt):
        """Update game state
        
        Args:
            dt (float): Delta time in seconds
        """
        # Update input
        self.update_input()
        
        # Update game objects
        if self.game_state == config.STATE_PLAYING:
            self.update_gameplay(dt)
        
        # Update effects
        self.effects.update(dt)
        self.force_push.update(dt)
        
        # Update scoreboard
        self.scoreboard.update(dt)
    
    def update_input(self):
        """Update input handling"""
        # Player 1 controls (Arrow keys)
        if pygame.K_UP in self.keys_pressed:
            self.paddle1.move_up()
        elif pygame.K_DOWN in self.keys_pressed:
            self.paddle1.move_down()
        else:
            self.paddle1.stop_moving()
        
        # Player 2 controls (W/S keys) or AI
        if self.ai_enabled:
            # AI controls player 2
            self.update_ai()
        else:
            # Human player 2 controls
            if pygame.K_w in self.keys_pressed:
                self.paddle2.move_up()
            elif pygame.K_s in self.keys_pressed:
                self.paddle2.move_down()
            else:
                self.paddle2.stop_moving()
    
    def update_gameplay(self, dt):
        """Update gameplay logic
        
        Args:
            dt (float): Delta time in seconds
        """
        # Update paddles
        self.paddle1.update(dt, config.WINDOW_HEIGHT)
        self.paddle2.update(dt, config.WINDOW_HEIGHT)
        
        # Update ball
        result = self.ball.update(dt, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Handle ball collision results
        if result == "score_left":
            self.handle_score(2)  # Player 2 scores
        elif result == "score_right":
            self.handle_score(1)  # Player 1 scores
        
        # Check paddle collisions
        if self.ball.collide_with_paddle(self.paddle1):
            self.effects.create_hit_effect(
                self.ball.x + self.ball.size // 2,
                self.ball.y + self.ball.size // 2,
                config.NEON_BLUE
            )
        
        if self.ball.collide_with_paddle(self.paddle2):
            self.effects.create_hit_effect(
                self.ball.x + self.ball.size // 2,
                self.ball.y + self.ball.size // 2,
                config.NEON_PINK
            )
        
        # Check for game over
        if self.scoreboard.game_over:
            self.game_state = config.STATE_GAME_OVER
    
    def handle_score(self, player_id):
        """Handle scoring
        
        Args:
            player_id (int): Player who scored
        """
        self.scoreboard.add_score(player_id)
        self.effects.create_score_effect(player_id)
        
        # Reset ball after a short delay
        pygame.time.wait(1000)  # 1 second delay
        self.ball.reset_ball()
    
    def restart_game(self):
        """Restart the game"""
        self.scoreboard.reset_scores()
        self.ball.reset_ball()
        self.paddle1.y = config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2
        self.paddle2.y = config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2
        self.effects.clear_effects()
        self.force_push.clear_effects()
        self.game_state = config.STATE_PLAYING
    
    def update_fps_counter(self, dt):
        """Update FPS counter
        
        Args:
            dt (float): Delta time in seconds
        """
        self.fps_counter += 1
        self.fps_timer += dt
        
        if self.fps_timer >= 1.0:  # Update every second
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = 0
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(config.BLACK)
        
        # Apply screen shake
        shake_offset = self.effects.get_screen_shake()
        if shake_offset != (0, 0):
            # Create a temporary surface for shake effect
            temp_surface = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            temp_surface.fill(config.BLACK)
            self.render_to_surface(temp_surface)
            self.screen.blit(temp_surface, shake_offset)
        else:
            self.render_to_surface(self.screen)
        
        # Draw FPS counter
        if config.SHOW_FPS:
            self.draw_fps_counter()
    
    def render_to_surface(self, surface):
        """Render game to a specific surface
        
        Args:
            surface (pygame.Surface): Surface to render to
        """
        # Draw background effects
        self.effects.draw(surface)
        
        # Draw game objects
        if self.game_state in [config.STATE_PLAYING, config.STATE_PAUSED, config.STATE_GAME_OVER]:
            self.paddle1.draw(surface)
            self.paddle2.draw(surface)
            self.ball.draw(surface)
            self.force_push.draw(surface)
        
        # Draw UI
        self.scoreboard.draw(surface)
        
        # Draw game state specific UI
        if self.game_state == config.STATE_PAUSED:
            self.draw_pause_screen(surface)
        elif self.game_state == config.STATE_GAME_OVER:
            self.draw_game_over_screen(surface)
        elif self.game_state == config.STATE_WAITING:
            self.draw_waiting_screen(surface)
        elif self.game_state == config.STATE_CONNECTING:
            self.draw_connecting_screen(surface)
    
    def draw_fps_counter(self):
        """Draw FPS counter"""
        font = pygame.font.Font(None, 24)
        fps_text = f"FPS: {self.current_fps}"
        fps_surface = font.render(fps_text, True, config.WHITE)
        self.screen.blit(fps_surface, (10, 10))
    
    def draw_pause_screen(self, surface):
        """Draw pause screen overlay
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(config.BLACK)
        surface.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.Font(None, 48)
        pause_text = "PAUSED"
        pause_surface = font.render(pause_text, True, config.NEON_YELLOW)
        pause_rect = pause_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        surface.blit(pause_surface, pause_rect)
        
        # Instructions
        font_small = pygame.font.Font(None, 24)
        instruction_text = "Press ESC to resume"
        instruction_surface = font_small.render(instruction_text, True, config.WHITE)
        instruction_rect = instruction_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 50))
        surface.blit(instruction_surface, instruction_rect)
    
    def draw_game_over_screen(self, surface):
        """Draw game over screen
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Game over screen is handled by scoreboard
        pass
    
    def draw_waiting_screen(self, surface):
        """Draw waiting for players screen
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        font = pygame.font.Font(None, 36)
        wait_text = "Waiting for players to connect..."
        wait_surface = font.render(wait_text, True, config.WHITE)
        wait_rect = wait_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        surface.blit(wait_surface, wait_rect)
        
        # Connection info
        font_small = pygame.font.Font(None, 24)
        info_text = f"Server running on port {config.SERVER_PORT}"
        info_surface = font_small.render(info_text, True, config.GRAY)
        info_rect = info_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 50))
        surface.blit(info_surface, info_rect)
    
    def draw_connecting_screen(self, surface):
        """Draw connecting screen
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        font = pygame.font.Font(None, 36)
        connect_text = "Connecting to server..."
        connect_surface = font.render(connect_text, True, config.WHITE)
        connect_rect = connect_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        surface.blit(connect_surface, connect_rect)
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        
        print(f"{'🖥️ Fullscreen' if self.fullscreen else '🪟 Windowed'} mode")
    
    def update_ai(self):
        """Update AI paddle movement"""
        if not self.ai_enabled:
            return
        
        # AI controls paddle 2
        paddle_center = self.paddle2.y + self.paddle2.height // 2
        ball_center = self.ball.y + self.ball.size // 2
        
        # Calculate prediction based on difficulty
        # Higher difficulty = better prediction
        import random
        prediction_error = (1 - self.ai_difficulty) * 100
        predicted_y = ball_center + random.uniform(-prediction_error, prediction_error)
        
        # Move paddle towards predicted position
        threshold = 5  # Dead zone to prevent jittering
        
        if predicted_y < paddle_center - threshold:
            self.paddle2.move_up()
        elif predicted_y > paddle_center + threshold:
            self.paddle2.move_down()
        else:
            self.paddle2.stop_moving()
        
        # AI force push logic
        # Try to use force push when ball is close and moving towards AI paddle
        if self.ball.vx > 0:  # Ball moving towards AI paddle (right side)
            distance_to_ball = abs(self.paddle2.x - self.ball.x)
            if distance_to_ball < 200 and self.paddle2.force_cooldown <= 0:
                # Random chance based on difficulty
                if random.random() < self.ai_difficulty * 0.3:  # 30% chance at max difficulty
                    self.paddle2.try_force_push(self.ball)
                    if self.paddle2.force_cooldown > 0:
                        self.effects.create_force_effect(
                            self.ball.x + self.ball.size // 2,
                            self.ball.y + self.ball.size // 2,
                            2
                        )
    
    def cleanup(self):
        """Cleanup resources"""
        pygame.quit()
    
    def get_game_state(self):
        """Get current game state for networking
        
        Returns:
            dict: Game state data
        """
        return {
            'game_state': self.game_state,
            'paddle1': self.paddle1.get_state(),
            'paddle2': self.paddle2.get_state(),
            'ball': self.ball.get_state(),
            'scoreboard': self.scoreboard.get_state()
        }
    
    def set_game_state(self, state):
        """Set game state from network data
        
        Args:
            state (dict): Game state data
        """
        self.game_state = state['game_state']
        self.paddle1.set_state(state['paddle1'])
        self.paddle2.set_state(state['paddle2'])
        self.ball.set_state(state['ball'])
        self.scoreboard.set_state(state['scoreboard'])
