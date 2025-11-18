#!/bin/bash
# CTF Lab Troubleshooting Script
# Diagnose systemd service and logging issues

echo "=== CTF Lab Troubleshooting ==="
echo ""

# Check if services exist
echo "1. Checking systemd services..."
if systemctl list-units --type=service | grep -q ctf-fake-flags; then
    echo "✓ ctf-fake-flags service exists"
else
    echo "✗ ctf-fake-flags service NOT found"
fi

if systemctl list-units --type=service | grep -q ctf-noise-generator; then
    echo "✓ ctf-noise-generator service exists"
else
    echo "✗ ctf-noise-generator service NOT found"
fi

# Check service status
echo ""
echo "2. Checking service status..."
echo "ctf-fake-flags status:"
sudo systemctl status ctf-fake-flags --no-pager -l | head -10

# Check cron jobs
echo ""
echo "3. Checking cron jobs..."
if sudo crontab -l -u uvmu 2>/dev/null | grep -q ctf; then
    echo "✓ Cron jobs found for uvmu user"
    sudo crontab -l -u uvmu
else
    echo "✗ No cron jobs found for uvmu user"
fi

# Check log files
echo ""
echo "4. Checking log files..."
if [ -f /var/log/ctf-fake-flags.log ]; then
    echo "✓ /var/log/ctf-fake-flags.log exists"
    ls -la /var/log/ctf-fake-flags.log
    echo "Last 5 lines:"
    tail -5 /var/log/ctf-fake-flags.log
else
    echo "✗ /var/log/ctf-fake-flags.log NOT found"
fi

if [ -f /var/log/ctf-real-flag.log ]; then
    echo "✓ /var/log/ctf-real-flag.log exists"
    ls -la /var/log/ctf-real-flag.log
    echo "Last 5 lines:"
    tail -5 /var/log/ctf-real-flag.log
else
    echo "✗ /var/log/ctf-real-flag.log NOT found"
fi

# Check script files
echo ""
echo "5. Checking script files..."
if [ -f /opt/ctf-lab/fake_flags.py ]; then
    echo "✓ /opt/ctf-lab/fake_flags.py exists"
    ls -la /opt/ctf-lab/fake_flags.py
else
    echo "✗ /opt/ctf-lab/fake_flags.py NOT found"
fi

if [ -f /opt/ctf-lab/real_flag.py ]; then
    echo "✓ /opt/ctf-lab/real_flag.py exists"
    ls -la /opt/ctf-lab/real_flag.py
else
    echo "✗ /opt/ctf-lab/real_flag.py NOT found"
fi

# Check uvmu user
echo ""
echo "6. Checking uvmu user..."
if id uvmu >/dev/null 2>&1; then
    echo "✓ uvmu user exists"
    id uvmu
else
    echo "✗ uvmu user NOT found"
fi

# Test script manually
echo ""
echo "7. Testing script manually..."
echo "Running: sudo -u uvmu python3 /opt/ctf-lab/fake_flags.py"
timeout 5 sudo -u uvmu python3 /opt/ctf-lab/fake_flags.py 2>&1 | head -10

echo ""
echo "=== Troubleshooting Complete ==="
echo "Check the output above for any issues marked with ✗"