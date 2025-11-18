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
cp fake_flags.py /opt/ctf-lab/
cp real_flag.py /opt/ctf-lab/
cp noise_generator.py /opt/ctf-lab/
chmod +x /opt/ctf-lab/*.py

# Create uvmu user if it doesn't exist
echo "Creating uvmu user..."
useradd -m -s /bin/bash uvmu 2>/dev/null || echo "User uvmu already exists"

# Setup systemd service for continuous fake flags
echo "Setting up systemd service for continuous fake flags..."
cat > /etc/systemd/system/ctf-fake-flags.service << EOF
[Unit]
Description=CTF Fake Flags Service
After=network.target

[Service]
Type=simple
User=uvmu
ExecStart=/usr/bin/python3 /opt/ctf-lab/fake_flags.py >> /var/log/ctf-fake-flags.log 2>&1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Setup cron job for real flag (runs every 5 minutes)
echo "Setting up cron job for real flag..."
cat > /etc/cron.d/ctf-real-flag << EOF
# CTF Real Flag - runs every 5 minutes
*/5 * * * * uvmu /usr/bin/python3 /opt/ctf-lab/real_flag.py >> /var/log/ctf-real-flag.log 2>&1
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
systemctl enable ctf-fake-flags
# systemctl enable ctf-noise-generator  # Uncomment if you want noise on this server too

systemctl enable cron
systemctl start cron

touch /var/log/ctf-fake-flags.log /var/log/ctf-real-flag.log /var/log/ctf-noise-generator.log
chown uvmu:uvmu /var/log/ctf-fake-flags.log /var/log/ctf-real-flag.log /var/log/ctf-noise-generator.log

echo "=== Setup Complete ==="
echo "Services are now active:"
echo "  - Fake flags run continuously (constant confusion)"
echo "  - Real flag runs every 5 minutes (only when admin logged in)"
echo "  - Noise generator runs every minute (optional)"
echo ""
echo "To start fake flags service:"
echo "  sudo systemctl start ctf-fake-flags"
echo ""
echo "To check cron jobs:"
echo "  sudo crontab -l -u uvmu"
echo ""
echo "To check logs:"
echo "  tail -f /var/log/ctf-fake-flags.log"
echo "  tail -f /var/log/ctf-real-flag.log"
echo "  tail -f /var/log/ctf-noise-generator.log"
echo ""
echo "To modify admin users, edit the admin_users list in fake_flags.py"
echo "Participants monitor network traffic with Wireshark - no login required."
echo "Fake flags run as uvmu user via systemd service."
echo "Real flag runs as uvmu user via cron job."