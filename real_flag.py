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
REAL_FLAG = "$FLAG{nahanapmo}"

def generate_all_ips(subnet):
    """Generate list of all valid IPs in the subnet (exclude .0, .254, .255)"""
    ips = [f"{subnet}.{i}" for i in range(1, 254)]  # 1-253 inclusive
    ips.append("172.16.120.11")  # Add test IP
    return ips

def generate_random_port(exclude_common=False):
    """Generate random port between 1024-65535, excluding common ports"""
    port = random.randint(1024, 65535)
    if exclude_common and port in [53, 80, 23]:
        return generate_random_port(exclude_common=True)
    return port

def send_real_flag():
    """Send the real flag to ALL IPs in subnet"""
    try:
        all_ips = generate_all_ips(SUBNET)

        for ip in all_ips:
            flag_port = generate_random_port(exclude_common=True)

            print(f"[{time.strftime('%H:%M:%S')}] Sending real flag to {ip}:{flag_port}")

            # Send the real flag
            try:
                proc = subprocess.run(['echo', REAL_FLAG], stdout=subprocess.PIPE)
                result = subprocess.run(['nc', '-u', '-w', '1', ip, str(flag_port)],
                                      input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=3)
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error sending real flag to {ip}:{flag_port}: {e}")

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