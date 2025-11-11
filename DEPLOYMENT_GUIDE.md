# 🚀 Open Agent Studio - Deployment Guide

## Overview

Open Agent Studio can be deployed in three configurations depending on your needs:

1. **Local Desktop** - Full features (browser + desktop automation)
2. **Cloud VPS** - Browser automation only (headless)
3. **Hybrid** - VPS for web tasks, local for desktop tasks

---

## 📋 Deployment Decision Matrix

| Feature | Local Desktop | Cloud VPS | Hybrid |
|---------|---------------|-----------|--------|
| **Browser Automation** | ✅ | ✅ | ✅ |
| **Desktop Apps** | ✅ | ❌ | ✅ (local) |
| **Screen Recording** | ✅ | ❌ | ✅ (local) |
| **OCR** | ✅ | ✅ | ✅ |
| **Chat UI** | ✅ | ❌ (use web) | ✅ (web) |
| **Remote Access** | ❌ | ✅ | ✅ |
| **Scalability** | Low | High | High |
| **Cost** | Free | $5-20/mo | $10-50/mo |

---

## 🖥️ Option 1: Local Desktop Deployment

### Prerequisites

- Python 3.10+
- Display/GUI environment
- 4GB+ RAM
- Anthropic API key

### Installation

```bash
# Clone repository
git clone https://github.com/mows21/Open-Agent-Studio.git
cd Open-Agent-Studio

# Install dependencies
pip install -r requirements_conversational.txt
playwright install

# Configure
cp config.json.example config.json
# Edit config.json and add your API key

# Run
python conversational_agent_studio.py
```

### Use Cases

✅ **Perfect for:**
- Personal automation
- Desktop application workflows
- Screen recording and demo creation
- Local file processing
- Mixed web + desktop tasks

❌ **Not ideal for:**
- Team collaboration (unless shared machine)
- Remote execution
- 24/7 scheduled tasks
- High availability

---

## ☁️ Option 2: Cloud VPS Deployment (Browser-Only)

### Why This Works

**Playwright can run headless on a VPS** without a display server. This is perfect for:
- Web scraping
- E2E testing
- Website monitoring
- API-driven automation

**Desktop automation won't work** because:
- No GUI applications available
- No display server (no X11/Wayland)
- PyAutoGUI requires a desktop environment

### VPS Requirements

- Ubuntu 20.04+ or Debian 11+
- 2GB+ RAM (4GB recommended)
- 20GB+ disk space
- Public IP (for API access)

### Recommended VPS Providers

| Provider | Cost | Performance | Notes |
|----------|------|-------------|-------|
| **DigitalOcean** | $6/mo | Good | Easy setup, great docs |
| **Hetzner** | €4/mo | Excellent | Best value in Europe |
| **AWS Lightsail** | $5/mo | Good | Easy if you're on AWS |
| **Linode** | $5/mo | Good | Reliable |
| **Vultr** | $6/mo | Good | Global datacenters |

### Setup Instructions

#### Step 1: Create VPS

```bash
# Example: DigitalOcean
# 1. Create droplet: Ubuntu 22.04, 2GB RAM
# 2. SSH into server
ssh root@your-vps-ip
```

#### Step 2: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.10+
apt install -y python3.10 python3-pip git

# Install Playwright dependencies (IMPORTANT for headless)
apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Install Tesseract for OCR (optional)
apt install -y tesseract-ocr
```

#### Step 3: Clone and Setup

```bash
# Clone repository
git clone https://github.com/mows21/Open-Agent-Studio.git
cd Open-Agent-Studio

# Install Python dependencies
pip3 install -r requirements_conversational.txt

