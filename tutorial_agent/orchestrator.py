#!/usr/bin/env python3
"""
Tutorial Creation Agent Orchestrator
Main coordinator for AI-powered tutorial creation
"""

import asyncio
from pathlib import Path
from typing import Optional
import os
from datetime import datetime
import json

# Import components
from .planner import TutorialPlanner, TutorialPlan
from .recorder import ScreenRecorder
from .executor import DemoExecutor
from .narrator import TutorialNarrator
from .editor import TutorialVideoEditor
from .live_cv_observer import LiveCVObserver


class TutorialCreationAgent:
    """
    Main orchestrator for AI tutorial creation

    Coordinates all components to create complete video tutorials:
    - Planning (Claude)
    - Recording (screen capture)
    - Execution (automated demo)
    - Narration (TTS)
    - Editing (MoviePy)
    - Live CV observation (optional self-aware mode)
    """

    def __init__(
        self,
        claude_api_key: str = None,
        elevenlabs_api_key: str = None,
        output_dir: Path = Path("output"),
        enable_live_cv: bool = False
    ):
        self.claude_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.elevenlabs_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.enable_live_cv = enable_live_cv

        if not self.claude_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set!")

        # Initialize components
        print("\n🚀 Initializing Tutorial Creation Agent...")

        self.planner = TutorialPlanner(self.claude_key)
        self.recorder = ScreenRecorder()
        self.narrator = TutorialNarrator(self.claude_key, self.elevenlabs_key)
        self.editor = TutorialVideoEditor()

        # Live CV Observer (optional)
        self.live_observer = None
        if enable_live_cv:
            print("   🔴 Live CV Observer enabled (self-aware mode)")
            self.live_observer = LiveCVObserver(
                claude_api_key=self.claude_key,
                observation_interval=2.0
            )

            # Set up observer callbacks
            async def on_suggestion(action: str):
                print(f"   💡 AI Suggestion: {action}")

            async def on_error(suggestions: list):
                print(f"   ⚠️  AI detected issues:")
                for s in suggestions:
                    print(f"      - {s}")

            self.live_observer.on_suggestion = on_suggestion
            self.live_observer.on_error_detected = on_error

        self.executor = DemoExecutor(self.recorder, self.live_observer)

        print("✓ Agent initialized\n")

    async def create_tutorial(
        self,
        topic: str,
        target_audience: str = "intermediate",
        max_duration_minutes: int = 15,
        auto_execute: bool = True,
        save_plan: bool = True
    ) -> Path:
        """
        Create complete tutorial from topic to final video

        Args:
            topic: Tutorial topic (e.g., "Build REST API with Flask")
            target_audience: "beginner", "intermediate", or "advanced"
            max_duration_minutes: Maximum tutorial length
            auto_execute: Automatically execute demo steps
            save_plan: Save tutorial plan to JSON

        Returns:
            Path to final video file
        """

        print(f"\n{'='*70}")
        print(f"🎓 Creating Tutorial: {topic}")
        print(f"{'='*70}\n")

        start_time = datetime.now()

        # Create project directory
        project_name = topic.replace(' ', '_')[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = self.output_dir / f"{project_name}_{timestamp}"
        project_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Project directory: {project_dir}\n")

        # Phase 1: Planning
        print("="*70)
        print("📋 Phase 1: Planning Tutorial Structure")
        print("="*70)

        plan = await self.planner.plan_tutorial(
            topic=topic,
            target_audience=target_audience,
            max_duration_minutes=max_duration_minutes
        )

        print(f"\n✓ Tutorial Plan Created:")
        print(f"   Title: {plan.title}")
        print(f"   Steps: {len(plan.steps)}")
        print(f"   Estimated Duration: ~{plan.duration_minutes} minutes")
        print(f"   Difficulty: {plan.difficulty}")

        if save_plan:
            plan_path = project_dir / "tutorial_plan.json"
            self.planner.save_plan(plan, plan_path)

        # Phase 2: Recording
        print(f"\n{'='*70}")
        print(f"🎥 Phase 2: Recording Demo ({len(plan.steps)} steps)")
        print(f"{'='*70}")

        clips = []

        if auto_execute:
            # Automatically execute and record each step
            print("\nAuto-execution mode: AI will perform demo automatically\n")

            for step in plan.steps:
                clip_path = await self.executor.execute_step(
                    step,
                    with_observation=self.enable_live_cv
                )
                clips.append(clip_path)

        else:
            # Manual recording mode
            print("\nManual recording mode: You control the demo\n")

            for step in plan.steps:
                print(f"\n{'─'*70}")
                print(f"📹 Step {step.step_number}: {step.title}")
                print(f"{'─'*70}")
                print(f"Description: {step.description}")
                print(f"Duration: {step.duration_seconds}s")
                print(f"\nActions to perform:")
                for action in step.actions:
                    print(f"  - {action}")

                input("\n👉 Press ENTER when ready to record...")

                clip_path = await self.recorder.record_clip(
                    name=f"step_{step.step_number}_{step.title.replace(' ', '_')}",
                    duration_seconds=step.duration_seconds
                )
                clips.append(clip_path)

        print(f"\n✓ Recorded {len(clips)} clips")

        # Phase 3: Narration
        print(f"\n{'='*70}")
        print(f"🎙️  Phase 3: Generating Narration")
        print(f"{'='*70}")

        narrations = []

        for step, clip in zip(plan.steps, clips):
            narration_data = await self.narrator.generate_narration(step, [clip])
            narrations.append(narration_data["audio_path"])

        # Generate intro/outro
        intro_outro = await self.narrator.generate_intro_outro(
            plan,
            output_name=project_name
        )

        print(f"\n✓ Generated narration for {len(narrations)} steps")

        # Phase 4: Video Editing
        print(f"\n{'='*70}")
        print(f"✂️  Phase 4: Editing Final Video")
        print(f"{'='*70}")

        output_video = project_dir / f"{project_name}.mp4"

        final_video = await self.editor.create_final_video(
            plan=plan,
            clips=clips,
            narrations=narrations,
            output_path=output_video
        )

        if not final_video:
            print("\n❌ Video editing failed!")
            return None

        # Generate thumbnail
        thumbnail_path = project_dir / f"{project_name}_thumbnail.jpg"
        self.editor.generate_thumbnail(final_video, thumbnail_path)

        # Save metadata
        metadata = {
            "title": plan.title,
            "description": plan.description,
            "topic": topic,
            "difficulty": plan.difficulty,
            "duration_minutes": plan.duration_minutes,
            "target_audience": target_audience,
            "created": timestamp,
            "steps": len(plan.steps),
            "auto_executed": auto_execute,
            "live_cv_enabled": self.enable_live_cv
        }

        metadata_path = project_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Learning summary (if live CV was enabled)
        if self.live_observer and len(self.live_observer.observation_history) > 0:
            learning_summary = self.live_observer.get_learning_summary()
            learning_path = project_dir / "learning_summary.json"

            with open(learning_path, 'w') as f:
                json.dump({
                    "total_observations": learning_summary["total_observations"],
                    "patterns_learned": learning_summary["patterns_learned"],
                    "top_patterns": [
                        {"pattern": p, "count": d["count"]}
                        for p, d in learning_summary["top_patterns"]
                    ]
                }, f, indent=2)

            print(f"\n📊 Live CV Learning Summary:")
            print(f"   Observations: {learning_summary['total_observations']}")
            print(f"   Patterns Learned: {learning_summary['patterns_learned']}")

        # Final summary
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n{'='*70}")
        print(f"✅ TUTORIAL CREATION COMPLETE!")
        print(f"{'='*70}")
        print(f"📹 Video: {final_video}")
        print(f"📸 Thumbnail: {thumbnail_path}")
        print(f"📄 Metadata: {metadata_path}")
        print(f"⏱️  Total Time: {elapsed:.1f}s")
        print(f"🎬 Tutorial Duration: ~{plan.duration_minutes} minutes")
        print(f"{'='*70}\n")

        return final_video

    async def create_from_plan(
        self,
        plan_path: Path,
        auto_execute: bool = True
    ) -> Path:
        """Create tutorial from existing plan JSON"""

        print(f"\n📂 Loading plan from: {plan_path}")

        plan = self.planner.load_plan(plan_path)

        print(f"✓ Loaded: {plan.title}")
        print(f"  Steps: {len(plan.steps)}")

        # Continue with normal workflow
        # (implementation similar to create_tutorial)

        return await self.create_tutorial(
            topic=plan.title,
            auto_execute=auto_execute
        )


# Example usage and CLI
if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        """Main entry point for tutorial agent"""

        print("\n" + "="*70)
        print("🤖 AI Tutorial Creation Agent")
        print("="*70)

        # Check for API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("\n❌ Error: ANTHROPIC_API_KEY environment variable not set!")
            print("\nSet it with:")
            print("  export ANTHROPIC_API_KEY='your-key-here'")
            sys.exit(1)

        # Create agent
        agent = TutorialCreationAgent(
            enable_live_cv=True  # Enable self-aware mode
        )

        # Interactive mode
        if len(sys.argv) > 1:
            # CLI mode: use argument as topic
            topic = " ".join(sys.argv[1:])
        else:
            # Interactive mode
            print("\nWhat tutorial would you like to create?")
            print("Examples:")
            print("  - Build a REST API with Flask")
            print("  - Python Virtual Environments Explained")
            print("  - Docker Compose for Beginners")
            print("  - Git Branching Strategies")

            topic = input("\nTopic: ").strip()

            if not topic:
                print("❌ No topic provided!")
                sys.exit(1)

        # Ask for audience
        print("\nTarget audience:")
        print("  1. Beginner")
        print("  2. Intermediate (default)")
        print("  3. Advanced")

        audience_choice = input("\nChoice (1-3): ").strip()
        audience_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
        audience = audience_map.get(audience_choice, "intermediate")

        # Ask for execution mode
        print("\nExecution mode:")
        print("  1. Auto-execute (AI performs demo automatically)")
        print("  2. Manual (you control the demo)")

        exec_choice = input("\nChoice (1-2): ").strip()
        auto_execute = exec_choice != "2"

        # Create tutorial
        video_path = await agent.create_tutorial(
            topic=topic,
            target_audience=audience,
            auto_execute=auto_execute,
            max_duration_minutes=15
        )

        if video_path:
            print(f"\n🎉 Tutorial ready: {video_path}")
            print(f"\nYou can now:")
            print(f"  - Watch the video")
            print(f"  - Upload to YouTube")
            print(f"  - Share with your audience")
        else:
            print("\n❌ Tutorial creation failed!")

    # Run
    asyncio.run(main())
