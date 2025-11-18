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
SUBNET = "172.16.200"
TEST_IP = "172.16.120.11"  # Kali testing IP
FLAG_INTERVAL = 5  # seconds between IPs for flag
NOISE_INTERVAL = 2  # seconds between IPs for noise
COMMON_PORTS = [53, 80, 23]  # DNS, HTTP, Telnet

# Fake FLAG messages for confusion + real flag (all sent via ICMP or UDP)
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

REAL_FLAG = "$flag{nahanapmo}"

def generate_all_ips(subnet):
    """Generate list of all IPs in the subnet"""
    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    ips.append(TEST_IP)  # Add test IP
    return ips

def get_random_ip(ip_list):
    """Get random IP from list for fair distribution"""
    return random.choice(ip_list)

def generate_random_port(exclude_common=False):
    """Generate random port between 1024-65535, optionally excluding common ports"""
    port = random.randint(1024, 65535)
    if exclude_common and port in COMMON_PORTS:
        return generate_random_port(exclude_common=True)
    return port


def send_flag_packet(ip, port):
    """Send flag packet to random port (UDP only for visibility)"""
    try:
        proc = subprocess.run(['echo', REAL_FLAG],
                            stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                              input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        print(f"*** SENT REAL FLAG TO {ip}:{port} via UDP ***")
    except subprocess.TimeoutExpired:
        print(f"Flag send to {ip}:{port} timed out")
    except Exception as e:
        print(f"Error sending flag to {ip}:{port}: {e}")

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
        print(f"Error checking admin login: {e}")
        return False

def send_fake_flag_packet(ip):
    """Send fake flag packet for confusion (only ICMP and UDP)"""
    try:
        fake_flag = random.choice(FAKE_FLAGS)
        packet_type = random.choice(['icmp', 'udp'])  # Only ICMP and UDP for flags

        if packet_type == 'icmp':
            # Send ICMP ping with flag as data (using hping3 if available, fallback to echo)
            try:
                proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
                result = subprocess.run(['nc', '-u', '-w', '1', ip, str(generate_random_port())],
                                      input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
            except:
                # Fallback: just send UDP
                proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
                result = subprocess.run(['nc', '-u', '-w', '1', ip, str(generate_random_port())],
                                      input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        else:  # UDP
            proc = subprocess.run(['echo', fake_flag], stdout=subprocess.PIPE)
            result = subprocess.run(['nc', '-u', '-w', '1', ip, str(generate_random_port())],
                                  input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        print(f"Sent fake flag '{fake_flag}' to {ip} via {packet_type.upper()}")
    except subprocess.TimeoutExpired:
        print(f"Fake flag send to {ip} timed out")
    except Exception as e:
        print(f"Error sending fake flag to {ip}: {e}")

def main():
    print("Starting Packet Sender for CTF Lab...")
    print("Flag will only be sent when admin users are logged in")
    print("Sending flags only (ICMP/UDP) - no noise from this script")
    print("Press Ctrl+C to stop")

    # Generate list of all IPs in subnet
    all_ips = generate_all_ips(SUBNET)
    print(f"Targeting {len(all_ips)} IPs in {SUBNET}.0/24 subnet")

    # Select random port for flag (fixed for this session)
    flag_port = generate_random_port(exclude_common=True)
    print(f"Flag will be sent to random port: {flag_port}")

    last_flag_time = 0
    admin_was_logged_in = False  # Track admin login state

    try:
        while True:
            current_time = time.time()
            admin_logged_in = is_admin_logged_in()

            # Randomly select IP for this cycle
            target_ip = get_random_ip(all_ips)

            if admin_logged_in:
                if not admin_was_logged_in:
                    # Admin just logged in - send ALL fake flags to ALL IPs once
                    print("Admin logged in - sending ALL fake flags to ALL IPs for complete coverage")
                    for ip in all_ips:  # Send to every IP in the subnet
                        for _ in range(6):  # Send 6 fake flags per IP (one for each original context)
                            send_fake_flag_packet(ip)
                    admin_was_logged_in = True

                # Send flag every 5 seconds to random IP when admin is online
                if current_time - last_flag_time >= FLAG_INTERVAL:
                    send_flag_packet(target_ip, flag_port)
                    last_flag_time = current_time
            else:
                if admin_was_logged_in:
                    print("Admin logged out - resetting flag state")
                    admin_was_logged_in = False
                # Reset flag timer when admin logs out
                last_flag_time = 0

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping packet sender...")
        sys.exit(0)

if __name__ == "__main__":
    main()