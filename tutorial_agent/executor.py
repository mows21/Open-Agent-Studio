#!/usr/bin/env python3
"""
Demo Executor - Executes tutorial steps with live CV observation
"""

import asyncio
from typing import List, Optional
from pathlib import Path
import subprocess
import platform
import os

# Import components
from .planner import TutorialStep
from .recorder import ScreenRecorder


class DemoExecutor:
    """
    Executes demo steps while recording

    Can be enhanced with live CV observer for self-debugging
    """

    def __init__(
        self,
        recorder: ScreenRecorder,
        live_observer: Optional['LiveCVObserver'] = None
    ):
        self.recorder = recorder
        self.live_observer = live_observer
        self.execution_log = []

        # Try to import input automation
        try:
            import pyautogui
            self.pyautogui = pyautogui
            pyautogui.PAUSE = 0.5  # Slow down for visibility
        except ImportError:
            print("⚠️  pyautogui not installed. Some features may not work.")
            print("   Install with: pip install pyautogui")
            self.pyautogui = None

    async def execute_step(
        self,
        step: TutorialStep,
        with_observation: bool = True
    ) -> Path:
        """Execute tutorial step and record it"""

        print(f"\n▶️  Executing Step {step.step_number}: {step.title}")
        self.execution_log.append(f"Step {step.step_number}: {step.title}")

        # Start live observation if available
        observation_task = None
        if with_observation and self.live_observer:
            observation_task = asyncio.create_task(
                self.live_observer.start_observing()
            )
            await asyncio.sleep(0.5)  # Let observer initialize

        # Start recording
        recording_task = asyncio.create_task(
            self.recorder.record_clip(
                name=f"step_{step.step_number}_{step.title.replace(' ', '_')}",
                duration_seconds=step.duration_seconds
            )
        )

        # Small delay to ensure recording started
        await asyncio.sleep(0.5)

        # Execute actions
        try:
            for action in step.actions:
                await self._execute_action(action)

        except Exception as e:
            print(f"❌ Error executing step: {e}")

            # If live observer available, debug the failure
            if self.live_observer:
                import mss
                import numpy as np

                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    screenshot = np.array(sct.grab(monitor))[:, :, :3]

                debug_result = await self.live_observer.debug_failure(
                    error_message=str(e),
                    expected_state=f"Completed: {action}",
                    actual_screenshot=screenshot
                )

                # Try top fix suggestion
                if debug_result.get('fixes'):
                    top_fix = debug_result['fixes'][0]
                    print(f"\n🔧 Attempting fix: {top_fix['strategy']}")
                    # Implementation would retry with suggested fix

        finally:
            # Stop observation
            if observation_task:
                self.live_observer.stop_observing()
                await observation_task

        # Wait for recording to complete
        clip_path = await recording_task

        return clip_path

    async def _execute_action(self, action: str):
        """Parse and execute single action"""

        # Parse action format: "command:parameter"
        if ":" not in action:
            print(f"⚠️  Invalid action format: {action}")
            return

        command, param = action.split(":", 1)

        print(f"  → {command}: {param}")
        self.execution_log.append(f"   {command}: {param}")

        if command == "open":
            await self._open_application(param)

        elif command == "create_file":
            await self._create_file(param)

        elif command == "type_code":
            await self._type_text(param, interval=0.05)

        elif command == "type_text":
            await self._type_text(param, interval=0.1)

        elif command == "run_terminal":
            await self._run_terminal_command(param)

        elif command == "click":
            await self._click_element(param)

        elif command == "wait":
            await asyncio.sleep(float(param))

        elif command == "screenshot":
            if self.pyautogui:
                self.pyautogui.screenshot(param)

        elif command == "hotkey":
            await self._press_hotkey(param)

        else:
            print(f"⚠️  Unknown command: {command}")

    async def _open_application(self, app_name: str):
        """Open application by name"""

        system = platform.system()

        try:
            if app_name == "vscode" or app_name == "code":
                subprocess.Popen(["code"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            elif app_name == "terminal":
                if system == "Windows":
                    subprocess.Popen(["cmd"])
                elif system == "Darwin":  # macOS
                    subprocess.Popen(["open", "-a", "Terminal"])
                else:  # Linux
                    subprocess.Popen(["gnome-terminal"])

            elif app_name == "browser" or app_name == "chrome":
                if system == "Windows":
                    subprocess.Popen(["start", "chrome"], shell=True)
                elif system == "Darwin":
                    subprocess.Popen(["open", "-a", "Google Chrome"])
                else:
                    subprocess.Popen(["google-chrome"])

            else:
                # Try to open directly
                subprocess.Popen([app_name])

            await asyncio.sleep(2)  # Wait for app to open

        except Exception as e:
            print(f"⚠️  Could not open {app_name}: {e}")

    async def _type_text(self, text: str, interval: float = 0.05):
        """Type text with human-like timing"""

        if not self.pyautogui:
            print(f"   [Would type: {text}]")
            return

        self.pyautogui.write(text, interval=interval)
        await asyncio.sleep(0.5)

    async def _run_terminal_command(self, command: str):
        """Execute terminal command"""

        if not self.pyautogui:
            print(f"   [Would run: {command}]")
            return

        # Type command in active terminal
        self.pyautogui.write(command, interval=0.05)
        self.pyautogui.press('enter')
        await asyncio.sleep(2)  # Wait for command output

    async def _click_element(self, description: str):
        """Click element (would use ML vision in production)"""

        # If live observer is active, ask it to find element
        if self.live_observer and len(self.live_observer.observation_history) > 0:
            latest_obs = self.live_observer.observation_history[-1]

            # Look for matching element in detected elements
            for elem in latest_obs.detected_elements:
                if description.lower() in elem['type'].lower():
                    x, y = elem['center']
                    print(f"   Found {elem['type']} at ({x}, {y})")

                    if self.pyautogui:
                        self.pyautogui.click(x, y)

                    await asyncio.sleep(0.5)
                    return

        # Fallback: placeholder
        print(f"  Clicking: {description}")
        await asyncio.sleep(0.5)

    async def _create_file(self, filename: str):
        """Create new file"""

        if not self.pyautogui:
            print(f"   [Would create: {filename}]")
            return

        # Assume VS Code is open
        self.pyautogui.hotkey('ctrl', 'n')  # New file
        await asyncio.sleep(0.5)
        self.pyautogui.hotkey('ctrl', 's')  # Save as
        await asyncio.sleep(0.5)
        self.pyautogui.write(filename)
        self.pyautogui.press('enter')
        await asyncio.sleep(1)

    async def _press_hotkey(self, keys: str):
        """Press keyboard shortcut"""

        if not self.pyautogui:
            print(f"   [Would press: {keys}]")
            return

        # Parse keys like "ctrl+s" or "alt+f4"
        key_list = keys.split('+')
        self.pyautogui.hotkey(*key_list)
        await asyncio.sleep(0.5)

    def get_execution_log(self) -> List[str]:
        """Get execution log for debugging"""
        return self.execution_log.copy()


# Example usage
if __name__ == "__main__":
    import asyncio
    from .planner import TutorialStep
    from .recorder import ScreenRecorder

    async def test_executor():
        recorder = ScreenRecorder()
        executor = DemoExecutor(recorder)

        # Create a test step
        test_step = TutorialStep(
            step_number=1,
            title="Open VS Code",
            description="Launch VS Code editor",
            actions=[
                "open:vscode",
                "wait:2",
                "hotkey:ctrl+n"
            ],
            narration="First, we'll open VS Code and create a new file.",
            duration_seconds=5,
            recording_type="screen"
        )

        print("\n" + "="*60)
        print("Demo Executor Test")
        print("="*60)

        clip = await executor.execute_step(test_step, with_observation=False)

        print(f"\n✅ Execution complete!")
        print(f"   Recording: {clip}")
        print(f"\nExecution Log:")
        for line in executor.get_execution_log():
            print(f"  {line}")

    asyncio.run(test_executor())
