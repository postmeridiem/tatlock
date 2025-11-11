# Docker Installation Guide

This guide covers running Tatlock using Docker and Docker Compose. The Docker setup follows the same decision patterns as the standard installation script, including automatic hardware classification, model selection, and database initialization.

## Prerequisites

- **Docker** 20.10 or later
- **Docker Compose** 2.0 or later
- **Ollama** running on the host system or in a separate Docker container
- **Minimum 4GB RAM** (8GB+ recommended for high-performance models)
- **Internet connection** (for initial model download)

### Setting Up Ollama

Tatlock requires Ollama to be running separately. You have two options:

**Option 1: Install Ollama on the Host System**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**Option 2: Run Ollama in a Separate Docker Container**

```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama:latest
```

**Important**: Ensure Ollama is accessible at `http://localhost:11434` (or configure `OLLAMA_HOST` accordingly).

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/postmeridiem/tatlock.git
cd tatlock
```

### 2. Configure Environment Variables (Optional)

Create a `.env` file in the project root to customize your installation:

```bash
# .env file (optional)
STARLETTE_SECRET=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
ADMIN_EMAIL=admin@yourdomain.com
SKIP_MODEL_DOWNLOAD=false
```

**Note**: If you don't create a `.env` file, the system will:
- Auto-generate a `STARLETTE_SECRET`
- Use default admin credentials (`admin` / `admin123`)
- Automatically download the recommended Ollama model

### 3. Ensure Ollama is Running

Make sure Ollama is running on your host system or in a separate container before starting Tatlock:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

### 4. Start Tatlock

```bash
docker compose up -d
```

This will:
1. Build and start the Tatlock application
2. Automatically detect hardware and select the optimal model
3. Initialize databases and create the admin user
4. Download the recommended Ollama model (if Ollama is accessible)

### 5. Access the Application

- **Login Page**: `http://localhost:8000/login`
- **Default Admin Credentials**: `admin` / `admin123` (or your custom credentials)
- **API Documentation**: `http://localhost:8000/docs`

**⚠️ Important**: Change the default admin password immediately after first login!

## Configuration Options

### Environment Variables

You can customize the Docker setup using environment variables in `docker-compose.yml` or a `.env` file:

#### Server Configuration

- `HOSTNAME` (default: `0.0.0.0`) - Server hostname
- `PORT` (default: `8000`) - Server port
- `OLLAMA_HOST` (default: `http://host.docker.internal:11434`) - Ollama service URL

**OLLAMA_HOST Configuration**:

The default `OLLAMA_HOST` works for Docker Desktop (macOS/Windows). For other setups:

- **Docker Desktop (macOS/Windows)**: `http://host.docker.internal:11434` (default)
- **Linux with host network**: `http://localhost:11434` or `http://127.0.0.1:11434`
- **Linux with bridge network**: `http://172.17.0.1:11434` (default Docker bridge gateway)
- **Separate Docker container**: `http://<container-name>:11434` (if on same network)
- **Remote Ollama**: `http://<remote-ip>:11434`

You can override this in `docker-compose.yml` or via environment variable:

```yaml
environment:
  OLLAMA_HOST: http://172.17.0.1:11434  # Linux example
```

#### Security Configuration

- `STARLETTE_SECRET` - Session secret key (auto-generated if not provided)
- `DEBUG_MODE` (default: `false`) - Enable debug mode

#### Admin User Configuration

- `ADMIN_USERNAME` (default: `admin`) - Admin username
- `ADMIN_PASSWORD` (default: `admin123`) - Admin password
- `ADMIN_FIRST_NAME` (default: `Administrator`) - Admin first name
- `ADMIN_LAST_NAME` (default: `User`) - Admin last name
- `ADMIN_EMAIL` (default: `admin@tatlock.local`) - Admin email

#### Model Configuration

- `SKIP_MODEL_DOWNLOAD` (default: `false`) - Set to `true` to skip automatic model download

### Example Custom Configuration

```yaml
# docker-compose.yml
services:
  tatlock:
    environment:
      HOSTNAME: 0.0.0.0
      PORT: 8000
      ADMIN_USERNAME: myadmin
      ADMIN_PASSWORD: secure-password-123
      ADMIN_EMAIL: admin@example.com
      SKIP_MODEL_DOWNLOAD: false
```

