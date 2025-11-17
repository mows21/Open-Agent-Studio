# 🎬 AI Tutorial Creation Agent - Setup Guide

Complete setup guide for the AI Tutorial Creation Agent with Live CV Observer.

---

## 📋 Prerequisites

- Python 3.9 or higher
- FFmpeg (for video processing)
- Anthropic API key (required)
- ElevenLabs API key (optional, for premium TTS)

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
cd Open-Agent-Studio

# Install tutorial agent requirements
pip install -r tutorial_agent/requirements.txt

# For YOLO support (optional, for live CV)
pip install ultralytics torch
```

### Step 2: Install FFmpeg

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Verify: `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Step 3: Set API Keys

```bash
# Required: Anthropic Claude API
export ANTHROPIC_API_KEY='sk-ant-...'

# Optional: Premium TTS
export ELEVENLABS_API_KEY='...'
```

Or create `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
```

### Step 4: Test Installation

```python
# Quick test
python examples/tutorial_agent_examples.py
```

✅ **Done!** You're ready to create tutorials.

---

## 🎯 Your First Tutorial

### Option 1: Interactive CLI

```bash
python -m tutorial_agent.orchestrator
```

Follow the prompts:
1. Enter tutorial topic
2. Select target audience
3. Choose execution mode
4. Watch as AI creates your tutorial!

### Option 2: Python Script

```python
import asyncio
from tutorial_agent import TutorialCreationAgent

async def main():
    agent = TutorialCreationAgent()

    video = await agent.create_tutorial(
        topic="Python Decorators Explained",
        target_audience="intermediate",
        auto_execute=True
    )

    print(f"Tutorial ready: {video}")

asyncio.run(main())
```

---

## 🔴 Enable Live CV Observer (Self-Aware Mode)

The **Live CV Observer** is the "side quest" - a self-aware automation system!

### What It Does

- 👁️ Watches screen in real-time
- 🧠 Understands context using Claude Vision
- 🎯 Detects UI elements with YOLO
- 💡 Suggests next actions
- 🔧 Self-debugs failures
- 📊 Learns patterns over time

### Setup

```bash
# Install YOLO for UI detection
pip install ultralytics torch

# First run downloads YOLO model (~6MB)
```

### Usage

```python
agent = TutorialCreationAgent(
    enable_live_cv=True  # 🔴 Enable self-aware mode
)

video = await agent.create_tutorial(
    topic="Docker Basics",
    auto_execute=True
)

# View learning summary
summary = agent.live_observer.get_learning_summary()
print(f"AI made {summary['total_observations']} observations")
print(f"Learned {summary['patterns_learned']} patterns")
```

---

## 📁 Project Structure

```
Open-Agent-Studio/
├── tutorial_agent/              # Main agent code
│   ├── __init__.py
│   ├── planner.py              # Claude tutorial planning
│   ├── recorder.py             # Screen recording (mss/dxcam)
│   ├── executor.py             # Demo execution
│   ├── narrator.py             # TTS narration
│   ├── editor.py               # Video editing (MoviePy)
│   ├── orchestrator.py         # Main coordinator
│   ├── live_cv_observer.py     # 🔴 Live CV system
│   ├── requirements.txt
│   └── README.md
├── examples/
│   └── tutorial_agent_examples.py  # 8 comprehensive examples
├── output/                     # Generated tutorials
│   └── [tutorial_name]/
│       ├── *.mp4              # Final video
│       ├── *_thumbnail.jpg
│       ├── tutorial_plan.json
│       ├── metadata.json
│       └── recordings/        # Individual clips
└── assets/                     # Optional templates
    ├── intro_template.mp4
    ├── outro_template.mp4
    └── background_music.mp3
```

---

## 🎨 Customization

### Custom Intro/Outro Videos

```bash
# Add your branded intro/outro
mkdir -p assets
cp your_intro.mp4 assets/intro_template.mp4
cp your_outro.mp4 assets/outro_template.mp4
```

