# 🤖 Conversational Agent Studio - Complete Guide

## Overview

The Conversational Agent Studio transforms Open Agent Studio from a node-based drag-and-drop tool into an **AI-powered conversational automation platform**. Instead of manually building workflows, you simply **describe what you want** and the AI agent:

1. ✅ **Understands** your intent
2. ✅ **Plans** the execution steps
3. ✅ **Executes** the task (desktop + browser)
4. ✅ **Self-debugs** when things go wrong
5. ✅ **Generates** reusable workflows
6. ✅ **Learns** from experience

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  ┌──────────┐  ┌────────────────┐  ┌─────────────────┐    │
│  │  Chat    │  │  Node Graph    │  │  Live Preview   │    │
│  │  Panel   │  │  Editor        │  │  & Execution    │    │
│  └────┬─────┘  └────────▲───────┘  └─────────────────┘    │
└───────┼──────────────────┼───────────────────────────────────┘
        │                  │
        ▼                  │ (generates workflows)
┌─────────────────────────────────────────────────────────────┐
│           CLAUDE AGENT SDK (Orchestrator)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Agent Loop:                                          │   │
│  │ • Parse user intent                                  │   │
│  │ • Create execution plan                              │   │
│  │ • Execute via MCP servers                            │   │
│  │ • Monitor & self-debug                               │   │
│  │ • Generate workflows                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (calls tools via MCP)
┌─────────────────────────────────────────────────────────────┐
│                   MCP SERVER LAYER                          │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ Desktop MCP    │  │ Browser MCP    │  │ Vision MCP   │  │
│  │ (pyautogui,    │  │ (Playwright)   │  │ (DeepSeek    │  │
│  │  OCR, vision)  │  │                │  │  OCR, BLIP)  │  │
│  └────────┬───────┘  └────────┬───────┘  └──────┬───────┘  │
└───────────┼──────────────────┼──────────────────┼──────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXECUTION LAYER                            │
│  Desktop Control    Web Automation    AI Vision             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Open-Agent-Studio.git
cd Open-Agent-Studio

# Install dependencies
pip install -r requirements_conversational.txt

