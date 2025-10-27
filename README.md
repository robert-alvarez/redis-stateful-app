# 🤖 Redis Memory Magic - Chat API Playground

A demo application showcasing **stateless vs stateful** LLM applications with **Redis-backed conversation memory** and support for both **cloud (ChatGPT)** and **local (Ollama)** inference.

## ✨ Features

### Two Powerful Dimensions

**💭 Memory Toggle**
- **Stateless:** No memory - watch it forget!
- **Stateful:** Redis-backed memory - remembers everything!

**🏢 Provider Toggle**
- **Cloud (ChatGPT):** OpenAI's cloud API (fast, powerful)
- **Local (Ollama):** Self-hosted inference on your machine (private, free, customizable)

### Under the Hood

- 🚀 **Responses API** - Latest OpenAI API for optimal performance (ChatGPT)
- 🦙 **Ollama** - Easy local LLM deployment with OpenAI-compatible API
- 📦 **Redis** - Fast in-memory conversation storage
- 🎯 **FastAPI** - Modern Python backend
- 🎨 **Clean UI** - Simple, responsive interface
- 🐳 **Docker Ready** - One-command deployment

## 🚀 Quick Start (Docker)

### Prerequisites

1. **Docker & Docker Compose** installed on your machine
2. **OpenAI API Key** (for Cloud provider) - Get one at [platform.openai.com](https://platform.openai.com)
3. **(Optional) Ollama** installed for Local provider - [ollama.com](https://ollama.com)

### Step 1: Clone and Configure

```bash
# Navigate to the project directory
cd stateless-chat-app

# Copy the environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

**Minimum required configuration in `.env`:**
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 2: (Optional) Set Up Ollama for Local Inference

If you want to use the **Local (Ollama)** provider:

```bash
# Install Ollama (macOS)
brew install ollama

# Or download from https://ollama.com

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull llama3.2

# Verify it's running
ollama list
```

The default Ollama configuration in `.env` should work out of the box:
```bash
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
```

**Note for Docker users:** If running Ollama on your host machine and the app in Docker, you may need to use:
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1  # macOS/Windows
# or
OLLAMA_BASE_URL=http://172.17.0.1:11434/v1  # Linux
```

### Step 3: Deploy with Docker Compose

```bash
# Start all services (Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 4: Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

**That's it!** 🎉

### Quick Start Scripts

For convenience, use the provided startup scripts:

```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

## 🎮 How to Use

1. **Open** http://localhost:3000 in your browser
2. **Test the Memory Toggle:**
   - Keep memory **OFF** (Stateless mode)
   - Say "My name is Alice"
   - Ask "What's my name?"
   - Watch it forget! 😅
   - Now toggle memory **ON** (Stateful mode)
   - Say "My name is Alice"
   - Ask "What's my name?"
   - Now it remembers! ✨

3. **Test the Provider Toggle:**
   - Start with **Cloud** (ChatGPT) - fast and powerful
   - Toggle to **Local** (Ollama) - runs on your machine
   - Notice responses still maintain conversation history (if memory is ON)

4. **Seamless Switching:**
   - All messages are logged to Redis regardless of mode
   - Switch between stateless/stateful anytime
   - Switch between cloud/local anytime
   - Conversation history persists across mode changes!

## 📦 Docker Deployment Details

### Services Architecture

The `docker-compose.yml` orchestrates three services:

```
┌─────────────────────────────────────────┐
│           Docker Network                │
│                                         │
│  ┌──────────┐   ┌──────────┐          │
│  │  Redis   │   │  Backend │          │
│  │  :6379   │◄──│  :9090   │          │
│  └──────────┘   └──────────┘          │
│                       ▲                │
│                       │                │
│                  ┌────▼──────┐        │
│                  │ Frontend  │        │
│                  │  :3000    │        │
│                  └───────────┘        │
└─────────────────────────────────────────┘
         │                │
         ▼                ▼
    ┌────────┐      ┌─────────┐
    │ChatGPT │      │ Ollama  │
    │ (API)  │      │ (Local) │
    └────────┘      └─────────┘
```

### Service Details

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **redis** | `redis:7-alpine` | 6379 | Conversation memory storage |
| **backend** | Built from `backend/Dockerfile` | 9090 | FastAPI application |
| **frontend** | Built from `frontend/Dockerfile` | 3000 | Nginx serving static files |

### Docker Commands Cheat Sheet

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (clears Redis data)
docker-compose down -v

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f redis
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build

# Check service status
docker-compose ps

# Execute command in running container
docker-compose exec backend bash
docker-compose exec redis redis-cli

# View Redis data
docker-compose exec redis redis-cli KEYS "*"
docker-compose exec redis redis-cli GET "chat:session:your_session_id:messages"
```

### Environment Variables

The application uses the following environment variables (configured in `.env`):

**OpenAI Configuration (Required for Cloud provider):**
```bash
OPENAI_API_KEY=sk-your-api-key-here  # REQUIRED
OPENAI_MODEL=gpt-5-mini              # Optional, default shown
```

**Ollama Configuration (Optional for Local provider):**
```bash
OLLAMA_BASE_URL=http://localhost:11434/v1  # Default Ollama endpoint
OLLAMA_API_KEY=ollama                      # Placeholder, not required
OLLAMA_MODEL=llama3.2                      # Your installed model
```

**Redis Configuration:**
```bash
REDIS_HOST=redis              # Service name in Docker network
REDIS_PORT=6379               # Default Redis port
REDIS_DB=0                    # Database number
REDIS_PASSWORD=               # Leave empty if no password
SESSION_TTL_SECONDS=3600      # Session expiration (1 hour)
```

### Volume Mounts

```yaml
volumes:
  redis-data:  # Persistent storage for Redis data
```

Redis data persists across container restarts but is deleted with `docker-compose down -v`.

## 🔧 Local Development (Without Docker)

If you prefer to run services locally without Docker:

### Prerequisites

- Python 3.11+
- Redis Server
- Node.js/npm (for frontend development) or any HTTP server

### Backend Setup

```bash
cd stateless-chat-app/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your API keys

# Run backend
python main.py
# Backend runs on http://localhost:9090
```

### Frontend Setup

```bash
cd stateless-chat-app/frontend

# Option 1: Simple HTTP server (Python)
python -m http.server 3000

# Option 2: Node.js HTTP server
npx http-server -p 3000

# Option 3: Just open index.html in browser
# (May have CORS issues with API calls)
```

### Redis Setup

```bash
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows
# Download from https://redis.io/download
```

## 📊 Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser (UI)                     │
│         http://localhost:3000 (Frontend)            │
└────────────────────┬────────────────────────────────┘
                     │ HTTP POST /chat
                     ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend :9090                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  main.py - API Routing & Mode Selection     │  │
│  └──────────────────────────────────────────────┘  │
│            │                          │             │
│  ┌─────────▼────────┐      ┌────────▼──────────┐  │
│  │ Stateless Mode   │      │  Stateful Mode    │  │
│  │ (No history)     │      │  (With history)   │  │
│  └─────────┬────────┘      └────────┬──────────┘  │
│            │                         │             │
│  ┌─────────▼─────────────────────────▼──────────┐ │
│  │         Memory Service (Redis)               │ │
│  │   - Store messages                           │ │
│  │   - Retrieve history                         │ │
│  │   - TTL management                           │ │
│  └──────────────────┬───────────────────────────┘ │
└─────────────────────┼───────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
  ┌─────────────┐          ┌─────────────┐
  │   Redis     │          │  External   │
  │   :6379     │          │  LLM APIs   │
  │             │          │             │
  │  Session    │          │  ChatGPT    │
  │  Storage    │          │    or       │
  │             │          │  Ollama     │
  └─────────────┘          └─────────────┘
```

### Request Flow

**Stateless Mode:**
```
1. User sends message
2. Backend stores message in Redis (for history tracking)
3. Backend sends ONLY current message to LLM
4. LLM responds (no context)
5. Backend stores response in Redis
6. User receives response
```

**Stateful Mode:**
```
1. User sends message
2. Backend stores message in Redis
3. Backend retrieves FULL conversation history from Redis
4. Backend sends entire history + current message to LLM
5. LLM responds (with full context)
6. Backend stores response in Redis
7. User receives response
```

## 📁 Project Structure

```
redis-stateful-app/
├── README.md                              # This file
├── stateless-chat-app/
│   ├── docker-compose.yml                 # Container orchestration
│   ├── start.sh                           # macOS/Linux startup script
│   ├── start.bat                          # Windows startup script
│   ├── .env.example                       # Environment template
│   ├── .env                               # Your config (gitignored)
│   │
│   ├── backend/                           # FastAPI Backend
│   │   ├── main.py                        # API endpoints & routing
│   │   ├── models.py                      # Pydantic request/response models
│   │   ├── memory_service.py              # Redis integration
│   │   ├── llm_service.py                 # ChatGPT stateless
│   │   ├── stateful_llm_service.py        # ChatGPT stateful
│   │   ├── ollama_service.py              # Ollama stateless
│   │   ├── stateful_ollama_service.py     # Ollama stateful
│   │   ├── requirements.txt               # Python dependencies
│   │   ├── Dockerfile                     # Backend container
│   │   └── .dockerignore
│   │
│   └── frontend/                          # Static Frontend
│       ├── index.html                     # Main UI
│       ├── app.js                         # JavaScript logic
│       ├── style.css                      # Styles & theming
│       ├── nginx.conf                     # Nginx configuration
│       ├── Dockerfile                     # Frontend container
│       └── .dockerignore
```

## 🎯 Key Concepts Demonstrated

### 1. Stateless vs Stateful Applications

**Problem:** Stateless LLMs have no memory
- Each request is independent
- The model forgets previous conversation
- Poor user experience for chat applications

**Solution:** Redis-backed conversation history
- Store messages in Redis with session IDs
- Retrieve full history for each request
- LLM sees entire conversation context

**Result:** Natural conversation flow with memory

### 2. Provider Flexibility

**Cloud (ChatGPT):**
- ✅ Fast responses
- ✅ High quality
- ✅ No infrastructure needed
- ❌ Costs per token
- ❌ Data sent to OpenAI

**Local (Ollama):**
- ✅ Free to use
- ✅ Complete data privacy
- ✅ Works offline
- ✅ Customizable models
- ❌ Requires local resources
- ❌ Slower than cloud (depends on hardware)

### 3. Seamless Mode Switching

**Key Innovation:**
- Messages are **ALWAYS** logged to Redis, even in stateless mode
- Enables switching from stateless to stateful without losing history
- Session IDs persist across mode changes
- Can switch providers mid-conversation

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Vanilla JavaScript, HTML5, CSS3 | Clean, dependency-free UI |
| **Backend** | FastAPI 0.109.0, Python 3.11 | High-performance async API |
| **Memory** | Redis 7 | Fast in-memory data store |
| **AI - Cloud** | OpenAI ChatGPT (gpt-5-mini) | Cloud-based LLM |
| **AI - Local** | Ollama (llama3.2) | Local LLM inference |
| **Server** | Uvicorn (ASGI) | Production-grade ASGI server |
| **Web Server** | Nginx | Static file serving |
| **Containers** | Docker, Docker Compose | Container orchestration |

## 🔍 API Endpoints

### Health Check
```
GET /
Returns service status and available providers
```

### Chat
```
POST /chat
Body: {
  "message": "Hello!",
  "mode": "stateless|stateful",
  "provider": "chatgpt|ollama",
  "session_id": "optional-session-id"
}

Response: {
  "response": "Hi there!",
  "mode": "stateful",
  "provider": "chatgpt",
  "session_id": "session_abc123",
  "message_count": 2
}
```

### Clear Session
```
POST /clear-session
Body: {
  "session_id": "session_abc123"
}

Response: {
  "status": "success",
  "message": "Session cleared"
}
```

## 🧪 Testing the Application

### Test 1: Memory Toggle

```
1. Keep Memory OFF (Stateless)
   - Send: "My name is Alice"
   - Send: "What's my name?"
   - Expected: "I don't know" or generic response

2. Toggle Memory ON (Stateful)
   - Send: "My name is Bob"
   - Send: "What's my name?"
   - Expected: "Your name is Bob"
```

### Test 2: Provider Toggle

```
1. Use Cloud (ChatGPT)
   - Send a message
   - Note the response style/speed

2. Toggle to Local (Ollama)
   - Send another message
   - Note the response style/speed
   - Conversation history still intact!
```

### Test 3: Seamless Switching

```
1. Memory OFF + Cloud
   - Say: "I like pizza"

2. Switch to Memory ON (keep Cloud)
   - Say: "What do I like?"
   - Expected: "You like pizza"

3. Switch to Local (keep Memory ON)
   - Say: "What food do I prefer?"
   - Expected: Still knows about pizza
```

## 🐛 Troubleshooting

### Issue: "Ollama services not available"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull a model if needed
ollama pull llama3.2

# For Docker: Update OLLAMA_BASE_URL in .env
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1  # Mac/Windows
```

### Issue: "ChatGPT service not available"

**Solution:**
```bash
# Check your .env file has valid API key
grep OPENAI_API_KEY .env

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# Restart backend
docker-compose restart backend
```

### Issue: "Redis connection failed"

**Solution:**
```bash
# Check Redis is running
docker-compose ps redis

# View Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### Issue: Frontend can't connect to backend

**Solution:**
```bash
# Check all services are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Check network connectivity
curl http://localhost:9090/

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Issue: Port already in use

**Solution:**
```bash
# Find what's using the port
lsof -i :3000  # or :9090, :6379

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

## 🔒 Production Deployment Considerations

### Security

1. **Environment Variables:**
   - Never commit `.env` to version control
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate API keys regularly

2. **Network Security:**
   - Use HTTPS (add SSL/TLS certificates)
   - Configure CORS properly (restrict origins)
   - Add rate limiting
   - Implement authentication

3. **Redis:**
   - Enable Redis password authentication
   - Use Redis ACLs
   - Enable encryption at rest
   - Use Redis Sentinel for high availability

### Scaling

1. **Horizontal Scaling:**
   ```yaml
   # docker-compose.yml
   backend:
     deploy:
       replicas: 3
   ```

2. **Load Balancing:**
   - Add Nginx or HAProxy for load balancing
   - Use Docker Swarm or Kubernetes

3. **Redis Scaling:**
   - Use Redis Cluster for distributed storage
   - Implement Redis replication
   - Consider managed Redis (AWS ElastiCache, Redis Cloud)

### Monitoring

```bash
# View resource usage
docker stats

# Health checks
curl http://localhost:9090/
curl http://localhost:3000/

# Redis monitoring
docker-compose exec redis redis-cli INFO stats
docker-compose exec redis redis-cli MONITOR
```

## 📚 Learn More

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contributing

This is a demo project for educational purposes. Feel free to:
- Fork and experiment
- Suggest improvements via issues
- Submit pull requests
- Use as a template for your projects

## 💡 Use Cases

This architecture pattern is useful for:
- **Chatbots** - Customer support, personal assistants
- **Conversational AI** - Multi-turn dialogues
- **Document Q&A** - Contextual document analysis
- **Code Assistants** - Programming help with context
- **Educational Tools** - Tutoring systems

## 📄 License

MIT License - feel free to use this for learning and building!

---

**Built with ❤️ to demonstrate Redis-backed memory in LLM applications**

🚀 **Get started now:**
```bash
cd stateless-chat-app
./start.sh
```
Then open http://localhost:3000 and start chatting! 🎉