## Hardware Classification

Tatlock automatically detects your container's hardware capabilities and selects the optimal Ollama model:

### Performance Tiers

- **High**: 8GB+ RAM, 4+ CPU cores, non-Apple Silicon → `gemma3-cortex:latest`
- **Medium**: 4-8GB RAM, 2-4 CPU cores, or Apple Silicon M2/M3 with >16GB RAM → `mistral:7b`
- **Low**: <4GB RAM, limited CPU, M1 processors, or Apple Silicon ≤16GB RAM → `mistral:7b`

The hardware classification is performed automatically during container initialization and saved to `hardware_config.py` for runtime efficiency.

## Volume Management

Docker Compose creates persistent volumes for:

- **`tatlock_hippocampus`**: User databases and memory storage
- **`tatlock_logs`**: Application logs

**Note**: Ollama models are stored separately (on the host system or in the Ollama container, depending on your setup).

### Viewing Volumes

```bash
# List all volumes
docker volume ls

# Inspect a volume
docker volume inspect tatlock_hippocampus
```

### Backing Up Data

```bash
# Backup hippocampus data
docker run --rm -v tatlock_hippocampus:/data -v $(pwd):/backup \
  alpine tar czf /backup/hippocampus-backup.tar.gz -C /data .

# Backup logs
docker run --rm -v tatlock_logs:/data -v $(pwd):/backup \
  alpine tar czf /backup/logs-backup.tar.gz -C /data .
```

### Restoring Data

```bash
# Restore hippocampus data
docker run --rm -v tatlock_hippocampus:/data -v $(pwd):/backup \
  alpine tar xzf /backup/hippocampus-backup.tar.gz -C /data

# Restore logs
docker run --rm -v tatlock_logs:/data -v $(pwd):/backup \
  alpine tar xzf /backup/logs-backup.tar.gz -C /data
```

## Managing the Services

### Start Services

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### View Logs

```bash
# All services
docker compose logs -f

# Tatlock only
docker compose logs -f tatlock
```

**Note**: Ollama logs are separate. If Ollama is running on the host, check system logs. If in a Docker container, use `docker logs ollama`.

### Restart Services

```bash
docker compose restart
```

### Rebuild After Code Changes

```bash
docker compose up -d --build
```

### Force Re-initialization

To force re-initialization (recreate databases, admin user, etc.):

```bash
# Stop services
docker compose down

# Remove volumes (⚠️ This deletes all data!)
docker volume rm tatlock_hippocampus tatlock_logs

# Start with force initialization
docker compose run --rm -e FORCE_INIT=true tatlock python docker-init.py

# Start services normally
docker compose up -d
```

## Troubleshooting

### Ollama Service Not Ready

If you see errors about Ollama not being available:

1. **Verify Ollama is running**:

```bash
# Check if Ollama is accessible from host
curl http://localhost:11434/api/tags

# If Ollama is in a Docker container
docker ps | grep ollama
docker logs ollama
```

2. **Check OLLAMA_HOST configuration**:

The default `OLLAMA_HOST` is `http://host.docker.internal:11434` which works for Docker Desktop. For Linux, you may need to:

```bash
# Option 1: Use host network mode (in docker-compose.yml)
network_mode: "host"

# Option 2: Set OLLAMA_HOST to Docker bridge gateway
OLLAMA_HOST: http://172.17.0.1:11434

# Option 3: Use host's IP address
OLLAMA_HOST: http://<your-host-ip>:11434
```

3. **Restart Ollama** (if running on host):
```bash
# macOS/Linux
ollama serve

# Or if running in Docker
docker restart ollama
```

The initialization script waits up to 60 seconds for Ollama to become available. If it times out, the model download will be skipped, and you can manually download models later.

### Model Download Fails

If model download fails during initialization:

1. **Check Ollama service**: Ensure Ollama is running and accessible from the container
2. **Check OLLAMA_HOST**: Verify the `OLLAMA_HOST` environment variable is correct
3. **Check network**: Ensure the container can reach Ollama and has internet access
4. **Manual download**: You can manually download models:

