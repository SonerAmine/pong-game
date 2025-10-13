# ===== PONG FORCE - PADDLE CLASS =====

import pygame
import math
import config

class Paddle:
    def __init__(self, x, y, player_id, color):
        """Initialize a paddle
        
        Args:
            x (int): X position
            y (int): Y position  
            player_id (int): Player ID (1 or 2)
            color (tuple): RGB color tuple
        """
        self.x = x
        self.y = y
        self.player_id = player_id
        self.color = color
        self.width = config.PADDLE_WIDTH
        self.height = config.PADDLE_HEIGHT
        self.speed = config.PADDLE_SPEED
        
        # Force push system
        self.force_meter = 0.0  # 0.0 to 1.0
        self.force_ready = False
        self.last_force_time = 0
        self.stunned = False
        self.stun_end_time = 0
        
        # Visual effects
        self.glow_intensity = 0.0
        self.target_glow = 0.0
        self.trail_points = []
        self.max_trail_length = 10
        
        # Create rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Movement state
        self.moving_up = False
        self.moving_down = False
        
    def update(self, dt, screen_height):
        """Update paddle state
        
        Args:
            dt (float): Delta time in seconds
            screen_height (int): Screen height for boundary checking
        """
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Update force meter
        self.update_force_meter(dt)
        
        # Update stun state
        if self.stunned and current_time >= self.stun_end_time:
            self.stunned = False
        
        # Update movement if not stunned
        if not self.stunned:
            self.update_movement(dt, screen_height)
        
        # Update visual effects
        self.update_visual_effects(dt)
        
        # Update collision rectangle
        self.rect.x = self.x
        self.rect.y = self.y
        
    def update_movement(self, dt, screen_height):
        """Update paddle movement"""
        # Calculate movement
        movement = 0
        if self.moving_up:
            movement -= self.speed * dt * 60  # Normalize for 60 FPS
        if self.moving_down:
            movement += self.speed * dt * 60
        
        # Apply movement
        new_y = self.y + movement
        
        # Boundary checking
        if new_y < 0:
            new_y = 0
        elif new_y + self.height > screen_height:
            new_y = screen_height - self.height
        
        # Add to trail
        if abs(movement) > 0.1:
            self.trail_points.append((self.x + self.width // 2, self.y + self.height // 2))
            if len(self.trail_points) > self.max_trail_length:
                self.trail_points.pop(0)
        
        self.y = new_y
    
    def update_force_meter(self, dt):
        """Update force push meter"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Fill meter over time
        if not self.force_ready:
            self.force_meter += config.FORCE_METER_FILL_RATE * dt
            if self.force_meter >= 1.0:
                self.force_meter = 1.0
                self.force_ready = True
                self.target_glow = 1.0
        
        # Check if enough time has passed since last force push
        if current_time - self.last_force_time >= config.FORCE_COOLDOWN:
            if not self.force_ready:
                self.force_ready = True
                self.target_glow = 1.0
    
    def update_visual_effects(self, dt):
        """Update visual effects"""
        # Smooth glow transition
        glow_diff = self.target_glow - self.glow_intensity
        self.glow_intensity += glow_diff * dt * 5  # Smooth transition
        
        # Fade trail points
        if len(self.trail_points) > 0:
            # Remove old trail points
            self.trail_points = self.trail_points[-self.max_trail_length:]
    
    def move_up(self):
        """Start moving up"""
        self.moving_up = True
    
    def move_down(self):
        """Start moving down"""
        self.moving_down = True
    
    def stop_moving(self):
        """Stop all movement"""
        self.moving_up = False
        self.moving_down = False
    
    def try_force_push(self, ball):
        """Attempt to use force push
        
        Args:
            ball (Ball): The game ball
            
        Returns:
            bool: True if force push was successful
        """
        if not self.force_ready or self.stunned:
            return False
        
        # Check if paddle is close enough to ball
        paddle_center_x = self.x + self.width // 2
        paddle_center_y = self.y + self.height // 2
        ball_center_x = ball.x + ball.size // 2
        ball_center_y = ball.y + ball.size // 2
        
        distance = math.sqrt(
            (paddle_center_x - ball_center_x) ** 2 + 
            (paddle_center_y - ball_center_y) ** 2
        )
        
        if distance <= config.FORCE_HIT_RANGE:
            # Successful force push
            self.activate_force_push(ball)
            return True
        else:
            # Failed force push - stun paddle
            self.stun_paddle()
            return False
    
    def activate_force_push(self, ball):
        """Activate force push on ball
        
        Args:
            ball (Ball): The game ball
        """
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Reset force meter
        self.force_meter = 0.0
        self.force_ready = False
        self.target_glow = 0.0
        self.last_force_time = current_time
        
        # Apply force to ball
        ball.apply_force_push(self.player_id)
        
        # Add visual effect
        self.glow_intensity = 2.0  # Flash effect
    
    def stun_paddle(self):
        """Stun the paddle for failed force push"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.stunned = True
        self.stun_end_time = current_time + config.FORCE_STUN_DURATION
        self.target_glow = 0.0
    
    def draw(self, screen):
        """Draw the paddle and its effects
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Draw trail
        if len(self.trail_points) > 1:
            for i, point in enumerate(self.trail_points):
                alpha = (i / len(self.trail_points)) * 128
                trail_color = (*self.color, int(alpha))
                pygame.draw.circle(screen, trail_color[:3], point, 3)
        
        # Draw glow effect
        if self.glow_intensity > 0:
            glow_size = int(self.glow_intensity * config.FORCE_GLOW_SIZE)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_color = (*self.color, int(self.glow_intensity * 100))
            pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
            
            glow_x = self.x + self.width // 2 - glow_size
            glow_y = self.y + self.height // 2 - glow_size
            screen.blit(glow_surface, (glow_x, glow_y))
        
        # Draw main paddle
        paddle_color = self.color
        if self.stunned:
            # Dim color when stunned
            paddle_color = tuple(int(c * 0.5) for c in self.color)
        
        pygame.draw.rect(screen, paddle_color, self.rect)
        
        # Draw force meter
        self.draw_force_meter(screen)
    
    def draw_force_meter(self, screen):
        """Draw the force meter below the paddle
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        meter_x = self.x - (config.FORCE_METER_WIDTH - self.width) // 2
        meter_y = self.y + self.height + 10
        
        # Background
        bg_rect = pygame.Rect(meter_x, meter_y, config.FORCE_METER_WIDTH, config.FORCE_METER_HEIGHT)
        pygame.draw.rect(screen, config.DARK_GRAY, bg_rect)
        pygame.draw.rect(screen, config.WHITE, bg_rect, 2)
        
        # Fill
        if self.force_meter > 0:
            fill_width = int(config.FORCE_METER_WIDTH * self.force_meter)
            fill_rect = pygame.Rect(meter_x, meter_y, fill_width, config.FORCE_METER_HEIGHT)
            
            if self.force_ready:
                # Bright color when ready
                fill_color = config.NEON_YELLOW
            else:
                # Normal color when charging
                fill_color = self.color
            
            pygame.draw.rect(screen, fill_color, fill_rect)
        
        # Ready indicator
        if self.force_ready:
            ready_text = "FORCE READY!"
            font = pygame.font.Font(None, 16)
            text_surface = font.render(ready_text, True, config.NEON_YELLOW)
            text_rect = text_surface.get_rect(center=(meter_x + config.FORCE_METER_WIDTH // 2, meter_y - 20))
            screen.blit(text_surface, text_rect)
    
    def get_state(self):
        """Get paddle state for networking
        
        Returns:
            dict: Paddle state data
        """
        return {
            'x': self.x,
            'y': self.y,
            'force_meter': self.force_meter,
            'force_ready': self.force_ready,
            'stunned': self.stunned,
            'glow_intensity': self.glow_intensity
        }
    
    def set_state(self, state):
        """Set paddle state from network data
        
        Args:
            state (dict): Paddle state data
        """
        self.x = state['x']
        self.y = state['y']
        self.force_meter = state['force_meter']
        self.force_ready = state['force_ready']
        self.stunned = state['stunned']
        self.glow_intensity = state['glow_intensity']
