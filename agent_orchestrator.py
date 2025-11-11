#!/usr/bin/env python3
"""
Claude Agent SDK Orchestrator
Main agent loop that understands tasks, plans execution, and self-debugs
"""

import anthropic
import json
import asyncio
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskStep:
    """Represents a single step in task execution"""
    description: str
    tool: str
    args: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, error
    result: Any = None
    error: str = None
    screenshot: str = None  # base64 screenshot
    timestamp: datetime = None


class AgentOrchestrator:
    """
    Main orchestrator that uses Claude Agent SDK to:
    1. Understand user intent
    2. Plan task execution
    3. Execute via MCP servers
    4. Self-debug failures
    5. Generate reusable workflows
    """

    def __init__(self, api_key: str, mcp_clients: Dict[str, Any]):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.mcp_clients = mcp_clients
        self.conversation_history = []
        self.current_task = None
        self.task_steps: List[TaskStep] = []

        # Callbacks for UI updates
        self.on_thinking_start: Callable = None
        self.on_thinking_end: Callable = None
        self.on_step_update: Callable = None
        self.on_task_complete: Callable = None
        self.on_error: Callable = None

    async def process_user_message(self, message: str) -> str:
        """
        Main entry point: User sends a message, agent processes it
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Notify UI: Agent is thinking
        if self.on_thinking_start:
            self.on_thinking_start("Understanding your request...")

        # Step 1: Understand intent and create plan
        plan = await self._understand_and_plan(message)

        if not plan:
            return "I'm sorry, I couldn't understand your request. Could you rephrase it?"

        # Step 2: Execute plan
        result = await self._execute_plan(plan)

        # Step 3: Generate workflow (if successful)
        if result["success"]:
            workflow = await self._generate_workflow(plan, result)
            result["workflow"] = workflow

        # Notify UI: Done
        if self.on_thinking_end:
            self.on_thinking_end()

        # Return response
        response = self._format_response(result)

        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    async def _understand_and_plan(self, message: str) -> Dict:
        """
        Use Claude to understand intent and create execution plan
        """
        system_prompt = """You are an expert automation agent. Your job is to:
1. Understand what the user wants to automate
2. Break it down into specific, executable steps
3. Choose the right tools (desktop vs browser)
4. Create a detailed plan

Available capabilities:
- **Desktop Automation**: Click, type, OCR, image recognition (any application)
- **Browser Automation**: Web navigation, form filling, data extraction (Playwright)
- **Vision AI**: Semantic element detection, screenshot analysis

For each step, specify:
- **action**: What to do
- **tool**: Which MCP server to use (desktop, browser, vision)
- **tool_name**: Specific tool (e.g., "click", "navigate", "ocr_text")
- **args**: Tool arguments
- **expected_result**: What we expect to happen
- **verification**: How to verify success

