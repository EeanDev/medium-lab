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
NOISE_INTERVAL = 10  # seconds between fake flag bursts (to all IPs)

# Fake FLAG messages for confusion
FAKE_FLAGS = [
    "FLAG{ThisIsNotMe}",
    "FLAG{TryAgain}",
    "FLAG{SORRY}",
    "FLAG{NotTheFlag}",
    "FLAG{AlmostThere}",
    "FLAG{WrongOne}",
    "FLAG{NOPE}",
    "FLAG{CloseButNo}"
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

def main():
    print("Starting Fake Flags Sender for CTF Lab...")
    print("Will send fake flags continuously in hierarchical order")
    print("Press Ctrl+C to stop")

    # Generate list of all IPs in subnet
    all_ips = generate_all_ips(SUBNET)
    print(f"Targeting {len(all_ips)} IPs in {SUBNET}.0/24 subnet")

    # Initialize flag index for hierarchical/iterative sending
    flag_index = 0

    try:
        while True:
            # Send fake flag to ALL IPs in subnet (hierarchical order)
            fake_flag = FAKE_FLAGS[flag_index % len(FAKE_FLAGS)]
            flag_index += 1  # Move to next flag for next iteration

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

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping fake flags sender...")
        sys.exit(0)

if __name__ == "__main__":
    main()