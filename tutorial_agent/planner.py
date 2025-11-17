#!/usr/bin/env python3
"""
Tutorial Planner - Claude-powered tutorial planning
"""

import anthropic
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os


@dataclass
class TutorialStep:
    """Single step in tutorial"""
    step_number: int
    title: str
    description: str
    actions: List[str]  # Computer use actions
    narration: str
    duration_seconds: int
    recording_type: str  # "screen", "code_editor", "terminal", "browser"

    def to_dict(self):
        return asdict(self)


@dataclass
class TutorialPlan:
    """Complete tutorial plan"""
    title: str
    description: str
    difficulty: str
    duration_minutes: int
    prerequisites: List[str]
    steps: List[TutorialStep]
    intro_script: str
    outro_script: str

    def to_dict(self):
        return {
            **{k: v for k, v in asdict(self).items() if k != 'steps'},
            'steps': [step.to_dict() for step in self.steps]
        }


class TutorialPlanner:
    """Claude-powered tutorial planning agent"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    async def plan_tutorial(
        self,
        topic: str,
        target_audience: str = "intermediate",
        max_duration_minutes: int = 15
    ) -> TutorialPlan:
        """Generate complete tutorial plan from topic"""

        system_prompt = """You are an expert software tutorial creator. Your job is to:
1. Break down complex topics into clear, sequential steps
2. Plan what to show on screen for each step
3. Write engaging narration scripts
4. Estimate timing for each segment
5. Ensure the flow is logical and educational

For each tutorial step, specify:
- What to demonstrate (code, terminal, browser, etc.)
- Exact actions to perform using this action format:
  * open:vscode - Open VS Code
  * create_file:app.py - Create new file
  * type_code:print("hello") - Type code
  * type_text:some text - Type regular text
  * run_terminal:python app.py - Run terminal command
  * click:element_description - Click UI element
  * wait:2 - Wait 2 seconds
  * screenshot:filename.png - Take screenshot

- Narration script (what to say during the step)
- Duration estimate in seconds

Output VALID JSON with complete tutorial structure. Ensure all JSON is properly formatted."""

        user_prompt = f"""Create a comprehensive software dev tutorial about: {topic}

Target audience: {target_audience}
Max duration: {max_duration_minutes} minutes

Requirements:
- Practical, hands-on approach
- Clear step-by-step progression
- Include code examples where relevant
- Professional and engaging narration
- Realistic timing estimates

Output complete JSON plan:
{{
  "title": "Tutorial title",
  "description": "What the viewer will learn",
  "difficulty": "beginner|intermediate|advanced",
  "duration_minutes": {max_duration_minutes},
  "prerequisites": ["required knowledge"],
  "steps": [
    {{
      "step_number": 1,
      "title": "Step title",
      "description": "What happens in this step",
      "actions": [
        "open:vscode",
        "create_file:app.py",
        "type_code:import flask",
        "run_terminal:python app.py"
      ],
      "narration": "Full script to narrate during this step. Should be natural and conversational.",
      "duration_seconds": 45,
      "recording_type": "code_editor"
    }}
  ],
  "intro_script": "Tutorial introduction narration. Hook the viewer and explain what they'll learn.",
  "outro_script": "Conclusion and next steps. Recap what was learned and encourage practice."
}}

IMPORTANT: Output ONLY valid JSON, no markdown formatting or explanations."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            # Parse Claude's response
            content = response.content[0].text.strip()

            # Extract JSON from markdown if needed
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # Parse JSON
            plan_data = json.loads(content)

            # Convert to structured plan
            return TutorialPlan(
                title=plan_data["title"],
                description=plan_data["description"],
                difficulty=plan_data["difficulty"],
                duration_minutes=plan_data["duration_minutes"],
                prerequisites=plan_data["prerequisites"],
                steps=[
                    TutorialStep(**step) for step in plan_data["steps"]
                ],
                intro_script=plan_data["intro_script"],
                outro_script=plan_data["outro_script"]
            )

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse tutorial plan JSON: {e}")
            print(f"Response content:\n{content}")
            raise
        except Exception as e:
            print(f"❌ Error creating tutorial plan: {e}")
            raise

    def save_plan(self, plan: TutorialPlan, filepath: str):
        """Save tutorial plan to JSON file"""
        import json
        from pathlib import Path

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(plan.to_dict(), f, indent=2)

        print(f"💾 Saved tutorial plan to {filepath}")

    def load_plan(self, filepath: str) -> TutorialPlan:
        """Load tutorial plan from JSON file"""
        import json

        with open(filepath, 'r') as f:
            plan_data = json.load(f)

        return TutorialPlan(
            title=plan_data["title"],
            description=plan_data["description"],
            difficulty=plan_data["difficulty"],
            duration_minutes=plan_data["duration_minutes"],
            prerequisites=plan_data["prerequisites"],
            steps=[
                TutorialStep(**step) for step in plan_data["steps"]
            ],
            intro_script=plan_data["intro_script"],
            outro_script=plan_data["outro_script"]
        )


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_planner():
        planner = TutorialPlanner()

        plan = await planner.plan_tutorial(
            topic="Building a REST API with Flask",
            target_audience="intermediate",
            max_duration_minutes=10
        )

        print(f"\n{'='*60}")
        print(f"Tutorial Plan: {plan.title}")
        print(f"{'='*60}")
        print(f"Description: {plan.description}")
        print(f"Difficulty: {plan.difficulty}")
        print(f"Duration: {plan.duration_minutes} minutes")
        print(f"\nSteps:")
        for step in plan.steps:
            print(f"  {step.step_number}. {step.title} ({step.duration_seconds}s)")
            print(f"     Actions: {step.actions[:2]}...")

        # Save plan
        planner.save_plan(plan, "tutorial_plans/flask_api_tutorial.json")

    asyncio.run(test_planner())