# Install Playwright browsers
playwright install
```

### 2. Configuration

Create `config.json`:

```json
{
  "anthropic_api_key": "sk-ant-...",
  "mcp_servers": {
    "desktop": {
      "command": "python",
      "args": ["mcp_servers/desktop_automation_mcp.py"]
    },
    "browser": {
      "command": "python",
      "args": ["mcp_servers/playwright_browser_mcp.py"]
    }
  }
}
```

### 3. Launch

```bash
python conversational_agent_studio.py
```

---

## Usage Examples

### Example 1: Simple Email Automation

**User:** "Check my Gmail and reply to urgent emails"

**Agent Process:**
1. 🧠 **Understands:** Need to access Gmail, identify urgent emails, compose replies
2. 📋 **Plans:**
   - Launch browser
   - Navigate to Gmail
   - Login (if needed)
   - Search for unread emails with "urgent" in subject
   - For each: analyze content, generate reply, send
3. ▶️ **Executes:** Uses Playwright MCP to automate browser
4. ✅ **Result:** Replies sent, workflow saved as "Urgent Email Responder"

### Example 2: Data Extraction

**User:** "Extract data from invoices in my Downloads folder into a spreadsheet"

**Agent Process:**
1. 🧠 **Understands:** OCR task - read PDFs, extract structured data, write to Excel
2. 📋 **Plans:**
   - List files in Downloads folder (filter *.pdf)
   - For each PDF:
     - Use DeepSeek-OCR to extract with structure preservation
     - Parse invoice data (number, date, total, items)
   - Create Excel file with results
3. ▶️ **Executes:** Uses Desktop MCP + Vision MCP
4. ✅ **Result:** Excel file created with all invoice data

### Example 3: Demo Video Creation

**User:** "Create a demo video showing how to use our app"

**Agent Process:**
1. 🧠 **Understands:** Screen recording + narration task
2. 📋 **Plans:**
   - Start screen recording
   - Navigate through app features (predetermined flow)
   - Capture key interactions
   - Stop recording
   - (Optional) Add voiceover using TTS
3. ▶️ **Executes:** Desktop automation for screen recording
4. ✅ **Result:** Demo video saved, workflow reusable

### Example 4: End-to-End Testing

**User:** "Run E2E tests on the login flow with various inputs"

**Agent Process:**
1. 🧠 **Understands:** Automated testing - try multiple scenarios
2. 📋 **Plans:**
   - Test valid credentials → Should succeed
   - Test invalid email → Should show error
   - Test wrong password → Should show error
   - Test empty fields → Should require input
   - Test SQL injection → Should sanitize
3. ▶️ **Executes:** Playwright for each test case
4. ✅ **Result:** Test report with pass/fail for each scenario

---

## MCP Servers Explained

### What are MCP Servers?

**Model Context Protocol (MCP)** servers are specialized tools that the Claude agent can call to perform specific actions. They're like "skills" that expand the agent's capabilities.

### Available MCP Servers

#### 1. **Desktop Automation MCP** (`desktop_automation_mcp.py`)

**Capabilities:**
- `take_screenshot` - Capture screen or region
- `ocr_text` - Extract text from screen regions
- `find_element` - Locate UI elements (template matching or semantic)
- `click` - Click at coordinates
- `type_text` - Type keyboard text
- `press_key` - Press specific keys/combinations
- `move_mouse` - Move cursor
- `analyze_screen` - AI vision analysis of screen
- `wait_for_element` - Wait for element to appear

**Use Cases:**
- Desktop applications (Excel, Word, etc.)
- System automation
- Image recognition tasks
- OCR from any application

#### 2. **Browser Automation MCP** (`playwright_browser_mcp.py`)

**Capabilities:**
- `browser_launch` - Start browser (Chrome/Firefox/Safari)
- `navigate` - Go to URL
- `click_element` - Click by selector or text
- `fill_input` - Fill form fields
- `press_key` - Keyboard input
- `screenshot` - Capture page/element
- `get_text` - Extract text from elements
- `wait_for_selector` - Wait for elements
- `evaluate_js` - Execute JavaScript
- `get_page_content` - Get HTML
- `network_intercept` - Monitor network requests

**Use Cases:**
- Web scraping
- Form automation
- Testing web applications
- Data extraction from websites

#### 3. **Vision Analysis MCP** (Future)

**Planned Capabilities:**
- DeepSeek-OCR integration
- BLIP image captioning
- Semantic element detection
- Complex document parsing

---

## Playwright vs Desktop Automation

### When to Use Playwright (Browser MCP)

✅ **Use for:**
- Web applications
- Need reliable selectors (CSS, XPath)
- JavaScript execution required
- Network monitoring needed
- Multi-tab scenarios
- Fast, precise web automation

❌ **Cannot use for:**
- Desktop applications
- System-level tasks
- Non-browser UIs

### When to Use Desktop Automation MCP

✅ **Use for:**
- Desktop applications (Excel, Photoshop, etc.)
- System automation (file management, etc.)
- Works on ANY application
- Screen-based (vision AI)
- Cross-platform compatibility

❌ **Limitations:**
- Slower than Playwright for web
- No DOM access
- Requires visual element detection

### Best Practice: Hybrid Approach

The agent **automatically chooses** the right tool:

```
Task: "Login to website and download reports"
  ↓
Agent Analysis:
  - "Login to website" → Use Playwright (faster, more reliable)
  - "Download reports" → Use Playwright
  ↓
Result: Pure browser automation
```

```
Task: "Open Excel from website, edit data, save PDF"
  ↓
Agent Analysis:
  - "Download from website" → Use Playwright
  - "Open Excel" → Use Desktop MCP
  - "Edit data" → Use Desktop MCP
  - "Save PDF" → Use Desktop MCP
  ↓
Result: Hybrid automation
```

---

## Self-Debugging System

### How It Works

When a step fails, the agent:

1. **Captures Context:**
   - Screenshot at time of failure
   - Error message
   - Previous successful steps
   - Original plan

2. **Analyzes Failure:**
   - Sends context to Claude
   - Gets diagnosis and fix suggestion

3. **Applies Fix:**
   - **Retry** - Try again with same parameters
   - **Modify** - Adjust parameters (e.g., longer timeout)
   - **Alternative** - Use different tool/approach
   - **Skip** - Continue to next step (if non-critical)

4. **Learns:**
   - Successful fixes stored
   - Applied to future similar failures

### Example: Self-Debug in Action

```
Step: Click "Submit" button
Error: Element not found

