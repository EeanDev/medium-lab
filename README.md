# CTF Lab Packet Sender

A Python-based packet sender for Capture The Flag (CTF) labs that hides the real flag among noise traffic and fake flags.

## Overview

This project creates a realistic CTF challenge where participants must analyze network traffic to find a hidden flag. The system sends:
- **Real flag**: `FLAG{YouFoundMe-2025}` to a random UDP port every 5 seconds
- **Fake flags**: Context-aware fake flags (like `FLAG{HTTP-Requests}`, `FLAG{LetMeIN}`, etc.) to create confusion
- **Noise traffic**: Various protocol packets (DNS, HTTP, Telnet, TCP, UDP, ICMP) at higher frequency

## Files

- `packet_sender.py` - Main script that sends the real flag + noise
- `noise_generator.py` - Noise-only script for distraction servers
- `setup.sh` - Ubuntu server setup and hardening script
- `README.md` - This documentation

## Setup Instructions

### 1. Server Preparation
Run the setup script on Ubuntu 24.04:
```bash
sudo ./setup.sh
```

This will:
- Install required packages (netcat, python3, ufw, etc.)
- Create a limited `ctf` user
- Configure firewall and SSH hardening
- Set up systemd services
- Enable automatic updates

### 2. Manual Setup (Alternative)
```bash
# Install dependencies
sudo apt update
sudo apt install netcat-openbsd python3 ufw fail2ban

# Create directories and copy files
sudo mkdir -p /opt/ctf-lab
sudo cp *.py /opt/ctf-lab/
sudo chown -R ctf:ctf /opt/ctf-lab/
```

### 3. SSH Key Setup
Add your SSH public key to the ctf user:
```bash
sudo -u ctf mkdir -p /home/ctf/.ssh
sudo -u ctf chmod 700 /home/ctf/.ssh
echo "your_public_key_here" | sudo -u ctf tee /home/ctf/.ssh/authorized_keys
sudo -u ctf chmod 600 /home/ctf/.ssh/authorized_keys
```

## Usage

### Start the Main Packet Sender
```bash
sudo systemctl start ctf-packet-sender
```

### Start Noise Generator (on distraction servers)
```bash
sudo systemctl start ctf-noise-generator
```

### Manual Testing
```bash
# Test packet sender
sudo -u ctf python3 /opt/ctf-lab/packet_sender.py

# Test noise generator
sudo -u ctf python3 /opt/ctf-lab/noise_generator.py
```

## Wireshark Analysis Guide

### Finding the Real Flag

1. **Filter for FLAG strings**:
   ```
   udp contains "FLAG"
   ```

2. **Look for patterns**:
   - Real flag: `FLAG{YouFoundMe-2025}` appears every 5 seconds
   - Fake flags: Various `FLAG{...}` strings appear randomly
   - Real flag goes to a **random high port** (1024-65535)
   - Fake flags go to common ports or random ports

3. **Identify the flag port**:
   - Find UDP packets containing `FLAG{YouFoundMe-2025}`
   - Note the destination port - this is the flag port
   - Filter by this port: `udp.port == [flag_port]`

4. **Timing analysis**:
   - Real flag: Exactly every 5 seconds
   - Fake flags: Random timing

### Noise Traffic Patterns

- **ICMP/Ping**: Echo requests to random IPs
- **DNS**: Queries for various domains to random IPs on port 53
- **HTTP**: GET/POST requests to random IPs on port 80
- **Telnet**: Connection attempts to random IPs on port 23
- **TCP**: SYN packets with "noise" payload to random ports
- **UDP**: Datagrams with "noise" payload to random ports

### Fake Flag Examples
- `FLAG{HTTP-Requests}` - Sent with HTTP traffic
- `FLAG{LetMeIN}` - Sent with Telnet traffic
- `FLAG{AlahuAkbar}` - Random fake flag
- `FLAG{DNSServer}` - Sent with DNS queries
- `FLAG{PortScan}` - Sent with TCP scans
- `FLAG{ICMPFlood}` - Sent with ping floods

## Configuration

Edit the scripts to customize:

### Flag Settings
```python
CONTEXT_FLAGS = {
    "real": "FLAG{YouFoundMe-2025}",  # Change this
    "dns": ["FLAG{DNSServer}", "FLAG{DomainLookup}"],  # Add more fakes
    # ...
}
```

### Timing
```python
FLAG_INTERVAL = 5    # Real flag frequency
NOISE_INTERVAL = 1   # Noise frequency
```

### Network Range
```python
SUBNET = "172.16.130"  # Target subnet
```

## Security Notes

- Scripts run as limited `ctf` user
- Firewall blocks all incoming traffic except SSH
- SSH hardened (no root login, no password auth)
- Automatic security updates enabled
- Services restart automatically on failure

## Troubleshooting

### Service won't start
```bash
sudo systemctl status ctf-packet-sender
sudo journalctl -u ctf-packet-sender -f
```

### Permission issues
```bash
sudo chown -R ctf:ctf /opt/ctf-lab/
sudo chmod +x /opt/ctf-lab/*.py
```

### Network issues
- Ensure the target subnet `172.16.130.0/24` is reachable
- Check firewall rules: `sudo ufw status`
- Test connectivity: `ping 172.16.130.1`

## Deployment Architecture

```
CTF Network (172.16.130.0/24)
├── Flag Server (runs packet_sender.py)
│   ├── Sends real flag every 5s to random port
│   ├── Sends noise traffic + fake flags
│   └── Hardened Ubuntu 24.04
├── Noise Server 1 (runs noise_generator.py)
│   └── Generates fake flags + noise only
├── Noise Server 2 (runs noise_generator.py)
│   └── Generates fake flags + noise only
└── Participant captures traffic with Wireshark
```

This setup creates a challenging CTF where participants must distinguish the real flag from numerous fake ones while analyzing live network traffic.