```bash
# If Ollama is on the host
ollama pull mistral:7b

# If Ollama is in a Docker container
docker exec ollama ollama pull mistral:7b

# Or use the Tatlock container (if Ollama is accessible)
docker compose exec tatlock python -c "import ollama; ollama.pull('mistral:7b')"
```

### Database Initialization Issues

If database initialization fails:

```bash
# Check Tatlock logs
docker compose logs tatlock

# Verify volumes are mounted correctly
docker compose exec tatlock ls -la /app/hippocampus

# Force re-initialization
docker compose run --rm -e FORCE_INIT=true tatlock python docker-init.py
```

### Port Already in Use

If port 8000 is already in use:

```yaml
# docker-compose.yml
services:
  tatlock:
    ports:
      - "8001:8000"  # Change host port to 8001
```

Then access the application at `http://localhost:8001`.

### Permission Issues

If you encounter permission issues:

```bash
# Check file ownership
docker compose exec tatlock ls -la /app

# Fix ownership (if needed, run as root temporarily)
docker compose exec -u root tatlock chown -R tatlock:tatlock /app
```

## Differences from Standard Installation

### What's the Same

- ✅ Hardware classification and model selection
- ✅ Database initialization with all tables, roles, groups, and tools
- ✅ Admin user creation
- ✅ Settings migration from environment to database
- ✅ All application features and functionality

### What's Different

- **No interactive prompts**: All configuration is done via environment variables
- **Ollama runs separately**: Ollama must be running on the host or in a separate container (not managed by docker-compose)
- **Persistent volumes**: Data persists across container restarts
- **No system service installation**: Services are managed via Docker Compose
- **No Material Icons download**: Icons are included in the Docker image
- **Network configuration**: May need to configure `OLLAMA_HOST` depending on your Docker setup

## Production Considerations

### Security

1. **Change default passwords**: Always set custom `ADMIN_PASSWORD`
2. **Use strong secrets**: Set a strong `STARLETTE_SECRET`
3. **Limit network exposure**: Use reverse proxy (nginx, Traefik) instead of exposing ports directly
4. **Regular backups**: Set up automated backups of volumes
5. **Update regularly**: Keep Docker images and dependencies updated

### Performance

1. **Resource limits**: Set appropriate CPU and memory limits:

```yaml
services:
  tatlock:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

2. **Model selection**: Use `SKIP_MODEL_DOWNLOAD=true` and manually select models for production
3. **Logging**: Configure log rotation to prevent disk space issues

### Monitoring

```bash
# Monitor resource usage
docker stats tatlock

# Check service health
docker compose ps

# View recent logs
docker compose logs --tail=100 tatlock

# Monitor Ollama (if running separately)
# On host: Check system resources
# In Docker: docker stats ollama
```

## Advanced Usage

### Custom Model Selection

To use a specific model regardless of hardware detection:

1. Set `SKIP_MODEL_DOWNLOAD=true` in environment
2. Manually download your preferred model:

```bash
docker compose exec ollama ollama pull your-model:tag
```

3. Edit `hardware_config.py` in the container or mount a custom version

### Development Mode

For development with live code reloading:

```yaml
# docker-compose.dev.yml
services:
  tatlock:
    volumes:
      - .:/app  # Mount source code
    environment:
      DEBUG_MODE: "true"
```

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Multi-Instance Setup

To run multiple Tatlock instances:

```yaml
services:
  tatlock1:
    # ... configuration ...
    ports:
      - "8000:8000"
  
  tatlock2:
    # ... configuration ...
    ports:
      - "8001:8000"
```

## Getting Help

- **Logs**: Check container logs for detailed error messages
- **Documentation**: See [README.md](README.md) for general information
- **Troubleshooting**: See [troubleshooting.md](troubleshooting.md) for common issues
- **Issues**: Report problems on the GitHub issue tracker

## Next Steps

After installation:

1. **Change admin password**: Log in and update your password
2. **Configure API keys**: Set up OpenWeather and Google Search API keys via the admin interface
3. **Create users**: Add additional users through the admin dashboard
4. **Explore features**: Check out the conversation interface, memory system, and tools

Enjoy using Tatlock with Docker! 🐳

