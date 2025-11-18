#!/bin/bash
# CTF Lab Reset/Cleanup Script
# Completely removes all CTF lab components
# Run with sudo privileges

set -e

echo "=== CTF Lab Reset/Cleanup ==="
echo "This will remove all CTF lab components but preserve the uvmu admin account"
echo "Press Ctrl+C to cancel or Enter to continue..."
read

# Nuclear cleanup - kill ALL python processes and CTF-related processes
echo "Nuclear cleanup - killing ALL python and CTF processes..."
pkill -9 -f python 2>/dev/null || echo "No python processes found"
pkill -9 -f ctf 2>/dev/null || echo "No CTF processes found"
pkill -9 -f packet 2>/dev/null || echo "No packet processes found"
pkill -9 -f flag 2>/dev/null || echo "No flag processes found"

# Wait a moment for processes to die
sleep 2

# Double-check and kill any remaining
ps aux | grep -E "(python|ctf|packet|flag)" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || echo "No remaining processes found"

# Stop and remove cron jobs
echo "Removing cron jobs..."
rm -f /etc/cron.d/ctf-real-flag
rm -f /etc/cron.d/ctf-noise-generator
rm -f /etc/cron.d/ctf-packet-sender  # Remove any old packet_sender cron jobs

# Stop and remove systemd services (if they exist)
echo "Removing systemd services..."
systemctl stop ctf-fake-flags 2>/dev/null || true
systemctl stop ctf-noise-generator 2>/dev/null || true
systemctl stop ctf-packet-sender 2>/dev/null || true  # Stop any old packet_sender service
systemctl disable ctf-fake-flags 2>/dev/null || true
systemctl disable ctf-noise-generator 2>/dev/null || true
systemctl disable ctf-packet-sender 2>/dev/null || true  # Disable any old packet_sender service
rm -f /etc/systemd/system/ctf-fake-flags.service
rm -f /etc/systemd/system/ctf-noise-generator.service
rm -f /etc/systemd/system/ctf-packet-sender.service  # Remove any old packet_sender service file
systemctl daemon-reload 2>/dev/null || true

# Remove CTF directory and files
echo "Removing CTF files and directories..."
rm -rf /opt/ctf-lab

# Remove log files
echo "Removing log files..."
rm -f /var/log/ctf-fake-flags.log
rm -f /var/log/ctf-real-flag.log
rm -f /var/log/ctf-noise-generator.log
rm -f /var/log/ctf-packet-sender.log  # Remove any old packet_sender logs

# Kill any processes running as old ctf user
echo "Killing any processes running as ctf user..."
pkill -u ctf 2>/dev/null || echo "No ctf user processes found"

# Remove old ctf user if it exists
echo "Removing old ctf user..."
userdel -r ctf 2>/dev/null || echo "ctf user not found or already removed"

# Note: uvmu user is preserved (admin account)
echo "Preserving uvmu user (admin account)..."

# Reset firewall to defaults
echo "Resetting firewall to defaults..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
echo "y" | ufw --force enable

# Optional: Remove installed packages
echo "Remove CTF-related packages? (netcat, ufw, etc.) [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Removing packages..."
    apt remove -y netcat-openbsd ufw fail2ban 2>/dev/null || true
    apt autoremove -y
fi

# Reload cron
echo "Reloading cron..."
systemctl restart cron 2>/dev/null || true

echo ""
echo "=== Nuclear Cleanup Complete ==="
echo "All CTF lab components have been NUKED:"
echo "  ✓ ALL python processes killed"
echo "  ✓ ALL CTF processes killed"
echo "  ✓ Cron jobs removed (ctf-real-flag, ctf-noise-generator, ctf-packet-sender)"
echo "  ✓ Systemd services removed (ctf-fake-flags, ctf-noise-generator, ctf-packet-sender)"
echo "  ✓ CTF files and directories removed (/opt/ctf-lab/)"
echo "  ✓ Log files removed (/var/log/ctf-*.log)"
echo "  ✓ Old ctf user processes killed and user removed"
echo "  ✓ uvmu user preserved (admin account)"
echo "  ✓ Firewall reset"
echo ""
echo "System reboot recommended for complete cleanup!"
echo ""
echo "Reboot now? (y/N)"
read -r reboot_choice
if [[ "$reboot_choice" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Rebooting system in 5 seconds..."
    sleep 5
    reboot
else
    echo "You can now run setup.sh for a fresh installation"
    echo "Or manually reboot with: sudo reboot"
fi