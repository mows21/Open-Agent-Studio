#!/usr/bin/env python3
"""
Playwright Browser Automation MCP Server
Provides browser automation capabilities via Model Context Protocol
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
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class PlaywrightBrowserMCP:
    """MCP Server for browser automation using Playwright"""

    def __init__(self):
        self.server = Server("playwright-browser")
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.setup_handlers()

    def setup_handlers(self):
        """Register all MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available browser automation tools"""
            return [
                Tool(
                    name="browser_launch",
                    description="Launch browser (Chrome/Firefox/Safari). Must be called before other browser operations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "browser_type": {
                                "type": "string",
                                "enum": ["chromium", "firefox", "webkit"],
                                "default": "chromium"
                            },
                            "headless": {
                                "type": "boolean",
                                "default": False,
                                "description": "Run in headless mode (no visible window)"
                            },
                            "viewport": {
                                "type": "object",
                                "properties": {
                                    "width": {"type": "number", "default": 1280},
                                    "height": {"type": "number", "default": 720}
                                }
                            }
                        }
                    }
                ),
                Tool(
                    name="navigate",
                    description="Navigate to URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to navigate to"
                            },
                            "wait_until": {
                                "type": "string",
                                "enum": ["load", "domcontentloaded", "networkidle"],
                                "default": "load"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="click_element",
                    description="Click element using selector or text",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {
                                "type": "string",
                                "description": "CSS selector, text content, or aria label"
                            },
                            "button": {
                                "type": "string",
                                "enum": ["left", "right", "middle"],
                                "default": "left"
                            },
                            "click_count": {
                                "type": "number",
                                "default": 1
                            },
                            "timeout": {
                                "type": "number",
                                "default": 30000,
                                "description": "Timeout in milliseconds"
                            }
                        },
                        "required": ["selector"]
                    }
                ),
                Tool(
                    name="fill_input",
                    description="Fill input field with text",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {
                                "type": "string",
                                "description": "CSS selector for input field"
                            },
                            "text": {
                                "type": "string",
                                "description": "Text to fill"
                            },
                            "clear_first": {
                                "type": "boolean",
                                "default": True
                            }
                        },
                        "required": ["selector", "text"]
                    }
                ),
                Tool(
                    name="press_key",
                    description="Press keyboard key",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Key to press (e.g., 'Enter', 'Escape', 'Control+A')"
                            },
                            "selector": {
                                "type": "string",
                                "description": "Optional: selector to focus before pressing key"
                            }
                        },
                        "required": ["key"]
                    }
                ),
                Tool(
                    name="screenshot",
                    description="Take screenshot of page or element",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {
                                "type": "string",
                                "description": "Optional: selector of element to screenshot"
                            },
                            "full_page": {
                                "type": "boolean",
                                "default": False,
                                "description": "Capture full scrollable page"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_text",
                    description="Extract text from element",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {
                                "type": "string",
                                "description": "CSS selector"
                            }
                        },
                        "required": ["selector"]
                    }
                ),
                Tool(
                    name="wait_for_selector",
                    description="Wait for element to appear in DOM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {
                                "type": "string",
                                "description": "CSS selector"
                            },
                            "state": {
                                "type": "string",
                                "enum": ["attached", "detached", "visible", "hidden"],
                                "default": "visible"
                            },
                            "timeout": {
                                "type": "number",
                                "default": 30000
                            }
                        },
                        "required": ["selector"]
                    }
                ),
                Tool(
                    name="evaluate_js",
                    description="Execute JavaScript in page context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "script": {
                                "type": "string",
                                "description": "JavaScript code to execute"
                            }
                        },
                        "required": ["script"]
                    }
                ),
                Tool(
                    name="get_page_content",
                    description="Get full HTML content of current page",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="network_intercept",
                    description="Intercept and monitor network requests",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url_pattern": {
                                "type": "string",
                                "description": "URL pattern to intercept (regex or glob)"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["log", "block", "modify"],
                                "default": "log"
                            }
                        }
                    }
                ),
                Tool(
                    name="browser_close",
                    description="Close browser and cleanup",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Execute tool and return results"""

            if name == "browser_launch":
                return await self._browser_launch(arguments)
            elif name == "navigate":
                return await self._navigate(arguments)
            elif name == "click_element":
                return await self._click_element(arguments)
            elif name == "fill_input":
                return await self._fill_input(arguments)
            elif name == "press_key":
                return await self._press_key(arguments)
            elif name == "screenshot":
                return await self._screenshot(arguments)
            elif name == "get_text":
                return await self._get_text(arguments)
            elif name == "wait_for_selector":
                return await self._wait_for_selector(arguments)
            elif name == "evaluate_js":
                return await self._evaluate_js(arguments)
            elif name == "get_page_content":
                return await self._get_page_content(arguments)
            elif name == "network_intercept":
                return await self._network_intercept(arguments)
            elif name == "browser_close":
                return await self._browser_close(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _browser_launch(self, args: dict) -> Sequence[TextContent]:
        """Launch browser"""
        browser_type = args.get("browser_type", "chromium")
        headless = args.get("headless", False)
        viewport = args.get("viewport", {"width": 1280, "height": 720})

        if self.playwright is None:
            self.playwright = await async_playwright().start()

        # Launch browser
        if browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(headless=headless)

        # Create context and page
        self.context = await self.browser.new_context(viewport=viewport)
        self.page = await self.context.new_page()

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "Browser launched",
                    "browser": browser_type,
                    "headless": headless,
                    "viewport": viewport
                }, indent=2)
            )
        ]

    async def _navigate(self, args: dict) -> Sequence[TextContent]:
        """Navigate to URL"""
        if not self.page:
            raise RuntimeError("Browser not launched. Call browser_launch first.")

        url = args["url"]
        wait_until = args.get("wait_until", "load")

        response = await self.page.goto(url, wait_until=wait_until)

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "url": url,
                    "status": response.status,
                    "title": await self.page.title(),
                    "url_final": self.page.url
                }, indent=2)
            )
        ]

    async def _click_element(self, args: dict) -> Sequence[TextContent]:
        """Click element"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        selector = args["selector"]
        button = args.get("button", "left")
        click_count = args.get("click_count", 1)
        timeout = args.get("timeout", 30000)

        try:
            await self.page.click(
                selector,
                button=button,
                click_count=click_count,
                timeout=timeout
            )

            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "clicked": True,
                        "selector": selector,
                        "button": button,
                        "click_count": click_count
                    }, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "clicked": False,
                        "error": str(e),
                        "selector": selector
                    })
                )
            ]

    async def _fill_input(self, args: dict) -> Sequence[TextContent]:
        """Fill input field"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        selector = args["selector"]
        text = args["text"]
        clear_first = args.get("clear_first", True)

        if clear_first:
            await self.page.fill(selector, "")

        await self.page.fill(selector, text)

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "filled": True,
                    "selector": selector,
                    "text_length": len(text)
                }, indent=2)
            )
        ]

    async def _press_key(self, args: dict) -> Sequence[TextContent]:
        """Press keyboard key"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        key = args["key"]
        selector = args.get("selector")

        if selector:
            await self.page.focus(selector)

        await self.page.keyboard.press(key)

        return [
            TextContent(
                type="text",
                text=f"Pressed key: {key}"
            )
        ]

    async def _screenshot(self, args: dict) -> Sequence[ImageContent | TextContent]:
        """Take screenshot"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        selector = args.get("selector")
        full_page = args.get("full_page", False)

        if selector:
            element = await self.page.query_selector(selector)
            if not element:
                return [
                    TextContent(
                        type="text",
                        text=f"Element not found: {selector}"
                    )
                ]
            screenshot_bytes = await element.screenshot()
        else:
            screenshot_bytes = await self.page.screenshot(full_page=full_page)

        # Convert to base64
        img_base64 = base64.b64encode(screenshot_bytes).decode()

        return [
            ImageContent(
                type="image",
                data=img_base64,
                mimeType="image/png"
            ),
            TextContent(
                type="text",
                text=f"Screenshot captured: {'element' if selector else 'full page' if full_page else 'viewport'}"
            )
        ]

    async def _get_text(self, args: dict) -> Sequence[TextContent]:
        """Extract text from element"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        selector = args["selector"]

        try:
            text = await self.page.text_content(selector)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "found": True,
                        "selector": selector,
                        "text": text
                    }, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "found": False,
                        "error": str(e)
                    })
                )
            ]

    async def _wait_for_selector(self, args: dict) -> Sequence[TextContent]:
        """Wait for selector"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        selector = args["selector"]
        state = args.get("state", "visible")
        timeout = args.get("timeout", 30000)

        try:
            await self.page.wait_for_selector(selector, state=state, timeout=timeout)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "found": True,
                        "selector": selector,
                        "state": state
                    }, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "found": False,
                        "timeout": timeout,
                        "error": str(e)
                    })
                )
            ]

    async def _evaluate_js(self, args: dict) -> Sequence[TextContent]:
        """Execute JavaScript"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        script = args["script"]

        try:
            result = await self.page.evaluate(script)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "result": result
                    }, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )
            ]

    async def _get_page_content(self, args: dict) -> Sequence[TextContent]:
        """Get page HTML content"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        content = await self.page.content()

        return [
            TextContent(
                type="text",
                text=content
            )
        ]

    async def _network_intercept(self, args: dict) -> Sequence[TextContent]:
        """Intercept network requests"""
        if not self.page:
            raise RuntimeError("Browser not launched")

        url_pattern = args.get("url_pattern", "*")
        action = args.get("action", "log")

        # Setup route handler
        async def route_handler(route):
            request = route.request
            print(f"Request: {request.method} {request.url}")

            if action == "block":
                await route.abort()
            elif action == "modify":
                # Could modify request/response here
                await route.continue_()
            else:  # log
                await route.continue_()

        await self.page.route(url_pattern, route_handler)

        return [
            TextContent(
                type="text",
                text=f"Network interception enabled for: {url_pattern} (action: {action})"
            )
        ]

    async def _browser_close(self, args: dict) -> Sequence[TextContent]:
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        return [
            TextContent(
                type="text",
                text="Browser closed"
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
    mcp = PlaywrightBrowserMCP()
    asyncio.run(mcp.run())
