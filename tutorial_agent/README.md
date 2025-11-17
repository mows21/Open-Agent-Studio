# 🎬 AI Tutorial Creation Agent

**Automatically create professional software development tutorials** using Claude AI, screen recording, and automated video editing.

---

## 🌟 Features

### Core Capabilities
- 🧠 **AI Planning**: Claude generates comprehensive tutorial outlines
- 🎥 **Auto-Recording**: Automated screen capture during execution
- 🎙️ **AI Narration**: Text-to-speech with professional voices
- ✂️ **Smart Editing**: Automated video assembly with transitions
- 📝 **Subtitles**: Auto-generated captions

### Advanced Features (Side Quest!)
- 👁️ **Live CV Observer**: Self-aware automation that watches itself work
- 🔧 **Self-Debugging**: AI detects failures and suggests fixes
- 📊 **Pattern Learning**: Learns from observations over time
- 💡 **Smart Suggestions**: AI recommends next actions in real-time

---

## 📦 Installation

### 1. Install Python Dependencies

```bash
cd tutorial_agent
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
```bash
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 3. Set Up API Keys

```bash
# Required: Anthropic API key
export ANTHROPIC_API_KEY='your-key-here'

# Optional: ElevenLabs for premium narration
export ELEVENLABS_API_KEY='your-key-here'
```

---

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from tutorial_agent import TutorialCreationAgent

async def create_tutorial():
    agent = TutorialCreationAgent()

    video = await agent.create_tutorial(
        topic="Building a REST API with Flask",
        target_audience="intermediate",
        auto_execute=True  # AI performs demo automatically
    )

    print(f"Tutorial ready: {video}")

asyncio.run(create_tutorial())
```

### Command Line Interface

```bash
# Interactive mode
python -m tutorial_agent.orchestrator

# Direct topic
python -m tutorial_agent.orchestrator "Docker Compose for Beginners"
```

### With Live CV Observer (Self-Aware Mode)

```python
# Enable live computer vision observation
agent = TutorialCreationAgent(
    enable_live_cv=True  # 🔴 AI watches itself work!
)

video = await agent.create_tutorial(
    topic="Git Branching Strategies",
    auto_execute=True
)
```

---

## 🎯 How It Works

### Pipeline Overview

```
1. Planning Phase (Claude AI)
   ├─ Parse tutorial topic
   ├─ Generate step-by-step outline
   ├─ Create demo script
   └─ Plan screen recordings

2. Recording Phase (Computer Use + Screen Capture)
   ├─ Execute demo steps automatically
   ├─ Record screen during execution
   ├─ Live CV observer (optional)
   └─ Capture specific code clips

3. Narration Phase (Claude + TTS)
   ├─ Generate narration script
   ├─ Add timestamps
   ├─ Convert to speech (ElevenLabs or gTTS)
   └─ Generate captions/subtitles

4. Editing Phase (MoviePy + FFmpeg)
   ├─ Concatenate clips
   ├─ Add intro/outro
   ├─ Overlay narration
   ├─ Add transitions
   └─ Export final video
```

---

## 🧠 Live CV Observer (The Side Quest!)

The **Live CV Observer** is a self-aware automation system that:

- 👁️ **Watches** your screen in real-time
- 🎯 **Detects** UI elements using YOLO
- 🧠 **Understands** context using Claude Vision
- 💡 **Suggests** next actions dynamically
- 🔧 **Self-debugs** when things go wrong
- 📊 **Learns** patterns over time

### How to Use

```python
from tutorial_agent.live_cv_observer import LiveCVObserver

observer = LiveCVObserver(
    claude_api_key="your-key",
    observation_interval=2.0  # Observe every 2 seconds
)

# Set up callbacks
async def on_observation(obs):
    print(f"Understanding: {obs.claude_analysis}")
    print(f"Confidence: {obs.confidence}")

async def on_suggestion(action):
    print(f"AI suggests: {action}")

observer.on_observation = on_observation
observer.on_suggestion = on_suggestion

# Start observing
await observer.start_observing()
```

### Self-Debugging Example

```python
# When automation fails, ask AI to debug
debug_result = await observer.debug_failure(
    error_message="Element not found",
    expected_state="Button should be visible",
    actual_screenshot=screenshot
)

print(f"Diagnosis: {debug_result['diagnosis']}")
print(f"Root cause: {debug_result['root_cause']}")

# Get ranked fix suggestions
for fix in debug_result['fixes']:
    print(f"  - {fix['strategy']} ({fix['likelihood']}% success)")
