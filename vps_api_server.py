#!/usr/bin/env python3
"""
VPS API Server for Open Agent Studio
Provides HTTP API for headless browser automation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import json
import os
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for web UI

# Load configuration
CONFIG_FILE = os.environ.get('CONFIG_FILE', 'config_vps.json')
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
else:
    logger.warning(f"Config file {CONFIG_FILE} not found. Using defaults.")
    config = {
        "api": {
            "host": "0.0.0.0",
            "port": 8080,
            "auth_token": os.environ.get("AUTH_TOKEN", "change-me")
        }
    }

# Get config values
AUTH_TOKEN = config.get('api', {}).get('auth_token') or os.environ.get('AUTH_TOKEN')
API_HOST = config.get('api', {}).get('host', '0.0.0.0')
API_PORT = config.get('api', {}).get('port', 8080)

# Task storage (in-memory for now, use Redis/DB for production)
tasks = {}
task_results = {}

# Initialize orchestrator (lazy loading)
orchestrator = None

def get_orchestrator():
    """Lazy load orchestrator"""
    global orchestrator
    if orchestrator is None:
        try:
            # Import here to avoid issues if not all dependencies available
            from agent_orchestrator import AgentOrchestrator

            api_key = config.get('anthropic_api_key') or os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                logger.error("No Anthropic API key found!")
                return None

            # Initialize MCP clients (browser only for VPS)
            mcp_clients = {}
            # TODO: Initialize browser MCP client

            orchestrator = AgentOrchestrator(api_key, mcp_clients)
            logger.info("✓ Agent orchestrator initialized")

        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            return None

    return orchestrator

def check_auth():
    """Check API authentication"""
    if not AUTH_TOKEN or AUTH_TOKEN == "change-me":
        logger.warning("⚠️  Using default auth token! Set AUTH_TOKEN environment variable.")

    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return token == AUTH_TOKEN

# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "vps",
        "timestamp": datetime.now().isoformat(),
        "capabilities": ["browser_automation", "ocr", "api"]
    })

@app.route('/info', methods=['GET'])
def info():
    """System information"""
    orch = get_orchestrator()

    return jsonify({
        "version": "2.0.0",
        "deployment": "vps",
        "features": {
            "browser_automation": True,
            "desktop_automation": False,
            "chat_ui": False,
            "api": True
        },
        "orchestrator_ready": orch is not None,
        "active_tasks": len(tasks),
        "completed_tasks": len(task_results)
    })

# ============================================================================
# Task Execution Endpoints
# ============================================================================

@app.route('/execute', methods=['POST'])
def execute_task():
    """Execute automation task"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    task_description = data.get('task')

    if not task_description:
        return jsonify({"error": "Missing 'task' field"}), 400

    # Get or create orchestrator
    orch = get_orchestrator()
    if not orch:
        return jsonify({
            "error": "Orchestrator not initialized. Check API key configuration."
        }), 500

    try:
        # Generate task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Store task
        tasks[task_id] = {
            "id": task_id,
            "description": task_description,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "sync": data.get('sync', True)  # Run synchronously by default
        }

        logger.info(f"📋 Executing task {task_id}: {task_description}")

        if data.get('sync', True):
            # Synchronous execution
            result = asyncio.run(orch.process_user_message(task_description))

            tasks[task_id]["status"] = "completed"
            task_results[task_id] = {
                "task_id": task_id,
                "result": result,
                "completed_at": datetime.now().isoformat()
            }

            logger.info(f"✓ Task {task_id} completed")

            return jsonify({
                "success": True,
                "task_id": task_id,
                "result": result
            })
        else:
            # Asynchronous execution (return immediately)
            # TODO: Implement background task execution
            return jsonify({
                "success": True,
                "task_id": task_id,
                "status": "queued",
                "message": "Task queued for execution. Use /tasks/{task_id} to check status."
            }), 202

    except Exception as e:
        logger.error(f"✗ Task execution failed: {e}")
        tasks[task_id]["status"] = "failed"

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get task status and result"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    if task_id in task_results:
        return jsonify(task_results[task_id])
    elif task_id in tasks:
        return jsonify(tasks[task_id])
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route('/tasks', methods=['GET'])
def list_tasks():
    """List all tasks"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "active_tasks": list(tasks.values()),
        "completed_tasks": list(task_results.values())
    })

# ============================================================================
# Workflow Endpoints
# ============================================================================

@app.route('/workflows', methods=['GET'])
def list_workflows():
    """List saved workflows"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    workflows_dir = Path('./workflows')
    if not workflows_dir.exists():
        return jsonify({"workflows": []})

    workflows = []
    for file in workflows_dir.glob('*.json'):
        try:
            with open(file) as f:
                workflow = json.load(f)
                workflows.append({
                    "name": file.stem,
                    "file": file.name,
                    "metadata": workflow.get("metadata", {})
                })
        except Exception as e:
            logger.error(f"Failed to load workflow {file}: {e}")

    return jsonify({"workflows": workflows})

@app.route('/workflows/<workflow_name>', methods=['GET'])
def get_workflow(workflow_name):
    """Get workflow details"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    workflow_file = Path(f'./workflows/{workflow_name}.json')
    if not workflow_file.exists():
        return jsonify({"error": "Workflow not found"}), 404

    with open(workflow_file) as f:
        workflow = json.load(f)

    return jsonify(workflow)

@app.route('/workflows/<workflow_name>/execute', methods=['POST'])
def execute_workflow(workflow_name):
    """Execute a saved workflow"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    # TODO: Implement workflow execution
    return jsonify({
        "message": "Workflow execution not yet implemented",
        "workflow": workflow_name
    }), 501

# ============================================================================
# Browser Automation Endpoints (Direct MCP access)
# ============================================================================

@app.route('/browser/navigate', methods=['POST'])
def browser_navigate():
    """Direct browser navigation"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    url = request.json.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' field"}), 400

    # TODO: Direct MCP call
    return jsonify({
        "message": "Direct MCP calls not yet implemented",
        "use": "POST /execute with task description instead"
    }), 501

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🤖 Open Agent Studio - VPS API Server")
    logger.info("=" * 60)
    logger.info(f"Mode: VPS (Browser automation only)")
    logger.info(f"Host: {API_HOST}")
    logger.info(f"Port: {API_PORT}")

    if AUTH_TOKEN == "change-me":
        logger.warning("⚠️  SECURITY WARNING: Using default auth token!")
        logger.warning("    Set AUTH_TOKEN environment variable for production")

    logger.info("=" * 60)

    # Run Flask app
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=False,
        threaded=True
    )
