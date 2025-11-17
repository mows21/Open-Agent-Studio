# Open Agent Studio - Chat-Based Deployment Control Guide

> Control your local Open Agent Studio deployment directly from the chat interface!

## Overview

You now have complete deployment control through three integrated systems:

1. **Control API** (`control_api.py`) - Flask API server running on `localhost:5000`
2. **Deployment CLI** (`deployment_cli.py`) - Python CLI for direct commands
3. **Deployment MCP** (`deployment_mcp.py`) - MCP server for chat integration

## Quick Start

### 1. Environment Setup

Create a `.env` file in the project root:

```env
# API Configuration
ANTHROPIC_API_KEY=your-api-key-here
AUTH_TOKEN=dev-token-change-in-production
CONTROL_API_URL=http://localhost:5000
API_HOST=0.0.0.0
API_PORT=8080

# Docker Configuration
DB_PASSWORD=your-postgres-password
```

### 2. Start the Deployment

```bash
# Navigate to project directory
cd Open-Agent-Studio

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Access the Control Panel

- **Control API Dashboard**: http://localhost:5000
- **Main Agent API**: http://localhost:8080
- **PostgreSQL**: localhost:5432

## Chat Commands (via MCP)

Once integrated with your chat, use these commands:

### Deployment Status & Control

```
"Show me the deployment status"
→ deployment_status

"Start the deployment"
→ start_deployment

"Stop all containers"
→ stop_deployment

"Restart the deployment"
→ restart_deployment

"Rebuild and start containers"
→ rebuild_deployment
```

### Service Management

```
"List all services"
→ list_services

"Start the openagent service"
→ start_service(service="openagent")

"Stop the postgres database"
→ stop_service(service="postgres")

"Restart the control panel"
→ restart_service(service="control-panel")
```

### Monitoring & Logs

```
"Show me the logs"
→ get_logs()

"Get the last 100 lines of openagent logs"
→ get_logs(service="openagent", lines=100)

"What are the container metrics?"
→ get_metrics()

"Run a health check"
→ health_check()
```

### Workflows

```
"List all workflows"
→ list_workflows()

"Show me the earnings workflow"
→ get_workflow(name="earnings.cheat")
```

### Configuration

```
"What's the deployment configuration?"
→ get_deployment_config()
```

## CLI Commands (Local Terminal)

Use the deployment CLI for direct control without chat:

```bash
# Status and control
python deployment_cli.py status
python deployment_cli.py up
python deployment_cli.py down
python deployment_cli.py restart
python deployment_cli.py rebuild

# Logs
python deployment_cli.py logs                    # All services, 50 lines
python deployment_cli.py logs openagent 100     # Specific service, 100 lines
python deployment_cli.py logs control-panel     # Default 50 lines

# Services
python deployment_cli.py services                # List services
python deployment_cli.py start openagent         # Start service
python deployment_cli.py stop postgres           # Stop service

# Workflows
python deployment_cli.py workflows              # List workflows
python deployment_cli.py workflow earnings.cheat # Show workflow

# Monitoring
python deployment_cli.py metrics                # CPU/Memory stats
python deployment_cli.py health                 # System health
python deployment_cli.py config                 # Configuration info
```

## API Endpoints (Control API on :5000)

All endpoints require `Authorization: Bearer <AUTH_TOKEN>` header (except `/health`)

### Health & Status

```
GET /health
→ Returns: {"status": "healthy", ...}

GET /api/status
→ Returns: deployment state and docker status
```

### Deployment Control

```
POST /api/deploy/up          → Start all containers
POST /api/deploy/down        → Stop all containers
POST /api/deploy/restart     → Restart all containers
POST /api/deploy/rebuild     → Rebuild and start
```

### Logs

```
GET /api/logs/<service>?lines=50      → Service logs
GET /api/logs/all?lines=50            → All services logs
```

### Services

```
GET /api/services                      → List all services
POST /api/service/<service>/start      → Start service
POST /api/service/<service>/stop       → Stop service
POST /api/service/<service>/restart    → Restart service
```

### Workflows

```
GET /api/workflows                     → List workflows
GET /api/workflow/<name>               → Get workflow details
```

### Monitoring

```
GET /api/metrics                       → Container metrics
GET /api/agent/health                  → Check agent health
GET /api/config                        → Get configuration
```

## Service Architecture

### Services Running

```
openagent          - Main Agent API (port 8080)
control-panel      - Control API (port 5000)
nginx              - Reverse proxy (ports 80, 443)
postgres           - Database (port 5432)
```

### Docker Compose Services

View with:
```bash
docker-compose config --services
```

Expected output:
```
openagent
control-panel
postgres
nginx
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker daemon
docker ps

