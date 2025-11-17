#!/usr/bin/env python3
"""
Open Agent Studio - Deployment Management MCP Server
Provides deployment control tools for chat-based management
"""

import json
import os
import sys
import requests
from typing import Any

# Add project to path
project_path = os.getenv('PYTHON_PATH', os.path.dirname(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Configuration
CONTROL_API = os.getenv('CONTROL_API_URL', 'http://localhost:5000')
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'dev-token')

HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json'
}


def request_api(method: str, endpoint: str, data: Any = None) -> dict:
    """Make request to control API"""
    url = f'{CONTROL_API}{endpoint}'

    try:
        if method == 'GET':
            response = requests.get(url, headers=HEADERS, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, json=data, timeout=10)
        else:
            return {'error': f'Unsupported method: {method}'}

        if response.status_code >= 400:
            return {'error': f'API error: {response.status_code}', 'response': response.text}

        return response.json()
    except requests.exceptions.ConnectionError as e:
        return {'error': f'Could not connect to {CONTROL_API}: {str(e)}'}
    except Exception as e:
        return {'error': str(e)}


# ==================== MCP TOOL DEFINITIONS ====================

TOOLS = {
    "deployment_status": {
        "description": "Get current deployment status and service information",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "start_deployment": {
        "description": "Start all containers",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "stop_deployment": {
        "description": "Stop all containers",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "restart_deployment": {
        "description": "Restart all containers",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "rebuild_deployment": {
        "description": "Rebuild and start all containers",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "list_services": {
        "description": "List all available services",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "start_service": {
        "description": "Start a specific service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name (e.g., openagent, control-panel, postgres)"
                }
            },
            "required": ["service"]
        }
    },
    "stop_service": {
        "description": "Stop a specific service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name"
                }
            },
            "required": ["service"]
        }
    },
    "restart_service": {
        "description": "Restart a specific service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name"
                }
            },
            "required": ["service"]
        }
    },
    "get_logs": {
        "description": "Get container logs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name (optional, defaults to all services)"
                },
                "lines": {
                    "type": "integer",
                    "description": "Number of log lines to retrieve (default: 50)"
                }
            },
            "required": []
        }
    },
    "get_metrics": {
        "description": "Get CPU and memory metrics for containers",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "health_check": {
        "description": "Run system health check",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "list_workflows": {
        "description": "List available workflows",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_workflow": {
        "description": "Get workflow details",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Workflow name"
                }
            },
            "required": ["name"]
        }
    },
    "get_deployment_config": {
        "description": "Get deployment configuration and endpoints",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


# ==================== TOOL IMPLEMENTATIONS ====================

def tool_deployment_status() -> dict:
    """Get deployment status"""
    return request_api('GET', '/api/status')


def tool_start_deployment() -> dict:
    """Start all containers"""
    result = request_api('POST', '/api/deploy/up')
    return {
        **result,
        'message': 'Deployment is starting. Containers may take 30-60 seconds to become available.'
    }


def tool_stop_deployment() -> dict:
    """Stop all containers"""
    result = request_api('POST', '/api/deploy/down')
    return {
        **result,
        'message': 'Deployment is stopping.'
    }


def tool_restart_deployment() -> dict:
    """Restart all containers"""
    result = request_api('POST', '/api/deploy/restart')
    return {
        **result,
        'message': 'Deployment is restarting. This may take 30-60 seconds.'
    }


def tool_rebuild_deployment() -> dict:
    """Rebuild and start containers"""
    result = request_api('POST', '/api/deploy/rebuild')
    return {
        **result,
        'message': 'Rebuilding containers. This may take several minutes depending on dependencies.'
    }


def tool_list_services() -> dict:
    """List all services"""
    return request_api('GET', '/api/services')


def tool_start_service(service: str) -> dict:
    """Start specific service"""
    return request_api('POST', f'/api/service/{service}/start')


def tool_stop_service(service: str) -> dict:
    """Stop specific service"""
    return request_api('POST', f'/api/service/{service}/stop')


def tool_restart_service(service: str) -> dict:
    """Restart specific service"""
    return request_api('POST', f'/api/service/{service}/restart')


def tool_get_logs(service: str = None, lines: int = 50) -> dict:
    """Get container logs"""
    if service:
        return request_api('GET', f'/api/logs/{service}?lines={lines}')
    else:
        return request_api('GET', f'/api/logs/all?lines={lines}')


def tool_get_metrics() -> dict:
    """Get container metrics"""
    return request_api('GET', '/api/metrics')


def tool_health_check() -> dict:
    """Run health check"""
    status = request_api('GET', '/api/status')
    agent = request_api('GET', '/api/agent/health')

    return {
        'deployment_healthy': 'docker' in status and status['docker'] is not None,
        'agent_healthy': agent.get('agent_healthy', False),
        'deployment_details': status,
        'agent_details': agent,
        'summary': {
            'control_panel': 'healthy' if 'docker' in status else 'unhealthy',
            'agent_api': 'healthy' if agent.get('agent_healthy') else 'unhealthy',
            'overall': 'healthy' if (
                'docker' in status and agent.get('agent_healthy')
            ) else 'unhealthy'
        }
    }


def tool_list_workflows() -> dict:
    """List workflows"""
    return request_api('GET', '/api/workflows')


def tool_get_workflow(name: str) -> dict:
    """Get workflow details"""
    return request_api('GET', f'/api/workflow/{name}')


def tool_get_deployment_config() -> dict:
    """Get deployment configuration"""
    return request_api('GET', '/api/config')


# ==================== MCP PROTOCOL HANDLERS ====================

def handle_list_tools():
    """Handle tools/list request"""
    return {
        "tools": [
            {
                "name": tool_name,
                "description": tool_def["description"],
                "inputSchema": tool_def["inputSchema"]
            }
            for tool_name, tool_def in TOOLS.items()
        ]
    }


def handle_call_tool(name: str, arguments: dict) -> dict:
    """Handle tools/call request"""
    tool_name = name

    # Deployment commands
    if tool_name == "deployment_status":
        return tool_deployment_status()
    elif tool_name == "start_deployment":
        return tool_start_deployment()
    elif tool_name == "stop_deployment":
        return tool_stop_deployment()
    elif tool_name == "restart_deployment":
        return tool_restart_deployment()
    elif tool_name == "rebuild_deployment":
        return tool_rebuild_deployment()

    # Service commands
    elif tool_name == "list_services":
        return tool_list_services()
    elif tool_name == "start_service":
        return tool_start_service(arguments.get("service"))
    elif tool_name == "stop_service":
        return tool_stop_service(arguments.get("service"))
    elif tool_name == "restart_service":
        return tool_restart_service(arguments.get("service"))

    # Logging and monitoring
    elif tool_name == "get_logs":
        return tool_get_logs(
            arguments.get("service"),
            arguments.get("lines", 50)
        )
    elif tool_name == "get_metrics":
        return tool_get_metrics()
    elif tool_name == "health_check":
        return tool_health_check()

    # Workflow commands
    elif tool_name == "list_workflows":
        return tool_list_workflows()
    elif tool_name == "get_workflow":
        return tool_get_workflow(arguments.get("name"))

    # Configuration
    elif tool_name == "get_deployment_config":
        return tool_get_deployment_config()

    else:
        return {"error": f"Unknown tool: {tool_name}"}


def handle_request(request_json: dict) -> dict:
    """Handle incoming request"""
    method = request_json.get("method")
    params = request_json.get("params", {})

    if method == "tools/list":
        return handle_list_tools()
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = handle_call_tool(tool_name, arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    elif method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "openagent-deployment",
                "version": "1.0.0"
            }
        }
    else:
        return {"error": f"Unknown method: {method}"}


# ==================== MAIN ====================

def main():
    """Main entry point for MCP server"""
    import sys
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting Open Agent Studio Deployment MCP Server")
    logger.info(f"Control API: {CONTROL_API}")

    # Simple MCP implementation
    # In production, this would use the proper MCP protocol
    # For now, we'll implement a stdio-based MCP server

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                request_json = json.loads(line)
                response = handle_request(request_json)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON"}))
                sys.stdout.flush()
            except Exception as e:
                print(json.dumps({"error": str(e)}))
                sys.stdout.flush()

    except KeyboardInterrupt:
        logger.info("Shutting down")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