### Custom Background Music

```bash
cp your_music.mp3 assets/background_music.mp3
```

The agent will automatically use these if present!

### Custom YOLO Model

Train on your specific UI elements:

```python
observer = LiveCVObserver(
    claude_api_key="...",
    yolo_model_path="models/my_ui_detector.pt"
)
```

### Custom Voice (ElevenLabs)

```python
# In narrator.py, line ~67
voice=Voice(
    voice_id="your-custom-voice-id",  # Get from elevenlabs.io
    settings=VoiceSettings(
        stability=0.75,
        similarity_boost=0.85,
        style=0.2  # Adjust for personality
    )
)
```

---

## 🧪 Testing

### Run All Examples

```bash
python examples/tutorial_agent_examples.py
```

Choose from 8 examples:
1. Simple tutorial
2. Manual recording
3. Self-aware mode
4. Custom config
5. Live CV standalone
6. Self-debugging demo
7. Batch creation
8. Integration example

### Test Individual Components

```bash
# Test screen recorder
python -m tutorial_agent.recorder

# Test live CV observer
python -m tutorial_agent.live_cv_observer

# Test narrator
python -m tutorial_agent.narrator

# Test video editor
python -m tutorial_agent.editor
```

---

## 🔧 Troubleshooting

### "FFmpeg not found"

```bash
# Test FFmpeg
ffmpeg -version

# If not found:
# Windows: Add ffmpeg.exe to PATH
# Mac: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### "ANTHROPIC_API_KEY not set"

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Set permanently (add to ~/.bashrc or ~/.zshrc)
export ANTHROPIC_API_KEY='sk-ant-...'
```

### "MoviePy import error"

```bash
pip uninstall moviepy
pip install moviepy==2.0.0
pip install imageio-ffmpeg
```

### "YOLO model download fails"

```python
# Manual download
from ultralytics import YOLO
model = YOLO('yolo11n.pt')  # Downloads to ~/.ultralytics/
```

### "No audio in video"

```bash
# Install TTS dependencies
pip install gtts pydub

# For premium quality
pip install elevenlabs
export ELEVENLABS_API_KEY='...'
```

### "Slow screen recording"

```bash
# Windows only - use DXCam (10x faster)
pip install dxcam

# Reduce FPS
# In code: await recorder.record_clip(name="test", fps=15)
```

---

## 🚀 Performance Optimization

### Speed Up Tutorial Creation

1. **Use DXCam** (Windows only) - 10x faster screen capture
2. **Reduce FPS** - Use 15-20 FPS instead of 30
3. **Smaller resolution** - Record at 720p instead of 1080p
4. **Skip live CV** - Disable for faster execution
5. **Use gTTS** - Faster than ElevenLabs (but lower quality)

### Reduce Video File Size

```python
# In editor.py
final_video.write_videofile(
    output_path,
    preset='fast',      # ultrafast → fast → medium
    crf=23,            # 18 (high) → 28 (low quality)
    bitrate='2000k'    # Lower bitrate
)
```

### Optimize YOLO Inference

```python
# Use smaller YOLO model
model = YOLO('yolo11n.pt')  # nano (fastest)
# vs
model = YOLO('yolo11s.pt')  # small
model = YOLO('yolo11m.pt')  # medium
```

---

## 📊 Advanced: Learning & Analytics

### View AI Learning Progress

```python
# After tutorial creation with live_cv enabled
summary = agent.live_observer.get_learning_summary()

print(f"Observations: {summary['total_observations']}")
print(f"Patterns learned: {summary['patterns_learned']}")

# Top patterns
for pattern, data in summary['top_patterns']:
    print(f"{pattern}: seen {data['count']}x")
    print(f"  First seen: {data['first_seen']}")
```

### Export Learning Data

```python
import json

# Export patterns database
with open('ai_learning.json', 'w') as f:
    json.dump(agent.live_observer.pattern_db, f, indent=2, default=str)
```

### Visualize Observations

