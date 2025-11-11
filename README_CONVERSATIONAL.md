# 🤖 Open Agent Studio - Conversational AI Edition

> **Transform any desktop or browser task into automation through simple conversation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude AI](https://img.shields.io/badge/Claude-AI-purple.svg)](https://anthropic.com)

## What is this?

Instead of dragging and dropping nodes or writing code, **just describe what you want** and watch the AI agent:

1. ✨ Understand your request
2. 📋 Plan the execution steps
3. 🚀 Execute on desktop & browser
4. 🔧 Self-debug when things break
5. 💾 Save as reusable workflows

---

## 🎥 Quick Demo

```
You: "Create demo videos of our product every week"

Agent: I'll help you automate demo video creation. Let me break this down:

1. Navigate to product site
2. Record key features
3. Add voiceover
4. Export video
5. Schedule weekly

Starting now... ⟳

✓ Successfully recorded demo (2m 34s)
✓ Workflow saved as 'Weekly Demo Creator'
✓ Scheduled for Mondays at 9am

Would you like to review the workflow or run it again?
```

---

## 🌟 Key Features

### 🗣️ **Natural Language Control**
Just chat with the agent - no programming required.

```
"Check my Gmail and reply to urgent emails"
"Extract data from invoices into Excel"
"Run end-to-end tests on the login flow"
"Create a weekly report and email it to the team"
```

### 🤖 **AI-Powered Orchestration**
Claude Agent SDK plans and executes complex multi-step tasks.

### 🌐 **Hybrid Automation**
- **Browser:** Playwright for fast, reliable web automation
- **Desktop:** PyAutoGUI for any application (Excel, Photoshop, etc.)
- **Smart Selection:** Agent automatically chooses the best tool

### 🔧 **Self-Debugging**
When something fails, the agent:
1. Analyzes the error
2. Figures out what went wrong
3. Tries alternative approaches
4. Learns for next time

### 📊 **Visual Workflows**
Every successful task becomes a reusable, editable node graph.

### 🎯 **Zero Learning Curve**
No need to learn node graphs, selectors, or automation concepts. Just describe what you want.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Open-Agent-Studio.git
cd Open-Agent-Studio

# Run setup script
chmod +x setup_conversational.sh
./setup_conversational.sh

# Or manually:
pip install -r requirements_conversational.txt
playwright install
```

### Configuration

1. Get your Anthropic API key from https://console.anthropic.com/
2. Edit `config.json`:

```json
{
  "anthropic_api_key": "sk-ant-YOUR_KEY_HERE"
}
```

### Launch

```bash
python conversational_agent_studio.py
```

---

## 💡 Usage Examples

### Example 1: Email Automation

**Input:**
```
"Check Gmail for emails from my boss and mark them as important"
```

**What happens:**
1. Agent launches browser with Playwright
2. Navigates to Gmail
3. Searches for sender
4. Marks emails as starred
5. Returns count of emails processed

**Time:** ~10 seconds (vs 2+ minutes manually)

---

### Example 2: Data Extraction

**Input:**
```
"Extract invoice data from PDFs in Downloads folder to Excel"
```

**What happens:**
1. Lists all PDF files
2. Uses DeepSeek-OCR to extract structured data
3. Parses invoice number, date, total, line items
4. Creates Excel with all data
5. Formats with proper columns and totals

**Time:** ~5 minutes for 50 invoices (vs 3+ hours manually)

---

### Example 3: Demo Video Creation

**Input:**
```
"Record a 3-minute demo of our app showing the signup flow"
```

**What happens:**
1. Starts screen recording
2. Opens your app
3. Goes through signup steps
4. Captures key interactions
5. Stops recording and saves video

**Time:** ~3 minutes (automated, consistent, reusable)

---

### Example 4: E2E Testing

**Input:**
```
"Test the login form with valid, invalid, and edge case inputs"
```

**What happens:**
1. Opens test environment
2. Tries valid credentials → ✓ Pass
3. Tries invalid email → ✓ Error shown correctly
4. Tries SQL injection → ✓ Sanitized properly
5. Tries empty fields → ✓ Validation works
6. Generates test report

**Time:** ~1 minute for 10 test cases (vs 20+ minutes manually)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  USER INTERFACE                          │
│   Chat Panel  |  Node Graph  |  Live Preview            │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│         CLAUDE AGENT SDK (Orchestrator)                  │
│  • Understand intent                                     │
│  • Plan execution                                        │
│  • Self-debug failures                                   │
│  • Generate workflows                                    │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│               MCP SERVER LAYER                           │
│   Desktop MCP  |  Browser MCP  |  Vision MCP            │
│  (pyautogui,   | (Playwright)  | (DeepSeek-OCR)         │
│   OCR, vision) |               |                         │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
         EXECUTION (Desktop + Web)
```

---

## 🆚 Comparison with Other Tools

| Feature | UIPath | Zapier | n8n | **Open Agent Studio** |
|---------|--------|--------|-----|----------------------|
| **Setup Time** | Hours | Minutes | Hours | **30 seconds** |
| **Learning Curve** | High | Low | Medium | **Zero (just chat)** |
| **Desktop Automation** | ✓ | ✗ | ✗ | **✓** |
| **Browser Automation** | ✓ | Limited | ✓ | **✓** |
| **Self-Debugging** | ✗ | ✗ | ✗ | **✓** |
| **Natural Language** | ✗ | ✗ | ✗ | **✓** |
| **Cost** | $$$ | $$ | $ (self-host) | **Free (API costs only)** |
| **Open Source** | ✗ | ✗ | ✓ | **✓** |

---

## 🔥 Advanced Features

### Multi-Agent Orchestration (Coming Soon)

```
You: "Every Monday at 9am, collect sales data, create a report,
      and email it to the team"

Agent 1: Data Collection
  • Queries CRM
  • Exports to CSV

Agent 2: Report Generation
  • Opens Excel
  • Creates charts
  • Generates PDF

Agent 3: Distribution
  • Composes email
  • Attaches report
  • Sends to mailing list

Result: Fully automated weekly process
```

### Voice Control (Coming Soon)

```
[Speaks] "Hey Agent, check my calendar for today"

[Agent responds] "You have 3 meetings:
  • 10am: Team standup
  • 2pm: Client demo
  • 4pm: 1-on-1 with Sarah"
```

### Mobile Remote Control (Coming Soon)

Run automations from your phone while away from computer.

---

## 🛠️ Development

### Project Structure

```
Open-Agent-Studio/
├── conversational_agent_studio.py  # Main application
├── chat_interface.py               # Chat UI component
├── agent_orchestrator.py           # Claude Agent SDK integration
├── mcp_servers/
│   ├── desktop_automation_mcp.py   # Desktop automation MCP
│   ├── playwright_browser_mcp.py   # Browser automation MCP
│   └── vision_mcp.py              # Vision AI MCP (future)
├── NodeGraphQt/                    # Original node graph editor
├── workflows/                      # Saved workflows
├── config.json                     # Configuration
└── CONVERSATIONAL_AGENT_GUIDE.md  # Detailed documentation
```

### Adding Custom MCP Servers

Create a new MCP server for specialized tasks:

```python
# mcp_servers/email_mcp.py
from mcp.server import Server

class EmailMCP:
    def __init__(self):
        self.server = Server("email-automation")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(name="send_email", ...),
                Tool(name="read_inbox", ...),
                Tool(name="filter_emails", ...),
            ]
```

Add to `config.json`:

```json
{
  "mcp_servers": {
    "email": {
      "command": "python",
      "args": ["mcp_servers/email_mcp.py"],
      "enabled": true
    }
  }
}
```

---

## 📚 Documentation

- **[Full Guide](CONVERSATIONAL_AGENT_GUIDE.md)** - Complete documentation
- **[API Reference](docs/api_reference.md)** - Developer API docs
- **[Examples](examples/)** - Pre-built workflows and examples
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and fixes

---

## 🤝 Contributing

We welcome contributions!

**Priority areas:**
- 🔧 New MCP servers (e.g., Email, Database, Cloud Storage)
- 📝 Workflow templates
- 🐛 Bug fixes and improvements
- 📖 Documentation
- 🧪 Testing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 🗺️ Roadmap

### Version 2.1 (Q2 2025)
- [ ] DeepSeek-OCR integration
- [ ] Workflow template library
- [ ] Team collaboration
- [ ] Cloud workflow sync

### Version 2.2 (Q3 2025)
- [ ] Voice control
- [ ] Mobile app
- [ ] Scheduled automation dashboard
- [ ] Analytics & reporting

### Version 3.0 (Q4 2025)
- [ ] Multi-agent orchestration
- [ ] Custom skill marketplace
- [ ] Enterprise features (SSO, audit logs)
- [ ] On-premise deployment

---

## 🐛 Troubleshooting

### Common Issues

**Agent not responding?**
- Check API key in `config.json`
- Verify internet connection
- Check Anthropic API status

**MCP server failed?**
```bash
# Test MCP servers directly
python mcp_servers/desktop_automation_mcp.py
python mcp_servers/playwright_browser_mcp.py
```

**Playwright not working?**
```bash
# Reinstall browsers
playwright install
playwright install-deps
```

**OCR not working?**
```bash
# Install Tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Verify: tesseract --version
```

See [Troubleshooting Guide](docs/troubleshooting.md) for more help.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Credits

**Built with:**
- [Claude AI](https://anthropic.com) - AI orchestration
- [Playwright](https://playwright.dev) - Browser automation
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - Desktop automation
- [PySide2](https://wiki.qt.io/Qt_for_Python) - UI framework
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP servers

**Inspired by:**
- UIPath, Zapier, n8n, Make.com - Automation platforms
- Devin, Cursor - AI coding assistants
- Open Interpreter - Natural language computing

---

## 🌟 Star History

If you find this useful, please star the repo!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/Open-Agent-Studio&type=Date)](https://star-history.com/#yourusername/Open-Agent-Studio&Date)

---

## 💬 Community

- **Discord:** [Join our server](https://discord.gg/your-server)
- **Twitter:** [@OpenAgentStudio](https://twitter.com/your-handle)
- **YouTube:** [Video tutorials](https://youtube.com/your-channel)
- **Email:** support@openagent.studio

---

## 🎯 Support the Project

If you're using Open Agent Studio and want to support development:

- ⭐ **Star** this repo
- 🐛 **Report** bugs and issues
- 💡 **Suggest** features
- 📝 **Write** documentation
- 💻 **Contribute** code
- 💬 **Share** with others

---

**Ready to automate anything? Get started now! 🚀**

```bash
git clone https://github.com/yourusername/Open-Agent-Studio.git
cd Open-Agent-Studio
./setup_conversational.sh
python conversational_agent_studio.py
```
