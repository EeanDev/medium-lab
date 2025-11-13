#!/bin/bash
# Ubuntu 24.04 CTF Lab Server Setup Script
# Run with sudo privileges

set -e

echo "=== CTF Lab Server Setup ==="

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "Installing required packages..."
apt install -y netcat-openbsd python3 python3-pip ufw fail2ban unattended-upgrades curl wget

# Create CTF user
echo "Creating ctf user..."
useradd -m -s /bin/bash ctf || echo "User ctf already exists"
mkdir -p /opt/ctf-lab
chown ctf:ctf /opt/ctf-lab

# Copy scripts
echo "Copying scripts to /opt/ctf-lab/..."
cp packet_sender.py /opt/ctf-lab/
cp noise_generator.py /opt/ctf-lab/
chown -R ctf:ctf /opt/ctf-lab/
chmod +x /opt/ctf-lab/*.py

# Setup systemd service
echo "Setting up systemd service..."
cat > /etc/systemd/system/ctf-packet-sender.service << EOF
[Unit]
Description=CTF Packet Sender Service
After=network.target

[Service]
Type=simple
User=ctf
ExecStart=/usr/bin/python3 /opt/ctf-lab/packet_sender.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Setup noise generator service (optional)
cat > /etc/systemd/system/ctf-noise-generator.service << EOF
[Unit]
Description=CTF Noise Generator Service
After=network.target

[Service]
Type=simple
User=ctf
ExecStart=/usr/bin/python3 /opt/ctf-lab/noise_generator.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Firewall configuration
echo "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw --force enable

# SSH hardening
echo "Hardening SSH..."
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh

# Enable automatic updates
echo "Enabling automatic updates..."
dpkg-reconfigure --frontend=noninteractive unattended-upgrades

# Enable services
echo "Enabling services..."
systemctl daemon-reload
systemctl enable ctf-packet-sender
# systemctl enable ctf-noise-generator  # Uncomment if you want noise on this server too

echo "=== Setup Complete ==="
echo "To start the packet sender: sudo systemctl start ctf-packet-sender"
echo "To start noise generator: sudo systemctl start ctf-noise-generator"
echo "To check status: sudo systemctl status ctf-packet-sender"
echo ""
echo "Make sure to add your SSH public key to /home/ctf/.ssh/authorized_keys"
echo "for passwordless login as the ctf user."