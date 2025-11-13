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
SUBNET = "172.16.130"
NOISE_INTERVAL = 0.5  # Very frequent noise
COMMON_PORTS = [53, 80, 23, 22, 443]

# Fake flags for maximum confusion
FAKE_FLAGS = [
    "FLAG{HTTP-Requests}",
    "FLAG{LetMeIN}",
    "FLAG{AlahuAkbar}",
    "FLAG{SystemHacked}",
    "FLAG{BackdoorOpen}",
    "FLAG{RootAccess}",
    "FLAG{DataStolen}",
    "FLAG{NetworkCompromised}",
    "FLAG{DNSServer}",
    "FLAG{WebServer}",
    "FLAG{PortScan}",
    "FLAG{ICMPFlood}",
    "FLAG{UDPFlood}",
    "FLAG{SYNflood}",
    "FLAG{EchoRequest}"
]

def generate_random_ip(subnet):
    """Generate random IP in the given subnet"""
    return f"{subnet}.{random.randint(1, 254)}"

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
                      input=proc.stdout, capture_output=True, timeout=2)
        print(f"Noise TCP to {ip}:{port}")
    except:
        pass

def send_noise_udp(ip, port, data="noise"):
    """Send UDP noise packet"""
    try:
        proc = subprocess.run(['echo', data], stdout=subprocess.PIPE)
        subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                      input=proc.stdout, capture_output=True, timeout=2)
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
                      input=proc.stdout, capture_output=True, timeout=2)
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
                      input=proc.stdout, capture_output=True, timeout=2)
        print(f"HTTP noise to {ip}:80")
    except:
        pass

def main():
    print("Starting Noise Generator for CTF Confusion...")
    print("Generating fake flags and noise traffic")
    print("Press Ctrl+C to stop")

    try:
        while True:
            ip = generate_random_ip(SUBNET)

            # Randomly choose noise type
            noise_type = random.choice([
                'ping', 'tcp', 'udp', 'dns', 'http', 'fake_flag',
                'ping', 'tcp', 'udp', 'fake_flag', 'fake_flag'  # Weighted for more fake flags
            ])

            if noise_type == 'ping':
                send_noise_ping(ip)
            elif noise_type == 'tcp':
                port = random.choice(COMMON_PORTS + [generate_random_port()])
                data = random.choice(["noise", "data", "test", "random" + str(random.randint(100,999))])
                send_noise_tcp(ip, port, data)
            elif noise_type == 'udp':
                port = random.choice(COMMON_PORTS + [generate_random_port()])
                data = random.choice(["noise", "data", "test", "random" + str(random.randint(100,999))])
                send_noise_udp(ip, port, data)
            elif noise_type == 'dns':
                send_dns_noise(ip)
            elif noise_type == 'http':
                send_http_noise(ip)
            elif noise_type == 'fake_flag':
                # Send fake flag to random port or common port
                if random.random() < 0.7:
                    port = generate_random_port()
                else:
                    port = random.choice(COMMON_PORTS)
                send_fake_flag(ip, port)

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping noise generator...")
        sys.exit(0)

if __name__ == "__main__":
    main()