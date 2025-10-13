# ===== PONG FORCE - GRAPHICAL MENU =====

import pygame
import sys
import config

class GameMenu:
    def __init__(self):
        """Initialize the game menu"""
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE + " - Menu")
        
        # Menu state
        self.running = True
        self.selected_option = 0
        self.menu_options = [
            "Play with Friend (Same PC)",
            "Play vs Robot",
            "Play Online Multiplayer"
        ]
        
        # Colors
        self.bg_color = config.BLACK
        self.title_color = config.NEON_YELLOW
        self.selected_color = config.NEON_PINK
        self.normal_color = config.WHITE
        self.subtitle_color = config.NEON_BLUE
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.option_font = pygame.font.Font(None, 36)
        self.subtitle_font = pygame.font.Font(None, 24)
        
        # Animation
        self.glow_alpha = 0
        self.glow_direction = 1
        
        # Clock
        self.clock = pygame.time.Clock()
        
    def run(self):
        """Run the menu and return selected option"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.selected_option
    
    def handle_events(self):
        """Handle menu events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.selected_option = 3  # Exit
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.running = False
                
                elif event.key == pygame.K_ESCAPE:
                    self.selected_option = -1  # Exit/Cancel
                    self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is over any option
                mouse_x, mouse_y = event.pos
                for i, option in enumerate(self.menu_options):
                    option_y = config.WINDOW_HEIGHT // 2 + i * 60
                    option_rect = pygame.Rect(
                        config.WINDOW_WIDTH // 2 - 200,
                        option_y - 20,
                        400,
                        40
                    )
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_option = i
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    for i, option in enumerate(self.menu_options):
                        option_y = config.WINDOW_HEIGHT // 2 + i * 60
                        option_rect = pygame.Rect(
                            config.WINDOW_WIDTH // 2 - 200,
                            option_y - 20,
                            400,
                            40
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = i
                            self.running = False
    
    def update(self):
        """Update menu animations"""
        # Pulse effect for title
        self.glow_alpha += self.glow_direction * 3
        if self.glow_alpha >= 255:
            self.glow_alpha = 255
            self.glow_direction = -1
        elif self.glow_alpha <= 100:
            self.glow_alpha = 100
            self.glow_direction = 1
    
    def render(self):
        """Render the menu"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw title with glow effect
        self.draw_title()
        
        # Draw subtitle
        self.draw_subtitle()
        
        # Draw menu options
        self.draw_options()
        
        # Draw controls hint
        self.draw_controls()
    
    def draw_title(self):
        """Draw the game title with glow effect"""
        title_text = "PONG FORCE"
        
        # Create glow effect
        glow_surface = self.title_font.render(title_text, True, self.title_color)
        glow_surface.set_alpha(self.glow_alpha)
        
        # Draw multiple layers for glow
        title_rect = glow_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 100))
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            self.screen.blit(glow_surface, glow_rect)
        
        # Draw main title
        title_surface = self.title_font.render(title_text, True, self.title_color)
        self.screen.blit(title_surface, title_rect)
    
    def draw_subtitle(self):
        """Draw subtitle"""
        subtitle_text = "Smash. Push. Win."
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_options(self):
        """Draw menu options"""
        for i, option in enumerate(self.menu_options):
            # Choose color based on selection
            if i == self.selected_option:
                color = self.selected_color
                # Draw selection indicator
                indicator_y = config.WINDOW_HEIGHT // 2 + i * 60
                pygame.draw.circle(
                    self.screen,
                    self.selected_color,
                    (config.WINDOW_WIDTH // 2 - 150, indicator_y),
                    5
                )
            else:
                color = self.normal_color
            
            # Render option text
            option_surface = self.option_font.render(option, True, color)
            option_rect = option_surface.get_rect(
                center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + i * 60)
            )
            self.screen.blit(option_surface, option_rect)
    
    def draw_controls(self):
        """Draw control hints"""
        hints = [
            "Use Arrow Keys or W/S to navigate",
            "Press ENTER or SPACE to select",
            "Press ESC to exit"
        ]
        
        y_offset = config.WINDOW_HEIGHT - 100
        for hint in hints:
            hint_surface = self.subtitle_font.render(hint, True, config.GRAY)
            hint_rect = hint_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(hint_surface, hint_rect)
            y_offset += 25


class HostInputDialog:
    """Dialog to get server IP address for client connection"""
    
    def __init__(self, default_host=config.SERVER_IP):
        """Initialize the input dialog
        
        Args:
            default_host (str): Default server IP address
        """
        self.screen = pygame.display.get_surface()
        self.running = True
        self.input_text = default_host
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.clock = pygame.time.Clock()
        
    def run(self):
        """Run the input dialog and return entered IP address"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.input_text if self.input_text else config.SERVER_IP
    
    def handle_events(self):
        """Handle input dialog events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.input_text = config.SERVER_IP
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.running = False
                
                elif event.key == pygame.K_ESCAPE:
                    self.input_text = config.SERVER_IP
                    self.running = False
                
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                
                else:
                    # Add character to input
                    if event.unicode.isprintable():
                        self.input_text += event.unicode
    
    def update(self):
        """Update cursor blinking"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink every 0.5 seconds
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def render(self):
        """Render the input dialog"""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(config.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        dialog_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 250,
            config.WINDOW_HEIGHT // 2 - 100,
            500,
            200
        )
        pygame.draw.rect(self.screen, config.DARK_GRAY, dialog_rect)
        pygame.draw.rect(self.screen, config.NEON_BLUE, dialog_rect, 3)
        
        # Draw title
        title_surface = self.title_font.render("Enter Server IP", True, config.NEON_YELLOW)
        title_rect = title_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 60)
        )
        self.screen.blit(title_surface, title_rect)
        
        # Draw input box
        input_box = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 200,
            config.WINDOW_HEIGHT // 2 - 10,
            400,
            40
        )
        pygame.draw.rect(self.screen, config.BLACK, input_box)
        pygame.draw.rect(self.screen, config.NEON_PINK, input_box, 2)
        
        # Draw input text
        input_surface = self.font.render(self.input_text, True, config.WHITE)
        self.screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
        
        # Draw cursor
        if self.cursor_visible:
            cursor_x = input_box.x + 10 + input_surface.get_width()
            pygame.draw.line(
                self.screen,
                config.WHITE,
                (cursor_x, input_box.y + 5),
                (cursor_x, input_box.y + 35),
                2
            )
        
        # Draw hint
        hint_text = "Press ENTER to connect, ESC to cancel"
        hint_surface = pygame.font.Font(None, 20).render(hint_text, True, config.GRAY)
        hint_rect = hint_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 60)
        )
        self.screen.blit(hint_surface, hint_rect)


