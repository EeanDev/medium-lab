#!/usr/bin/env python3
"""
Packet Sender Script for CTF Lab
Sends noise packets and hides flag in random port packet.
Runs on Ubuntu 24.04 LTS using netcat and system commands.
"""

import subprocess
import random
import time
import socket
import sys

# Configuration
SUBNET = "172.16.130"
FLAG_INTERVAL = 5  # seconds
NOISE_INTERVAL = 1  # seconds
COMMON_PORTS = [53, 80, 23]  # DNS, HTTP, Telnet

# Context-aware flags for confusion
CONTEXT_FLAGS = {
    "dns": ["FLAG{DNSServer}", "FLAG{YouStillDidn'tFindMe-2025}"],
    "http": ["FLAG{HTTP-Requests}", "FLAG{UMAKITSO-2024}"],
    "telnet": ["FLAG{LetMeIN}", "FLAG{decoy-2025}"],
    "tcp": ["FLAG{PortScan}", "FLAG{UMAKITSO-2023}"],
    "udp": ["FLAG{UDPStream}", "FLAG{Isthisme?No}"],
    "ping": ["FLAG{ICMPFlood}", "FLAG{HAHAHAHA}"],
    "real": "FLAG{YouFoundMe-2025}"
}

def generate_random_ip(subnet):
    """Generate random IP in the given subnet (e.g., 172.16.130.x)"""
    return f"{subnet}.{random.randint(1, 254)}"

def generate_random_port(exclude_common=False):
    """Generate random port between 1024-65535, optionally excluding common ports"""
    port = random.randint(1024, 65535)
    if exclude_common and port in COMMON_PORTS:
        return generate_random_port(exclude_common=True)
    return port

