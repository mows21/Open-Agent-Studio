#!/usr/bin/env python3
"""
Open Agent Studio - Local Deployment Control API
Enables chat-based management and monitoring of local Docker deployments
"""

import os
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Configuration
API_PORT = int(os.getenv('API_PORT', 5000))
API_HOST = os.getenv('API_HOST', '0.0.0.0')
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'dev-token')

# Deployment state
deployment_state = {
    'status': 'initialized',
    'timestamp': datetime.now().isoformat(),
    'services': {},
    'last_command': None
}


def check_auth():
    """Verify authentication token"""
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth[7:]
        return token == AUTH_TOKEN
    return False


def run_command(cmd: List[str]) -> Dict:
    """Execute shell command and return result"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timeout',
            'return_code': -1
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'return_code': -1
        }


def get_docker_status() -> Dict:
    """Get status of all services"""
    result = run_command(['docker', 'compose', 'ps', '--format', 'json'])

    if not result['success']:
        return {'error': 'Could not get service status'}

    try:
        services = json.loads(result['stdout'])
        return {
            'services': services,
            'timestamp': datetime.now().isoformat()
        }
    except json.JSONDecodeError:
        return {'error': 'Invalid Docker response', 'raw': result['stdout']}


# ==================== HEALTH & STATUS ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'openagent-control-panel'
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get deployment status"""
    docker_status = get_docker_status()
    return jsonify({
        'deployment': deployment_state,
        'docker': docker_status
    })


# ==================== DOCKER MANAGEMENT ====================

@app.route('/api/deploy/up', methods=['POST'])
def deploy_up():
    """Start all containers"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    logger.info('Starting deployment...')
    result = run_command(['docker', 'compose', 'up', '-d'])

    deployment_state['status'] = 'running' if result['success'] else 'error'
    deployment_state['last_command'] = 'up'
    deployment_state['timestamp'] = datetime.now().isoformat()

    return jsonify({
        'success': result['success'],
        'message': 'Containers starting...',
        'details': result,
        'status': get_docker_status()
    })


@app.route('/api/deploy/down', methods=['POST'])
def deploy_down():
    """Stop all containers"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    logger.info('Stopping deployment...')
    result = run_command(['docker', 'compose', 'down'])

    deployment_state['status'] = 'stopped'
    deployment_state['last_command'] = 'down'
    deployment_state['timestamp'] = datetime.now().isoformat()

    return jsonify({
        'success': result['success'],
        'message': 'Containers stopping...',
        'details': result
    })


@app.route('/api/deploy/restart', methods=['POST'])
def deploy_restart():
    """Restart all containers"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    logger.info('Restarting deployment...')
    result = run_command(['docker', 'compose', 'restart'])

    deployment_state['status'] = 'running'
    deployment_state['last_command'] = 'restart'
    deployment_state['timestamp'] = datetime.now().isoformat()

    return jsonify({
        'success': result['success'],
        'message': 'Containers restarting...',
        'details': result,
        'status': get_docker_status()
    })


@app.route('/api/deploy/rebuild', methods=['POST'])
def deploy_rebuild():
    """Rebuild containers"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    logger.info('Rebuilding deployment...')
    result = run_command(['docker', 'compose', 'up', '-d', '--build'])

    deployment_state['status'] = 'running' if result['success'] else 'error'
    deployment_state['last_command'] = 'rebuild'
    deployment_state['timestamp'] = datetime.now().isoformat()

    return jsonify({
        'success': result['success'],
        'message': 'Rebuilding containers...',
        'details': result,
        'status': get_docker_status()
    })


@app.route('/api/logs/<service>', methods=['GET'])
def get_logs(service: str):
    """Get logs for specific service"""
    lines = request.args.get('lines', default=50, type=int)

    result = run_command(['docker', 'compose', 'logs', '--tail', str(lines), service])

    return jsonify({
        'service': service,
        'lines': lines,
        'logs': result['stdout'],
        'success': result['success']
    })


@app.route('/api/logs/all', methods=['GET'])
def get_all_logs():
    """Get logs for all services"""
    lines = request.args.get('lines', default=50, type=int)

    result = run_command(['docker', 'compose', 'logs', '--tail', str(lines)])

    return jsonify({
        'lines': lines,
        'logs': result['stdout'],
        'success': result['success']
    })


# ==================== SERVICE MANAGEMENT ====================

