# Open Agent Studio - Quick Deployment Reference

## One-Time Setup

```bash
# Clone/navigate to project
cd Open-Agent-Studio

# Create .env file
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and AUTH_TOKEN

# Build and start
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Quick Commands Cheat Sheet

### From Chat Interface

```
Status:      "Show deployment status" / "Are we healthy?"
Start:       "Start everything" / "Bring it up"
Stop:        "Stop deployment" / "Shut it down"
Restart:     "Restart services" / "Bounce everything"
Rebuild:     "Rebuild containers" / "Fresh start"

Logs:        "Show me the logs" / "Get error logs from openagent"
Metrics:     "What's the CPU usage?" / "Show resource usage"
Health:      "Run health check" / "Everything working?"

Services:    "List services" / "What's running?"
Start SVC:   "Start postgres" / "Turn on the database"
Stop SVC:    "Stop nginx" / "Disable the proxy"
Restart SVC: "Restart control-panel"

Workflows:   "List workflows" / "Show available automation"
```

### From Terminal

```bash
# Status
docker-compose ps
docker-compose logs -f

# Control
docker-compose up -d              # Start all
docker-compose down               # Stop all
docker-compose restart            # Restart all
docker-compose up -d --build      # Rebuild all

# Logs
docker-compose logs -f openagent              # Watch agent logs
docker-compose logs --tail=50 control-panel  # Last 50 lines

# Services
docker-compose start openagent    # Start one service
docker-compose stop postgres      # Stop one service
docker-compose restart openagent  # Restart one service

# Metrics
docker stats --no-stream
watch -n 2 'docker ps'
```

### Python CLI

```bash
python deployment_cli.py status              # Show status
python deployment_cli.py up                  # Start deployment
python deployment_cli.py down                # Stop deployment
python deployment_cli.py logs openagent 100  # Get logs
python deployment_cli.py metrics             # CPU/Memory
python deployment_cli.py health              # Health check
```

## URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Agent API | http://localhost:8080 | Main automation API |
| Control Panel | http://localhost:5000 | Deployment control |
| Nginx HTTP | http://localhost:80 | Reverse proxy (HTTP) |
| Nginx HTTPS | https://localhost:443 | Reverse proxy (HTTPS) |
| PostgreSQL | localhost:5432 | Database |
| Docker Socket | /var/run/docker.sock | Docker API |

## Service Names

- `openagent` - Main agent/API server
- `control-panel` - Deployment control API
- `nginx` - Reverse proxy
- `postgres` - Database

## Environment Variables

```env
# Required
ANTHROPIC_API_KEY=your-key-here
AUTH_TOKEN=your-token-here

# Optional
CONTROL_API_URL=http://localhost:5000
API_HOST=0.0.0.0
API_PORT=8080
DB_PASSWORD=openagent
LOG_LEVEL=INFO
BROWSER_HEADLESS=true
BROWSER_TYPE=chromium
```

## Common Issues & Fixes

### Port Already in Use
```bash
# Kill process on port 5000
lsof -i :5000 | kill -9 <PID>

# Or change port in docker-compose.yml
```

### Containers Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild fresh
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Connection Refused
```bash
# Verify services are running
docker-compose ps

# Check health
curl http://localhost:8080/health
curl http://localhost:5000/health
```

### Database Issues
```bash
# Reset database
docker-compose down
docker volume rm openagent-studio_postgres_data
docker-compose up -d
```

## Monitoring

### Real-time Logs
```bash
docker-compose logs -f
```

### Service Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

### Health Status
```bash
curl http://localhost:8080/health
curl http://localhost:5000/health
```

## Authentication

All API endpoints require:
```
Authorization: Bearer <AUTH_TOKEN>
```

except:
- `/health` endpoints (public)

## File Locations

- **Project Root**: `c:\Users\dusti\.claude\Documents\GitHub\Open-Agent-Studio\`
- **Control API**: `control_api.py`
- **Deployment CLI**: `deployment_cli.py`
- **MCP Server**: `deployment_mcp.py`
- **Docker Compose**: `docker-compose.yml`
- **Workflows**: `./workflows/`
- **Logs**: `./logs/`

## Next Steps

1. **Start**: `docker-compose up -d`
2. **Verify**: `docker-compose ps`
3. **Chat**: "Show me deployment status"
4. **Explore**: Check out `DEPLOYMENT_CHAT_GUIDE.md`
5. **Deploy VPS**: See `DEPLOYMENT_GUIDE.md` when ready

---

For detailed guide: See `DEPLOYMENT_CHAT_GUIDE.md`
For architecture: See `ARCHITECTURE_SUMMARY.md`
For VPS deployment: See `DEPLOYMENT_GUIDE.md`