# Install Playwright browsers (headless)
playwright install chromium
playwright install-deps
```

#### Step 4: Configure for Headless

Create `config_vps.json`:

```json
{
  "anthropic_api_key": "sk-ant-YOUR_KEY_HERE",

  "mcp_servers": {
    "browser": {
      "command": "python3",
      "args": ["mcp_servers/playwright_browser_mcp.py"],
      "enabled": true
    },
    "desktop": {
      "enabled": false,
      "note": "Desktop automation disabled on VPS (no display)"
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
    "auth_token": "your-secret-token-here"
  }
}
```

#### Step 5: Create API Server

Create `vps_api_server.py`:

```python
#!/usr/bin/env python3
"""
API Server for VPS deployment
Provides HTTP API for agent orchestration
"""

from flask import Flask, request, jsonify
from agent_orchestrator import AgentOrchestrator
import asyncio
import json

app = Flask(__name__)

# Load config
with open('config_vps.json') as f:
    config = json.load(f)

# Initialize orchestrator
mcp_clients = {}  # TODO: Initialize MCP clients
orchestrator = AgentOrchestrator(
    api_key=config['anthropic_api_key'],
    mcp_clients=mcp_clients
)

# Simple auth
AUTH_TOKEN = config['api']['auth_token']

def check_auth():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return token == AUTH_TOKEN

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "mode": "vps"})

@app.route('/execute', methods=['POST'])
async def execute_task():
    """Execute automation task"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    task_description = data.get('task')

    if not task_description:
        return jsonify({"error": "Missing 'task' field"}), 400

    try:
        result = await orchestrator.process_user_message(task_description)
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/workflows', methods=['GET'])
def list_workflows():
    """List saved workflows"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    # TODO: Implement workflow listing
    return jsonify({"workflows": []})

if __name__ == '__main__':
    app.run(
        host=config['api']['host'],
        port=config['api']['port'],
        debug=False
    )
```

#### Step 6: Run as Service

Create systemd service `/etc/systemd/system/openagent.service`:

```ini
[Unit]
Description=Open Agent Studio API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Open-Agent-Studio
ExecStart=/usr/bin/python3 vps_api_server.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
systemctl daemon-reload
systemctl enable openagent
systemctl start openagent
systemctl status openagent
```

#### Step 7: Setup Nginx (Optional)

```bash
# Install Nginx
apt install -y nginx certbot python3-certbot-nginx

# Create config
cat > /etc/nginx/sites-available/openagent << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/openagent /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Get SSL certificate
certbot --nginx -d your-domain.com
```

### Using VPS via API

**From local machine:**

```bash
# Execute task
curl -X POST https://your-domain.com/execute \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Navigate to example.com and extract the page title"
  }'

# Response:
{
  "success": true,
  "result": "Task completed. Title: Example Domain"
}
```

**From Python:**

```python
import requests

API_URL = "https://your-domain.com"
AUTH_TOKEN = "your-secret-token"

def execute_task(task_description):
    response = requests.post(
        f"{API_URL}/execute",
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
        json={"task": task_description}
    )
    return response.json()

# Use it
result = execute_task("Search Google for 'Python automation'")
print(result)
```

### VPS Limitations

❌ **Cannot do:**
- Desktop application automation (Excel, Photoshop, etc.)
- Screen recording
- Tasks requiring GUI

✅ **Can do:**
- Web scraping
- Browser automation (headless)
- E2E testing
- OCR from images/PDFs
- API integrations
- Data processing

---

## 🌐 Option 3: Hybrid Deployment

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Cloud VPS                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │ • Browser automation (headless)                   │   │
│  │ • Agent orchestrator                              │   │
│  │ • Web UI (Flask)                                  │   │
│  │ • Workflow storage                                │   │
│  └──────────────────┬───────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────┘
                      │ (API calls)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Local Agent  │ │ Local Agent  │ │ Local Agent  │
│ (Desktop 1)  │ │ (Desktop 2)  │ │ (Desktop 3)  │
│              │ │              │ │              │
│ • Desktop    │ │ • Desktop    │ │ • Desktop    │
│   automation │ │   automation │ │   automation │
│ • Connects   │ │ • Connects   │ │ • Connects   │
│   to VPS     │ │   to VPS     │ │   to VPS     │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Setup

**1. Deploy VPS (as in Option 2)**

**2. Install local agents:**

```bash
# On each local machine
pip install -r requirements_conversational.txt