def send_ping(ip):
    """Send ICMP ping packet"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip],
                              capture_output=True, text=True, timeout=2)
        print(f"Sent ping to {ip}")
    except subprocess.TimeoutExpired:
        print(f"Ping to {ip} timed out")
    except Exception as e:
        print(f"Error sending ping to {ip}: {e}")

def send_tcp_packet(ip, port, data="noise"):
    """Send TCP packet using netcat"""
    try:
        proc = subprocess.run(['echo', data],
                            stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-w', '1', ip, str(port)],
                              input=proc.stdout, capture_output=True, text=True, timeout=2)
        print(f"Sent TCP packet to {ip}:{port}")
    except subprocess.TimeoutExpired:
        print(f"TCP connection to {ip}:{port} timed out")
    except Exception as e:
        print(f"Error sending TCP to {ip}:{port}: {e}")

def send_udp_packet(ip, port, data="noise"):
    """Send UDP packet using netcat"""
    try:
        proc = subprocess.run(['echo', data],
                            stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                              input=proc.stdout, capture_output=True, text=True, timeout=2)
        print(f"Sent UDP packet to {ip}:{port}")
    except subprocess.TimeoutExpired:
        print(f"UDP send to {ip}:{port} timed out")
    except Exception as e:
        print(f"Error sending UDP to {ip}:{port}: {e}")

def send_dns_query(ip):
    """Send DNS query using dig"""
    try:
        result = subprocess.run(['dig', '@' + ip, 'example.com', '+short', '+timeout=1'],
                              capture_output=True, text=True, timeout=2)
        print(f"Sent DNS query to {ip}:53")
    except subprocess.TimeoutExpired:
        print(f"DNS query to {ip} timed out")
    except Exception as e:
        print(f"Error sending DNS query to {ip}: {e}")

def send_http_request(ip):
    """Send HTTP GET request"""
    try:
        http_request = "GET / HTTP/1.0\r\nHost: example.com\r\n\r\n"
        proc = subprocess.run(['echo', '-e', http_request],
                            stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-w', '1', ip, '80'],
                              input=proc.stdout, capture_output=True, text=True, timeout=2)
        print(f"Sent HTTP request to {ip}:80")
    except subprocess.TimeoutExpired:
        print(f"HTTP request to {ip}:80 timed out")
    except Exception as e:
        print(f"Error sending HTTP to {ip}:80: {e}")

def send_telnet_attempt(ip):
    """Send Telnet connection attempt"""
    try:
        result = subprocess.run(['nc', '-w', '1', ip, '23'],
                              input=b'', capture_output=True, timeout=2)
        print(f"Sent Telnet attempt to {ip}:23")
    except subprocess.TimeoutExpired:
        print(f"Telnet attempt to {ip}:23 timed out")
    except Exception as e:
        print(f"Error sending Telnet to {ip}:23: {e}")

def send_flag_packet(ip, port):
    """Send flag packet to random port"""
    try:
        flag = CONTEXT_FLAGS["real"]
        proc = subprocess.run(['echo', flag],
                            stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                              input=proc.stdout, capture_output=True, text=True, timeout=2)
        print(f"*** SENT REAL FLAG TO {ip}:{port} ***")
    except subprocess.TimeoutExpired:
        print(f"Flag send to {ip}:{port} timed out")
    except Exception as e:
        print(f"Error sending flag to {ip}:{port}: {e}")

def send_fake_flag_packet(ip, port, context):
    """Send fake flag packet for confusion"""
    try:
        fake_flag = random.choice(CONTEXT_FLAGS[context])
        proc = subprocess.run(['echo', fake_flag],
                            stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                              input=proc.stdout, capture_output=True, text=True, timeout=2)
        print(f"Sent fake flag '{fake_flag}' to {ip}:{port}")
    except subprocess.TimeoutExpired:
        print(f"Fake flag send to {ip}:{port} timed out")
    except Exception as e:
        print(f"Error sending fake flag to {ip}:{port}: {e}")

def is_admin_logged_in():
    """Check if admin users are currently logged in"""
    try:
        result = subprocess.run(['who'], capture_output=True, text=True, timeout=5)
        admin_users = ['root']  # Add your admin usernames here
        for line in result.stdout.split('\n'):
            if line.strip():
                user = line.split()[0]
                if user in admin_users:
                    return True
        return False
    except Exception as e:
        print(f"Error checking admin login: {e}")
        return False

def send_noise_only():
    """Send only noise packets (no real flag)"""
    noise_ip = generate_random_ip(SUBNET)

    # Cycle through different packet types with fake flags
    packet_type = random.choice(['ping', 'dns', 'http', 'telnet', 'tcp', 'udp'])

    if packet_type == 'ping':
        send_ping(noise_ip)
        # Sometimes send fake ping flag
        if random.random() < 0.3:
            send_fake_flag_packet(noise_ip, generate_random_port(), 'ping')
    elif packet_type == 'dns':
        send_dns_query(noise_ip)
        # Sometimes send fake DNS flag
        if random.random() < 0.3:
            send_fake_flag_packet(noise_ip, 53, 'dns')
    elif packet_type == 'http':
        send_http_request(noise_ip)
        # Sometimes send fake HTTP flag
        if random.random() < 0.3:
            send_fake_flag_packet(noise_ip, 80, 'http')
    elif packet_type == 'telnet':
        send_telnet_attempt(noise_ip)
        # Sometimes send fake telnet flag
        if random.random() < 0.3:
            send_fake_flag_packet(noise_ip, 23, 'telnet')
    elif packet_type == 'tcp':
        port = generate_random_port()
        send_tcp_packet(noise_ip, port)
        # Sometimes send fake TCP flag
        if random.random() < 0.3:
            send_fake_flag_packet(noise_ip, port, 'tcp')
    elif packet_type == 'udp':
        port = generate_random_port()
        send_udp_packet(noise_ip, port)
        # Sometimes send fake UDP flag
        if random.random() < 0.3:
            send_fake_flag_packet(noise_ip, port, 'udp')

def main():
    print("Starting Packet Sender for CTF Lab...")
    print("Flag will only be sent when admin users are logged in")
    print("Press Ctrl+C to stop")

    # Select random port for flag (fixed for this session)
    flag_port = generate_random_port(exclude_common=True)
    print(f"Flag will be sent to random port: {flag_port}")

    last_flag_time = 0

    try:
        while True:
            current_time = time.time()
            admin_logged_in = is_admin_logged_in()

            if admin_logged_in:
                print("Admin logged in - sending flag + noise")
                # Send flag every 5 seconds when admin is online
                if current_time - last_flag_time >= FLAG_INTERVAL:
                    flag_ip = generate_random_ip(SUBNET)
                    send_flag_packet(flag_ip, flag_port)
                    last_flag_time = current_time
            else:
                print("No admin logged in - sending noise only")
                # Reset flag timer when admin logs out
                last_flag_time = 0

            # Always send noise packets
            send_noise_only()

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping packet sender...")
        sys.exit(0)

if __name__ == "__main__":
    main()