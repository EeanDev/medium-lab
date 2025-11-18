#!/usr/bin/env python3
"""
Real Flag Sender Script for CTF Lab
Sends the real flag once, run by cron every 5 minutes
Runs on Ubuntu 24.04 LTS using netcat.
"""

import subprocess
import random
import time

# Configuration
SUBNET = "172.16.200"

# Real flag
REAL_FLAG = "$flag{nahanapmo}"

def generate_all_ips(subnet):
    """Generate list of all IPs in the subnet"""
    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    ips.append("172.16.120.11")  # Add test IP
    return ips

def get_random_ip(ip_list):
    """Get random IP from list"""
    return random.choice(ip_list)

def generate_random_port(exclude_common=False):
    """Generate random port between 1024-65535, excluding common ports"""
    port = random.randint(1024, 65535)
    if exclude_common and port in [53, 80, 23]:
        return generate_random_port(exclude_common=True)
    return port

def send_real_flag():
    """Send the real flag to a random IP"""
    try:
        # Generate random IP and port
        all_ips = generate_all_ips(SUBNET)
        target_ip = get_random_ip(all_ips)
        flag_port = generate_random_port(exclude_common=True)

        # Send the real flag
        proc = subprocess.run(['echo', REAL_FLAG], stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-u', '-w', '1', target_ip, str(flag_port)],
                              input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)

        print(f"[{time.strftime('%H:%M:%S')}] *** SENT REAL FLAG TO {target_ip}:{flag_port} ***")

    except subprocess.TimeoutExpired:
        print(f"[{time.strftime('%H:%M:%S')}] Real flag send timed out")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error sending real flag: {e}")

def main():
    print(f"[{time.strftime('%H:%M:%S')}] Real Flag Sender starting...")
    send_real_flag()
    print(f"[{time.strftime('%H:%M:%S')}] Real Flag Sender completed")

if __name__ == "__main__":
    main()