class OnlineSubmenu:
    """Submenu for online multiplayer options"""
    
    def __init__(self):
        """Initialize the online submenu"""
        self.screen = pygame.display.get_surface()
        self.running = True
        self.selected_option = 0
        self.options = [
            "Host a Game",
            "Join a Game",
            "Back to Menu"
        ]
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.clock = pygame.time.Clock()
        
    def run(self):
        """Run the submenu and return selected option"""
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.selected_option
    
    def handle_events(self):
        """Handle submenu events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.selected_option = -1
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == 2:  # Back to Menu
                        self.selected_option = -1
                    self.running = False
                
                elif event.key == pygame.K_ESCAPE:
                    self.selected_option = -1
                    self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for i, option in enumerate(self.options):
                    option_y = config.WINDOW_HEIGHT // 2 + i * 60
                    option_rect = pygame.Rect(
                        config.WINDOW_WIDTH // 2 - 200,
                        option_y - 20,
                        400,
                        40
                    )
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_option = i
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    for i, option in enumerate(self.options):
                        option_y = config.WINDOW_HEIGHT // 2 + i * 60
                        option_rect = pygame.Rect(
                            config.WINDOW_WIDTH // 2 - 200,
                            option_y - 20,
                            400,
                            40
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = i
                            if self.selected_option == 2:  # Back to Menu
                                self.selected_option = -1
                            self.running = False
    
    def render(self):
        """Render the submenu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(config.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = "Online Multiplayer"
        title_surface = self.title_font.render(title_text, True, config.NEON_BLUE)
        title_rect = title_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 100)
        )
        self.screen.blit(title_surface, title_rect)
        
        # Draw options
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = config.NEON_PINK
                # Draw selection indicator
                indicator_y = config.WINDOW_HEIGHT // 2 + i * 60
                pygame.draw.circle(
                    self.screen,
                    config.NEON_PINK,
                    (config.WINDOW_WIDTH // 2 - 120, indicator_y),
                    5
                )
            else:
                color = config.WHITE
            
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(
                center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + i * 60)
            )
            self.screen.blit(option_surface, option_rect)