# View initialization logs
docker-compose logs --tail=100 openagent

# Check if ports are in use
netstat -tuln | grep 5000
netstat -tuln | grep 8080

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Control API Not Responding

```bash
# Check if container is running
docker ps | grep control-panel

# View control-panel logs
docker-compose logs control-panel

# Restart it
docker-compose restart control-panel

# Test connectivity
curl http://localhost:5000/health
```

### Agent API Health Issues

```bash
# Check main API status
curl http://localhost:8080/health

# View logs
docker-compose logs -f openagent

# Restart main service
docker-compose restart openagent
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres

# Reset database (careful!)
docker-compose down
docker volume rm openagent-studio_postgres_data
docker-compose up -d
```

## Advanced Usage

### Custom Workflows

Place `.cheat` workflow files in `/workflows/` directory:

```json
{
  "name": "example_workflow",
  "steps": [
    {"action": "click", "target": "button#submit"},
    {"action": "type", "text": "Hello World"}
  ]
}
```

Then access via:
```
"Load the example_workflow"
→ get_workflow(name="example_workflow.cheat")
```

### Scaling Services

Scale specific services:

```bash
# Scale openagent to 3 replicas
docker-compose up -d --scale openagent=3

# Revert to single instance
docker-compose up -d --scale openagent=1
```

### Environment Variables

Change settings via `.env`:

```env
# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=DEBUG

# Browser settings
BROWSER_HEADLESS=true
BROWSER_TYPE=chromium

# API configuration
API_HOST=0.0.0.0
API_PORT=8080

# Database
DB_PASSWORD=secure-password-here
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### SSL/TLS Setup

Configure Nginx with SSL:

1. Place certificates in `./ssl/` directory
2. Update `nginx.conf` with certificate paths
3. Restart: `docker-compose restart nginx`

## Integration with Chat

### Initial Setup

1. Ensure `deployment_mcp.py` is configured in your MCP config
2. Verify MCP server is running:
   ```
   "Check deployment system status"
   → health_check()
   ```

3. Start using natural language commands:
   ```
   "I need to restart the database"
   → restart_service(service="postgres")
   ```

### Chat-based Workflows

You can combine chat commands:

```
"First, show me the current status, then restart everything and check health"

1. deployment_status()
2. restart_deployment()
3. health_check()
```

## Monitoring Dashboard

Real-time monitoring via CLI:

```bash
# Watch logs in real-time
docker-compose logs -f

# Watch specific service
docker-compose logs -f openagent

# Watch metrics (requires watch command)
watch -n 2 'docker stats --no-stream'
```

## Performance Tuning

### For Local Development

Keep `docker-compose.yml` as-is (all services running)

### For Production (VPS)

When deploying to DigitalOcean/Hostinger:

1. Remove unnecessary services from docker-compose
2. Configure environment for headless operation
3. Set up proper SSL certificates
4. Configure backup strategy for PostgreSQL
5. Monitor resource usage

See `DEPLOYMENT_GUIDE.md` for VPS-specific instructions.

## Security Considerations

### Local Development

- AUTH_TOKEN set to `dev-token` is fine for local use
- Keep API port (5000) accessible only locally
- Use `.env` file (add to .gitignore)

### Production

- Generate secure AUTH_TOKEN:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- Use environment variables for all secrets
- Enable SSL/TLS via Nginx
- Restrict API access to authorized IPs
- Enable authentication on PostgreSQL
- Run security scans: `docker scan openagent-studio`

## Support & Troubleshooting

For issues:

1. Check logs first: `docker-compose logs -f`
2. Try restarting: `docker-compose restart`
3. Check health: Use `health_check()` from chat
4. Review configuration: `get_deployment_config()`

## Next Steps

- Deploy to DigitalOcean VPS (see `DEPLOYMENT_GUIDE.md`)
- Configure scheduled workflows (cron)
- Set up monitoring alerts
- Create custom automation workflows
- Integrate with external APIs

---

**Last Updated**: 2024
**Version**: 1.0.0
