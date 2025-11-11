#!/usr/bin/env python3
"""
Desktop Automation MCP Server
Exposes Open Agent Studio capabilities via Model Context Protocol
"""

import asyncio
import json
import base64
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io


class DesktopAutomationMCP:
    """MCP Server for desktop automation capabilities"""

    def __init__(self):
        self.server = Server("desktop-automation")
        self.screenshot_history = []
        self.setup_handlers()

    def setup_handlers(self):
        """Register all MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available desktop automation tools"""
            return [
                Tool(
                    name="take_screenshot",
                    description="Capture screenshot of entire screen or specific region. Returns image and base64.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "object",
                                "description": "Optional region to capture {x, y, width, height}",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "width": {"type": "number"},
                                    "height": {"type": "number"}
                                }
                            }
                        }
                    }
                ),
                Tool(
                    name="ocr_text",
                    description="Extract text from screen region using OCR. Returns detected text.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "object",
                                "required": ["x", "y", "width", "height"],
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "width": {"type": "number"},
                                    "height": {"type": "number"}
                                }
                            },
                            "engine": {
                                "type": "string",
                                "enum": ["pytesseract", "deepseek"],
                                "default": "pytesseract"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="find_element",
                    description="Find UI element on screen using semantic description or image template. Returns coordinates.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Natural language description (e.g., 'blue submit button')"
                            },
                            "template_image": {
                                "type": "string",
                                "description": "Base64 encoded template image to match"
                            },
                            "confidence_threshold": {
                                "type": "number",
                                "default": 0.8,
                                "description": "Minimum confidence for match (0-1)"
                            }
                        }
                    }
                ),
                Tool(
                    name="click",
                    description="Click at coordinates or on found element",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "button": {
                                "type": "string",
                                "enum": ["left", "right", "middle"],
                                "default": "left"
                            },
                            "clicks": {
                                "type": "number",
                                "default": 1
                            }
                        },
                        "required": ["x", "y"]
                    }
                ),
                Tool(
                    name="type_text",
                    description="Type text using keyboard",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to type"
                            },
                            "interval": {
                                "type": "number",
                                "default": 0.05,
                                "description": "Delay between keystrokes (seconds)"
                            }
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="press_key",
                    description="Press keyboard key or key combination",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "keys": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key(s) to press, e.g., ['ctrl', 'c']"
                            }
                        },
                        "required": ["keys"]
                    }
                ),
                Tool(
                    name="move_mouse",
                    description="Move mouse cursor to coordinates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "duration": {
                                "type": "number",
                                "default": 0.5,
                                "description": "Movement duration (seconds)"
                            }
                        },
                        "required": ["x", "y"]
                    }
                ),
                Tool(
                    name="analyze_screen",
                    description="Use vision AI to analyze current screen and answer questions about it",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Question about the screen (e.g., 'What buttons are visible?')"
                            },
                            "region": {
                                "type": "object",
                                "description": "Optional region to analyze"
                            }
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="wait_for_element",
                    description="Wait until element appears on screen (polling with timeout)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Element description"
                            },
                            "timeout": {
                                "type": "number",
                                "default": 30,
                                "description": "Timeout in seconds"
                            },
                            "poll_interval": {
                                "type": "number",
                                "default": 1,
                                "description": "Check interval in seconds"
                            }
                        },
                        "required": ["description"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Execute tool and return results"""

            if name == "take_screenshot":
                return await self._take_screenshot(arguments)
            elif name == "ocr_text":
                return await self._ocr_text(arguments)
            elif name == "find_element":
                return await self._find_element(arguments)
            elif name == "click":
                return await self._click(arguments)
            elif name == "type_text":
                return await self._type_text(arguments)
            elif name == "press_key":
                return await self._press_key(arguments)
            elif name == "move_mouse":
                return await self._move_mouse(arguments)
            elif name == "analyze_screen":
                return await self._analyze_screen(arguments)
            elif name == "wait_for_element":
                return await self._wait_for_element(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _take_screenshot(self, args: dict) -> Sequence[TextContent | ImageContent]:
        """Capture screenshot"""
        region = args.get("region")

        if region:
            screenshot = pyautogui.screenshot(
                region=(region["x"], region["y"], region["width"], region["height"])
            )
        else:
            screenshot = pyautogui.screenshot()

        # Convert to base64
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Store in history
        self.screenshot_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "base64": img_base64,
            "region": region
        })

        return [
            ImageContent(
                type="image",
                data=img_base64,
                mimeType="image/png"
            ),
            TextContent(
                type="text",
                text=f"Screenshot captured: {screenshot.size[0]}x{screenshot.size[1]}px"
            )
        ]

    async def _ocr_text(self, args: dict) -> Sequence[TextContent]:
        """Extract text using OCR"""
        region = args["region"]
        engine = args.get("engine", "pytesseract")

        # Capture region
        screenshot = pyautogui.screenshot(
            region=(region["x"], region["y"], region["width"], region["height"])
        )

        # Convert to OpenCV format
        img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Preprocess
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        if engine == "pytesseract":
            # Use pytesseract
            text = pytesseract.image_to_string(thresh, lang='eng', config='--psm 6')
            data = pytesseract.image_to_data(thresh, lang='eng', output_type=pytesseract.Output.DICT)

            # Calculate confidence
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "text": text.strip(),
                        "confidence": round(avg_confidence, 2),
                        "engine": "pytesseract",
                        "word_count": len(text.split())
                    }, indent=2)
                )
            ]

        elif engine == "deepseek":
            # TODO: Integrate DeepSeek-OCR when available
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "DeepSeek-OCR not yet implemented",
                        "fallback": "Use pytesseract engine"
                    })
                )
            ]

    async def _find_element(self, args: dict) -> Sequence[TextContent]:
        """Find element on screen"""
        description = args.get("description")
        template_image = args.get("template_image")
        confidence_threshold = args.get("confidence_threshold", 0.8)

        if template_image:
            # Template matching approach
            screenshot = pyautogui.screenshot()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Decode template
            template_bytes = base64.b64decode(template_image)
            template_np = np.frombuffer(template_bytes, np.uint8)
            template_cv = cv2.imdecode(template_np, cv2.IMREAD_COLOR)

            # Multi-scale template matching
            best_match = None
            best_confidence = 0

            for scale in np.linspace(0.5, 1.5, 20):
                resized = cv2.resize(template_cv, None, fx=scale, fy=scale)

                if resized.shape[0] > screenshot_cv.shape[0] or resized.shape[1] > screenshot_cv.shape[1]:
                    continue

                result = cv2.matchTemplate(screenshot_cv, resized, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val > best_confidence:
                    best_confidence = max_val
                    best_match = {
                        "x": int(max_loc[0] + resized.shape[1] / 2),
                        "y": int(max_loc[1] + resized.shape[0] / 2),
                        "width": resized.shape[1],
                        "height": resized.shape[0],
                        "confidence": float(max_val),
                        "scale": float(scale)
                    }

            if best_match and best_confidence >= confidence_threshold:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "found": True,
                            "method": "template_matching",
                            **best_match
                        }, indent=2)
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "found": False,
                            "best_confidence": float(best_confidence),
                            "threshold": confidence_threshold
                        })
                    )
                ]

        elif description:
            # Semantic targeting approach (requires vision model)
            # TODO: Integrate with BLIP/LLM for semantic element detection
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Semantic targeting requires vision model integration",
                        "suggestion": "Use template_image instead, or implement vision model"
                    })
                )
            ]

    async def _click(self, args: dict) -> Sequence[TextContent]:
        """Perform mouse click"""
        x = args["x"]
        y = args["y"]
        button = args.get("button", "left")
        clicks = args.get("clicks", 1)

        pyautogui.click(x, y, clicks=clicks, button=button)

        return [
            TextContent(
                type="text",
                text=f"Clicked {button} button {clicks} time(s) at ({x}, {y})"
            )
        ]

    async def _type_text(self, args: dict) -> Sequence[TextContent]:
        """Type text"""
        text = args["text"]
        interval = args.get("interval", 0.05)

        pyautogui.write(text, interval=interval)

        return [
            TextContent(
                type="text",
                text=f"Typed {len(text)} characters: '{text[:50]}...'" if len(text) > 50 else f"Typed: '{text}'"
            )
        ]

    async def _press_key(self, args: dict) -> Sequence[TextContent]:
        """Press keyboard key(s)"""
        keys = args["keys"]

        if len(keys) == 1:
            pyautogui.press(keys[0])
            action = f"Pressed '{keys[0]}'"
        else:
            pyautogui.hotkey(*keys)
            action = f"Pressed key combination: {' + '.join(keys)}"

        return [
            TextContent(
                type="text",
                text=action
            )
        ]

    async def _move_mouse(self, args: dict) -> Sequence[TextContent]:
        """Move mouse cursor"""
        x = args["x"]
        y = args["y"]
        duration = args.get("duration", 0.5)

        pyautogui.moveTo(x, y, duration=duration)

        return [
            TextContent(
                type="text",
                text=f"Moved mouse to ({x}, {y}) in {duration}s"
            )
        ]

    async def _analyze_screen(self, args: dict) -> Sequence[TextContent | ImageContent]:
        """Analyze screen with vision AI"""
        question = args["question"]
        region = args.get("region")

        # Capture screenshot
        if region:
            screenshot = pyautogui.screenshot(
                region=(region["x"], region["y"], region["width"], region["height"])
            )
        else:
            screenshot = pyautogui.screenshot()

        # Convert to base64
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Return screenshot for Claude to analyze
        # The actual vision analysis will be done by Claude Agent SDK
        return [
            ImageContent(
                type="image",
                data=img_base64,
                mimeType="image/png"
            ),
            TextContent(
                type="text",
                text=f"Screen captured for analysis. Question: {question}"
            )
        ]

    async def _wait_for_element(self, args: dict) -> Sequence[TextContent]:
        """Wait for element to appear"""
        description = args["description"]
        timeout = args.get("timeout", 30)
        poll_interval = args.get("poll_interval", 1)

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Try to find element
            result = await self._find_element({"description": description})
            result_data = json.loads(result[0].text)

            if result_data.get("found"):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "found": True,
                            "wait_time": round(asyncio.get_event_loop().time() - start_time, 2),
                            **result_data
                        }, indent=2)
                    )
                ]

            await asyncio.sleep(poll_interval)

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "found": False,
                    "timeout": timeout,
                    "description": description
                })
            )
        ]

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


if __name__ == "__main__":
    mcp = DesktopAutomationMCP()
    asyncio.run(mcp.run())
