# ===== PONG FORCE - GAME SERVER =====

import socket
import threading
import json
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_loop import GameLoop
import config

class GameServer:
    def __init__(self, host, port):
        """Initialize the game server
        
        Args:
            host (str): Server host address
            port (int): Server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.clients = []
        self.running = False
        
        # Game state
        self.game_loop = None
        self.game_thread = None
        
        # Network settings
        self.max_clients = 2
        self.buffer_size = config.BUFFER_SIZE
        self.update_rate = config.NETWORK_UPDATE_RATE
        
        # Message handling
        self.message_handlers = {
            config.MSG_CONNECT: self.handle_connect,
            config.MSG_DISCONNECT: self.handle_disconnect,
            config.MSG_INPUT: self.handle_input,
            config.MSG_FORCE_PUSH: self.handle_force_push,
            config.MSG_PAUSE: self.handle_pause,
            config.MSG_RESTART: self.handle_restart
        }
    
    def start(self):
        """Start the server with improved error handling"""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                self.socket.bind((self.host, self.port))
            except OSError as e:
                if e.errno == 10048:  # Port already in use on Windows
                    print(f"❌ Port {self.port} is already in use!")
                    print(f"💡 Close other instances of Pong Force or use a different port")
                    input("Press Enter to exit...")
                    return
                else:
                    raise
            
            self.socket.listen(self.max_clients)
            
            self.running = True
            print(f"✅ Server started successfully!")
            print(f"📍 Listening on {self.host}:{self.port}")
            print(f"🌐 Share your PUBLIC IP with other players")
            print(f"💡 Find your IP at: www.whatismyip.com")
            print(f"⏳ Waiting for {self.max_clients} player(s) to connect...")
            
            # Start game loop
            self.start_game()
            
            # Start accepting connections
            self.accept_connections()
            
        except KeyboardInterrupt:
            print("\n🛑 Server interrupted by user")
            self.stop()
        except Exception as e:
            print(f"❌ Server error: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")
            self.stop()
    
    def start_game(self):
        """Start the game loop"""
        # Use existing pygame screen instead of creating a new one
        self.game_loop = GameLoop()
        self.game_loop.is_server = True
        self.game_loop.game_state = config.STATE_WAITING
        
        # Don't start game thread yet - will be started in run_with_gui()
        self.game_thread = None
    
    def run_game_loop(self):
        """Run the game loop (in separate thread)"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Update game
            self.game_loop.update(dt)
            
            # Send game state to clients
            self.broadcast_game_state()
            
            # Cap update rate
            time.sleep(1.0 / self.update_rate)
    
    def accept_connections(self):
        """Accept client connections"""
        print("⏳ Waiting for players to connect...")
        
        while self.running:
            try:
                # Accept connection
                client_socket, address = self.socket.accept()
                print(f"🔗 Client connected from {address}")
                
                # Check if we have room for more clients
                if len(self.clients) >= self.max_clients:
                    print(f"❌ Server full, rejecting connection from {address}")
                    client_socket.close()
                    continue
                
                # Create client handler
                client_handler = ClientHandler(client_socket, address, self)
                self.clients.append(client_handler)
                
                # Start client handler thread
                client_thread = threading.Thread(target=client_handler.run, daemon=True)
                client_thread.start()
                
                # Start game if we have enough players
                if len(self.clients) == self.max_clients:
                    self.start_game_session()
                
            except Exception as e:
                if self.running:
                    print(f"❌ Connection error: {e}")
                break
    
    def start_game_session(self):
        """Start the game session"""
        print("🎮 Starting game session with 2 players!")
        self.game_loop.game_state = config.STATE_PLAYING
        
        # Send game start message to all clients
        message = {
            'type': 'game_start',
            'data': {
                'message': 'Game starting!'
            }
        }
        self.broadcast_message(message)
    
    def handle_connect(self, client, data):
        """Handle client connection
        
        Args:
            client (ClientHandler): Client that connected
            data (dict): Connection data
        """
        print(f"✅ Client {client.address} connected")
        
        # Send welcome message
        welcome_message = {
            'type': 'welcome',
            'data': {
                'player_id': len(self.clients),
                'message': 'Welcome to Pong Force!'
            }
        }
        client.send_message(welcome_message)
    
    def handle_disconnect(self, client, data):
        """Handle client disconnection
        
        Args:
            client (ClientHandler): Client that disconnected
            data (dict): Disconnect data
        """
        print(f"👋 Player {client.player_id} ({client.address}) disconnected")
        
        if client in self.clients:
            self.clients.remove(client)
        
        # Pause game if not enough players
        if len(self.clients) < self.max_clients:
            self.game_loop.game_state = config.STATE_WAITING
            print(f"⏸️ Game paused - waiting for more players ({len(self.clients)}/{self.max_clients})")
            
            # Notify remaining clients
            if self.clients:
                message = {
                    'type': 'player_disconnected',
                    'data': {
                        'message': f'Player {client.player_id} disconnected. Waiting for new player...'
                    }
                }
                self.broadcast_message(message)
    
    def handle_input(self, client, data):
        """Handle client input
        
        Args:
            client (ClientHandler): Client that sent input
            data (dict): Input data
        """
        if not self.game_loop or self.game_loop.game_state != config.STATE_PLAYING:
            return
        
        # Apply input to appropriate paddle
        player_id = client.player_id
        input_type = data.get('input')
        
        if player_id == 1:
            paddle = self.game_loop.paddle1
        else:
            paddle = self.game_loop.paddle2
        
        # Handle input
        if input_type == 'up':
            paddle.move_up()
        elif input_type == 'down':
            paddle.move_down()
        elif input_type == 'stop':
            paddle.stop_moving()
    
    def handle_force_push(self, client, data):
        """Handle force push request
        
        Args:
            client (ClientHandler): Client that sent force push
            data (dict): Force push data
        """
        if not self.game_loop or self.game_loop.game_state != config.STATE_PLAYING:
            return
        
        player_id = client.player_id
        
        if player_id == 1:
            paddle = self.game_loop.paddle1
        else:
            paddle = self.game_loop.paddle2
        
        # Try force push
        if paddle.try_force_push(self.game_loop.ball):
            # Create force effect
            self.game_loop.effects.create_force_effect(
                self.game_loop.ball.x + self.game_loop.ball.size // 2,
                self.game_loop.ball.y + self.game_loop.ball.size // 2,
                player_id
            )
    
    def handle_pause(self, client, data):
        """Handle pause request
        
        Args:
            client (ClientHandler): Client that sent pause
            data (dict): Pause data
        """
        if self.game_loop:
            if self.game_loop.game_state == config.STATE_PLAYING:
                self.game_loop.game_state = config.STATE_PAUSED
            elif self.game_loop.game_state == config.STATE_PAUSED:
                self.game_loop.game_state = config.STATE_PLAYING
    
    def handle_restart(self, client, data):
        """Handle restart request
        
        Args:
            client (ClientHandler): Client that sent restart
            data (dict): Restart data
        """
        if self.game_loop:
            self.game_loop.restart_game()
    
    def broadcast_message(self, message):
        """Broadcast message to all clients
        
        Args:
            message (dict): Message to broadcast
        """
        for client in self.clients[:]:  # Copy list to avoid modification during iteration
            try:
                client.send_message(message)
            except:
                # Remove disconnected client
                self.clients.remove(client)
    
    def broadcast_game_state(self):
        """Broadcast current game state to all clients"""
        if not self.game_loop:
            return
        
        game_state = self.game_loop.get_game_state()
        
        message = {
            'type': 'game_state',
            'data': game_state
        }
        
        self.broadcast_message(message)
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            client.disconnect()
        
        # Close server socket
        if self.socket:
            self.socket.close()
        
        print("🛑 Server stopped")
    
    def run(self):
        """Run the server (main entry point)"""
        try:
            self.start()
        except KeyboardInterrupt:
            print("\n🛑 Server interrupted by user")
        finally:
            self.stop()
    
    def run_with_gui(self):
        """Run the server with GUI (for menu integration)"""
        import pygame
        
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                self.socket.bind((self.host, self.port))
            except OSError as e:
                if e.errno == 10048:  # Port already in use on Windows
                    print(f"❌ Port {self.port} is already in use!")
                    return False
                else:
                    raise
            
            self.socket.listen(self.max_clients)
            self.running = True
            
            print(f"✅ Server started successfully!")
            print(f"📍 Listening on {self.host}:{self.port}")
            
            # Start game loop
            self.start_game()
            
            # Start accepting connections in background thread
            accept_thread = threading.Thread(target=self.accept_connections_gui, daemon=True)
            accept_thread.start()
            
            # Run the game loop in main thread (with GUI)
            self.game_loop.main_loop()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Server interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Server error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.stop()
    
    def accept_connections_gui(self):
        """Accept connections in background thread for GUI mode"""
        print("⏳ Waiting for players to connect...")
        
        while self.running:
            try:
                # Set timeout so we can check self.running periodically
                self.socket.settimeout(1.0)
                
                try:
                    # Accept connection
                    client_socket, address = self.socket.accept()
                    print(f"🔗 Client connected from {address}")
                    
                    # Check if we have room for more clients
                    if len(self.clients) >= self.max_clients:
                        print(f"❌ Server full, rejecting connection from {address}")
                        client_socket.close()
                        continue
                    
                    # Create client handler
                    client_handler = ClientHandler(client_socket, address, self)
                    self.clients.append(client_handler)
                    
                    # Send welcome message
                    self.handle_connect(client_handler, {})
                    
                    # Start client handler thread
                    client_thread = threading.Thread(target=client_handler.run, daemon=True)
                    client_thread.start()
                    
                    # Start game if we have enough players
                    if len(self.clients) == self.max_clients:
                        self.start_game_session()
                        
                        # Start game update thread now
                        if not self.game_thread:
                            self.game_thread = threading.Thread(target=self.run_game_loop, daemon=True)
                            self.game_thread.start()
                
                except socket.timeout:
                    # Timeout is normal, just continue
                    continue
                    
            except Exception as e:
                if self.running:
                    print(f"❌ Connection error: {e}")
                break

