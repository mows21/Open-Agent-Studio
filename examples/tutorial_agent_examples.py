#!/usr/bin/env python3
"""
Tutorial Agent Examples
Comprehensive examples showing how to use the AI Tutorial Creation Agent
"""

import asyncio
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tutorial_agent import TutorialCreationAgent
from tutorial_agent.live_cv_observer import LiveCVObserver


# ============================================================================
# Example 1: Simple Tutorial Creation
# ============================================================================

async def example_1_simple_tutorial():
    """Create a simple tutorial with default settings"""

    print("\n" + "="*70)
    print("Example 1: Simple Tutorial Creation")
    print("="*70)

    agent = TutorialCreationAgent()

    video = await agent.create_tutorial(
        topic="Python Virtual Environments Explained",
        target_audience="beginner",
        auto_execute=True
    )

    print(f"\n✅ Video created: {video}")


# ============================================================================
# Example 2: Manual Recording Mode
# ============================================================================

async def example_2_manual_recording():
    """Create tutorial with manual control over recording"""

    print("\n" + "="*70)
    print("Example 2: Manual Recording Mode")
    print("="*70)

    agent = TutorialCreationAgent()

    # You control when to record each step
    video = await agent.create_tutorial(
        topic="Docker Compose for Beginners",
        target_audience="intermediate",
        auto_execute=False,  # Manual mode!
        max_duration_minutes=12
    )

    print(f"\n✅ Video created: {video}")


# ============================================================================
# Example 3: Self-Aware Mode with Live CV Observer
# ============================================================================

async def example_3_self_aware_mode():
    """
    Tutorial creation with live computer vision observation

    The AI watches itself work, understands context, and can self-debug!
    """

    print("\n" + "="*70)
    print("Example 3: Self-Aware Mode (Live CV Observer)")
    print("="*70)

    # Enable live CV observation
    agent = TutorialCreationAgent(
        enable_live_cv=True  # 🔴 Self-aware mode!
    )

    video = await agent.create_tutorial(
        topic="Git Branching Strategies",
        target_audience="intermediate",
        auto_execute=True
    )

    # Get learning summary
    if agent.live_observer:
        summary = agent.live_observer.get_learning_summary()

        print("\n📊 AI Learning Summary:")
        print(f"   Total observations: {summary['total_observations']}")
        print(f"   Patterns learned: {summary['patterns_learned']}")

        if summary['top_patterns']:
            print("\n   Top patterns observed:")
            for pattern, data in summary['top_patterns']:
                print(f"     - {pattern} (seen {data['count']}x)")

    print(f"\n✅ Video created: {video}")


# ============================================================================
# Example 4: Custom Configuration
# ============================================================================

async def example_4_custom_config():
    """Tutorial with custom configuration"""

    print("\n" + "="*70)
    print("Example 4: Custom Configuration")
    print("="*70)

    # Custom output directory and API keys
    agent = TutorialCreationAgent(
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),  # Premium TTS
        output_dir=Path("my_tutorials"),
        enable_live_cv=True
    )

    video = await agent.create_tutorial(
        topic="Building Microservices with FastAPI",
        target_audience="advanced",
        max_duration_minutes=20,
        auto_execute=True,
        save_plan=True  # Save plan JSON for reuse
    )

    print(f"\n✅ Video created: {video}")


# ============================================================================
# Example 5: Live CV Observer Standalone
# ============================================================================

async def example_5_live_cv_standalone():
    """
    Use Live CV Observer independently

    Watch your screen and get AI insights in real-time!
    """

    print("\n" + "="*70)
    print("Example 5: Standalone Live CV Observer")
    print("="*70)

    observer = LiveCVObserver(
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        observation_interval=2.0  # Observe every 2 seconds
    )

    # Set up callbacks
    async def on_observation(obs):
        print(f"\n📊 [{obs.timestamp.strftime('%H:%M:%S')}]")
        print(f"   Understanding: {obs.claude_analysis[:100]}...")
        print(f"   Detected: {len(obs.detected_elements)} UI elements")
        print(f"   Confidence: {obs.confidence:.0%}")

    async def on_suggestion(action):
        print(f"\n💡 AI Suggests: {action}")

    async def on_error(suggestions):
        print(f"\n⚠️  Issues Detected:")
        for s in suggestions:
            print(f"      - {s}")

    observer.on_observation = on_observation
    observer.on_suggestion = on_suggestion
    observer.on_error_detected = on_error

    print("\nAI is now watching your screen...")
    print("It will provide insights every 2 seconds.")
    print("Press Ctrl+C to stop\n")

    try:
        # Observe for 30 seconds
        task = asyncio.create_task(observer.start_observing())
        await asyncio.sleep(30)
        observer.stop_observing()
        await task
    except KeyboardInterrupt:
        observer.stop_observing()

    # Show learning summary
    summary = observer.get_learning_summary()
    print(f"\n📊 Learning Summary:")
    print(f"   Observations: {summary['total_observations']}")
    print(f"   Patterns learned: {summary['patterns_learned']}")