Agent Self-Debug:
1. Takes screenshot
2. Analyzes: "Page might still be loading"
3. Fix Strategy: "Wait for element + longer timeout"
4. Retry with modified args: {timeout: 10000, wait_until: "visible"}
5. Success! ✓

Learns: "For submit buttons, always wait for visibility"
```

---

## Workflow Generation

### Automatic Workflow Creation

After successfully completing a task, the agent generates a **reusable workflow**:

**Input:** User conversation + successful execution

**Output:** Open Agent Studio node graph

```json
{
  "nodes": {
    "node_0": {
      "name": "Launch Browser",
      "type": "browser_launch",
      "custom": {
        "browser": "chromium",
        "headless": false
      }
    },
    "node_1": {
      "name": "Navigate to Gmail",
      "type": "navigate",
      "custom": {
        "url": "https://gmail.com"
      }
    },
    ...
  },
  "connections": [
    {"out": ["node_0", 0], "in": ["node_1", 0]},
    ...
  ],
  "metadata": {
    "name": "Gmail Urgent Email Responder",
    "created": "2025-01-15T10:30:00",
    "success_rate": "100%"
  }
}
```

### Workflow Benefits

1. **Reusable** - Run the same task anytime with one click
2. **Editable** - Modify in node graph editor
3. **Schedulable** - Set up recurring automation
4. **Shareable** - Export and share with team
5. **Debuggable** - Visual representation of steps

---

## Advanced Features

### 1. Context-Aware Execution

The agent maintains context across messages:

```
User: "Open Gmail"
Agent: ✓ Gmail opened

User: "Find emails from John"
Agent: (knows Gmail is already open)
       ✓ Searching in Gmail for "from:john"

User: "Reply to the latest one"
Agent: (knows which emails are being referenced)
       ✓ Composing reply to john@example.com
```

### 2. Multi-Step Planning

For complex tasks, the agent creates **multi-phase plans**:

```
Task: "Automate weekly report generation"

Plan:
Phase 1: Data Collection (steps 1-5)
  1. Access database
  2. Query weekly stats
  3. Export to CSV

Phase 2: Processing (steps 6-10)
  6. Open Excel
  7. Import CSV
  8. Create charts
  9. Calculate summaries

Phase 3: Distribution (steps 11-15)
  11. Generate PDF
  12. Compose email
  13. Attach PDF
  14. Send to team
  15. Archive in shared drive
```

### 3. Error Recovery

The agent tries multiple strategies before giving up:

```
Attempt 1: Click button by CSS selector → Failed
  ↓
Attempt 2: Click button by XPath → Failed
  ↓
Attempt 3: Click button by text content → Failed
  ↓
Attempt 4: Use vision AI to find button → Success! ✓
```

### 4. Learning & Improvement

The system learns from:
- Successful executions (stores patterns)
- Failed attempts (stores fixes)
- User feedback (corrections)
- Usage frequency (optimizes common tasks)

---

## Configuration Options

### `config.json` Full Schema

```json
{
  "anthropic_api_key": "sk-ant-...",

  "mcp_servers": {
    "desktop": {
      "command": "python",
      "args": ["mcp_servers/desktop_automation_mcp.py"],
      "env": {},
      "enabled": true
    },
    "browser": {
      "command": "python",
      "args": ["mcp_servers/playwright_browser_mcp.py"],
      "env": {},
      "enabled": true
    }
  },

  "agent": {
    "model": "claude-sonnet-4-20250514",
    "max_retries": 3,
    "timeout": 300,
    "self_debug": true,
    "verbose": false
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
    "save_directory": "./workflows",
    "backup": true
  }
}
```

---

## Troubleshooting

### Common Issues

#### 1. Agent Not Responding

**Problem:** Chat sends message but no response

**Solutions:**
- Check API key is valid (`config.json`)
- Verify internet connection
- Check Anthropic API status
- Look for errors in execution log

#### 2. MCP Server Connection Failed

**Problem:** "Desktop MCP not available"

**Solutions:**
```bash
# Test MCP server directly
python mcp_servers/desktop_automation_mcp.py

# Check for missing dependencies
pip install -r requirements_conversational.txt

# Verify Python version (3.10+)
python --version
```

#### 3. Playwright Browser Won't Launch

**Problem:** Browser automation fails

**Solutions:**
```bash
# Install Playwright browsers
playwright install

# Install dependencies
playwright install-deps

