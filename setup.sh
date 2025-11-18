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

# Create CTF directory
echo "Creating CTF directory..."
mkdir -p /opt/ctf-lab

# Copy scripts
echo "Copying scripts to /opt/ctf-lab/..."
cp packet_sender.py /opt/ctf-lab/
cp noise_generator.py /opt/ctf-lab/
chmod +x /opt/ctf-lab/*.py

# Setup systemd service for continuous flag sending
echo "Setting up systemd service for continuous flag sending..."
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

# Setup noise generator cron job (optional)
cat > /etc/cron.d/ctf-noise-generator << EOF
# CTF Noise Generator - runs every minute for distraction
* * * * * root /usr/bin/python3 /opt/ctf-lab/noise_generator.py >> /var/log/ctf-noise-generator.log 2>&1
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

# Enable services and create log files
echo "Enabling services and setting up logging..."
systemctl daemon-reload
systemctl enable ctf-packet-sender
# systemctl enable ctf-noise-generator  # Uncomment if you want noise on this server too

systemctl enable cron
systemctl start cron

touch /var/log/ctf-packet-sender.log /var/log/ctf-noise-generator.log
chown ctf:ctf /var/log/ctf-packet-sender.log /var/log/ctf-noise-generator.log

echo "=== Setup Complete ==="
echo "Services are now active:"
echo "  - Packet sender runs continuously (flag every 5 minutes when admin logged in)"
echo "  - Noise generator runs every minute (optional)"
echo ""
echo "To start the packet sender:"
echo "  sudo systemctl start ctf-packet-sender"
echo ""
echo "To check status:"
echo "  sudo systemctl status ctf-packet-sender"
echo ""
echo "To check logs:"
echo "  tail -f /var/log/ctf-packet-sender.log"
echo "  tail -f /var/log/ctf-noise-generator.log"
echo ""
echo "To modify admin users, edit the admin_users list in packet_sender.py"
echo "Packet sender runs as ctf user via systemd service."