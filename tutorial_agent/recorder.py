#!/usr/bin/env python3
"""
Screen Recorder - High-performance screen recording
"""

import asyncio
import numpy as np
from datetime import datetime
from pathlib import Path
import subprocess
import platform
import sys
from typing import Optional, Tuple


class ScreenRecorder:
    """High-performance screen recorder with multiple backends"""

    def __init__(self, output_dir: Path = Path("recordings")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.recording = False
        self.current_clip = None

        # Auto-select best recorder for platform
        self.backend = self._select_backend()

    def _select_backend(self):
        """Choose fastest screen recorder for platform"""
        system = platform.system()

        if system == "Windows":
            try:
                import dxcam
                print("✓ Using DXCam (Windows - fastest)")
                return WindowsDXCamRecorder()
            except ImportError:
                print("✓ Using MSS (cross-platform)")
                return MSSRecorder()
        else:
            print("✓ Using MSS (cross-platform)")
            return MSSRecorder()

    async def record_clip(
        self,
        name: str,
        duration_seconds: Optional[int] = None,
        region: Optional[Tuple[int, int, int, int]] = None,  # (x, y, width, height)
        fps: int = 30
    ) -> Path:
        """Record screen clip with optional duration limit"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"{name}_{timestamp}.mp4"

        print(f"\n🎥 Recording: {name}")
        if duration_seconds:
            print(f"   Duration: {duration_seconds}s")
        else:
            print(f"   Duration: Manual stop (call stop_recording())")

        self.recording = True
        frames = []
        start_time = asyncio.get_event_loop().time()
        frame_count = 0

        try:
            while self.recording:
                # Capture frame
                frame = await self.backend.grab_frame(region)
                if frame is not None:
                    frames.append(frame)
                    frame_count += 1

                # Check duration limit
                if duration_seconds:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= duration_seconds:
                        break

                # Maintain FPS
                await asyncio.sleep(1/fps)

        except KeyboardInterrupt:
            print("\n⏹️  Recording interrupted by user")

        finally:
            # Save video
            if frames:
                print(f"   Saving {len(frames)} frames...")
                self._save_video(frames, output_path, fps)
                print(f"✓ Saved: {output_path}")
            else:
                print("⚠️  No frames captured!")

            self.recording = False

        return output_path

    def stop_recording(self):
        """Stop current recording"""
        print("\n⏹️  Stopping recording...")
        self.recording = False

    def _save_video(self, frames: list, output_path: Path, fps: int):
        """Save frames as MP4 using FFmpeg"""

        if not frames:
            return

        height, width = frames[0].shape[:2]

        # FFmpeg command for high-quality MP4
        command = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{width}x{height}',
            '-pix_fmt', 'bgr24',
            '-r', str(fps),
            '-i', '-',  # Input from pipe
            '-an',  # No audio (for now)
            '-vcodec', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '18',  # High quality
            str(output_path)
        ]

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Write frames to FFmpeg
            for frame in frames:
                process.stdin.write(frame.tobytes())

            process.stdin.close()
            process.wait()

        except Exception as e:
            print(f"❌ Error saving video with FFmpeg: {e}")
            print("   Make sure FFmpeg is installed: https://ffmpeg.org/download.html")


class MSSRecorder:
    """Cross-platform screen capture using MSS"""

    def __init__(self):
        try:
            import mss
            self.sct = mss.mss()
        except ImportError:
            print("❌ mss not installed. Run: pip install mss")
            sys.exit(1)

    async def grab_frame(self, region=None):
        """Grab single frame"""
        import mss

        if region:
            monitor = {
                "top": region[1],
                "left": region[0],
                "width": region[2],
                "height": region[3]
            }
        else:
            monitor = self.sct.monitors[1]  # Primary monitor

        sct_img = self.sct.grab(monitor)
        # Convert to numpy array (BGR format for OpenCV/FFmpeg)
        img = np.array(sct_img)
        # Convert BGRA to BGR
        return img[:, :, :3]


class WindowsDXCamRecorder:
    """Windows-only ultra-fast recorder (120fps+)"""

    def __init__(self):
        try:
            import dxcam
            self.camera = dxcam.create()
        except ImportError:
            print("❌ dxcam not installed. Run: pip install dxcam")
            sys.exit(1)

    async def grab_frame(self, region=None):
        """Grab frame using DirectX"""
        if region:
            return self.camera.grab(region=region)
        return self.camera.grab()


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_recorder():
        recorder = ScreenRecorder()

        print("\n" + "="*60)
        print("Screen Recorder Test")
        print("="*60)
        print("Recording 5 seconds of your screen...")
        print("Move your mouse around to test!")

        clip = await recorder.record_clip(
            name="test_recording",
            duration_seconds=5,
            fps=30
        )

        print(f"\n✅ Recording complete: {clip}")
        print(f"   Size: {clip.stat().st_size / 1024 / 1024:.2f} MB")

    asyncio.run(test_recorder())