```python
import matplotlib.pyplot as plt

# Plot observations over time
observations = agent.live_observer.observation_history

timestamps = [obs.timestamp for obs in observations]
confidences = [obs.confidence for obs in observations]

plt.plot(timestamps, confidences)
plt.title('AI Confidence Over Time')
plt.xlabel('Time')
plt.ylabel('Confidence')
plt.savefig('ai_confidence.png')
```

---

## 🔗 Integration with Open Agent Studio

### As MCP Server

Create `/mcp_servers/tutorial_creation_mcp.py`:

```python
from mcp.server import Server
from tutorial_agent import TutorialCreationAgent

# Expose tutorial creation as MCP tools
# See examples/tutorial_agent_examples.py for full code
```

### As Node Graph Nodes

Add tutorial creation nodes to NodeGraphQt:

1. **Plan Node** - Generate tutorial plan
2. **Record Node** - Record screen
3. **Narrate Node** - Generate narration
4. **Edit Node** - Compile final video

### With Conversational Agent

```python
# conversational_agent_studio.py integration
from tutorial_agent import TutorialCreationAgent

class ConversationalAgentStudio:
    def setup_tutorial_creation(self):
        self.tutorial_agent = TutorialCreationAgent()

        # Add menu action
        create_tutorial = QtWidgets.QAction("Create Tutorial", self)
        create_tutorial.triggered.connect(self.create_tutorial_dialog)
```

---

## 📚 Next Steps

1. ✅ **Create your first tutorial** - Start with simple topic
2. 🔴 **Try live CV mode** - Experience self-aware automation
3. 🎨 **Customize branding** - Add your intro/outro
4. 📦 **Batch create** - Generate tutorial series
5. 🚀 **Integrate** - Add to your automation workflows

---

## 💡 Tips & Best Practices

### Tutorial Topic Selection

- ✅ Start with **concrete, hands-on topics**
- ✅ Keep scope **narrow and focused**
- ✅ Include **working code examples**
- ❌ Avoid **abstract theory-only** topics

### Recording Quality

- Record at **1920x1080** for best quality
- Use **external mic** for better audio (if manual)
- Close **unnecessary applications** for clean screen
- Use **dark theme** editors (better visibility)

### Narration

- Keep scripts **conversational**, not formal
- Use **short sentences** (easier for TTS)
- Add **pauses** with `wait` commands
- Test narration **before final render**

### Self-Aware Mode

- Enable for **complex workflows** that might fail
- Review **learning summary** after each tutorial
- Use **debug suggestions** when automation breaks
- Perfect for **iterative refinement**

---

## 🎯 Example Workflows

### Workflow 1: Quick Tutorial

```bash
# 1. Plan
python -c "
from tutorial_agent import TutorialPlanner
import asyncio
planner = TutorialPlanner()
asyncio.run(planner.plan_tutorial('Python List Comprehensions'))
"

# 2. Review plan, then create
python -m tutorial_agent.orchestrator "Python List Comprehensions"
```

### Workflow 2: Tutorial Series

Create 10 tutorials on Python basics:

```python
topics = [
    "Variables and Data Types",
    "Control Flow (if/else)",
    "Loops in Python",
    # ... 7 more
]

for topic in topics:
    await agent.create_tutorial(topic, "beginner")
```

### Workflow 3: Debugging Failed Automation

```python
# Tutorial creation failed? Use live CV to debug
observer = LiveCVObserver(...)

# Let it watch while you manually reproduce issue
await observer.start_observing()

# After 30 seconds, ask for debug analysis
# AI will have observed the failure and can suggest fixes
```

---

## 📞 Support

- 📖 **Full Docs**: `tutorial_agent/README.md`
- 💻 **Examples**: `examples/tutorial_agent_examples.py`
- 🐛 **Issues**: GitHub Issues
- 📧 **Email**: rohan@cheatlayer.com

---

**Happy Tutorial Creating! 🎬**

*"The best way to learn is to teach - let AI help you teach better!"*
