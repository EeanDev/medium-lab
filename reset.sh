#!/bin/bash
# CTF Lab Reset/Cleanup Script
# Completely removes all CTF lab components
# Run with sudo privileges

set -e

echo "=== CTF Lab Reset/Cleanup ==="
echo "This will remove all CTF lab components but preserve the uvmu admin account"
echo "Press Ctrl+C to cancel or Enter to continue..."
read

# Stop and remove cron jobs
echo "Removing cron jobs..."
rm -f /etc/cron.d/ctf-real-flag
rm -f /etc/cron.d/ctf-noise-generator

# Stop and remove systemd services (if they exist)
echo "Removing systemd services..."
systemctl stop ctf-fake-flags 2>/dev/null || true
systemctl stop ctf-noise-generator 2>/dev/null || true
systemctl disable ctf-fake-flags 2>/dev/null || true
systemctl disable ctf-noise-generator 2>/dev/null || true
rm -f /etc/systemd/system/ctf-fake-flags.service
rm -f /etc/systemd/system/ctf-noise-generator.service
systemctl daemon-reload 2>/dev/null || true

# Remove CTF directory and files
echo "Removing CTF files and directories..."
rm -rf /opt/ctf-lab

# Remove log files
echo "Removing log files..."
rm -f /var/log/ctf-fake-flags.log
rm -f /var/log/ctf-real-flag.log
rm -f /var/log/ctf-noise-generator.log

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
echo "=== Cleanup Complete ==="
echo "All CTF lab components have been removed:"
echo "  ✓ Cron jobs removed (ctf-real-flag, ctf-noise-generator)"
echo "  ✓ Systemd services removed (ctf-fake-flags, ctf-noise-generator)"
echo "  ✓ CTF files and directories removed (/opt/ctf-lab/)"
echo "  ✓ Log files removed (/var/log/ctf-*.log)"
echo "  ✓ uvmu user preserved (admin account)"
echo "  ✓ Firewall reset"
echo ""
echo "You can now run setup.sh for a fresh installation"