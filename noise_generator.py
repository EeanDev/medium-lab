#!/usr/bin/env python3
"""
Noise-Only Packet Generator for CTF Lab Distraction
Creates confusion across multiple Ubuntu servers
"""

import subprocess
import random
import time
import socket
import sys

# Configuration
SUBNET = "172.16.200"
TEST_IP = "172.16.120.11"  # Kali testing IP
NOISE_INTERVAL = 2  # 2 seconds between IPs
COMMON_PORTS = [53, 80, 23, 22, 443]

# Fake flags for maximum confusion
FAKE_FLAGS = [
    "{HTTP-Requests}",
    "{LetMeIN}",
    "{AlahuAkbar}",
    "{SystemHacked}",
    "{BackdoorOpen}",
    "{RootAccess}",
    "{DataStolen}",
    "{DNSServer}",
    "{WebServer}",
    "{PortScan}",
    "{ICMPFlood}",
    "{UDPFlood}",
    "{SYNflood}",
    "{EchoRequest}"
]

def generate_all_ips(subnet):
    """Generate list of all IPs in the subnet"""
    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    ips.append(TEST_IP)  # Add test IP
    return ips

def get_random_ip(ip_list):
    """Get random IP from list for fair distribution"""
    return random.choice(ip_list)

def generate_random_port():
    """Generate random port between 1024-65535"""
    return random.randint(1024, 65535)

def send_noise_ping(ip):
    """Send ping noise"""
    try:
        subprocess.run(['ping', '-c', '1', '-W', '1', ip],
                      capture_output=True, timeout=2)
        print(f"Noise ping to {ip}")
    except:
        pass

def send_noise_tcp(ip, port, data="noise"):
    """Send TCP noise packet"""
    try:
        proc = subprocess.run(['echo', data], stdout=subprocess.PIPE)
        subprocess.run(['nc', '-w', '1', ip, str(port)],
                      input=proc.stdout, capture_output=True, text=True, timeout=2)
        print(f"Noise TCP to {ip}:{port}")
    except:
        pass

def send_noise_udp(ip, port, data="noise"):
    """Send UDP noise packet"""
    try:
        proc = subprocess.run(['echo', data], stdout=subprocess.PIPE)
        subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                      input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        print(f"Noise UDP to {ip}:{port}")
    except:
        pass

def send_fake_flag(ip, port=None):
    """Send fake flag to create confusion"""
    try:
        if port is None:
            port = generate_random_port()
        fake_flag = random.choice(FAKE_FLAGS)
        proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
        subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                      input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        print(f"FAKE FLAG '{fake_flag}' to {ip}:{port}")
    except:
        pass

def send_dns_noise(ip):
    """Send DNS query noise"""
    try:
        domains = ['example.com', 'google.com', 'test.local', 'noise.net']
        domain = random.choice(domains)
        subprocess.run(['dig', '@' + ip, domain, '+short', '+timeout=1'],
                      capture_output=True, timeout=2)
        print(f"DNS noise to {ip}: {domain}")
    except:
        pass

def send_http_noise(ip):
    """Send HTTP request noise"""
    try:
        requests = [
            "GET / HTTP/1.0\r\n\r\n",
            "GET /admin HTTP/1.0\r\n\r\n",
            "GET /login HTTP/1.0\r\n\r\n",
            "POST /api HTTP/1.0\r\n\r\n"
        ]
        request = random.choice(requests)
        proc = subprocess.run(['echo', '-e', request], stdout=subprocess.PIPE)
        subprocess.run(['nc', '-w', '1', ip, '80'],
                      input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        print(f"HTTP noise to {ip}:80")
    except:
        pass

def main():
    print("Starting Noise Generator for CTF Confusion...")
    print("Random IP selection: fair distribution to all IPs")
    print("Generating fake flags and noise traffic")
    print("Press Ctrl+C to stop")

    # Generate list of all IPs in subnet
    all_ips = generate_all_ips(SUBNET)
    print(f"Targeting {len(all_ips)} IPs in {SUBNET}.0/24 subnet")

    try:
        while True:
            # Get random IP for fair distribution
            ip = get_random_ip(all_ips)

            # Reduced noise: simple TCP/UDP/ping only
            noise_type = random.choice(['tcp', 'udp', 'tcp', 'udp', 'ping'])

            if noise_type == 'ping':
                send_noise_ping(ip)
            elif noise_type == 'tcp':
                port = generate_random_port()
                data = random.choice(["noise", "data", "test"])
                send_noise_tcp(ip, port, data)
            elif noise_type == 'udp':
                port = generate_random_port()
                data = random.choice(["noise", "data", "test"])
                send_noise_udp(ip, port, data)

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping noise generator...")
        sys.exit(0)

if __name__ == "__main__":
    main()