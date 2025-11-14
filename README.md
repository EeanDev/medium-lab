# CTF Lab Packet Sender

A Python-based packet sender for Capture The Flag (CTF) labs that hides the real flag among noise traffic and fake flags.

## Overview

This project creates a realistic CTF challenge where participants must analyze network traffic to find a hidden flag. The system sends packets randomly to IPs in the subnet:
- **Real flag**: `$flag{nahanapmo}` sent via UDP every 5 seconds (only when admin logged in)
- **Fake flags**: 12 confusing FLAG messages sent via ICMP/UDP to create confusion
- **Noise traffic**: TCP/UDP/ping packets sent by separate noise generator
- **Special IP**: 172.16.130.33 receives unusual traffic volume

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

## CTF Challenge Questions

### Medium Level Network Forensics Challenge

**Network:** 172.16.200.0/24 + 172.16.120.11

1. **Which particular IP address has an unusual number of traffic being sent to your network 172.16.200.0/24?**
   `172.16.130.33`

2. **Find your flag present hidden within the messages.**
   `FLAG{nahanapmo}`

3. **What is the exact time interval between the appearance of the flag present? (Number only)**
   `5`

4. **How many unique FLAG messages do you see in the traffic? (Sum only)**
   `13`

5. **What are the protocols used to send the messages? Use comma(,) to separate.**
   `UDP,ICMP`

6. **What do you call the opposite of the source port pattern being used to send the messages?**
   `Well-known ports/Common Ports`

## Wireshark Analysis Guide

### Finding the Real Flag

1. **Filter for FLAG strings**:
```
udp contains "flag" or icmp contains "flag"
```

2. **Look for patterns**:
   - Real flag: `$flag{nahanapmo}` appears every 5 seconds
   - Fake flags: Various `FLAG{...}` strings appear randomly
   - Special IP: `172.16.130.33` gets unusual traffic
   - Protocols: Only UDP and ICMP contain FLAG messages

3. **Identify the flag**:
   - Look for the unique `$flag{...}` format (not `FLAG{...}`)
   - Check timing: exactly 5-second intervals
   - Verify protocols: UDP and ICMP only

### Traffic Patterns

- **FLAG Messages**: Only in UDP and ICMP packets (13 unique messages)
- **Noise Traffic**: TCP, UDP, ping from noise generator
- **Special IP**: 172.16.130.33 receives 3x more traffic
- **Timing**: Flags every 5 seconds, noise every 2 seconds

### Message Examples
- Real: `$flag{nahanapmo}`
- Fake: `FLAG{ThisIsNotMe}`, `FLAG{SORRY}`, `FLAG{FLAGGOT}`, etc.

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