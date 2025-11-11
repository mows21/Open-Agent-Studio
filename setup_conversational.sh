#!/bin/bash
# Setup script for Conversational Agent Studio

set -e

echo "🤖 Setting up Conversational Agent Studio..."
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.10+ required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version OK"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements_conversational.txt

echo "✓ Python dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers (Chrome, Firefox, Safari)..."
playwright install

echo "✓ Playwright browsers installed"
echo ""

# Check for Tesseract OCR
echo "Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "✓ Tesseract found: $TESSERACT_VERSION"
else
    echo "⚠️  Tesseract OCR not found."
    echo ""
    echo "Please install Tesseract OCR:"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "  macOS: brew install tesseract"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    echo "You can continue setup, but OCR features will not work."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Create config.json if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "Creating config.json template..."
    cat > config.json << EOF
{
  "anthropic_api_key": "YOUR_API_KEY_HERE",
  "mcp_servers": {
    "desktop": {
      "command": "python",
      "args": ["mcp_servers/desktop_automation_mcp.py"],
      "enabled": true
    },
    "browser": {
      "command": "python",
      "args": ["mcp_servers/playwright_browser_mcp.py"],
      "enabled": true
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
    "headless": false,
    "viewport": {
      "width": 1280,
      "height": 720
    }
  },
  "desktop": {
    "screenshot_on_error": true,
    "ocr_engine": "pytesseract",
    "confidence_threshold": 0.8
  },
  "workflows": {
    "auto_save": true,
    "save_directory": "./workflows"
  }
}
EOF
    echo "✓ config.json created"
    echo ""
    echo "⚠️  Please edit config.json and add your Anthropic API key!"
else
    echo "✓ config.json already exists"
fi

echo ""

# Create workflows directory
mkdir -p workflows
echo "✓ Workflows directory created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Get your Anthropic API key from: https://console.anthropic.com/"
echo "2. Edit config.json and add your API key"
echo "3. Run the application: python conversational_agent_studio.py"
echo ""
echo "📚 See CONVERSATIONAL_AGENT_GUIDE.md for detailed documentation"
echo ""