```

---

## 📖 Examples

### Example 1: Python Tutorial

```python
video = await agent.create_tutorial(
    topic="Python Virtual Environments with venv",
    target_audience="beginner",
    max_duration_minutes=8
)
```

### Example 2: Web Development

```python
video = await agent.create_tutorial(
    topic="Build a Todo App with React Hooks",
    target_audience="intermediate",
    max_duration_minutes=15
)
```

### Example 3: DevOps

```python
video = await agent.create_tutorial(
    topic="Kubernetes Deployment with Helm Charts",
    target_audience="advanced",
    max_duration_minutes=20
)
```

### Example 4: Manual Recording Mode

```python
# You control the demo, AI handles everything else
video = await agent.create_tutorial(
    topic="Advanced Git Workflows",
    auto_execute=False  # Manual mode
)

# Agent will prompt you when to record each step
```

---

## 🎨 Customization

### Custom Intro/Outro

Place video files in `assets/`:
- `intro_template.mp4` - Custom intro
- `outro_template.mp4` - Custom outro
- `background_music.mp3` - Background music

### Custom YOLO Model

Train your own UI element detector:

```python
observer = LiveCVObserver(
    claude_api_key="your-key",
    yolo_model_path="path/to/your/model.pt"
)
```

### Custom Voices

ElevenLabs supports many voices:

```python
# In narrator.py, change voice ID
voice=Voice(
    voice_id="your-voice-id",  # Browse at elevenlabs.io
    settings=VoiceSettings(
        stability=0.75,
        similarity_boost=0.85
    )
)
```

---

## 📁 Output Structure

```
output/
└── Building_REST_API_with_Flask_20250116_143022/
    ├── Building_REST_API_with_Flask.mp4    # Final video
    ├── Building_REST_API_with_Flask_thumbnail.jpg
    ├── tutorial_plan.json                   # Original plan
    ├── metadata.json                        # Tutorial metadata
    ├── learning_summary.json                # CV learning (if enabled)
    └── recordings/
        ├── step_1_Setup_Flask.mp4
        ├── step_2_Create_Routes.mp4
        └── step_3_Test_API.mp4
```

---

## 🔧 Troubleshooting

### FFmpeg Not Found

```bash
# Test FFmpeg installation
ffmpeg -version

# If not found, install:
# Windows: Download from ffmpeg.org
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### MoviePy Import Error

```bash
pip install moviepy==2.0.0
pip install imageio-ffmpeg
```

### YOLO Model Download

```python
# First run downloads YOLO model automatically
# If fails, manually download:
from ultralytics import YOLO
model = YOLO('yolo11n.pt')  # Downloads to ~/.ultralytics/
```

### No Audio in Video

```bash
# Install audio dependencies
pip install pydub
pip install gtts  # For free TTS

# For premium TTS
pip install elevenlabs
export ELEVENLABS_API_KEY='your-key'
```

---

## 🎯 Performance Tips

### Speed Up Recording

```python
# Use faster screen capture (Windows only)
pip install dxcam

# Reduce FPS for smaller files
await recorder.record_clip(name="test", fps=15)  # Default: 30
```

### Reduce Video File Size

```python
# In editor.py, adjust quality
final_video.write_videofile(
    output_path,
    preset='ultrafast',  # Change to 'fast' or 'medium'
    crf=23  # Higher = smaller file (18-28 recommended)
)
```

### Faster Observations

```python
# Reduce observation frequency
observer = LiveCVObserver(
    observation_interval=5.0  # Every 5 seconds instead of 2
)
```

---

## 🤝 Integration with Open Agent Studio

### Use Tutorial Agent as MCP Server

```python
# mcp_servers/tutorial_creation_mcp.py
from mcp.server import Server
from tutorial_agent import TutorialCreationAgent

class TutorialCreationMCP:
    def __init__(self):
        self.server = Server("tutorial-creation")
        self.agent = TutorialCreationAgent()
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="create_tutorial",
                    description="Create video tutorial from topic",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "audience": {"type": "string"}
                        }
                    }
                )
            ]
```

### Use with Node Graph

Create nodes for tutorial creation steps in Open Agent Studio's visual editor.

---

## 📊 Advanced: Learning from Observations

```python
# Get patterns learned by CV observer
summary = observer.get_learning_summary()

print(f"Observations: {summary['total_observations']}")
print(f"Patterns learned: {summary['patterns_learned']}")

for pattern, data in summary['top_patterns']:
    print(f"  - {pattern}: seen {data['count']}x")
```

---

## 🚀 Roadmap

- [ ] Multi-language support (i18n)
- [ ] Auto-upload to YouTube
- [ ] Template library (common tutorial types)
- [ ] Live streaming mode
- [ ] Multi-camera support
- [ ] Advanced editing (zoom, pan, highlights)
- [ ] Voice cloning integration
- [ ] Collaborative tutorial creation

---

## 📄 License

Part of Open Agent Studio - Open Source

---

## 🙏 Credits

Built with:
- Claude AI (Anthropic) - Planning & narration
- YOLO (Ultralytics) - Computer vision
- MoviePy - Video editing
- ElevenLabs - Premium TTS
- FFmpeg - Video processing

---

## 📞 Support

- 📧 Email: rohan@cheatlayer.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

**Happy tutorial creating! 🎬**