# Run local agent
python local_agent.py --vps-url https://your-domain.com --token your-token
```

**3. Create local agent script:**

Create `local_agent.py`:

```python
#!/usr/bin/env python3
"""
Local Agent - Connects to VPS and executes desktop tasks
"""

import requests
import time
import argparse
from mcp_servers.desktop_automation_mcp import DesktopAutomationMCP

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vps-url', required=True)
    parser.add_argument('--token', required=True)
    parser.add_argument('--poll-interval', type=int, default=5)
    args = parser.parse_args()

    print(f"🤖 Local agent starting...")
    print(f"📡 Connecting to: {args.vps_url}")

    # Initialize desktop MCP
    desktop_mcp = DesktopAutomationMCP()

    # Poll for tasks
    while True:
        try:
            response = requests.get(
                f"{args.vps_url}/agent/tasks",
                headers={"Authorization": f"Bearer {args.token}"}
            )

            if response.status_code == 200:
                tasks = response.json().get('tasks', [])

                for task in tasks:
                    print(f"📋 Executing task: {task['id']}")
                    # Execute task via desktop MCP
                    # ... implementation ...

            time.sleep(args.poll_interval)

        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(args.poll_interval)

if __name__ == '__main__':
    main()
```

### Benefits

✅ **Best of both worlds:**
- VPS handles web automation (scalable, 24/7)
- Local machines handle desktop tasks
- Remote access via web UI
- Team collaboration

---

## 🔒 Security Considerations

### VPS Security

```bash
# 1. Setup firewall
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
ufw enable

# 2. Disable root SSH (after setting up user)
echo "PermitRootLogin no" >> /etc/ssh/sshd_config
systemctl restart sshd

# 3. Use strong auth tokens
# Generate: openssl rand -hex 32

# 4. Enable fail2ban
apt install -y fail2ban
systemctl enable fail2ban
```

### API Security

- ✅ Use HTTPS (Let's Encrypt)
- ✅ Use strong auth tokens
- ✅ Rate limiting (nginx or application-level)
- ✅ IP whitelisting (if possible)
- ✅ Monitor access logs

---

## 📊 Cost Comparison

| Deployment | Setup | Monthly Cost | Maintenance |
|------------|-------|--------------|-------------|
| **Local Desktop** | 30 min | $0 | Low |
| **Cloud VPS** | 2 hours | $5-20 | Medium |
| **Hybrid** | 4 hours | $10-50 | High |

**Plus API costs:**
- Anthropic Claude API: ~$0.01-0.10 per task (depends on complexity)

---

## 🎯 Recommendations

### For Personal Use
→ **Local Desktop**
- Free
- Full features
- Easy setup

### For Web Automation Only
→ **Cloud VPS**
- Always online
- Scalable
- No local machine needed

### For Teams
→ **Hybrid**
- Best flexibility
- Remote access
- Handles all task types

---

## 📚 Next Steps

1. **Choose deployment model** based on your needs
2. **Follow setup instructions** above
3. **Test with simple tasks** first
4. **Scale up** as needed

---

## 🐛 Troubleshooting

### VPS: "Playwright browser failed to launch"

```bash
# Install missing dependencies
playwright install-deps
```

### VPS: "OCR not working"

```bash
# Install Tesseract
apt install tesseract-ocr tesseract-ocr-eng
```

### API: "Connection refused"

```bash
# Check service status
systemctl status openagent

# Check logs
journalctl -u openagent -f
```

### Nginx: "502 Bad Gateway"

```bash
# Check if API is running
curl http://localhost:8080/health

# Check nginx logs
tail -f /var/log/nginx/error.log
```

---

## 📞 Support

For deployment issues:
- GitHub Issues: https://github.com/mows21/Open-Agent-Studio/issues
- Documentation: See README_CONVERSATIONAL.md
- Community: Discord (link in README)
