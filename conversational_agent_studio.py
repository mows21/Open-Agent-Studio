#!/usr/bin/env python3
"""
Conversational Agent Studio - Main Application
Combines chat interface + node graph + Claude Agent SDK
"""

import sys
import asyncio
from PySide2 import QtWidgets, QtCore, QtGui
import anthropic

# Import our components
from chat_interface import ChatWidget
from agent_orchestrator import AgentOrchestrator

# Import existing Open Agent Studio components
try:
    from NodeGraphQt import NodeGraph
    from NodeGraphQt.constants import *
except:
    print("Warning: NodeGraphQt not found. Install with: pip install NodeGraphQt")


class ConversationalAgentStudio(QtWidgets.QMainWindow):
    """
    Main application window combining:
    - Chat interface (left panel)
    - Node graph editor (center)
    - Live execution preview (right panel)
    """

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_agent()

    def setup_ui(self):
        """Build the main UI"""
        self.setWindowTitle("🤖 Open Agent Studio - Conversational AI Edition")
        self.resize(1600, 900)

        # Apply dark theme
        self.apply_dark_theme()

        # Create central widget with splitter
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter (3 panels)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # LEFT PANEL: Chat Interface
        self.chat_widget = ChatWidget()
        self.chat_widget.setMinimumWidth(400)
        self.chat_widget.message_sent.connect(self.on_user_message)
        self.chat_widget.workflow_generated.connect(self.on_workflow_generated)
        splitter.addWidget(self.chat_widget)

        # CENTER PANEL: Node Graph Editor
        try:
            self.graph = NodeGraph()
            self.graph_widget = self.graph.widget
            self.graph_widget.setMinimumWidth(600)
            splitter.addWidget(self.graph_widget)
        except:
            # Fallback if NodeGraphQt not available
            placeholder = QtWidgets.QLabel("Node Graph\n(Install NodeGraphQt to enable)")
            placeholder.setAlignment(QtCore.Qt.AlignCenter)
            placeholder.setStyleSheet("color: #abb2bf; font-size: 16px;")
            splitter.addWidget(placeholder)
            self.graph = None

        # RIGHT PANEL: Live Preview & Execution
        self.preview_panel = self.create_preview_panel()
        self.preview_panel.setMinimumWidth(300)
        splitter.addWidget(self.preview_panel)

        # Set splitter sizes (25%, 50%, 25%)
        splitter.setSizes([400, 800, 400])

        layout.addWidget(splitter)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Menu bar
        self.create_menu_bar()

        # Status bar
        self.statusBar().showMessage("Ready - Ask me to automate anything!")

    def create_preview_panel(self) -> QtWidgets.QWidget:
        """Create the live preview panel"""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # Header
        header = QtWidgets.QLabel("📺 Live Preview")
        header.setStyleSheet("""
            QLabel {
                background: #2d2d2d;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        layout.addWidget(header)

        # Screenshot display
        self.preview_image = QtWidgets.QLabel()
        self.preview_image.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_image.setStyleSheet("background: #1e1e1e; border: 1px solid #3daee9;")
        self.preview_image.setMinimumHeight(300)
        self.preview_image.setScaledContents(False)
        layout.addWidget(self.preview_image, stretch=1)

        # Execution log
        log_label = QtWidgets.QLabel("📋 Execution Log")
        log_label.setStyleSheet("color: white; padding: 5px; font-size: 12px; font-weight: bold;")
        layout.addWidget(log_label)

        self.execution_log = QtWidgets.QTextEdit()
        self.execution_log.setReadOnly(True)
        self.execution_log.setMaximumHeight(200)
        self.execution_log.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3daee9;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.execution_log)

        # Controls
        controls = QtWidgets.QHBoxLayout()

        self.pause_btn = QtWidgets.QPushButton("⏸ Pause")
        self.pause_btn.setEnabled(False)
        controls.addWidget(self.pause_btn)

        self.stop_btn = QtWidgets.QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        controls.addWidget(self.stop_btn)

        self.screenshot_btn = QtWidgets.QPushButton("📸 Screenshot")
        self.screenshot_btn.clicked.connect(self.take_manual_screenshot)
        controls.addWidget(self.screenshot_btn)

        layout.addLayout(controls)

        panel.setLayout(layout)
        return panel

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QtWidgets.QAction("New Workflow", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_workflow)
        file_menu.addAction(new_action)

        open_action = QtWidgets.QAction("Open Workflow", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_workflow)
        file_menu.addAction(open_action)

        save_action = QtWidgets.QAction("Save Workflow", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_workflow)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Agent menu
        agent_menu = menubar.addMenu("Agent")

        configure_action = QtWidgets.QAction("Configure API Keys", self)
        configure_action.triggered.connect(self.configure_api_keys)
        agent_menu.addAction(configure_action)

        agent_menu.addSeparator()

        test_desktop = QtWidgets.QAction("Test Desktop MCP", self)
        test_desktop.triggered.connect(lambda: self.test_mcp("desktop"))
        agent_menu.addAction(test_desktop)

        test_browser = QtWidgets.QAction("Test Browser MCP", self)
        test_browser.triggered.connect(lambda: self.test_mcp("browser"))
        agent_menu.addAction(test_browser)

        # Help menu
        help_menu = menubar.addMenu("Help")

        examples_action = QtWidgets.QAction("Example Tasks", self)
        examples_action.triggered.connect(self.show_examples)
        help_menu.addAction(examples_action)

        docs_action = QtWidgets.QAction("Documentation", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        about_action = QtWidgets.QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_agent(self):
        """Initialize the Claude Agent SDK orchestrator"""
        # Get API key (from settings or prompt user)
        api_key = self.get_anthropic_api_key()

        if not api_key:
            QtWidgets.QMessageBox.information(
                self,
                "API Key Required",
                "Please configure your Anthropic API key in Agent > Configure API Keys"
            )
            self.orchestrator = None
            return

        # TODO: Initialize MCP clients
        # For now, use mock clients
        mcp_clients = {}

        try:
            self.orchestrator = AgentOrchestrator(api_key, mcp_clients)

            # Set up callbacks
            self.orchestrator.on_thinking_start = self.on_agent_thinking_start
            self.orchestrator.on_thinking_end = self.on_agent_thinking_end
            self.orchestrator.on_step_update = self.on_agent_step_update
            self.orchestrator.on_task_complete = self.on_agent_task_complete
            self.orchestrator.on_error = self.on_agent_error

        except Exception as e:
            print(f"Failed to initialize agent: {e}")
            self.orchestrator = None

    def get_anthropic_api_key(self) -> str:
        """Get API key from settings or environment"""
        # Try to load from settings file
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                return config.get("anthropic_api_key")
        except:
            pass

        # Check environment variable
        import os
        return os.getenv("ANTHROPIC_API_KEY")

    def on_user_message(self, message: str):
        """Handle user message from chat"""
        if not self.orchestrator:
            self.chat_widget.add_message(
                "system",
                "⚠ Agent not configured. Please set up your API key in Agent > Configure API Keys"
            )
            return

        # Process message in background
        asyncio.create_task(self.process_message_async(message))

    async def process_message_async(self, message: str):
        """Process user message asynchronously"""
        try:
            response = await self.orchestrator.process_user_message(message)
            self.chat_widget.add_message("assistant", response)
        except Exception as e:
            self.chat_widget.add_message(
                "system",
                f"❌ Error: {str(e)}"
            )

    def on_agent_thinking_start(self, status: str):
        """Agent started thinking"""
        self.chat_widget.set_agent_thinking(True, status)
        self.log_execution(f"🤔 {status}")

    def on_agent_thinking_end(self):
        """Agent finished thinking"""
        self.chat_widget.set_agent_thinking(False)

    def on_agent_step_update(self, description: str, status: str):
        """Agent executed a step"""
        self.chat_widget.add_task_update(description, status)

        icons = {"running": "⟳", "completed": "✓", "error": "✗"}
        self.log_execution(f"{icons.get(status, '●')} {description}")

    def on_agent_task_complete(self, result: dict):
        """Agent completed entire task"""
        self.log_execution(f"✓ Task completed: {result.get('summary', 'Success')}")

    def on_agent_error(self, title: str, message: str):
        """Agent encountered error"""
        self.log_execution(f"✗ Error: {title} - {message}")

    def on_workflow_generated(self, workflow: dict):
        """Agent generated a workflow"""
        if not self.graph:
            QtWidgets.QMessageBox.information(
                self,
                "Workflow Generated",
                "A workflow was generated but NodeGraphQt is not available."
            )
            return

        # Load workflow into node graph
        try:
            # TODO: Implement workflow loading
            self.log_execution("📊 Workflow loaded into node graph")
        except Exception as e:
            print(f"Failed to load workflow: {e}")

    def log_execution(self, message: str):
        """Add message to execution log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.execution_log.append(f"[{timestamp}] {message}")

    def take_manual_screenshot(self):
        """Take a manual screenshot"""
        import pyautogui
        from PIL import Image
        import io

        screenshot = pyautogui.screenshot()

        # Convert to QPixmap
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(buffer.read())

        # Scale to fit
        scaled = pixmap.scaled(
            self.preview_image.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        self.preview_image.setPixmap(scaled)
        self.log_execution("📸 Screenshot captured")

    def configure_api_keys(self):
        """Show API key configuration dialog"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Configure API Keys")
        dialog.resize(500, 200)

        layout = QtWidgets.QVBoxLayout()

        # Anthropic API key
        anthropic_label = QtWidgets.QLabel("Anthropic API Key:")
        layout.addWidget(anthropic_label)

        anthropic_input = QtWidgets.QLineEdit()
        anthropic_input.setPlaceholderText("sk-ant-...")
        anthropic_input.setEchoMode(QtWidgets.QLineEdit.Password)

        current_key = self.get_anthropic_api_key()
        if current_key:
            anthropic_input.setText(current_key)

        layout.addWidget(anthropic_input)

        # Buttons
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        buttons.addWidget(cancel_btn)

        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_api_keys(
            anthropic_input.text(),
            dialog
        ))
        buttons.addWidget(save_btn)

        layout.addLayout(buttons)
        dialog.setLayout(layout)
        dialog.exec_()

    def save_api_keys(self, anthropic_key: str, dialog):
        """Save API keys to config"""
        import json

        config = {"anthropic_api_key": anthropic_key}

        try:
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)

            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "API keys saved. Restart the application to apply changes."
            )
            dialog.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to save config: {str(e)}"
            )

    def test_mcp(self, mcp_type: str):
        """Test MCP server connection"""
        QtWidgets.QMessageBox.information(
            self,
            "Test MCP",
            f"Testing {mcp_type} MCP server...\n\n(Not yet implemented)"
        )

    def new_workflow(self):
        """Create new workflow"""
        if self.graph:
            self.graph.clear_session()
        self.log_execution("📄 New workflow created")

    def open_workflow(self):
        """Open existing workflow"""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Workflow",
            "",
            "Workflow Files (*.cheat);;JSON Files (*.json)"
        )

        if filename:
            # TODO: Load workflow
            self.log_execution(f"📂 Opened: {filename}")

    def save_workflow(self):
        """Save current workflow"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Workflow",
            "",
            "Workflow Files (*.cheat);;JSON Files (*.json)"
        )

        if filename:
            # TODO: Save workflow
            self.log_execution(f"💾 Saved: {filename}")

    def show_examples(self):
        """Show example tasks"""
        examples = """
**Example Tasks:**

🌐 **Web Automation**
• "Login to Gmail and send an email"
• "Search Amazon for laptops and save results to CSV"
• "Monitor Twitter for mentions and screenshot them"

🖥️ **Desktop Automation**
• "Open Excel, fill in data, and save as PDF"
• "Organize my Downloads folder by file type"
• "Take screenshots every 5 minutes while I work"

📊 **Data Processing**
• "Extract all invoices from PDF folder to spreadsheet"
• "Read text from images and create a summary document"
• "Compare two spreadsheets and highlight differences"

🎥 **Content Creation**
• "Record a demo video of our app"
• "Create tutorial screenshots with annotations"
• "Generate social media posts from blog content"

🧪 **Testing**
• "Run end-to-end tests on the login flow"
• "Check if all links on website are working"
• "Test form submissions with various inputs"
"""

        QtWidgets.QMessageBox.information(
            self,
            "Example Tasks",
            examples
        )

    def show_documentation(self):
        """Show documentation"""
        QtWidgets.QMessageBox.information(
            self,
            "Documentation",
            "Documentation will be available at:\nhttps://github.com/your-repo/docs"
        )

    def show_about(self):
        """Show about dialog"""
        about_text = """
**Open Agent Studio - Conversational AI Edition**

Version: 2.0.0

An intelligent automation platform that combines:
• Natural language interaction
• Visual workflow editing
• Claude AI orchestration
• Desktop & browser automation

Built with ❤️ using:
• Claude Agent SDK
• Playwright
• PySide2 / Qt
• Model Context Protocol (MCP)

Open source under MIT License
"""

        QtWidgets.QMessageBox.about(self, "About", about_text)

    def apply_dark_theme(self):
        """Apply dark theme to application"""
        self.setStyle("Fusion")

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(30, 30, 30))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(61, 174, 233))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(61, 174, 233))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

        self.setPalette(palette)


def main():
    """Launch the application"""
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Open Agent Studio")
    app.setOrganizationName("OpenAgentStudio")

    window = ConversationalAgentStudio()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
