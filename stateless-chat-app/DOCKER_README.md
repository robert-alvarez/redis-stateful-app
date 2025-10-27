# 🐳 Redis Memory Magic - Docker Deployment Guide

Run the entire Redis Memory Magic Chat application with a single command! This Docker setup includes:
- ✅ Backend API (FastAPI)
- ✅ Frontend UI (Nginx)
- ✅ Redis (Conversation memory)
- ✅ Ollama integration (Local LLM inference)

## 📋 Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)
- (Optional) OpenAI API key for ChatGPT provider
- (Optional) Ollama installed on your local machine for local inference ([Download here](https://ollama.com))

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd stateless-chat-app
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration (optional - for ChatGPT provider)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini

# Ollama Configuration (for local inference)
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_MODEL=qwen3:0.6b
```

**Note:** The default Ollama URL uses `host.docker.internal` to access Ollama running on your host machine. If you don't have an OpenAI API key, you can use only the Ollama provider!

### 3. Start Everything

```bash
docker-compose up -d
```

This will:
1. Pull all necessary Docker images
2. Build the backend and frontend
3. Start Redis, Backend, and Frontend
4. Connect to your local Ollama server (if installed)

### 4. Access the Application

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:9090
- **API Docs:** http://localhost:9090/docs

## 🎮 Usage

1. Open http://localhost:3000 in your browser
2. Toggle between:
   - **Memory:** Stateless ↔ Stateful
   - **Provider:** Cloud (ChatGPT) ↔ Local (Ollama)
3. Start chatting!

### Testing Local Inference

1. Make sure Ollama is running on your machine: `ollama serve`
2. Pull a model: `ollama pull qwen3:0.6b`
3. Toggle to **Local** provider (this uses your local Ollama)
4. Turn **memory ON**
5. Say "My name is [Your Name]"
6. Ask "What's my name?"
7. It remembers! ✨

## 📊 Container Architecture

```
┌───────────────────────────────────────────┐
│          Docker Network (Local)           │
│                                           │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  │
│  │ Frontend │  │ Backend  │  │ Redis │  │
│  │  :3000   │→ │  :9090   │→ │ :6379 │  │
│  └──────────┘  └──────────┘  └───────┘  │
└───────────────────┬───────────────────────┘
                    │
                    ↓
            ┌──────────────┐
            │    Ollama    │
            │  (Host OS)   │
            │   :11434     │
            └──────────────┘
```

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f redis
```

### Stop Everything

```bash
docker-compose down
```

### Stop and Remove Data

```bash
docker-compose down -v
```

### Rebuild After Code Changes

```bash
docker-compose up -d --build
```

### Check Status

```bash
docker-compose ps
```

## 🔧 Configuration

### Using Only ChatGPT (Cloud)

If you only want to use ChatGPT and don't need local inference:

1. Set your OpenAI API key in `.env`
2. Use only Cloud provider in the UI

### Using Only Ollama (Local)

If you only want local inference without ChatGPT:

1. Don't set `OPENAI_API_KEY`
2. Install and run Ollama on your machine
3. Use only Local provider in the UI

### Ollama Setup Guide

To set up Ollama for local inference:

1. **Install Ollama:**
   - Visit [ollama.com](https://ollama.com)
   - Download and install for your OS (Mac, Linux, Windows)

2. **Start Ollama:**
   ```bash
   ollama serve
   ```

3. **Pull a Model:**
   ```bash
   # Small, fast model (recommended for testing)
   ollama pull qwen3:0.6b

   # Other popular models:
   # ollama pull llama3.2
   # ollama pull mistral
   # ollama pull phi3
   ```

4. **Verify It's Running:**
   ```bash
   curl http://localhost:11434/v1/models
   ```

5. **Update .env (optional):**
   ```bash
   # Default values work out of the box
   OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
   OLLAMA_MODEL=qwen3:0.6b
   ```

## 📦 Distributed Deployment

### Save as Docker Image

```bash
# Build and save
docker-compose build
docker save -o chat-app.tar \
  stateless-chat-app-backend:latest \
  stateless-chat-app-frontend:latest

# On another machine
docker load -i chat-app.tar
docker-compose up -d
```

### Push to Docker Hub

```bash
# Tag images
docker tag stateless-chat-app-backend:latest yourusername/chat-backend:latest
docker tag stateless-chat-app-frontend:latest yourusername/chat-frontend:latest

# Push
docker push yourusername/chat-backend:latest
docker push yourusername/chat-frontend:latest
```

### Pull and Run Anywhere

```bash
# Download docker-compose.yml and .env
docker-compose pull
docker-compose up -d
```

## 🐛 Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running on your host
curl http://localhost:11434/v1/models

# Test Ollama connectivity from backend container (Mac/Windows)
docker exec -it chat-backend curl http://host.docker.internal:11434/v1/models

# Start Ollama if it's not running
ollama serve
```

### Backend Can't Connect to Redis

```bash
# Check Redis
docker exec -it redis-memory redis-cli ping
# Should return: PONG
```

### Frontend Can't Reach Backend

1. Check backend logs: `docker-compose logs backend`
2. Verify backend is running: `curl http://localhost:9090/`
3. Check CORS settings in `backend/main.py`

### Ollama Connection Issues

If you can't connect to Ollama:
1. Verify Ollama is running: `ollama list` should show your models
2. Check Ollama is serving: `curl http://localhost:11434/v1/models`
3. On Linux, you may need to use `--network host` or the container's IP instead of `host.docker.internal`
4. Verify you've pulled a model: `ollama pull qwen3:0.6b`

## 🔒 Security Notes

- The `.env` file contains secrets - **never commit it to git**
- Use `.env.example` as a template
- In production, use secrets management (Docker Secrets, Kubernetes Secrets, etc.)
- Configure proper CORS origins in `backend/main.py` for production

## 🚀 Production Deployment

For production:

1. **Use proper secrets management**
2. **Configure CORS properly** (not `allow_origins=["*"]`)
3. **Add HTTPS** (use nginx reverse proxy or Traefik)
4. **Set resource limits** in docker-compose.yml
5. **Use health checks** (already configured)
6. **Set up monitoring** (Prometheus, Grafana)
7. **Configure log aggregation** (ELK, Loki)

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Ollama Documentation](https://ollama.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Available Ollama Models](https://ollama.com/library)

## 💡 Tips

- **Ollama** - Must be running on your host machine before using Local provider
- **Conversations persist** - Stored in Docker volume `redis-data`
- **Clean slate:** `docker-compose down -v` removes all data
- **Development mode:** Use `docker-compose up` (without `-d`) to see live logs
- **Model switching:** Use different Ollama models by setting `OLLAMA_MODEL` in `.env`
- **No API costs:** Ollama runs completely locally with no API fees

---

**Built with:** Docker 🐳 | FastAPI ⚡ | Redis 🔴 | Ollama 🦙 | OpenAI 🤖