class ClientHandler:
    def __init__(self, socket, address, server):
        """Initialize client handler
        
        Args:
            socket (socket.socket): Client socket
            address (tuple): Client address
            server (GameServer): Server instance
        """
        self.socket = socket
        self.address = address
        self.server = server
        self.player_id = len(server.clients) + 1
        self.running = True
    
    def run(self):
        """Run client handler"""
        try:
            while self.running:
                # Receive message
                data = self.socket.recv(self.server.buffer_size)
                if not data:
                    break
                
                # Parse message
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.handle_message(message)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from {self.address}")
                    continue
                
        except Exception as e:
            print(f"❌ Client handler error for {self.address}: {e}")
        finally:
            self.disconnect()
    
    def handle_message(self, message):
        """Handle incoming message
        
        Args:
            message (dict): Message data
        """
        message_type = message.get('type')
        data = message.get('data', {})
        
        if message_type in self.server.message_handlers:
            handler = self.server.message_handlers[message_type]
            handler(self, data)
        else:
            print(f"❌ Unknown message type: {message_type}")
    
    def send_message(self, message):
        """Send message to client
        
        Args:
            message (dict): Message to send
        """
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            print(f"❌ Error sending message to {self.address}: {e}")
            raise
    
    def disconnect(self):
        """Disconnect client"""
        self.running = False
        if self.socket:
            self.socket.close()
        
        # Notify server of disconnection
        if self in self.server.clients:
            self.server.handle_disconnect(self, {})