# Test Playwright
python -c "from playwright.sync_api import sync_playwright; \
           p = sync_playwright().start(); \
           browser = p.chromium.launch(); \
           print('Success!')"
```

#### 4. OCR Not Working

**Problem:** Text extraction fails

**Solutions:**
```bash
# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Verify installation
tesseract --version
```

---

## Performance Tips

### 1. Use Headless Browser (Faster)

```json
{
  "browser": {
    "headless": true
  }
}
```

### 2. Reduce Screenshot Quality

```python
# In desktop_automation_mcp.py
screenshot = pyautogui.screenshot()
screenshot.save(buffered, format="PNG", optimize=True, quality=75)
```

### 3. Cache Common Elements

The agent automatically caches element locations for faster re-detection.

### 4. Parallel Execution

For independent tasks, the agent executes steps in parallel:

```
Task: "Check Gmail AND Slack for messages"

Parallel Execution:
  Thread 1: Check Gmail → 3 seconds
  Thread 2: Check Slack → 3 seconds

Total Time: 3 seconds (not 6!)
```

---

## API Reference

### AgentOrchestrator Class

```python
class AgentOrchestrator:
    def __init__(self, api_key: str, mcp_clients: Dict[str, Any])

    async def process_user_message(self, message: str) -> str
        """Main entry point for processing user messages"""

    # Callbacks
    on_thinking_start: Callable[[str], None]
    on_thinking_end: Callable[[], None]
    on_step_update: Callable[[str, str], None]
    on_task_complete: Callable[[dict], None]
    on_error: Callable[[str, str], None]
```

### MCP Client Interface

```python
class MCPClient:
    async def call_tool(self, tool_name: str, args: dict) -> Any
        """Call a tool on the MCP server"""

    async def list_tools(self) -> List[Tool]
        """Get available tools"""
```

---

## Comparison: Conversational vs Traditional

| Aspect | Traditional (Drag-Drop) | Conversational |
|--------|------------------------|----------------|
| **Setup Time** | 10-30 minutes | 30 seconds |
| **Learning Curve** | Medium (understand nodes) | Low (just describe task) |
| **Flexibility** | High (full control) | High (AI adapts) |
| **Self-Debugging** | Manual | Automatic |
| **Reusability** | Node graphs | Node graphs + Natural language |
| **Error Handling** | User must fix | Agent self-fixes |
| **Multi-Platform** | Manual switching | Automatic detection |
| **Best For** | Power users, precise control | Quick automation, non-technical users |

**Recommendation:** Use both!
- Start conversationally to quickly create workflows
- Fine-tune in node graph editor for precision
- Combine chat commands with visual editing

---

## Roadmap

### Version 2.1 (Q2 2025)

- [ ] DeepSeek-OCR integration
- [ ] Workflow templates library
- [ ] Team collaboration features
- [ ] Cloud workflow storage

### Version 2.2 (Q3 2025)

- [ ] Voice input support
- [ ] Mobile remote control
- [ ] Scheduled automation dashboard
- [ ] Analytics & reporting

### Version 3.0 (Q4 2025)

- [ ] Multi-agent orchestration
- [ ] Custom skill development platform
- [ ] Marketplace for workflows
- [ ] Enterprise features (SSO, audit logs)

---

## Contributing

We welcome contributions! Areas of focus:

1. **New MCP Servers** - Add more automation capabilities
2. **Workflow Templates** - Share common automation patterns
3. **Self-Debugging** - Improve error recovery strategies
4. **Documentation** - Help others learn the system
5. **Testing** - Write tests for agent behavior

See `CONTRIBUTING.md` for details.

---

## License

MIT License - See `LICENSE` file

---

## Support

- **Documentation:** https://github.com/your-repo/docs
- **Issues:** https://github.com/your-repo/issues
- **Discord:** https://discord.gg/your-server
- **Email:** support@example.com

---

## Credits

Built with:
- [Claude AI](https://anthropic.com) - AI orchestration
- [Playwright](https://playwright.dev) - Browser automation
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - Desktop automation
- [PySide2](https://wiki.qt.io/Qt_for_Python) - UI framework
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP servers

Inspired by:
- UIPath, Zapier, n8n, Make.com - Automation platforms
- Devin, Cursor - AI coding assistants
- Open Interpreter - Natural language computing

---

**Happy Automating! 🚀**
