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
        
        # Always use existing display surface (menu created it)
        # Just update the caption
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            # Create new surface only if none exists
            if self.fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                # Use RESIZABLE flag to enable window buttons (minimize, maximize, close)
                self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        
        pygame.display.set_caption(config.TITLE + " - Game")
        
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
        
        # Score delay timer (non-blocking)
        self.score_delay_active = False
        self.score_delay_timer = 0
        self.score_delay_duration = 1.5  # seconds
        
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
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.windowed_size = (event.w, event.h)
                if not self.fullscreen:
                    self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            
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
            elif self.game_state == config.STATE_GAME_OVER:
                self.running = False  # Return to menu
        
        elif key == pygame.K_q:
            # Quit to menu
            self.running = False
        
        elif key == pygame.K_F11 or key == pygame.K_f:
            # Toggle fullscreen
            self.toggle_fullscreen()
        
        elif key == pygame.K_r:
            if self.game_state == config.STATE_GAME_OVER:
                self.restart_game()
        
        elif key == pygame.K_SPACE:
            if self.game_state == config.STATE_PLAYING and not self.score_delay_active:
                # Player 1 force push
                if self.paddle1.try_force_push(self.ball):
                    self.effects.create_force_effect(
                        self.ball.x + self.ball.size // 2,
                        self.ball.y + self.ball.size // 2,
                        1
                    )
        
        elif key == pygame.K_e:
            if self.game_state == config.STATE_PLAYING and not self.score_delay_active:
                # Player 2 force push (only if not AI)
                if not self.ai_enabled and self.paddle2.try_force_push(self.ball):
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
        # Update score delay timer
        if self.score_delay_active:
            self.score_delay_timer += dt
            if self.score_delay_timer >= self.score_delay_duration:
                self.score_delay_active = False
                self.score_delay_timer = 0
                self.ball.reset_ball()
        
        # Update input
        if not self.score_delay_active:
            self.update_input()
        
        # Update game objects
        if self.game_state == config.STATE_PLAYING and not self.score_delay_active:
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
        # Add score immediately
        self.scoreboard.add_score(player_id)
        self.effects.create_score_effect(player_id)
        
        # Reset ball position to center immediately
        self.ball.x = config.WINDOW_WIDTH // 2 - self.ball.size // 2
        self.ball.y = config.WINDOW_HEIGHT // 2 - self.ball.size // 2
        
        # Start non-blocking delay before ball moves again
        self.score_delay_active = True
        self.score_delay_timer = 0
        
        # Stop ball movement during delay
        self.ball.vx = 0
        self.ball.vy = 0
    
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
        
        # Draw quit button (always visible during gameplay)
        if self.game_state in [config.STATE_PLAYING, config.STATE_PAUSED]:
            self.draw_quit_button(surface)
        
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
    
    def draw_quit_button(self, surface):
        """Draw quit to menu button in top-right corner"""
        # Button dimensions
        button_width = 120
        button_height = 35
        button_x = config.WINDOW_WIDTH - button_width - 10
        button_y = 10
        
        # Draw button background
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Check if mouse is over button
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos)
        
        # Button color based on hover
        if is_hover:
            button_color = config.NEON_PINK
            text_color = config.NEON_YELLOW
        else:
            button_color = config.DARK_GRAY
            text_color = config.WHITE
        
        # Draw button
        pygame.draw.rect(surface, button_color, button_rect, border_radius=5)
        pygame.draw.rect(surface, config.WHITE, button_rect, 2, border_radius=5)
        
        # Draw button text
        font = pygame.font.Font(None, 22)
        text_surface = font.render("Menu (Q)", True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Handle click
        mouse_buttons = pygame.mouse.get_pressed()
        if is_hover and mouse_buttons[0]:  # Left click
            self.running = False  # Return to menu
    
    def draw_pause_screen(self, surface):
        """Draw pause screen overlay
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(config.BLACK)
        surface.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.Font(None, 72)
        pause_text = "PAUSED"
        pause_surface = font.render(pause_text, True, config.NEON_YELLOW)
        pause_rect = pause_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 60))
        surface.blit(pause_surface, pause_rect)
        
        # Instructions
        font_small = pygame.font.Font(None, 28)
        instructions = [
            "Press ESC to resume",
            "Press Q to quit to menu",
            "Press F11 for fullscreen",
            "",
            "Controls:",
            "P1: Arrows + SPACE",
            "P2: W/S + E"
        ]
        
        y_offset = config.WINDOW_HEIGHT // 2 + 20
        for instruction in instructions:
            instruction_surface = font_small.render(instruction, True, config.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))
            surface.blit(instruction_surface, instruction_rect)
            y_offset += 40
    
    def draw_game_over_screen(self, surface):
        """Draw game over screen with quit option
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Draw scoreboard's game over first
        # Then add quit instruction
        font_small = pygame.font.Font(None, 24)
        quit_text = "Press ESC to return to menu"
        quit_surface = font_small.render(quit_text, True, config.GRAY)
        quit_rect = quit_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 100))
        surface.blit(quit_surface, quit_rect)
    
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
            # Get current display info for fullscreen
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
        else:
            # Return to windowed mode with RESIZABLE flag
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        
        print(f"{'🖥️ Fullscreen' if self.fullscreen else '🪟 Windowed'} mode")
    
    def update_ai(self):
        """Update AI paddle movement with improved intelligence"""
        if not self.ai_enabled or self.score_delay_active:
            return
        
        import random
        import math
        
        # AI controls paddle 2
        paddle_center_y = self.paddle2.y + self.paddle2.height // 2
        ball_center_y = self.ball.y + self.ball.size // 2
        ball_center_x = self.ball.x + self.ball.size // 2
        
        # Predict where the ball will be
        if self.ball.vx > 0:  # Ball moving towards AI
            # Calculate intersection point
            time_to_reach = (self.paddle2.x - ball_center_x) / max(abs(self.ball.vx), 0.1)
            predicted_y = ball_center_y + (self.ball.vy * time_to_reach)
            
            # Account for wall bounces
            while predicted_y < 0 or predicted_y > config.WINDOW_HEIGHT:
                if predicted_y < 0:
                    predicted_y = abs(predicted_y)
                elif predicted_y > config.WINDOW_HEIGHT:
                    predicted_y = 2 * config.WINDOW_HEIGHT - predicted_y
            
            # Add difficulty-based error
            prediction_error = (1 - self.ai_difficulty) * 50
            target_y = predicted_y + random.uniform(-prediction_error, prediction_error)
        else:
            # Ball moving away - return to center
            target_y = config.WINDOW_HEIGHT // 2
        
        # Move paddle towards target position
        threshold = 10  # Dead zone to prevent jittering
        speed_multiplier = 1.0 + (self.ai_difficulty * 0.3)  # Faster at higher difficulty
        
        if target_y < paddle_center_y - threshold:
            self.paddle2.move_up()
            # Increase speed for higher difficulty
            if self.ai_difficulty > 0.7:
                self.paddle2.y -= self.paddle2.speed * 0.2
        elif target_y > paddle_center_y + threshold:
            self.paddle2.move_down()
            # Increase speed for higher difficulty
            if self.ai_difficulty > 0.7:
                self.paddle2.y += self.paddle2.speed * 0.2
        else:
            self.paddle2.stop_moving()
        
        # AI force push logic - strategic but not automatic
        if self.ball.vx > 0:  # Ball moving towards AI paddle
            distance_to_ball = abs(self.paddle2.x - self.ball.x)
            
            # Use force push ONLY when:
            # 1. Ball is very close and fast
            # 2. Force is ready
            # 3. Random chance (not every time)
            ball_speed = math.sqrt(self.ball.vx**2 + self.ball.vy**2)
            
            if (distance_to_ball < 100 and 
                ball_speed > config.BALL_SPEED * 1.5 and 
                self.paddle2.force_ready and
                not self.score_delay_active):
                
                # Reduce chance significantly - AI shouldn't spam Force Push
                use_force_chance = self.ai_difficulty * 0.15  # Max 15% chance (was 50%)
                if random.random() < use_force_chance:
                    if self.paddle2.try_force_push(self.ball):
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
