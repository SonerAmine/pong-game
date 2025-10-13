# ===== PONG FORCE - GAME CLIENT =====

import socket
import threading
import json
import time
import sys
import os
import pygame

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_loop import GameLoop
import config

class GameClient:
    def __init__(self, host, port):
        """Initialize the game client
        
        Args:
            host (str): Server host address
            port (int): Server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.connected = False
        
        # Game state
        self.game_loop = None
        self.player_id = None
        
        # Network settings
        self.buffer_size = config.BUFFER_SIZE
        
        # Input handling
        self.input_queue = []
        self.last_input_time = 0
        self.input_throttle = 1.0 / 60  # Send input 60 times per second max
        
        # Error handling
        self.error_message = None
        self.error_title = None
        
        # Clock for FPS limiting
        self.clock = pygame.time.Clock()
    
    def connect(self):
        """Connect to server with timeout and detailed error messages"""
        try:
            print(f"🔗 Attempting to connect to {self.host}:{self.port}...")
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set connection timeout (10 seconds)
            self.socket.settimeout(10.0)
            
            # Try to connect
            self.socket.connect((self.host, self.port))
            
            # Connection successful - remove timeout for normal operation
            self.socket.settimeout(None)
            
            self.connected = True
            self.running = True
            print(f"✅ Connected to server at {self.host}:{self.port}")
            
            return True
            
        except socket.timeout:
            error_msg = f"❌ Connection timeout: Server at {self.host}:{self.port} did not respond.\nPlease check:\n- Server is running\n- IP address is correct\n- Firewall allows connection"
            print(error_msg)
            self.show_error_dialog("Connection Timeout", error_msg)
            return False
            
        except socket.gaierror:
            error_msg = f"❌ Invalid address: Could not resolve hostname '{self.host}'.\nPlease check that the IP address is correct."
            print(error_msg)
            self.show_error_dialog("Invalid Address", error_msg)
            return False
            
        except ConnectionRefusedError:
            error_msg = f"❌ Connection refused: Server at {self.host}:{self.port} refused connection.\nPlease check:\n- Server is running\n- Port {self.port} is correct\n- Firewall allows connection"
            print(error_msg)
            self.show_error_dialog("Connection Refused", error_msg)
            return False
            
        except Exception as e:
            error_msg = f"❌ Connection failed: {str(e)}\n\nPlease verify:\n- Server is running\n- IP address and port are correct\n- Network connection is working"
            print(error_msg)
            self.show_error_dialog("Connection Error", error_msg)
            return False
    
    def start_game(self):
        """Start the game loop"""
        self.game_loop = GameLoop()
        self.game_loop.is_client = True
        self.game_loop.game_state = config.STATE_CONNECTING
        
        # Start network thread
        network_thread = threading.Thread(target=self.network_loop, daemon=True)
        network_thread.start()
        
        # Start input thread
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()
        
        # Run game loop in main thread
        self.run_game_loop()
    
    def network_loop(self):
        """Network communication loop"""
        while self.running and self.connected:
            try:
                # Receive message
                data = self.socket.recv(self.buffer_size)
                if not data:
                    break
                
                # Parse message
                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)
                
            except Exception as e:
                if self.running:
                    print(f"❌ Network error: {e}")
                break
        
        self.disconnect()
    
    def input_loop(self):
        """Input handling loop"""
        while self.running:
            try:
                # Process input queue
                if self.input_queue and time.time() - self.last_input_time >= self.input_throttle:
                    input_data = self.input_queue.pop(0)
                    self.send_input(input_data)
                    self.last_input_time = time.time()
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                if self.running:
                    print(f"❌ Input error: {e}")
                break
    
    def run_game_loop(self):
        """Run the game loop"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle pygame events
            self.handle_events()
            
            # Update game
            if self.game_loop:
                self.game_loop.update(dt)
            
            # Render
            if self.game_loop:
                self.game_loop.render()
                pygame.display.flip()
            
            # Cap frame rate
            self.clock.tick(config.FPS)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)
            
            elif event.type == pygame.KEYUP:
                self.handle_key_release(event.key)
    
    def handle_key_press(self, key):
        """Handle key press
        
        Args:
            key (int): Pygame key constant
        """
        if not self.connected or not self.game_loop:
            return
        
        # Map keys to input
        input_mapping = {
            pygame.K_UP: 'up',
            pygame.K_DOWN: 'down',
            pygame.K_w: 'up',
            pygame.K_s: 'down',
            pygame.K_SPACE: 'force_push',
            pygame.K_LSHIFT: 'force_push',
            pygame.K_RSHIFT: 'force_push',
            pygame.K_ESCAPE: 'pause',
            pygame.K_r: 'restart'
        }
        
        if key in input_mapping:
            input_type = input_mapping[key]
            self.queue_input(input_type)
    
    def handle_key_release(self, key):
        """Handle key release
        
        Args:
            key (int): Pygame key constant
        """
        if not self.connected or not self.game_loop:
            return
        
        # Handle stop input for movement keys
        if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s]:
            self.queue_input('stop')
    
    def queue_input(self, input_type):
        """Queue input for sending to server
        
        Args:
            input_type (str): Type of input
        """
        # Only queue movement and action inputs
        if input_type in ['up', 'down', 'stop', 'force_push', 'pause', 'restart']:
            self.input_queue.append(input_type)
    
    def send_input(self, input_type):
        """Send input to server
        
        Args:
            input_type (str): Type of input
        """
        if not self.connected:
            return
        
        message = {
            'type': config.MSG_INPUT,
            'data': {
                'input': input_type
            }
        }
        
        # Special handling for force push
        if input_type == 'force_push':
            message['type'] = config.MSG_FORCE_PUSH
            message['data'] = {}
        
        # Special handling for pause
        elif input_type == 'pause':
            message['type'] = config.MSG_PAUSE
            message['data'] = {}
        
        # Special handling for restart
        elif input_type == 'restart':
            message['type'] = config.MSG_RESTART
            message['data'] = {}
        
        self.send_message(message)
    
    def handle_message(self, message):
        """Handle incoming message from server
        
        Args:
            message (dict): Message data
        """
        message_type = message.get('type')
        data = message.get('data', {})
        
        if message_type == 'welcome':
            self.handle_welcome(data)
        elif message_type == 'game_start':
            self.handle_game_start(data)
        elif message_type == 'game_state':
            self.handle_game_state(data)
        else:
            print(f"❌ Unknown message type: {message_type}")
    
    def handle_welcome(self, data):
        """Handle welcome message
        
        Args:
            data (dict): Welcome data
        """
        self.player_id = data.get('player_id')
        print(f"🎮 Welcome! You are Player {self.player_id}")
        
        if self.game_loop:
            self.game_loop.game_state = config.STATE_WAITING
    
    def handle_game_start(self, data):
        """Handle game start message
        
        Args:
            data (dict): Game start data
        """
        print("🎮 Game starting!")
        
        if self.game_loop:
            self.game_loop.game_state = config.STATE_PLAYING
    
    def handle_game_state(self, data):
        """Handle game state update
        
        Args:
            data (dict): Game state data
        """
        if self.game_loop:
            self.game_loop.set_game_state(data)
    
    def send_message(self, message):
        """Send message to server
        
        Args:
            message (dict): Message to send
        """
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            self.disconnect()
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        self.connected = False
        
        if self.socket:
            self.socket.close()
        
        print("👋 Disconnected from server")
    
    def show_error_dialog(self, title, message):
        """Store error message for display
        
        Args:
            title (str): Error title
            message (str): Error message
        """
        self.error_title = title
        self.error_message = message
    
    def run(self):
        """Run the client (main entry point)"""
        try:
            # Connect to server
            if not self.connect():
                # Connection failed - error dialog will be shown by main.py
                return
            
            # Start game
            self.start_game()
            
        except KeyboardInterrupt:
            print("\n🛑 Client interrupted by user")
        except Exception as e:
            error_msg = f"❌ Client error: {str(e)}"
            print(error_msg)
            self.show_error_dialog("Client Error", error_msg)
        finally:
            self.disconnect()
    
    def run_with_gui(self):
        """Run the client with GUI (for menu integration)"""
        try:
            # Connect to server
            if not self.connect():
                # Connection failed - error dialog will be shown by main.py
                return False
            
            # Initialize game loop with existing screen
            self.game_loop = GameLoop()
            self.game_loop.is_client = True
            self.game_loop.game_state = config.STATE_CONNECTING
            
            # Start network thread
            network_thread = threading.Thread(target=self.network_loop, daemon=True)
            network_thread.start()
            
            # Start input thread  
            input_thread = threading.Thread(target=self.input_loop, daemon=True)
            input_thread.start()
            
            # Run game loop in main thread (with GUI)
            self.game_loop.main_loop()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Client interrupted by user")
            return False
        except Exception as e:
            error_msg = f"❌ Client error: {str(e)}"
            print(error_msg)
            self.show_error_dialog("Client Error", error_msg)
            return False
        finally:
            self.disconnect()
