# CTF Lab Packet Sender

A Python-based packet sender for Capture The Flag (CTF) labs that hides the real flag among noise traffic and fake flags.

## Overview

This project creates a realistic CTF challenge where participants must analyze network traffic to find a hidden flag. The system sends packets randomly to IPs in the subnet for fair distribution:
- **Real flag**: `$flag{nahanapmo}` to a random UDP port, sent to random IPs every 5 seconds (only when admin logged in)
- **Fake flags**: Confusing fake flags (like `FLAG{ThisIsNotMe}`, `FLAG{TryAgain}`, `FLAG{SORRY}`, etc.) to create confusion
- **Noise traffic**: Simple packets (TCP, UDP, ping) sent to random IPs every 2 seconds

## Files

- `packet_sender.py` - Main script that sends the real flag + noise
- `noise_generator.py` - Noise-only script for distraction servers
- `setup.sh` - Ubuntu server setup and hardening script
- `reset.sh` - Complete cleanup script to remove all CTF components
- `README.md` - This documentation

## Setup Instructions

### 1. Download from GitHub
```bash
# Clone the repository
git clone https://github.com/EeanDev/medium-lab.git
cd medium-lab
```

### 2. Server Preparation
Run the setup script on Ubuntu 24.04:
```bash
sudo ./setup.sh
```

This will:
- Install required packages (netcat, python3, ufw, etc.)
- Create a limited `ctf` user
- Configure firewall and SSH hardening
- Set up cron jobs for automatic execution
- Enable automatic updates

### 3. Configure Admin Users
Edit the admin users list in `packet_sender.py`:
```python
admin_users = ['root', 'your_username']  # Add your admin usernames
```

### 4. SSH Key Setup
Add your SSH public key to the ctf user:
```bash
sudo -u ctf mkdir -p /home/ctf/.ssh
sudo -u ctf chmod 700 /home/ctf/.ssh
echo "your_public_key_here" | sudo -u ctf tee /home/ctf/.ssh/authorized_keys
sudo -u ctf chmod 600 /home/ctf/.ssh/authorized_keys
```

### 5. Verify Setup
```bash
# Check cron jobs
sudo crontab -l

# Check logs
tail -f /var/log/ctf-packet-sender.log
```

## Reset/Cleanup

To completely remove all CTF lab components and start fresh:

```bash
sudo ./reset.sh
```

This will:
- Remove all cron jobs
- Stop and remove systemd services
- Delete CTF files and directories
- Remove log files
- Delete the CTF user (if exists)
- Reset firewall to defaults
- Optionally remove installed packages

After running reset.sh, you can run setup.sh for a fresh installation.

## Usage

### Automatic Operation (Cron Jobs)
The scripts run automatically via cron jobs:
- **Packet sender**: Every 2 minutes (flag only when admin logged in)
- **Noise generator**: Every minute (optional distraction)

### Manual Testing
```bash
# Test packet sender
sudo -u ctf python3 /opt/ctf-lab/packet_sender.py

# Test noise generator
sudo -u ctf python3 /opt/ctf-lab/noise_generator.py
```

### Check Logs
```bash
tail -f /var/log/ctf-packet-sender.log
tail -f /var/log/ctf-noise-generator.log
```

## Wireshark Analysis Guide

### Finding the Real Flag

1. **Filter for FLAG strings**:
   ```
   udp contains "FLAG"
   ```

2. **Look for patterns**:
   - Real flag: `FLAG{nahanapmo}` appears every 5 seconds
   - Fake flags: Various confusing `FLAG{...}` strings appear randomly
   - Real flag goes to a **random high port** (1024-65535)
   - Fake flags go to common ports or random ports

3. **Identify the flag port**:
   - Find UDP packets containing `FLAG{nahanapmo}`
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
- `FLAG{ThisIsNotMe}` - DNS-related fake
- `FLAG{SORRY}` - HTTP-related fake
- `FLAG{FLAGGOT}` - Telnet-related fake
- `FLAG{WrongOne}` - TCP-related fake
- `FLAG{CloseButNo}` - UDP-related fake
- `FLAG{NoFlagHere}` - Ping-related fake

## Configuration

Edit the scripts to customize:

### Flag Settings
```python
CONTEXT_FLAGS = {
    "real": "FLAG{nahanapmo}",  # Change this
    "dns": ["FLAG{ThisIsNotMe}", "FLAG{TryAgain}"],  # Add more fakes
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
SUBNET = "172.16.200"  # Target subnet (sequential IP sending)
TEST_IP = "172.16.120.11"  # Additional test IP
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
- Ensure the target subnet `172.16.200.0/24` is reachable
- Check firewall rules: `sudo ufw status`
- Test connectivity: `ping 172.16.200.1`

## Deployment Architecture

```
CTF Network (172.16.200.0/24)
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