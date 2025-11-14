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

# Setup cron job for conditional flag sending
echo "Setting up cron job for conditional packet sending..."
cat > /etc/cron.d/ctf-packet-sender << EOF
# CTF Packet Sender - runs every 2 minutes, sends flag only when admin logged in
*/2 * * * * root /usr/bin/python3 /opt/ctf-lab/packet_sender.py >> /var/log/ctf-packet-sender.log 2>&1
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

# Enable cron and create log files
echo "Enabling cron and setting up logging..."
systemctl enable cron
systemctl start cron
touch /var/log/ctf-packet-sender.log /var/log/ctf-noise-generator.log

echo "=== Setup Complete ==="
echo "Cron jobs are now active:"
echo "  - Packet sender runs every 2 minutes (flag only when admin logged in)"
echo "  - Noise generator runs every minute (optional)"
echo ""
echo "To check logs:"
echo "  tail -f /var/log/ctf-packet-sender.log"
echo "  tail -f /var/log/ctf-noise-generator.log"
echo ""
echo "To modify admin users, edit the admin_users list in packet_sender.py"
echo "Scripts run as root via cron jobs."