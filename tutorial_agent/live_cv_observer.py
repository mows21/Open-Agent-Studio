#!/usr/bin/env python3
"""
Live Computer Vision Observer
Real-time screen analysis with YOLO + Claude Vision for self-aware automation

This is the "side quest" - an AI agent that watches itself work!
"""

import asyncio
import numpy as np
import cv2
import base64
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import anthropic
import json


@dataclass
class ObservationResult:
    """Result from observing screen"""
    timestamp: datetime
    screenshot_b64: str
    detected_elements: List[Dict]  # YOLO detections
    claude_analysis: str  # Claude's understanding
    suggested_next_action: Optional[str]
    confidence: float
    debug_suggestions: List[str]


class LiveCVObserver:
    """
    Self-aware automation observer

    Watches screen in real-time, understands context, suggests next steps,
    and debugs failures automatically.
    """

    def __init__(
        self,
        claude_api_key: str,
        yolo_model_path: Optional[str] = None,
        observation_interval: float = 1.0  # Observe every N seconds
    ):
        self.claude = anthropic.Anthropic(api_key=claude_api_key)
        self.observation_interval = observation_interval
        self.observing = False

        # Load YOLO for UI element detection
        self.yolo_model = self._load_yolo_model(yolo_model_path)

        # Observation history for learning
        self.observation_history: List[ObservationResult] = []
        self.pattern_db = {}  # Learned patterns

        # Callbacks
        self.on_observation: Optional[Callable] = None
        self.on_suggestion: Optional[Callable] = None
        self.on_error_detected: Optional[Callable] = None

    def _load_yolo_model(self, model_path: Optional[str]):
        """Load YOLO model for UI element detection"""
        try:
            from ultralytics import YOLO

            if model_path and Path(model_path).exists():
                print(f"✓ Loading custom YOLO model: {model_path}")
                return YOLO(model_path)
            else:
                # Use pre-trained YOLO11 or YOLO26 when available
                print("✓ Loading YOLO11n (nano - fast for real-time)")
                return YOLO('yolo11n.pt')

        except ImportError:
            print("⚠️  ultralytics not installed. UI detection disabled.")
            print("   Install with: pip install ultralytics")
            return None

    async def start_observing(self, mss_instance=None):
        """Start continuous observation loop"""

        if mss_instance is None:
            import mss
            mss_instance = mss.mss()

        print("\n👁️  Starting Live CV Observer...")
        print(f"   Observation interval: {self.observation_interval}s")

        self.observing = True

        try:
            while self.observing:
                # Capture screen
                screenshot = self._capture_screen(mss_instance)

                # Observe and analyze
                observation = await self._observe_and_analyze(screenshot)

                # Store in history
                self.observation_history.append(observation)

                # Trigger callbacks
                if self.on_observation:
                    await self.on_observation(observation)

                if observation.suggested_next_action and self.on_suggestion:
                    await self.on_suggestion(observation.suggested_next_action)

                if observation.debug_suggestions and self.on_error_detected:
                    await self.on_error_detected(observation.debug_suggestions)

                # Wait before next observation
                await asyncio.sleep(self.observation_interval)

        except KeyboardInterrupt:
            print("\n⏹️  Observation stopped by user")

        finally:
            self.observing = False

    def stop_observing(self):
        """Stop observation loop"""
        self.observing = False

    def _capture_screen(self, mss_instance):
        """Capture current screen state"""
        monitor = mss_instance.monitors[1]
        screenshot = mss_instance.grab(monitor)
        return np.array(screenshot)[:, :, :3]  # Remove alpha channel

    async def _observe_and_analyze(self, screenshot: np.ndarray) -> ObservationResult:
        """
        Main observation logic:
        1. Detect UI elements with YOLO
        2. Understand context with Claude Vision
        3. Suggest next action
        4. Detect errors/issues
        """

        timestamp = datetime.now()

        # 1. Detect UI elements with YOLO
        detected_elements = []
        if self.yolo_model:
            detected_elements = self._detect_ui_elements(screenshot)

        # 2. Convert screenshot to base64 for Claude
        screenshot_b64 = self._screenshot_to_base64(screenshot)

        # 3. Ask Claude to understand context and suggest next action
        analysis = await self._claude_analyze_screen(
            screenshot_b64,
            detected_elements
        )

        return ObservationResult(
            timestamp=timestamp,
            screenshot_b64=screenshot_b64,
            detected_elements=detected_elements,
            claude_analysis=analysis.get("understanding", ""),
            suggested_next_action=analysis.get("next_action"),
            confidence=analysis.get("confidence", 0.0),
            debug_suggestions=analysis.get("debug_suggestions", [])
        )

    def _detect_ui_elements(self, screenshot: np.ndarray) -> List[Dict]:
        """Detect UI elements using YOLO"""

        if not self.yolo_model:
            return []

        try:
            # Run YOLO inference
            results = self.yolo_model(screenshot, verbose=False)[0]

            elements = []
            for box in results.boxes:
                elements.append({
                    "type": results.names[int(box.cls[0])],
                    "bbox": box.xyxy[0].cpu().numpy().tolist(),
                    "confidence": float(box.conf[0]),
                    "center": [
                        int((box.xyxy[0][0] + box.xyxy[0][2]) / 2),
                        int((box.xyxy[0][1] + box.xyxy[0][3]) / 2)
                    ]
                })

            return elements

        except Exception as e:
            print(f"⚠️  YOLO detection error: {e}")
            return []

    def _screenshot_to_base64(self, screenshot: np.ndarray) -> str:
        """Convert screenshot to base64 for Claude"""

        # Resize for efficiency (Claude works well with 1024x1024)
        height, width = screenshot.shape[:2]
        max_size = 1024

        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            screenshot = cv2.resize(screenshot, (new_width, new_height))

        # Encode as PNG
        _, buffer = cv2.imencode('.png', screenshot)
        return base64.b64encode(buffer).decode('utf-8')

    async def _claude_analyze_screen(
        self,
        screenshot_b64: str,
        detected_elements: List[Dict]
    ) -> Dict:
        """
        Ask Claude to analyze screen and suggest next action

        This is the "brain" of the self-aware automation!
        """

        # Build context from detected elements
        elements_context = ""
        if detected_elements:
            elements_context = "\n\nDetected UI elements (YOLO):\n"
            for elem in detected_elements[:10]:  # Top 10
                elements_context += f"- {elem['type']} at ({elem['center'][0]}, {elem['center'][1]}) [confidence: {elem['confidence']:.2f}]\n"

        # Include recent observation history for context
        history_context = ""
        if len(self.observation_history) > 0:
            history_context = "\n\nRecent observations (last 3):\n"
            for obs in self.observation_history[-3:]:
                history_context += f"- {obs.timestamp.strftime('%H:%M:%S')}: {obs.claude_analysis[:100]}...\n"

        prompt = f"""You are an AI observing a computer screen in real-time. Your job is to:
1. Understand what's currently happening
2. Detect if anything looks wrong (errors, unexpected states)
3. Suggest the next logical action
4. Provide debugging advice if needed

{elements_context}
{history_context}

Analyze this screenshot and return JSON:
{{
  "understanding": "What's currently happening on screen (be specific)",
  "state": "idle|working|error|loading|complete",
  "next_action": "Suggested next action (or null if none needed)",
  "confidence": 0.95,
  "issues_detected": ["list of potential problems"],
  "debug_suggestions": ["suggestions if error detected"],
  "patterns_observed": ["recurring patterns you notice"]
}}

Be concise but specific. Focus on actionable insights."""

        try:
            response = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            # Parse response
            content = response.content[0].text.strip()

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)

            # Learn patterns
            if "patterns_observed" in analysis:
                self._learn_patterns(analysis["patterns_observed"])

            return analysis

        except Exception as e:
            print(f"⚠️  Claude analysis error: {e}")
            return {
                "understanding": "Analysis failed",
                "state": "unknown",
                "next_action": None,
                "confidence": 0.0,
                "issues_detected": [],
                "debug_suggestions": []
            }

    def _learn_patterns(self, patterns: List[str]):
        """Learn patterns over time for smarter suggestions"""

        for pattern in patterns:
            if pattern not in self.pattern_db:
                self.pattern_db[pattern] = {
                    "first_seen": datetime.now(),
                    "count": 1,
                    "contexts": []
                }
            else:
                self.pattern_db[pattern]["count"] += 1

    async def debug_failure(
        self,
        error_message: str,
        expected_state: str,
        actual_screenshot: np.ndarray
    ) -> Dict:
        """
        Self-debugging: Analyze failure and suggest fixes

        This is called when automation fails
        """

        print(f"\n🔧 Self-Debugging Mode Activated")
        print(f"   Error: {error_message}")

        screenshot_b64 = self._screenshot_to_base64(actual_screenshot)
        detected_elements = []

        if self.yolo_model:
            detected_elements = self._detect_ui_elements(actual_screenshot)

        prompt = f"""DEBUGGING MODE: An automation step failed.

**Error:** {error_message}
**Expected State:** {expected_state}
**Detected Elements:** {len(detected_elements)} UI elements found

Analyze this screenshot to diagnose the failure:

1. What went wrong?
2. Why did it fail?
3. What's the root cause?
4. Suggest 3 fixes ranked by likelihood of success (0-100%)

Return JSON:
{{
  "diagnosis": "what went wrong",
  "root_cause": "why it happened",
  "fixes": [
    {{
      "strategy": "specific fix to try",
      "likelihood": 95,
      "implementation": "how to implement this fix"
    }}
  ],
  "alternative_approach": "completely different way to achieve the goal"
}}"""

        try:
            response = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            content = response.content[0].text.strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            debug_result = json.loads(content)

            print(f"\n✓ Debug Analysis:")
            print(f"   Diagnosis: {debug_result['diagnosis']}")
            print(f"   Root Cause: {debug_result['root_cause']}")
            print(f"\n   Top Fix: {debug_result['fixes'][0]['strategy']} ({debug_result['fixes'][0]['likelihood']}% success rate)")

            return debug_result

        except Exception as e:
            print(f"❌ Debug analysis failed: {e}")
            return {
                "diagnosis": "Could not diagnose",
                "root_cause": "Analysis error",
                "fixes": [],
                "alternative_approach": "Manual intervention required"
            }

    def get_learning_summary(self) -> Dict:
        """Get summary of learned patterns"""

        return {
            "total_observations": len(self.observation_history),
            "patterns_learned": len(self.pattern_db),
            "top_patterns": sorted(
                self.pattern_db.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )[:5],
            "observation_duration": (
                self.observation_history[-1].timestamp - self.observation_history[0].timestamp
                if self.observation_history else None
            )
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    import os

    async def test_live_observer():
        """Test the live CV observer"""

        observer = LiveCVObserver(
            claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
            observation_interval=2.0  # Observe every 2 seconds
        )

        # Set up callbacks
        async def on_observation(obs: ObservationResult):
            print(f"\n📊 Observation at {obs.timestamp.strftime('%H:%M:%S')}")
            print(f"   Understanding: {obs.claude_analysis[:80]}...")
            print(f"   Detected: {len(obs.detected_elements)} UI elements")
            print(f"   Confidence: {obs.confidence:.0%}")

        async def on_suggestion(action: str):
            print(f"\n💡 Suggested Action: {action}")

        async def on_error(suggestions: List[str]):
            print(f"\n⚠️  Issues detected!")
            for suggestion in suggestions:
                print(f"   - {suggestion}")

        observer.on_observation = on_observation
        observer.on_suggestion = on_suggestion
        observer.on_error_detected = on_error

        print("\n" + "="*60)
        print("Live CV Observer Test")
        print("="*60)
        print("The AI will watch your screen and understand what's happening...")
        print("Press Ctrl+C to stop\n")

        # Run for 20 seconds
        try:
            task = asyncio.create_task(observer.start_observing())
            await asyncio.sleep(20)
            observer.stop_observing()
            await task
        except KeyboardInterrupt:
            observer.stop_observing()

        # Show learning summary
        summary = observer.get_learning_summary()
        print(f"\n" + "="*60)
        print("Learning Summary")
        print("="*60)
        print(f"Total Observations: {summary['total_observations']}")
        print(f"Patterns Learned: {summary['patterns_learned']}")

        if summary['top_patterns']:
            print(f"\nTop Patterns:")
            for pattern, data in summary['top_patterns']:
                print(f"  - {pattern} (seen {data['count']}x)")

    asyncio.run(test_live_observer())
