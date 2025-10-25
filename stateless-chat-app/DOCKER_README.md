# 🐳 Redis Memory Magic - Docker Deployment Guide

Run the entire Redis Memory Magic Chat application with a single command! This Docker setup includes:
- ✅ Backend API (FastAPI)
- ✅ Frontend UI (Nginx)
- ✅ Redis (Conversation memory)
- ✅ vLLM integration (Self-hosted LLM inference on AWS)

## 📋 Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)
- (Optional) OpenAI API key for ChatGPT provider
- vLLM server running on AWS for self-hosted inference (see configuration below)

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

# vLLM Configuration (for self-hosted inference on AWS)
VLLM_BASE_URL=http://your-vllm-server:8000/v1
VLLM_API_KEY=EMPTY
VLLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
```

**Note:** Configure your vLLM server URL to point to your AWS deployment. If you don't have an OpenAI API key, you can use only the vLLM provider!

### 3. Start Everything

```bash
docker-compose up -d
```

This will:
1. Pull all necessary Docker images
2. Build the backend and frontend
3. Start Redis, Backend, and Frontend
4. Connect to your vLLM server on AWS

### 4. Access the Application

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:9090
- **API Docs:** http://localhost:9090/docs

## 🎮 Usage

1. Open http://localhost:3000 in your browser
2. Toggle between:
   - **Memory:** Stateless ↔ Stateful
   - **Provider:** ChatGPT ↔ vLLM (AWS)
3. Start chatting!

### Testing Self-Hosted Inference

1. Toggle to **vLLM** provider (this uses your AWS vLLM server)
2. Turn **memory ON**
3. Say "My name is [Your Name]"
4. Ask "What's my name?"
5. It remembers! ✨

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
            │ vLLM Server  │
            │   (AWS EC2)  │
            │    :8000     │
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

If you only want to use ChatGPT and don't need self-hosted inference:

1. Set your OpenAI API key in `.env`
2. Use only ChatGPT provider in the UI

### Using Only vLLM (Self-Hosted)

If you only want self-hosted inference without ChatGPT:

1. Don't set `OPENAI_API_KEY`
2. Configure `VLLM_BASE_URL` to point to your AWS vLLM server
3. Use only vLLM provider in the UI

### vLLM AWS Deployment Guide

To deploy vLLM on AWS:

1. **Launch GPU Instance:**
   ```bash
   # Recommended instance types:
   # g5.xlarge - 1x A10G (24GB) - Good for 7B-13B models
   # g5.2xlarge - 1x A10G (24GB) - Better performance
   # g5.12xlarge - 4x A10G (96GB) - Large models
   # p3.2xlarge - 1x V100 (16GB) - Alternative option
   ```

2. **Install vLLM:**
   ```bash
   pip install vllm
   ```

3. **Start vLLM Server:**
   ```bash
   vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct \
     --host 0.0.0.0 \
     --port 8000 \
     --api-key EMPTY
   ```

4. **Configure Security Group:**
   - Allow inbound TCP on port 8000 from your IP

5. **Update .env:**
   ```bash
   VLLM_BASE_URL=http://your-ec2-public-ip:8000/v1
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

### vLLM Server Not Responding

```bash
# Test vLLM server connectivity from backend container
docker exec -it chat-backend curl http://your-vllm-server:8000/v1/models

# Check if vLLM is running on AWS
ssh your-aws-server "ps aux | grep vllm"
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

### vLLM Connection Issues

If you can't connect to your vLLM server:
1. Verify the server is running: `ssh your-aws-server "curl localhost:8000/v1/models"`
2. Check security group allows inbound traffic on port 8000
3. Verify the URL in `.env` is correct
4. Test connectivity: `curl http://your-vllm-server:8000/v1/models`

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
- [vLLM Documentation](https://docs.vllm.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [AWS EC2 GPU Instances](https://aws.amazon.com/ec2/instance-types/)

## 💡 Tips

- **vLLM server** - Must be running on AWS before starting the application
- **Conversations persist** - Stored in Docker volume `redis-data`
- **Clean slate:** `docker-compose down -v` removes all data
- **Development mode:** Use `docker-compose up` (without `-d`) to see live logs
- **Cost optimization:** Use spot instances on AWS for vLLM to reduce costs

---

**Built with:** Docker 🐳 | FastAPI ⚡ | Redis 🔴 | vLLM 🚀 | OpenAI 🤖
