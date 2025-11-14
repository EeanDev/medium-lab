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

# Fake FLAG messages for confusion + real flag
CONTEXT_FLAGS = {
    "dns": ["FLAG{ThisIsNotMe}", "FLAG{TryAgain}"],
    "http": ["FLAG{SORRY}", "FLAG{NotTheFlag}"],
    "telnet": ["FLAG{FLAGGOT}", "FLAG{NiceTry}"],
    "tcp": ["FLAG{WrongOne}", "FLAG{KeepLooking}"],
    "udp": ["FLAG{CloseButNo}", "FLAG{GettingWarmer}"],
    "ping": ["FLAG{NoFlagHere}", "FLAG{NOPENOPE}"],
    "real": "$flag{nahanapmo}"
}

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
                              input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
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
                              input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
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
                              input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
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
    """Send flag packet to random port (UDP only for visibility)"""
    try:
        flag = CONTEXT_FLAGS["real"]
        proc = subprocess.run(['echo', flag],
                            stdout=subprocess.PIPE)
        result = subprocess.run(['nc', '-u', '-w', '1', ip, str(port)],
                              input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
        print(f"*** SENT REAL FLAG TO {ip}:{port} via UDP ***")
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
                              input=proc.stdout.decode('utf-8'), capture_output=True, text=True, timeout=2)
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

def send_fake_flag_packet(ip, context):
    """Send fake flag packet for confusion (only ICMP and UDP)"""
    try:
        fake_flag = random.choice(CONTEXT_FLAGS[context])
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
    print("Special IP 172.16.130.33 gets unusual traffic")
    print("Press Ctrl+C to stop")

    # Generate list of all IPs in subnet
    all_ips = generate_all_ips(SUBNET)
    print(f"Targeting {len(all_ips)} IPs in {SUBNET}.0/24 subnet")

    # Select random port for flag (fixed for this session)
    flag_port = generate_random_port(exclude_common=True)
    print(f"Flag will be sent to random port: {flag_port}")

    # Special IP that gets unusual traffic
    SPECIAL_IP = "172.16.130.33"
    last_flag_time = 0

    try:
        while True:
            current_time = time.time()
            admin_logged_in = is_admin_logged_in()

            # Randomly select IP for this cycle
            target_ip = get_random_ip(all_ips)

            # Special IP gets 3x more chance of being selected
            if random.random() < 0.3:  # 30% chance to override with special IP
                target_ip = SPECIAL_IP

            if admin_logged_in:
                print(f"Admin logged in - sending flags to IP {target_ip}")
                # Send flag every 5 seconds to random IP when admin is online
                if current_time - last_flag_time >= FLAG_INTERVAL:
                    send_flag_packet(target_ip, flag_port)
                    last_flag_time = current_time

                # Send fake flags to create confusion (only ICMP/UDP)
                contexts = ['dns', 'http', 'telnet', 'tcp', 'udp', 'ping']
                for context in random.sample(contexts, random.randint(1, 3)):  # 1-3 fake flags per cycle
                    send_fake_flag_packet(target_ip, context)
            else:
                print(f"No admin logged in - no flag traffic")
                # Reset flag timer when admin logs out
                last_flag_time = 0

            time.sleep(NOISE_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping packet sender...")
        sys.exit(0)

if __name__ == "__main__":
    main()