@app.route('/api/services', methods=['GET'])
def list_services():
    """List all services"""
    result = run_command(['docker', 'compose', 'config', '--services'])

    services = result['stdout'].strip().split('\n') if result['success'] else []

    return jsonify({
        'services': services,
        'count': len(services),
        'status': get_docker_status()
    })


@app.route('/api/service/<service>/start', methods=['POST'])
def start_service(service: str):
    """Start specific service"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    logger.info(f'Starting service: {service}')
    result = run_command(['docker', 'compose', 'start', service])

    return jsonify({
        'service': service,
        'success': result['success'],
        'message': f'Service {service} starting...',
        'details': result
    })


@app.route('/api/service/<service>/stop', methods=['POST'])
def stop_service(service: str):
    """Stop specific service"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    logger.info(f'Stopping service: {service}')
    result = run_command(['docker', 'compose', 'stop', service])

    return jsonify({
        'service': service,
        'success': result['success'],
        'message': f'Service {service} stopping...',
        'details': result
    })


@app.route('/api/service/<service>/restart', methods=['POST'])
def restart_service(service: str):
    """Restart specific service"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401

    logger.info(f'Restarting service: {service}')
    result = run_command(['docker', 'compose', 'restart', service])

    return jsonify({
        'service': service,
        'success': result['success'],
        'message': f'Service {service} restarting...',
        'details': result
    })


# ==================== WORKFLOW MANAGEMENT ====================

@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    """List available workflows"""
    workflows_dir = '/app/workflows'

    try:
        if os.path.exists(workflows_dir):
            workflows = [f for f in os.listdir(workflows_dir)
                        if f.endswith('.cheat')]
            return jsonify({
                'workflows': workflows,
                'count': len(workflows),
                'path': workflows_dir
            })
        else:
            return jsonify({
                'workflows': [],
                'count': 0,
                'message': f'Workflows directory not found: {workflows_dir}'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow/<name>', methods=['GET'])
def get_workflow(name: str):
    """Get workflow content"""
    workflow_file = f'/app/workflows/{name}'

    try:
        if os.path.exists(workflow_file):
            with open(workflow_file, 'r') as f:
                content = json.load(f)
            return jsonify({
                'name': name,
                'content': content,
                'last_modified': datetime.fromtimestamp(
                    os.path.getmtime(workflow_file)
                ).isoformat()
            })
        else:
            return jsonify({'error': 'Workflow not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== AGENT API PROXY ====================

@app.route('/api/agent/health', methods=['GET'])
def agent_health():
    """Check if main agent API is healthy"""
    try:
        import requests
        response = requests.get('http://openagent:8080/health', timeout=5)
        return jsonify({
            'agent_healthy': response.status_code == 200,
            'agent_response': response.json() if response.status_code == 200 else None
        })
    except Exception as e:
        return jsonify({
            'agent_healthy': False,
            'error': str(e)
        }), 503


# ==================== METRICS & MONITORING ====================

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        # Get container stats
        result = run_command([
            'docker', 'stats', '--no-stream',
            '--format', '{{.Container}}|{{.CPUPerc}}|{{.MemUsage}}'
        ])

        metrics = []
        if result['success']:
            for line in result['stdout'].strip().split('\n'):
                if line:
                    parts = line.split('|')
                    metrics.append({
                        'container': parts[0] if len(parts) > 0 else 'unknown',
                        'cpu': parts[1].strip() if len(parts) > 1 else '0%',
                        'memory': parts[2].strip() if len(parts) > 2 else '0MB'
                    })

        return jsonify({
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CONFIGURATION ====================

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get deployment configuration"""
    return jsonify({
        'api_host': API_HOST,
        'api_port': API_PORT,
        'services': [
            'openagent',
            'control-panel',
            'nginx',
            'postgres'
        ],
        'endpoints': {
            'main_api': 'http://localhost:8080',
            'control_panel': 'http://localhost:5000',
            'nginx_http': 'http://localhost:80',
            'nginx_https': 'https://localhost:443',
            'postgres': 'postgres://localhost:5432'
        }
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f'Starting Control Panel API on {API_HOST}:{API_PORT}')
    logger.info(f'Main Agent API: http://openagent:8080')
    logger.info(f'Use Authorization header: "Bearer {AUTH_TOKEN[:20]}..."')

    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=os.getenv('FLASK_ENV') == 'development',
        use_reloader=False
    )