# ============================================================================
# Example 6: Self-Debugging Demo
# ============================================================================

async def example_6_self_debugging():
    """
    Demonstrate self-debugging capabilities

    When automation fails, AI analyzes the screen and suggests fixes!
    """

    print("\n" + "="*70)
    print("Example 6: Self-Debugging Demo")
    print("="*70)

    observer = LiveCVObserver(
        claude_api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Simulate a failure scenario
    import mss
    import numpy as np

    print("\nCapturing current screen state...")

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))[:, :, :3]

    print("Asking AI to debug a simulated failure...\n")

    # Ask AI to debug
    debug_result = await observer.debug_failure(
        error_message="Element 'Submit Button' not found on page",
        expected_state="Submit button should be visible after form fill",
        actual_screenshot=screenshot
    )

    print("\n🔧 Debug Analysis:")
    print(f"   Diagnosis: {debug_result['diagnosis']}")
    print(f"   Root Cause: {debug_result['root_cause']}")
    print("\n   Suggested Fixes:")
    for i, fix in enumerate(debug_result.get('fixes', []), 1):
        print(f"   {i}. {fix['strategy']} ({fix['likelihood']}% success)")
        print(f"      → {fix['implementation']}")

    if debug_result.get('alternative_approach'):
        print(f"\n   Alternative Approach:")
        print(f"   {debug_result['alternative_approach']}")


# ============================================================================
# Example 7: Batch Tutorial Creation
# ============================================================================

async def example_7_batch_creation():
    """Create multiple tutorials in batch"""

    print("\n" + "="*70)
    print("Example 7: Batch Tutorial Creation")
    print("="*70)

    agent = TutorialCreationAgent()

    topics = [
        "Python Decorators Explained",
        "Understanding Async/Await in Python",
        "Docker Multi-Stage Builds"
    ]

    videos = []

    for topic in topics:
        print(f"\n{'─'*70}")
        print(f"Creating: {topic}")
        print(f"{'─'*70}")

        video = await agent.create_tutorial(
            topic=topic,
            target_audience="intermediate",
            max_duration_minutes=10,
            auto_execute=True
        )

        if video:
            videos.append(video)

    print("\n" + "="*70)
    print(f"✅ Batch Complete: {len(videos)} tutorials created")
    print("="*70)

    for video in videos:
        print(f"  - {video}")


# ============================================================================
# Example 8: Integration with Open Agent Studio
# ============================================================================

async def example_8_integration():
    """
    Example showing integration with Open Agent Studio workflows
    """

    print("\n" + "="*70)
    print("Example 8: Integration with Open Agent Studio")
    print("="*70)

    from tutorial_agent.planner import TutorialPlanner

    # Step 1: Plan tutorial (can be saved as node in graph)
    planner = TutorialPlanner()

    plan = await planner.plan_tutorial(
        topic="Creating Automation Workflows",
        target_audience="intermediate"
    )

    # Step 2: Save plan as reusable workflow
    plan_path = Path("workflows/automation_tutorial.json")
    planner.save_plan(plan, plan_path)

    print(f"\n✓ Tutorial plan saved: {plan_path}")
    print(f"  This plan can now be:")
    print(f"  - Loaded into Open Agent Studio node graph")
    print(f"  - Reused for multiple recordings")
    print(f"  - Modified and customized")

    # Step 3: Load and execute plan
    loaded_plan = planner.load_plan(plan_path)

    print(f"\n✓ Plan loaded: {loaded_plan.title}")
    print(f"  Steps: {len(loaded_plan.steps)}")

    # Step 4: Execute with agent
    agent = TutorialCreationAgent()
    # video = await agent.create_from_plan(plan_path)


# ============================================================================
# Main Menu
# ============================================================================

async def main():
    """Interactive example selector"""

    print("\n" + "="*70)
    print("🎬 AI Tutorial Creation Agent - Examples")
    print("="*70)

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ Error: ANTHROPIC_API_KEY not set!")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        return

    examples = {
        "1": ("Simple Tutorial Creation", example_1_simple_tutorial),
        "2": ("Manual Recording Mode", example_2_manual_recording),
        "3": ("Self-Aware Mode (Live CV)", example_3_self_aware_mode),
        "4": ("Custom Configuration", example_4_custom_config),
        "5": ("Live CV Observer Standalone", example_5_live_cv_standalone),
        "6": ("Self-Debugging Demo", example_6_self_debugging),
        "7": ("Batch Tutorial Creation", example_7_batch_creation),
        "8": ("Integration with Open Agent Studio", example_8_integration),
    }

    print("\nChoose an example:")
    print()
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")

    print(f"\n  0. Run all examples")
    print(f"  q. Quit")

    choice = input("\nChoice: ").strip()

    if choice == 'q':
        print("Goodbye!")
        return

    if choice == '0':
        # Run all examples
        for key, (name, func) in examples.items():
            print(f"\n\n{'#'*70}")
            print(f"Running: {name}")
            print(f"{'#'*70}")
            await func()
        return

    if choice in examples:
        name, func = examples[choice]
        await func()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    asyncio.run(main())
