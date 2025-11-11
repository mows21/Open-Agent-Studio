#!/usr/bin/env python3
"""
Chat Interface for Open Agent Studio
Allows users to describe tasks in natural language
"""

from PySide2 import QtWidgets, QtCore, QtGui
import json
from datetime import datetime


class ChatMessage:
    """Represents a single chat message"""

    def __init__(self, role: str, content: str, timestamp=None):
        self.role = role  # 'user', 'assistant', 'system', 'tool'
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = {}


class ChatWidget(QtWidgets.QWidget):
    """Chat interface widget for conversational automation"""

    # Signals
    message_sent = QtCore.Signal(str)  # User sent a message
    task_started = QtCore.Signal(dict)  # Agent started a task
    task_completed = QtCore.Signal(dict)  # Agent completed task
    workflow_generated = QtCore.Signal(dict)  # Agent generated workflow

    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self.is_agent_thinking = False
        self.setup_ui()

    def setup_ui(self):
        """Build the chat interface"""
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QtWidgets.QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3daee9, stop:1 #2d8ec5);
                padding: 12px;
                border-radius: 0px;
            }
        """)
        header_layout = QtWidgets.QHBoxLayout()

        title = QtWidgets.QLabel("🤖 AI Assistant")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Status indicator
        self.status_label = QtWidgets.QLabel("● Ready")
        self.status_label.setStyleSheet("color: #2ecc71; font-size: 12px;")
        header_layout.addWidget(self.status_label)

        # Clear chat button
        clear_btn = QtWidgets.QPushButton("🗑")
        clear_btn.setFixedSize(30, 30)
        clear_btn.setToolTip("Clear chat history")
        clear_btn.clicked.connect(self.clear_chat)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(clear_btn)

        header.setLayout(header_layout)
        layout.addWidget(header)

        # Chat messages area
        self.messages_area = QtWidgets.QScrollArea()
        self.messages_area.setWidgetResizable(True)
        self.messages_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #1e1e1e;
            }
        """)

        self.messages_container = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout()
        self.messages_layout.setAlignment(QtCore.Qt.AlignTop)
        self.messages_layout.setSpacing(10)
        self.messages_container.setLayout(self.messages_layout)

        self.messages_area.setWidget(self.messages_container)
        layout.addWidget(self.messages_area, stretch=1)

        # Quick actions (example tasks)
        quick_actions_label = QtWidgets.QLabel("Quick Actions:")
        quick_actions_label.setStyleSheet("color: #abb2bf; font-size: 11px; padding: 5px;")
        layout.addWidget(quick_actions_label)

        quick_actions = QtWidgets.QHBoxLayout()
        quick_actions.setSpacing(5)

        examples = [
            "📧 Automate email replies",
            "🎥 Create demo video",
            "📊 Extract data from PDFs",
            "🧪 Run E2E tests"
        ]

        for example in examples:
            btn = QtWidgets.QPushButton(example)
            btn.setStyleSheet("""
                QPushButton {
                    background: #2d2d2d;
                    border: 1px solid #3daee9;
                    color: #abb2bf;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: #3daee9;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, text=example: self.send_quick_action(text))
            quick_actions.addWidget(btn)

        layout.addLayout(quick_actions)

        # Input area
        input_container = QtWidgets.QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background: #2d2d2d;
                border-top: 1px solid #3daee9;
                padding: 10px;
            }
        """)
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.input_field = QtWidgets.QTextEdit()
        self.input_field.setPlaceholderText("Describe the task you want to automate... (Shift+Enter to send)")
        self.input_field.setMaximumHeight(100)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3daee9;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        self.input_field.installEventFilter(self)
        input_layout.addWidget(self.input_field, stretch=1)

        # Send button
        self.send_btn = QtWidgets.QPushButton("Send")
        self.send_btn.setFixedSize(80, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #3daee9;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #5ec7ff;
            }
            QPushButton:pressed {
                background: #2d8ec5;
            }
            QPushButton:disabled {
                background: #4a4a4a;
                color: #7a7a7a;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        input_container.setLayout(input_layout)
        layout.addWidget(input_container)

        self.setLayout(layout)

        # Add welcome message
        self.add_welcome_message()

    def add_welcome_message(self):
        """Add initial welcome message"""
        welcome_text = """👋 **Welcome to Open Agent Studio!**

I can help you automate any desktop or browser task. Just describe what you want to do, and I'll:

1. **Understand** your task
2. **Execute** it step-by-step
3. **Debug** any issues automatically
4. **Save** the workflow for reuse

**Examples:**
• "Check my Gmail and reply to urgent emails"
• "Create a demo video of our product"
• "Extract data from these invoices into a spreadsheet"
• "Run end-to-end tests on the website"

What would you like to automate?"""

        self.add_message("assistant", welcome_text)

    def eventFilter(self, obj, event):
        """Handle keyboard shortcuts"""
        if obj == self.input_field and event.type() == QtCore.QEvent.KeyPress:
            # Shift+Enter to send
            if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def send_message(self):
        """Send user message"""
        text = self.input_field.toPlainText().strip()

        if not text:
            return

        if self.is_agent_thinking:
            QtWidgets.QMessageBox.warning(
                self,
                "Agent Busy",
                "The agent is currently working on a task. Please wait..."
            )
            return

        # Add user message
        self.add_message("user", text)

        # Clear input
        self.input_field.clear()

        # Emit signal for processing
        self.message_sent.emit(text)

    def send_quick_action(self, text):
        """Send a quick action example"""
        # Remove emoji prefix
        clean_text = text.split(" ", 1)[1] if " " in text else text
        self.input_field.setPlainText(clean_text)
        self.send_message()

    def add_message(self, role: str, content: str, metadata: dict = None):
        """Add message to chat"""
        message = ChatMessage(role, content)
        if metadata:
            message.metadata = metadata
        self.messages.append(message)

        # Create message widget
        message_widget = self.create_message_widget(message)
        self.messages_layout.addWidget(message_widget)

        # Scroll to bottom
        QtCore.QTimer.singleShot(100, self.scroll_to_bottom)

    def create_message_widget(self, message: ChatMessage) -> QtWidgets.QWidget:
        """Create visual widget for a message"""
        widget = QtWidgets.QWidget()

        # Determine styling based on role
        if message.role == "user":
            bg_color = "#3daee9"
            text_color = "white"
            alignment = QtCore.Qt.AlignRight
            avatar = "👤"
        elif message.role == "assistant":
            bg_color = "#2d2d2d"
            text_color = "#d4d4d4"
            alignment = QtCore.Qt.AlignLeft
            avatar = "🤖"
        elif message.role == "system":
            bg_color = "#f39c12"
            text_color = "white"
            alignment = QtCore.Qt.AlignCenter
            avatar = "ℹ️"
        elif message.role == "tool":
            bg_color = "#2ecc71"
            text_color = "white"
            alignment = QtCore.Qt.AlignLeft
            avatar = "🔧"
        else:
            bg_color = "#2d2d2d"
            text_color = "#d4d4d4"
            alignment = QtCore.Qt.AlignLeft
            avatar = "●"

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        if message.role != "user":
            layout.addStretch()

        # Message bubble
        bubble = QtWidgets.QFrame()
        bubble.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border-radius: 10px;
                padding: 10px;
                max-width: 600px;
            }}
        """)

        bubble_layout = QtWidgets.QVBoxLayout()
        bubble_layout.setSpacing(5)

        # Avatar + Role
        header = QtWidgets.QLabel(f"{avatar} {message.role.capitalize()}")
        header.setStyleSheet(f"color: {text_color}; font-size: 10px; font-weight: bold;")
        bubble_layout.addWidget(header)

        # Content (support markdown-like formatting)
        content_label = QtWidgets.QLabel()
        content_label.setTextFormat(QtCore.Qt.MarkdownText)
        content_label.setText(message.content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"color: {text_color}; font-size: 13px;")
        content_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        bubble_layout.addWidget(content_label)

        # Timestamp
        timestamp = QtWidgets.QLabel(message.timestamp.strftime("%H:%M:%S"))
        timestamp.setStyleSheet(f"color: {text_color}; font-size: 9px; opacity: 0.7;")
        timestamp.setAlignment(QtCore.Qt.AlignRight)
        bubble_layout.addWidget(timestamp)

        # Action buttons (for assistant messages with workflows)
        if message.role == "assistant" and message.metadata.get("has_workflow"):
            actions = QtWidgets.QHBoxLayout()

            view_workflow_btn = QtWidgets.QPushButton("📊 View Workflow")
            view_workflow_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    border: 1px solid white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.2);
                }
            """)
            view_workflow_btn.clicked.connect(
                lambda: self.workflow_generated.emit(message.metadata.get("workflow"))
            )
            actions.addWidget(view_workflow_btn)

            run_again_btn = QtWidgets.QPushButton("▶ Run Again")
            run_again_btn.setStyleSheet("""
                QPushButton {
                    background: #2ecc71;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: #27ae60;
                }
            """)
            actions.addWidget(run_again_btn)

            bubble_layout.addLayout(actions)

        bubble.setLayout(bubble_layout)
        layout.addWidget(bubble)

        if message.role == "user":
            layout.addStretch()

        widget.setLayout(layout)
        return widget

    def set_agent_thinking(self, thinking: bool, status_text: str = None):
        """Update agent thinking status"""
        self.is_agent_thinking = thinking
        self.send_btn.setEnabled(not thinking)

        if thinking:
            self.status_label.setText("● " + (status_text or "Thinking..."))
            self.status_label.setStyleSheet("color: #f39c12; font-size: 12px;")

            # Add thinking indicator message
            self.add_thinking_indicator()
        else:
            self.status_label.setText("● Ready")
            self.status_label.setStyleSheet("color: #2ecc71; font-size: 12px;")

            # Remove thinking indicator
            self.remove_thinking_indicator()

    def add_thinking_indicator(self):
        """Add animated thinking indicator"""
        self.thinking_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        # Animated dots
        self.thinking_label = QtWidgets.QLabel("🤖 Thinking")
        self.thinking_label.setStyleSheet("color: #abb2bf; font-size: 12px; font-style: italic;")
        layout.addWidget(self.thinking_label)

        self.thinking_dots = QtWidgets.QLabel(".")
        self.thinking_dots.setStyleSheet("color: #abb2bf; font-size: 12px;")
        layout.addWidget(self.thinking_dots)

        layout.addStretch()

        self.thinking_widget.setLayout(layout)
        self.messages_layout.addWidget(self.thinking_widget)

        # Animate dots
        self.thinking_timer = QtCore.QTimer()
        self.thinking_timer.timeout.connect(self._animate_thinking)
        self.thinking_timer.start(500)

    def _animate_thinking(self):
        """Animate thinking dots"""
        current = self.thinking_dots.text()
        if len(current) >= 3:
            self.thinking_dots.setText(".")
        else:
            self.thinking_dots.setText(current + ".")

    def remove_thinking_indicator(self):
        """Remove thinking indicator"""
        if hasattr(self, 'thinking_widget'):
            self.messages_layout.removeWidget(self.thinking_widget)
            self.thinking_widget.deleteLater()

        if hasattr(self, 'thinking_timer'):
            self.thinking_timer.stop()

    def add_task_update(self, step: str, status: str = "running"):
        """Add task execution update"""
        icons = {
            "running": "⟳",
            "completed": "✓",
            "error": "✗"
        }

        colors = {
            "running": "#f39c12",
            "completed": "#2ecc71",
            "error": "#e74c3c"
        }

        icon = icons.get(status, "●")
        color = colors.get(status, "#abb2bf")

        update_text = f"{icon} {step}"

        # Add as system message
        self.add_message("system", update_text)

    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.messages_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_chat(self):
        """Clear all messages"""
        # Remove all message widgets
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.messages.clear()
        self.add_welcome_message()


if __name__ == "__main__":
    """Test the chat widget"""
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Apply dark theme
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(30, 30, 30))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    app.setPalette(palette)

    # Create window
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Chat Interface Test")
    window.resize(500, 700)

    chat = ChatWidget()

    # Test message handlers
    def on_message(text):
        print(f"User sent: {text}")
        chat.set_agent_thinking(True, "Processing task...")

        # Simulate task
        QtCore.QTimer.singleShot(2000, lambda: chat.add_task_update("Taking screenshot", "completed"))
        QtCore.QTimer.singleShot(3000, lambda: chat.add_task_update("Finding element", "running"))
        QtCore.QTimer.singleShot(4000, lambda: chat.add_task_update("Clicking button", "completed"))
        QtCore.QTimer.singleShot(5000, lambda: finish_task())

    def finish_task():
        chat.set_agent_thinking(False)
        chat.add_message("assistant", "✓ Task completed successfully!\n\nI've saved the workflow as 'Gmail Automation'. You can run it anytime.", {"has_workflow": True, "workflow": {}})

    chat.message_sent.connect(on_message)

    window.setCentralWidget(chat)
    window.show()

    sys.exit(app.exec_())
