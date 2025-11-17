#!/usr/bin/env python3
"""
Tutorial Video Editor - Automated video editing with MoviePy
"""

from pathlib import Path
from typing import List, Optional
import sys


class TutorialVideoEditor:
    """Automated video editing with MoviePy"""

    def __init__(self, assets_dir: Path = Path("assets")):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True, parents=True)

        # Check if moviepy is installed
        try:
            from moviepy.editor import VideoFileClip
            self.moviepy_available = True
        except ImportError:
            print("⚠️  MoviePy not installed. Video editing will be limited.")
            print("   Install with: pip install moviepy")
            self.moviepy_available = False

    async def create_final_video(
        self,
        plan,
        clips: List[Path],
        narrations: List[Path],
        output_path: Path
    ) -> Path:
        """Assemble final tutorial video"""

        if not self.moviepy_available:
            print("❌ Cannot create video without MoviePy")
            return None

        from moviepy.editor import (
            VideoFileClip, AudioFileClip, CompositeVideoClip,
            TextClip, concatenate_videoclips, CompositeAudioClip
        )
        import moviepy.video.fx.all as vfx

        print("\n🎬 Starting video editing...")
        print(f"   Clips: {len(clips)}")
        print(f"   Output: {output_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        all_clips = []

        try:
            # 1. Intro (if exists)
            intro_template = self.assets_dir / "intro_template.mp4"
            if intro_template.exists():
                intro_clip = VideoFileClip(str(intro_template))
                intro_with_title = self._add_title_overlay(intro_clip, plan.title)
                all_clips.append(intro_with_title)
            else:
                # Create text-based intro
                intro_clip = self._create_text_intro(plan.title, plan.description)
                all_clips.append(intro_clip)

            # 2. Process each tutorial step
            print("\n📹 Processing tutorial steps...")
            for i, (clip_path, narration_path) in enumerate(zip(clips, narrations)):
                print(f"   Processing Step {i+1}/{len(clips)}...")

                step_clip = self._process_step_clip(
                    clip_path,
                    narration_path,
                    step_number=i+1
                )

                if step_clip:
                    all_clips.append(step_clip)

            # 3. Outro (if exists)
            outro_template = self.assets_dir / "outro_template.mp4"
            if outro_template.exists():
                outro_clip = VideoFileClip(str(outro_template))
                all_clips.append(outro_clip)
            else:
                # Create text-based outro
                outro_clip = self._create_text_outro(plan.title)
                all_clips.append(outro_clip)

            # 4. Concatenate everything
            print("\n🔗 Concatenating clips...")
            final_video = concatenate_videoclips(all_clips, method="compose")

            # 5. Add background music (optional)
            bg_music = self.assets_dir / "background_music.mp3"
            if bg_music.exists():
                print("🎵 Adding background music...")
                final_video = self._add_background_music(final_video, bg_music)

            # 6. Export
            print(f"\n📤 Exporting final video to {output_path}...")
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4,
                logger=None  # Suppress verbose output
            )

            # Cleanup
            for clip in all_clips:
                clip.close()

            print(f"\n✅ Tutorial video complete: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Video editing error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_text_intro(self, title: str, description: str, duration: int = 5) -> 'VideoFileClip':
        """Create simple text-based intro"""
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

        # Background
        bg = ColorClip(size=(1920, 1080), color=(20, 20, 40), duration=duration)

        # Title
        title_clip = TextClip(
            title,
            fontsize=80,
            color='white',
            font='Arial-Bold',
            method='caption',
            size=(1600, None)
        ).set_position('center').set_duration(duration)

        # Description
        desc_clip = TextClip(
            description,
            fontsize=40,
            color='lightgray',
            font='Arial',
            method='caption',
            size=(1400, None)
        ).set_position(('center', 700)).set_duration(duration)

        return CompositeVideoClip([bg, title_clip, desc_clip])

    def _create_text_outro(self, title: str, duration: int = 3) -> 'VideoFileClip':
        """Create simple text-based outro"""
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

        bg = ColorClip(size=(1920, 1080), color=(20, 20, 40), duration=duration)

        text_clip = TextClip(
            f"Thanks for watching!\n\n{title}",
            fontsize=60,
            color='white',
            font='Arial-Bold',
            method='caption',
            size=(1400, None)
        ).set_position('center').set_duration(duration)

        return CompositeVideoClip([bg, text_clip])

    def _add_title_overlay(self, clip, title: str):
        """Add title text overlay to clip"""
        from moviepy.editor import TextClip, CompositeVideoClip

        try:
            txt_clip = TextClip(
                title,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(clip.w - 200, None)
            )

            txt_clip = txt_clip.set_position('center').set_duration(clip.duration)

            return CompositeVideoClip([clip, txt_clip])
        except Exception as e:
            print(f"⚠️  Could not add title overlay: {e}")
            return clip

    def _process_step_clip(
        self,
        video_path: Path,
        audio_path: Path,
        step_number: int
    ):
        """Process individual step clip"""
        from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
        import moviepy.video.fx.all as vfx

        try:
            # Load video
            clip = VideoFileClip(str(video_path))

            # Load narration audio
            if audio_path.exists() and audio_path.stat().st_size > 0:
                narration = AudioFileClip(str(audio_path))

                # Sync clip duration with narration
                if clip.duration < narration.duration:
                    # Slow down video slightly to match
                    speed = clip.duration / narration.duration
                    clip = clip.fx(vfx.speedx, speed)
                else:
                    # Trim video to match narration
                    clip = clip.subclip(0, min(clip.duration, narration.duration))

                # Set audio
                clip = clip.set_audio(narration)

            # Add step number overlay
            try:
                step_text = TextClip(
                    f"Step {step_number}",
                    fontsize=30,
                    color='white',
                    bg_color='rgba(0,0,0,0.7)',
                    font='Arial',
                    method='label'
                )
                step_text = step_text.set_position(('left', 'top')).set_duration(3)

                clip = CompositeVideoClip([clip, step_text.set_start(0)])
            except:
                pass  # Skip overlay if it fails

            # Add fade in/out
            clip = clip.fx(vfx.fadein, 0.5).fx(vfx.fadeout, 0.5)

            return clip

        except Exception as e:
            print(f"⚠️  Error processing clip {video_path}: {e}")
            return None

    def _add_background_music(self, video, music_path: Path):
        """Add background music at low volume"""
        from moviepy.editor import AudioFileClip, CompositeAudioClip
        import moviepy.audio.fx.all as afx

        try:
            music = AudioFileClip(str(music_path))

            # Loop music to match video length
            if music.duration < video.duration:
                music = afx.audio_loop(music, duration=video.duration)
            else:
                music = music.subclip(0, video.duration)

            # Lower volume (10% of original)
            music = music.volumex(0.1)

            # Mix with existing audio
            if video.audio:
                final_audio = CompositeAudioClip([video.audio, music])
                video = video.set_audio(final_audio)
            else:
                video = video.set_audio(music)

            return video

        except Exception as e:
            print(f"⚠️  Could not add background music: {e}")
            return video

    def generate_thumbnail(
        self,
        video_path: Path,
        output_path: Path,
        timestamp: float = 5.0
    ):
        """Generate YouTube thumbnail from video"""

        if not self.moviepy_available:
            print("⚠️  Cannot generate thumbnail without MoviePy")
            return

        from moviepy.editor import VideoFileClip

        try:
            clip = VideoFileClip(str(video_path))

            # Get frame at timestamp
            frame = clip.get_frame(min(timestamp, clip.duration - 1))

            # Save as high-quality image
            from PIL import Image
            img = Image.fromarray(frame)
            img = img.resize((1280, 720), Image.LANCZOS)
            img.save(output_path, quality=95)

            clip.close()

            print(f"📸 Thumbnail generated: {output_path}")

        except Exception as e:
            print(f"⚠️  Thumbnail generation error: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_editor():
        editor = TutorialVideoEditor()

        print("\n" + "="*60)
        print("Tutorial Video Editor Test")
        print("="*60)
        print("\nNote: This requires actual video clips to test fully.")
        print("The editor can:")
        print("  - Concatenate clips")
        print("  - Add narration audio")
        print("  - Add text overlays")
        print("  - Generate thumbnails")
        print("  - Add background music")

    asyncio.run(test_editor())
