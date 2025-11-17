#!/usr/bin/env python3
"""
Open Agent Studio - Deployment CLI
Command-line tool for managing local deployments from chat
"""

import os
import requests
import json
import sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration
CONTROL_API = os.getenv('CONTROL_API_URL', 'http://localhost:5000')
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'dev-token')

HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json'
}


def request_api(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """Make request to control API"""
    url = f'{CONTROL_API}{endpoint}'

    try:
        if method == 'GET':
            response = requests.get(url, headers=HEADERS, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, json=data, timeout=10)
        else:
            return {'error': f'Unsupported method: {method}'}

        return response.json()
    except requests.exceptions.ConnectionError:
        return {'error': f'Could not connect to {CONTROL_API}'}
    except Exception as e:
        return {'error': str(e)}


# ==================== DEPLOYMENT COMMANDS ====================

def cmd_status():
    """Show deployment status"""
    result = request_api('GET', '/api/status')
    print(json.dumps(result, indent=2))


def cmd_up():
    """Start all containers"""
    result = request_api('POST', '/api/deploy/up')
    print(f"Deployment status: {result.get('status', 'unknown')}")
    if result.get('success'):
        print("✓ Containers are starting...")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")


def cmd_down():
    """Stop all containers"""
    result = request_api('POST', '/api/deploy/down')
    print(f"✓ Stopping deployment...")


def cmd_restart():
    """Restart all containers"""
    result = request_api('POST', '/api/deploy/restart')
    if result.get('success'):
        print("✓ Containers are restarting...")
    else:
        print(f"✗ Error: {result.get('error')}")


def cmd_rebuild():
    """Rebuild and start containers"""
    result = request_api('POST', '/api/deploy/rebuild')
    if result.get('success'):
        print("✓ Rebuilding containers...")
    else:
        print(f"✗ Error: {result.get('error')}")


def cmd_logs(service: Optional[str] = None, lines: int = 50):
    """View container logs"""
    if service:
        result = request_api('GET', f'/api/logs/{service}?lines={lines}')
    else:
        result = request_api('GET', f'/api/logs/all?lines={lines}')

    if result.get('success'):
        print(result.get('logs', ''))
    else:
        print(f"✗ Error: {result.get('error')}")


def cmd_services():
    """List all services"""
    result = request_api('GET', '/api/services')
    services = result.get('services', [])
    print(f"Available services ({len(services)}):")
    for svc in services:
        print(f"  - {svc}")


def cmd_service_start(service: str):
    """Start specific service"""
    result = request_api('POST', f'/api/service/{service}/start')
    if result.get('success'):
        print(f"✓ Starting {service}...")
    else:
        print(f"✗ Error: {result.get('error')}")


def cmd_service_stop(service: str):
    """Stop specific service"""
    result = request_api('POST', f'/api/service/{service}/stop')
    if result.get('success'):
        print(f"✓ Stopping {service}...")
    else:
        print(f"✗ Error: {result.get('error')}")


def cmd_service_restart(service: str):
    """Restart specific service"""
    result = request_api('POST', f'/api/service/{service}/restart')
    if result.get('success'):
        print(f"✓ Restarting {service}...")
    else:
        print(f"✗ Error: {result.get('error')}")


def cmd_workflows():
    """List workflows"""
    result = request_api('GET', '/api/workflows')
    workflows = result.get('workflows', [])
    print(f"Available workflows ({len(workflows)}):")
    for wf in workflows:
        print(f"  - {wf}")


def cmd_workflow_info(name: str):
    """Show workflow details"""
    result = request_api('GET', f'/api/workflow/{name}')
    if 'error' in result:
        print(f"✗ Error: {result.get('error')}")
    else:
        print(f"Workflow: {result.get('name')}")
        print(f"Last modified: {result.get('last_modified')}")
        print("Content:")
        print(json.dumps(result.get('content'), indent=2))


def cmd_metrics():
    """Show system metrics"""
    result = request_api('GET', '/api/metrics')
    metrics = result.get('metrics', [])
    print("Container Metrics:")
    print(f"{'Container':<20} {'CPU':<10} {'Memory':<15}")
    print("-" * 45)
    for m in metrics:
        print(f"{m['container']:<20} {m['cpu']:<10} {m['memory']:<15}")


def cmd_config():
    """Show configuration"""
    result = request_api('GET', '/api/config')
    print("Deployment Configuration:")
    print(json.dumps(result, indent=2))


def cmd_health():
    """Check system health"""
    result = request_api('GET', '/api/status')

    print("System Health Check:")
    print(f"Control Panel: {'✓ Healthy' if 'docker' in result else '✗ Error'}")

    agent_result = request_api('GET', '/api/agent/health')
    print(f"Agent API: {'✓ Healthy' if agent_result.get('agent_healthy') else '✗ Not responding'}")

    docker = result.get('docker', {})
    services = docker.get('services', [])
    print(f"Services: {len(services)} running")


# ==================== MAIN ====================

def main():
    """Main CLI handler"""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    # Deployment commands
    if command == 'status':
        cmd_status()
    elif command == 'up':
        cmd_up()
    elif command == 'down':
        cmd_down()
    elif command == 'restart':
        cmd_restart()
    elif command == 'rebuild':
        cmd_rebuild()

    # Logging commands
    elif command == 'logs':
        service = sys.argv[2] if len(sys.argv) > 2 else None
        lines = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        cmd_logs(service, lines)

    # Service commands
    elif command == 'services':
        cmd_services()
    elif command == 'start':
        if len(sys.argv) < 3:
            print("Usage: deployment_cli.py start <service>")
            return
        cmd_service_start(sys.argv[2])
    elif command == 'stop':
        if len(sys.argv) < 3:
            print("Usage: deployment_cli.py stop <service>")
            return
        cmd_service_stop(sys.argv[2])

    # Workflow commands
    elif command == 'workflows':
        cmd_workflows()
    elif command == 'workflow':
        if len(sys.argv) < 3:
            print("Usage: deployment_cli.py workflow <name>")
            return
        cmd_workflow_info(sys.argv[2])

    # Monitoring commands
    elif command == 'metrics':
        cmd_metrics()
    elif command == 'health':
        cmd_health()
    elif command == 'config':
        cmd_config()

    # Help
    elif command in ['-h', '--help', 'help']:
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


def print_help():
    """Print help message"""
    help_text = """
Open Agent Studio - Deployment CLI

USAGE: python deployment_cli.py <command> [options]

DEPLOYMENT COMMANDS:
  status          Show current deployment status
  up              Start all containers
  down            Stop all containers
  restart         Restart all containers
  rebuild         Rebuild and start containers

LOGGING COMMANDS:
  logs [service] [lines]    View logs (default: all services, 50 lines)
  logs openagent 100        View last 100 lines of openagent logs
  logs control-panel        View control-panel logs

SERVICE COMMANDS:
  services        List all available services
  start <svc>     Start specific service
  stop <svc>      Stop specific service
  restart <svc>   Restart specific service

WORKFLOW COMMANDS:
  workflows       List available workflows
  workflow <name> Show workflow details

MONITORING COMMANDS:
  metrics         Show CPU/memory metrics
  health          Run health check
  config          Show configuration

EXAMPLES:
  python deployment_cli.py status
  python deployment_cli.py up
  python deployment_cli.py logs openagent 100
  python deployment_cli.py start postgres
  python deployment_cli.py metrics

ENVIRONMENT:
  CONTROL_API_URL     Control panel URL (default: http://localhost:5000)
  AUTH_TOKEN          API authentication token
"""
    print(help_text)


if __name__ == '__main__':
    main()