Return JSON:
{
  "task_summary": "brief description",
  "task_type": "desktop|browser|hybrid",
  "complexity": "simple|moderate|complex",
  "estimated_time": "seconds",
  "steps": [
    {
      "step_number": 1,
      "description": "human-readable description",
      "action": "specific action",
      "tool": "desktop|browser|vision",
      "tool_name": "specific_tool",
      "args": {},
      "expected_result": "what should happen",
      "verification": "how to check success"
    }
  ],
  "success_criteria": "how to know if entire task succeeded"
}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=self.conversation_history
        )

        # Parse response
        content = response.content[0].text

        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            plan = json.loads(content)
            return plan
        except json.JSONDecodeError as e:
            print(f"Failed to parse plan: {e}")
            print(f"Content: {content}")
            return None

    async def _execute_plan(self, plan: Dict) -> Dict:
        """
        Execute the plan step-by-step with self-debugging
        """
        self.task_steps = []
        results = []
        all_success = True

        for step_data in plan["steps"]:
            # Create step object
            step = TaskStep(
                description=step_data["description"],
                tool=step_data["tool"],
                args=step_data.get("args", {}),
                timestamp=datetime.now()
            )
            self.task_steps.append(step)

            # Notify UI
            if self.on_step_update:
                self.on_step_update(step.description, "running")

            # Execute step
            step.status = "running"

            try:
                # Determine which MCP client to use
                if step_data["tool"] == "desktop":
                    mcp_client = self.mcp_clients.get("desktop")
                elif step_data["tool"] == "browser":
                    mcp_client = self.mcp_clients.get("browser")
                elif step_data["tool"] == "vision":
                    mcp_client = self.mcp_clients.get("vision")
                else:
                    raise ValueError(f"Unknown tool type: {step_data['tool']}")

                if not mcp_client:
                    raise RuntimeError(f"MCP client for '{step_data['tool']}' not available")

                # Call tool
                tool_name = step_data["tool_name"]
                result = await mcp_client.call_tool(tool_name, step_data.get("args", {}))

                step.result = result
                step.status = "completed"

                # Notify UI
                if self.on_step_update:
                    self.on_step_update(step.description, "completed")

                results.append({
                    "step": step_data["step_number"],
                    "success": True,
                    "result": result
                })

            except Exception as e:
                step.status = "error"
                step.error = str(e)
                all_success = False

                # Notify UI
                if self.on_step_update:
                    self.on_step_update(step.description, "error")

                # Try to self-debug
                fixed = await self._self_debug(step, plan, results)

                if fixed:
                    step.status = "completed"
                    all_success = True
                    if self.on_step_update:
                        self.on_step_update(f"✓ Fixed: {step.description}", "completed")
                else:
                    # Critical failure, stop execution
                    if self.on_error:
                        self.on_error(f"Failed: {step.description}", str(e))
                    break

        return {
            "success": all_success,
            "steps": results,
            "task_summary": plan["task_summary"]
        }

    async def _self_debug(self, failed_step: TaskStep, plan: Dict, previous_results: List) -> bool:
        """
        Self-debugging: Analyze failure and attempt fix
        """
        print(f"🔧 Self-debugging step: {failed_step.description}")

        # Take screenshot for context
        screenshot_result = None
        try:
            desktop_client = self.mcp_clients.get("desktop")
            if desktop_client:
                screenshot_result = await desktop_client.call_tool("take_screenshot", {})
        except:
            pass

        # Ask Claude to analyze the failure
        debug_prompt = f"""A step in the automation failed. Please analyze and suggest a fix.

**Failed Step:**
{json.dumps({
    "description": failed_step.description,
    "tool": failed_step.tool,
    "args": failed_step.args,
    "error": failed_step.error
}, indent=2)}

**Previous Successful Steps:**
{json.dumps(previous_results, indent=2)}

**Original Plan:**
{json.dumps(plan, indent=2)}

Based on the error, what likely went wrong? Suggest a fix as JSON:
{{
  "diagnosis": "what went wrong",
  "fix_strategy": "retry|modify_args|skip|alternative_approach",
  "new_args": {{}},  // if modify_args
  "alternative_tool": "",  // if alternative_approach
  "explanation": "why this should work"
}}"""

        debug_messages = self.conversation_history + [{
            "role": "user",
            "content": debug_prompt
        }]

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=debug_messages
        )

        content = response.content[0].text

        try:
            # Parse fix suggestion
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            fix = json.loads(content)

            # Apply fix
            if fix["fix_strategy"] == "retry":
                # Simple retry
                print(f"  → Retrying with same args...")
                # Implement retry logic
                return False  # TODO: Implement

            elif fix["fix_strategy"] == "modify_args":
                # Retry with modified args
                print(f"  → Retrying with modified args: {fix['new_args']}")
                failed_step.args.update(fix["new_args"])
                # TODO: Actually retry the step
                return False

            elif fix["fix_strategy"] == "alternative_approach":
                # Try different tool
                print(f"  → Trying alternative: {fix['alternative_tool']}")
                # TODO: Implement alternative
                return False

            else:
                return False

        except Exception as e:
            print(f"Failed to parse debug suggestion: {e}")
            return False

    async def _generate_workflow(self, plan: Dict, result: Dict) -> Dict:
        """
        Generate a reusable workflow from successful execution
        """
        # Convert executed steps into Open Agent Studio node graph format
        nodes = []
        connections = []

        for i, step in enumerate(self.task_steps):
            if step.status != "completed":
                continue

            # Create node definition
            node = {
                "id": f"node_{i}",
                "name": step.description,
                "type": self._map_tool_to_node_type(step.tool, step.args),
                "custom": {
                    "Data": json.dumps({
                        "type": step.tool,
                        **step.args
                    })
                }
            }
            nodes.append(node)

            # Create connection to previous node
            if i > 0:
                connections.append({
                    "out": [f"node_{i-1}", 0],
                    "in": [f"node_{i}", 0]
                })

        workflow = {
            "nodes": {node["id"]: node for node in nodes},
            "connections": connections,
            "metadata": {
                "name": plan["task_summary"],
                "created": datetime.now().isoformat(),
                "task_type": plan.get("task_type", "unknown"),
                "success_rate": "100%"
            }
        }

        return workflow

    def _map_tool_to_node_type(self, tool: str, args: Dict) -> str:
        """Map MCP tool to Open Agent Studio node type"""
        # TODO: Create proper mapping
        mapping = {
            "take_screenshot": "nodes.widget.ImageNode",
            "ocr_text": "nodes.widget.ImageNode",
            "click": "nodes.basic.BasicNodeA",
            "type_text": "nodes.basic.BasicNodeB",
            "navigate": "nodes.basic.BasicNodeA",
        }
        return mapping.get(tool, "nodes.basic.BasicNodeA")

    def _format_response(self, result: Dict) -> str:
        """Format execution result as user-friendly message"""
        if result["success"]:
            response = f"✓ **Task completed successfully!**\n\n"
            response += f"**Summary:** {result['task_summary']}\n\n"
            response += f"**Steps executed:** {len(result['steps'])}\n\n"

            if result.get("workflow"):
                response += "I've saved this as a reusable workflow. You can run it anytime or edit it in the node graph."

            return response
        else:
            response = f"✗ **Task partially completed**\n\n"
            response += f"Completed {len([s for s in result['steps'] if s['success']])} of {len(result['steps'])} steps.\n\n"
            response += "Some steps failed. Would you like me to try a different approach?"
            return response


# Example usage
async def main():
    """Test the orchestrator"""

    # Mock MCP clients (in real implementation, these would be actual MCP connections)
    class MockMCPClient:
        def __init__(self, name):
            self.name = name

        async def call_tool(self, tool_name, args):
            print(f"  → Calling {self.name}.{tool_name}({args})")
            await asyncio.sleep(1)  # Simulate work
            return {"success": True, "data": "mock result"}

    mcp_clients = {
        "desktop": MockMCPClient("desktop"),
        "browser": MockMCPClient("browser"),
        "vision": MockMCPClient("vision")
    }

    # Create orchestrator
    orchestrator = AgentOrchestrator(
        api_key="your-api-key",
        mcp_clients=mcp_clients
    )

    # Set up callbacks
    def on_thinking_start(status):
        print(f"🤔 {status}")

    def on_step_update(description, status):
        icons = {"running": "⟳", "completed": "✓", "error": "✗"}
        print(f"  {icons[status]} {description}")

    orchestrator.on_thinking_start = on_thinking_start
    orchestrator.on_step_update = on_step_update

    # Process message
    response = await orchestrator.process_user_message(
        "Open Gmail and mark all unread emails as read"
    )

    print(f"\n🤖 Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
