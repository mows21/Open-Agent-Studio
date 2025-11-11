#!/bin/bash
# Quick VPS deployment script for Open Agent Studio

set -e

echo "🚀 Open Agent Studio - VPS Deployment"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script should be run as root for system setup"
    echo "   Run: sudo ./deploy_vps.sh"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Cannot detect OS"
    exit 1
fi

echo "📋 Detected OS: $OS"
echo ""

# Update system
echo "1️⃣  Updating system..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt update && apt upgrade -y
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum update -y
else
    echo "⚠️  Unsupported OS. Please install dependencies manually."
fi

# Install Python 3.10+
echo ""
echo "2️⃣  Installing Python 3.10+..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt install -y python3.10 python3-pip git curl
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum install -y python310 python3-pip git curl
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $PYTHON_VERSION"

# Install Playwright system dependencies
echo ""
echo "3️⃣  Installing Playwright dependencies..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt install -y \
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
        libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
        libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0
fi

# Install Tesseract OCR
echo ""
echo "4️⃣  Installing Tesseract OCR..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt install -y tesseract-ocr tesseract-ocr-eng
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum install -y tesseract
fi

# Clone repository (if not already cloned)
if [ ! -d "Open-Agent-Studio" ]; then
    echo ""
    echo "5️⃣  Cloning repository..."
    git clone https://github.com/mows21/Open-Agent-Studio.git
    cd Open-Agent-Studio
else
    echo ""
    echo "5️⃣  Repository already cloned"
    cd Open-Agent-Studio
    git pull
fi

# Install Python dependencies
echo ""
echo "6️⃣  Installing Python dependencies..."
pip3 install -r requirements_conversational.txt
pip3 install flask flask-cors

# Install Playwright browsers
echo ""
echo "7️⃣  Installing Playwright browsers (this may take a few minutes)..."
playwright install chromium
playwright install-deps

# Create config file
if [ ! -f "config_vps.json" ]; then
    echo ""
    echo "8️⃣  Creating config file..."

    # Prompt for API key
    read -p "Enter your Anthropic API key (or press Enter to set later): " API_KEY

    # Generate random auth token
    AUTH_TOKEN=$(openssl rand -hex 32)

    cat > config_vps.json << EOF
{
  "anthropic_api_key": "${API_KEY:-YOUR_API_KEY_HERE}",
  "mcp_servers": {
    "browser": {
      "command": "python3",
      "args": ["mcp_servers/playwright_browser_mcp.py"],
      "enabled": true
    },
    "desktop": {
      "enabled": false,
      "note": "Desktop automation not available on VPS"
    }
  },
  "agent": {
    "model": "claude-sonnet-4-20250514",
    "max_retries": 3,
    "timeout": 300,
    "self_debug": true
  },
  "browser": {
    "default_browser": "chromium",
    "headless": true,
    "viewport": {
      "width": 1920,
      "height": 1080
    }
  },
  "api": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 8080,
    "auth_token": "$AUTH_TOKEN"
  }
}
EOF

    echo "✓ Config created: config_vps.json"
    echo "✓ Auth token: $AUTH_TOKEN"
    echo ""
    echo "⚠️  SAVE THIS TOKEN! You'll need it to access the API."
    echo "   Add to your requests: Authorization: Bearer $AUTH_TOKEN"
else
    echo ""
    echo "8️⃣  Config file already exists"
fi

# Create systemd service
echo ""
echo "9️⃣  Creating systemd service..."
cat > /etc/systemd/system/openagent.service << EOF
[Unit]
Description=Open Agent Studio API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 vps_api_server.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable openagent

echo "✓ Systemd service created and enabled"

# Setup firewall
echo ""
echo "🔟 Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp  # SSH
    ufw allow 8080/tcp  # API
    echo "✓ UFW firewall configured"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=22/tcp
    firewall-cmd --permanent --add-port=8080/tcp
    firewall-cmd --reload
    echo "✓ Firewalld configured"
else
    echo "⚠️  No firewall detected. Please configure manually."
fi

# Start service
echo ""
echo "1️⃣1️⃣  Starting service..."
systemctl start openagent

sleep 3

# Check status
if systemctl is-active --quiet openagent; then
    echo "✓ Service started successfully!"
else
    echo "❌ Service failed to start. Check logs:"
    echo "   sudo journalctl -u openagent -f"
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "🌐 API URL: http://$SERVER_IP:8080"
echo "🔑 Auth Token: Check config_vps.json"
echo ""
echo "📋 Test the API:"
echo "   curl http://$SERVER_IP:8080/health"
echo ""
echo "📝 Execute a task:"
echo '   curl -X POST http://'"$SERVER_IP"':8080/execute \'
echo '     -H "Authorization: Bearer YOUR_TOKEN" \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"task": "Navigate to example.com"}'"'"
echo ""
echo "📊 Check status:"
echo "   sudo systemctl status openagent"
echo ""
echo "📜 View logs:"
echo "   sudo journalctl -u openagent -f"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Save your auth token from config_vps.json"
echo "   2. Set up Nginx + SSL for production (see DEPLOYMENT_GUIDE.md)"
echo "   3. Configure rate limiting and monitoring"
echo ""
echo "📚 Full documentation: DEPLOYMENT_GUIDE.md"
echo ""
