#!/usr/bin/env python3
"""
Tutorial Narrator - Generate narration scripts and convert to speech
"""

import anthropic
from pathlib import Path
import pysrt
from datetime import timedelta
import os
from typing import List, Optional
import json


class TutorialNarrator:
    """Generate narration script and convert to speech"""

    def __init__(
        self,
        claude_api_key: str = None,
        elevenlabs_api_key: str = None
    ):
        self.claude_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.elevenlabs_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")

        if not self.claude_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.claude = anthropic.Anthropic(api_key=self.claude_key)

        # Output directories
        self.audio_dir = Path("audio")
        self.subtitle_dir = Path("subtitles")
        self.audio_dir.mkdir(exist_ok=True)
        self.subtitle_dir.mkdir(exist_ok=True)

    async def generate_narration(
        self,
        step,
        video_clips: List[Path]
    ) -> dict:
        """Generate timed narration for video clips"""

        print(f"\n🎙️  Generating narration for Step {step.step_number}...")

        # Claude refines the narration script
        refined_script = await self._refine_script(step)

        # Generate speech
        audio_path = await self._text_to_speech(
            refined_script,
            output_name=f"narration_step_{step.step_number}"
        )

        # Generate subtitles
        subtitle_path = await self._generate_subtitles(
            refined_script,
            step.duration_seconds,
            output_name=f"step_{step.step_number}"
        )

        return {
            "script": refined_script,
            "audio_path": audio_path,
            "subtitle_path": subtitle_path
        }

    async def _refine_script(self, step) -> str:
        """Use Claude to refine narration script"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Refine this tutorial narration script to be:
- Clear and concise
- Engaging and professional
- Natural when spoken aloud
- Timed for approximately {step.duration_seconds} seconds
- Educational but not patronizing

Original script:
{step.narration}

Output ONLY the refined script, no explanation or formatting.
Make it sound like a professional tutorial narrator speaking naturally."""
            }]
        )

        refined = response.content[0].text.strip()

        # Remove any markdown formatting
        refined = refined.replace('**', '').replace('*', '')

        return refined

    async def _text_to_speech(
        self,
        text: str,
        output_name: str
    ) -> Path:
        """Convert text to speech using ElevenLabs (or fallback to gTTS)"""

        output_path = self.audio_dir / f"{output_name}.mp3"

        if self.elevenlabs_key:
            # Premium TTS with ElevenLabs
            try:
                from elevenlabs import generate, save, Voice, VoiceSettings

                print(f"   Using ElevenLabs TTS (premium quality)...")

                audio = generate(
                    text=text,
                    voice=Voice(
                        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice (professional)
                        settings=VoiceSettings(
                            stability=0.75,
                            similarity_boost=0.85,
                            style=0.0,
                            use_speaker_boost=True
                        )
                    ),
                    model="eleven_monolingual_v1",
                    api_key=self.elevenlabs_key
                )

                save(audio, str(output_path))
                print(f"✓ Generated: {output_path}")
                return output_path

            except ImportError:
                print("⚠️  elevenlabs not installed, falling back to gTTS")
                print("   Install with: pip install elevenlabs")
            except Exception as e:
                print(f"⚠️  ElevenLabs error: {e}, falling back to gTTS")

        # Fallback: Google TTS (free)
        try:
            from gtts import gTTS

            print(f"   Using Google TTS (free)...")

            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(str(output_path))

            print(f"✓ Generated: {output_path}")
            return output_path

        except ImportError:
            print("❌ gTTS not installed. Install with: pip install gtts")
            # Create placeholder
            output_path.touch()
            return output_path

    async def _generate_subtitles(
        self,
        text: str,
        duration: int,
        output_name: str
    ) -> Path:
        """Generate SRT subtitles"""

        output_path = self.subtitle_dir / f"{output_name}.srt"

        try:
            # Split text into subtitle segments
            words = text.split()

            if len(words) == 0:
                # Empty subtitle file
                output_path.touch()
                return output_path

            words_per_second = len(words) / duration
            words_per_subtitle = max(5, int(words_per_second * 3))  # ~3 second chunks

            subtitles = pysrt.SubRipFile()

            start_time = 0
            for i in range(0, len(words), words_per_subtitle):
                chunk = " ".join(words[i:i + words_per_subtitle])
                chunk_duration = len(chunk.split()) / words_per_second

                sub = pysrt.SubRipItem(
                    index=len(subtitles) + 1,
                    start=timedelta(seconds=start_time),
                    end=timedelta(seconds=start_time + chunk_duration),
                    text=chunk
                )
                subtitles.append(sub)

                start_time += chunk_duration

            subtitles.save(str(output_path), encoding='utf-8')
            print(f"✓ Generated subtitles: {output_path}")

        except Exception as e:
            print(f"⚠️  Subtitle generation error: {e}")
            # Create placeholder
            output_path.touch()

        return output_path

    async def generate_intro_outro(
        self,
        plan,
        output_name: str
    ) -> dict:
        """Generate intro and outro narration"""

        print("\n🎬 Generating intro/outro narration...")

        # Generate intro audio
        intro_path = await self._text_to_speech(
            plan.intro_script,
            output_name=f"{output_name}_intro"
        )

        # Generate outro audio
        outro_path = await self._text_to_speech(
            plan.outro_script,
            output_name=f"{output_name}_outro"
        )

        return {
            "intro_audio": intro_path,
            "outro_audio": outro_path
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    from .planner import TutorialStep

    async def test_narrator():
        narrator = TutorialNarrator()

        # Test step
        test_step = TutorialStep(
            step_number=1,
            title="Setup Flask",
            description="Install and configure Flask",
            actions=["run_terminal:pip install flask"],
            narration="First, we need to install Flask. Flask is a lightweight web framework for Python that makes it easy to build web applications. Let's install it using pip.",
            duration_seconds=15,
            recording_type="terminal"
        )

        print("\n" + "="*60)
        print("Tutorial Narrator Test")
        print("="*60)

        narration = await narrator.generate_narration(test_step, [])

        print(f"\n✅ Narration complete!")
        print(f"   Script: {narration['script'][:100]}...")
        print(f"   Audio: {narration['audio_path']}")
        print(f"   Subtitles: {narration['subtitle_path']}")

    asyncio.run(test_narrator())
