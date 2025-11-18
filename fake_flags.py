#!/usr/bin/env python3
"""
Fake Flags Sender Script for CTF Lab
Continuously sends fake flags to create confusion
Runs on Ubuntu 24.04 LTS using netcat.
"""

import subprocess
import random
import time
import socket
import sys

# Configuration
SUBNET = "172.16.200"
NOISE_INTERVAL = 30  # seconds between fake flag bursts (to all IPs)

# Fake FLAG messages for confusion
FAKE_FLAGS = [
    "FLAG{ThisIsNotMe}",
    "FLAG{TryAgain}",
    "FLAG{SORRY}",
    "FLAG{NotTheFlag}",
    "FLAG{AlmostThere}",
    "FLAG{NiceTry}",
    "FLAG{WrongOne}",
    "FLAG{KeepLooking}",
    "FLAG{CloseButNo}",
    "FLAG{GettingWarmer}",
    "FLAG{NoFlagHere}",
    "FLAG{NOPENOPE}"
]

def generate_all_ips(subnet):
    """Generate list of all valid IPs in the subnet (exclude .0, .254, .255)"""
    ips = [f"{subnet}.{i}" for i in range(1, 254)]  # 1-253 inclusive
    ips.append("172.16.120.11")  # Add test IP
    return ips

def get_random_ip(ip_list):
    """Get random IP from list for fair distribution"""
    return random.choice(ip_list)

def generate_random_port(exclude_common=False):
    """Generate random port between 1024-65535, optionally excluding common ports"""
    port = random.randint(1024, 65535)
    if exclude_common and port in [53, 80, 23]:
        return generate_random_port(exclude_common=True)
    return port

def send_fake_flag(ip):
    """Send fake flag packet for confusion (only ICMP and UDP)"""
    try:
        fake_flag = random.choice(FAKE_FLAGS)
        packet_type = random.choice(['icmp', 'udp'])  # Only ICMP and UDP for flags

        if packet_type == 'icmp':
            # Try ICMP first, fallback to UDP
            proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
            result = subprocess.run(['nc', '-u', '-w', '1', ip, str(generate_random_port())],
                                  input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        else:  # UDP
            proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
            result = subprocess.run(['nc', '-u', '-w', '1', ip, str(generate_random_port())],
                                  input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        print(f"[{time.strftime('%H:%M:%S')}] Sent fake flag '{fake_flag}' to {ip} via {packet_type.upper()}")
    except subprocess.TimeoutExpired:
        print(f"[{time.strftime('%H:%M:%S')}] Fake flag send to {ip} timed out")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error sending fake flag to {ip}: {e}")

def is_admin_logged_in():
    """Check if admin users are currently logged in"""
    try:
        result = subprocess.run(['who'], capture_output=True, text=True, timeout=5)
        admin_users = ['root', 'uvmu']  # Add your admin usernames here
        for line in result.stdout.split('\n'):
            if line.strip():
                user = line.split()[0]
                if user in admin_users:
                    return True
        return False
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error checking admin login: {e}")
        return False

def main():
    print("Starting Fake Flags Sender for CTF Lab...")
    print("Will send fake flags continuously when admin users are logged in")
    print("Press Ctrl+C to stop")

    # Generate list of all IPs in subnet
    all_ips = generate_all_ips(SUBNET)
    print(f"Targeting {len(all_ips)} IPs in {SUBNET}.0/24 subnet")

    try:
        while True:
            current_time = time.time()
            admin_logged_in = is_admin_logged_in()

            if admin_logged_in:
                # Send fake flag to ALL IPs in subnet
                fake_flag = random.choice(FAKE_FLAGS)
                print(f"[{time.strftime('%H:%M:%S')}] Sending fake flag '{fake_flag}' to ALL {len(all_ips)} IPs")

                for ip in all_ips:
                    packet_type = random.choice(['icmp', 'udp'])
                    try:
                        if packet_type == 'icmp':
                            proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
                            result = subprocess.run(['nc', '-u', '-w', '1', ip, str(generate_random_port())],
                                  input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
                        else:  # UDP
                            proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
                            result = subprocess.run(['nc', '-u', '-w', '1', ip, str(generate_random_port())],
                                  input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
                        print(f"[{time.strftime('%H:%M:%S')}] Sent '{fake_flag}' to {ip}")
                    except Exception as e:
                        print(f"[{time.strftime('%H:%M:%S')}] Error sending to {ip}: {e}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] No admin logged in - waiting...")

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping fake flags sender...")
        sys.exit(0)

if __name__ == "__main__":
    main()