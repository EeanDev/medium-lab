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
FLAG_INTERVAL = 300  # seconds between real flags (5 minutes)
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
    admin_was_logged_in = False
    fake_flag_index = 0  # Track which fake flag to send next
    last_fake_flag_time = 0

    try:
        while True:
            current_time = time.time()
            admin_logged_in = is_admin_logged_in()
            print(f"[{time.strftime('%H:%M:%S')}] Admin logged in: {admin_logged_in}, Cycle: {fake_flag_index}")

            # Randomly select IP for real flag
            target_ip = get_random_ip(all_ips)

            if admin_logged_in:
                if not admin_was_logged_in:
                    print("Admin logged in - starting sequential flag sending")
                    fake_flag_index = 0
                    last_fake_flag_time = current_time
                    admin_was_logged_in = True

                # Send fake flags sequentially every 25 seconds
                if current_time - last_fake_flag_time >= 25 and fake_flag_index < len(FAKE_FLAGS):
                    fake_flag = FAKE_FLAGS[fake_flag_index]
                    print(f"Sending fake flag {fake_flag_index + 1}/12: {fake_flag}")

                    # Send this fake flag to ALL IPs
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
                            print(f"Sent '{fake_flag}' to {ip}")
                        except Exception as e:
                            print(f"Error sending to {ip}: {e}")

                    fake_flag_index += 1
                    last_fake_flag_time = current_time

                # Send real flag after all fake flags (approximately every 5 minutes)
                elif fake_flag_index >= len(FAKE_FLAGS):
                    if current_time - last_flag_time >= FLAG_INTERVAL:
                        send_flag_packet(target_ip, flag_port)
                        last_flag_time = current_time
                        # Reset cycle after sending real flag
                        fake_flag_index = 0
                        last_fake_flag_time = current_time

            else:
                if admin_was_logged_in:
                    print("Admin logged out - resetting flag sequence")
                    admin_was_logged_in = False
                    fake_flag_index = 0
                else:
                    print("No admin logged in - waiting...")
                last_flag_time = 0

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping packet sender...")
        sys.exit(0)

if __name__ == "__main__":
    main()