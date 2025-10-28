# 🚀 Redis Memory Magic - LLM Chat Application

A production-ready chat application demonstrating **stateless vs stateful LLM architecture** with Redis-backed conversation memory. Switch between cloud (ChatGPT) and local (Ollama) inference providers seamlessly while maintaining conversation history.

## 📖 Overview

This application showcases the fundamental difference between stateless and stateful AI applications:

- **Stateless Mode**: Each message is sent to the LLM without context - the AI forgets previous messages
- **Stateful Mode**: Full conversation history is maintained in Redis - the AI remembers your entire conversation

Additionally, you can switch between:
- **Cloud Provider (ChatGPT)**: Fast, powerful responses from OpenAI's API
- **Local Provider (Ollama)**: Privacy-focused, offline inference running on your machine

### Key Features

✨ **Dual Memory Modes**
- Toggle between stateless and stateful conversation modes in real-time
- Messages always stored in Redis for seamless mode switching
- Session-based memory with automatic TTL expiration

🌐 **Dual Provider Support**
- Cloud: OpenAI ChatGPT via Responses API (GPT-5)
- Local: Ollama for private, offline inference
- Switch providers mid-conversation without losing history

🏗️ **Modern Architecture**
- FastAPI backend with async support
- Redis Stack with MessageHistory for optimized LLM message management
- Docker Compose for one-command deployment
- Vanilla JavaScript frontend (no build tools required)

🔧 **Production Features**
- Health checks for all services
- Session TTL management
- Error handling and graceful degradation
- Docker volume persistence
- Comprehensive logging

## 🏛️ Architecture

### High-Level System Design

```
┌──────────────────────────────────────────────────────┐
│                   User Browser                       │
│              http://localhost:3000                   │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Backend :9090                   │
│  ┌────────────────────────────────────────────────┐ │
│  │           Request Router (main.py)             │ │
│  └──────────────┬─────────────────┬───────────────┘ │
│                 │                 │                  │
│    ┌────────────▼──────┐  ┌──────▼────────────┐    │
│    │  Stateless Mode   │  │  Stateful Mode    │    │
│    │  - No history     │  │  - Full history   │    │
│    │  - Single message │  │  - Context aware  │    │
│    └────────────┬──────┘  └──────┬────────────┘    │
│                 │                 │                  │
│    ┌────────────▼─────────────────▼──────────────┐  │
│    │     MemoryService (memory_service.py)       │  │
│    │  - MessageHistory (RedisVL)                 │  │
│    │  - Session management                       │  │
│    │  - TTL handling                             │  │
│    └────────────┬────────────────────────────────┘  │
└─────────────────┼───────────────────────────────────┘
                  │
     ┌────────────┴───────────┐
     ▼                        ▼
┌──────────────┐      ┌────────────────────┐
│ Redis Stack  │      │  External LLM APIs │
│    :6379     │      │                    │
│              │      │  ┌──────────────┐  │
│ MessageHist  │      │  │   ChatGPT    │  │
│ Session Data │      │  │  (OpenAI)    │  │
│              │      │  └──────────────┘  │
└──────────────┘      │                    │
                      │  ┌──────────────┐  │
                      │  │   Ollama     │  │
                      │  │  (Local)     │  │
                      │  └──────────────┘  │
                      └────────────────────┘
```

### Request Flow Comparison

**Stateless Mode Flow:**
```
User Message → Store in Redis → Send ONLY current message to LLM
→ Get Response → Store Response → Return to User
```
*Result: LLM has no memory of previous messages*

**Stateful Mode Flow:**
```
User Message → Store in Redis → Retrieve FULL history from Redis
→ Send entire conversation to LLM → Get Contextual Response
→ Store Response → Return to User
```
*Result: LLM remembers entire conversation context*

## 🚀 Quick Start with Docker

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (includes Docker Compose) - [Download here](https://www.docker.com/products/docker-desktop)
- **OpenAI API Key** (for ChatGPT provider) - [Get one here](https://platform.openai.com)
- **(Optional) Ollama** (for local inference) - [Download here](https://ollama.com)

### Step 1: Clone the Repository

```bash
# Clone or download this repository
cd redis-stateful-app
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory with your configuration:

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values
nano .env  # or use your preferred editor
```

**Minimum Required Configuration:**

```bash
# ============================================================================
# OpenAI Configuration (REQUIRED for Cloud provider)
# ============================================================================
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
OPENAI_MODEL=gpt-5-mini

# ============================================================================
# Ollama Configuration (OPTIONAL - for Local provider)
# ============================================================================
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_MODEL=llama3.2:3b

# ============================================================================
# Redis Configuration (defaults work fine)
# ============================================================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
SESSION_TTL_SECONDS=3600
```

**Important Notes:**
- **OpenAI API Key**: Required if you want to use ChatGPT (Cloud provider)
- **Ollama**: Optional - only needed if you want local inference
- **Docker Network**: The `host.docker.internal` URL allows Docker containers to access services on your host machine

### Step 3: (Optional) Set Up Ollama for Local Inference

If you want to use the local Ollama provider:

```bash
# 1. Install Ollama
# Download from https://ollama.com or use:
brew install ollama  # macOS

# 2. Start Ollama service
ollama serve

# 3. Pull a model (in a new terminal)
ollama pull llama3.2:3b  # Recommended: balanced performance

# Other model options:
# ollama pull qwen3:0.6b      # Smaller, faster
# ollama pull llama3.2        # Larger, better quality
# ollama pull mistral         # Alternative model

# 4. Verify installation
ollama list
curl http://localhost:11434/api/tags
```

### Step 4: Start the Application

```bash
# Start all services (Redis, Backend, Frontend)
docker-compose up -d

# View startup logs
docker-compose logs -f

# Check service status
docker-compose ps
```

**Expected Output:**
```
NAME            STATUS                  PORTS
redis-memory    Up (healthy)           0.0.0.0:6379->6379/tcp
chat-backend    Up (healthy)           0.0.0.0:9090->9090/tcp
chat-frontend   Up (healthy)           0.0.0.0:3000->80/tcp
```

### Step 5: Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

**Additional URLs:**
- Backend API: http://localhost:9090
- API Documentation: http://localhost:9090/docs (FastAPI Swagger UI)
- Health Check: http://localhost:9090/

**🎉 That's it! You're ready to start chatting!**

### Quick Start Scripts

For convenience, use the provided startup scripts:

```bash
# macOS/Linux
chmod +x start.sh
./start.sh

# Windows
start.bat
```

These scripts will:
1. Check if Docker is running
2. Create `.env` if it doesn't exist
3. Start all services
4. Display access URLs

## 🎯 How to Use

### Testing Memory Modes

**Test 1: Stateless Mode (No Memory)**

1. Keep the **Memory toggle OFF** (Stateless)
2. Send: "My name is Alice"
3. Send: "What's my name?"
4. **Expected**: The AI will say it doesn't know your name

**Test 2: Stateful Mode (With Memory)**

1. Toggle **Memory ON** (Stateful)
2. Send: "My name is Bob"
3. Send: "What's my name?"
4. **Expected**: The AI will say "Your name is Bob"

### Testing Provider Switching

**Test 3: Cloud vs Local Providers**

1. Start with **Cloud (ChatGPT)** selected
2. Have a short conversation
3. Toggle to **Local (Ollama)**
4. Continue the conversation
5. **Expected**: History is preserved across provider changes!

### Seamless Mode Switching

**Test 4: Switching Mid-Conversation**

1. **Memory OFF** + Cloud provider
2. Send: "I love pizza"
3. Switch **Memory ON** (keep Cloud)
4. Send: "What food do I like?"
5. **Expected**: "You like pizza" (history was always stored!)

### Understanding the UI

```
┌────────────────────────────────────────────┐
│  Chat                    [No Memory]  ⚙️   │  ← Header
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Memory:  Stateless ○───○ Stateful        │  ← Memory Toggle
│  Provider: Cloud ○───○ Local              │  ← Provider Toggle
├────────────────────────────────────────────┤
│                                            │
│  [User Message Bubble]                     │  ← Messages
│                  [AI Response Bubble]      │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Type your message...                 │ │  ← Input
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

**Badge Indicators:**
- "No Memory" - Stateless mode active
- "Remembering" - Stateful mode active
- Visual feedback on provider switching

## 📦 Docker Services

The application consists of three Docker services:

### Service Overview

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **redis** | redis/redis-stack-server:latest | 6379 | Conversation memory storage with RediSearch |
| **backend** | Built from `backend/Dockerfile` | 9090 | FastAPI application server |
| **frontend** | Built from `frontend/Dockerfile` | 3000 | Nginx serving static files |

### Redis Stack

Uses Redis Stack Server which includes:
- Redis core database
- RediSearch for MessageHistory functionality
- JSON support for complex data structures

**Persistent Storage**: Redis data is stored in a Docker volume named `redis-data`

### Backend (FastAPI)

**Key Files:**
- `main.py` - API endpoints and request routing
- `memory_service.py` - Redis integration with MessageHistory
- `models.py` - Pydantic models for validation
- `llm_service.py` - ChatGPT stateless service
- `stateful_llm_service.py` - ChatGPT stateful service
- `ollama_service.py` - Ollama stateless service
- `stateful_ollama_service.py` - Ollama stateful service

**Dependencies**: See `backend/requirements.txt` for full list including:
- FastAPI 0.118.0
- OpenAI 2.6.1 (Responses API support)
- Redis 5.0.1
- RedisVL 0.9.0 (MessageHistory)

### Frontend (Nginx)

**Static Files:**
- `index.html` - Main UI structure
- `app.js` - JavaScript logic and API calls
- `style.css` - Styling and themes
- `nginx.conf` - Web server configuration

**Features:**
- Responsive design
- Dark/light theme toggle
- Real-time provider/mode switching
- Message history display

## 🛠️ Docker Management

### Essential Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove all data (clears Redis)
docker-compose down -v

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f redis
docker-compose logs -f frontend

# Check service status
docker-compose ps

# Restart a specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose down
docker-compose up -d --build

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec redis redis-cli
docker-compose exec frontend sh
```

### Debugging Commands

```bash
# Check Redis connectivity
docker-compose exec redis redis-cli ping
# Expected: PONG

# View Redis keys
docker-compose exec redis redis-cli KEYS "*"

# View a specific session
docker-compose exec redis redis-cli KEYS "chat_history:*"

# Check backend health
curl http://localhost:9090/

# Check if Ollama is accessible from backend (macOS/Windows)
docker-compose exec backend curl http://host.docker.internal:11434/api/tags
```

### Resource Monitoring

```bash
# View container resource usage
docker stats

# View detailed container info
docker-compose ps -a

# View networks
docker network ls

# View volumes
docker volume ls
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "ChatGPT service not available"

**Symptoms:**
- Error message when trying to use Cloud provider
- Backend logs show OpenAI API errors

**Solutions:**

```bash
# Check if API key is set
grep OPENAI_API_KEY .env

# Verify API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-key-here"

# Check backend logs
docker-compose logs backend | grep -i openai

# Restart backend to reload environment
docker-compose restart backend
```

#### 2. "Ollama services not available"

**Symptoms:**
- Local provider unavailable or errors
- "Connection refused" errors

**Solutions:**

```bash
# Verify Ollama is running on host
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Check if model is installed
ollama list

# Pull model if missing
ollama pull llama3.2:3b

# Test connectivity from container (macOS/Windows)
docker-compose exec backend curl http://host.docker.internal:11434/api/tags

# For Linux: Update OLLAMA_BASE_URL in .env to:
OLLAMA_BASE_URL=http://172.17.0.1:11434/v1
# Or use: --network host in Docker
```

#### 3. "Redis connection failed"

**Symptoms:**
- Backend startup errors
- "Failed to connect to Redis" in logs

**Solutions:**

```bash
# Check Redis container status
docker-compose ps redis

# View Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis

# Check if Redis port is available
lsof -i :6379

# If port conflict, stop conflicting service or change port in docker-compose.yml
```

#### 4. "Frontend can't connect to backend"

**Symptoms:**
- UI loads but messages don't send
- CORS errors in browser console

**Solutions:**

```bash
# Verify backend is running
docker-compose ps backend

# Check backend health
curl http://localhost:9090/

# View backend logs
docker-compose logs backend

# Check for CORS errors in browser console (F12)

# Verify backend URL in frontend code
grep -r "localhost:9090" frontend/

# Restart all services
docker-compose restart
```

#### 5. "Port already in use"

**Symptoms:**
- Docker fails to start services
- "bind: address already in use" error

**Solutions:**

```bash
# Find what's using the ports
lsof -i :3000  # Frontend
lsof -i :9090  # Backend
lsof -i :6379  # Redis

# Kill the conflicting process
kill -9 <PID>

# Or modify ports in docker-compose.yml:
# ports:
#   - "3001:80"    # Change host port
#   - "9091:9090"
#   - "6380:6379"
```

#### 6. "MessageHistory initialization failed"

**Symptoms:**
- "unknown command 'FT._LIST'" error
- Backend fails to initialize MessageHistory

**Solutions:**

This means Redis Stack is not running (using basic Redis instead).

```bash
# Verify Redis Stack image
docker-compose ps redis

# Check image name should be: redis/redis-stack-server:latest

# If using wrong image, update docker-compose.yml:
# image: redis/redis-stack-server:latest

# Remove old Redis container and recreate
docker-compose down -v
docker-compose up -d
```

#### 7. "Docker daemon not running"

**Symptoms:**
- "Cannot connect to the Docker daemon" error

**Solutions:**

```bash
# macOS: Start Docker Desktop application

# Linux: Start Docker service
sudo systemctl start docker

# Verify Docker is running
docker ps

# Check Docker version
docker --version
docker-compose --version
```

### Health Check Endpoints

Test these endpoints to verify service health:

```bash
# Backend health
curl http://localhost:9090/

# Expected response:
# {
#   "status": "running",
#   "app": "Redis Memory Magic - Chat API Playground",
#   "services_available": {
#     "chatgpt": { "stateless": true, "stateful": true },
#     "ollama": { "stateless": true, "stateful": true }
#   }
# }

# Frontend health
curl http://localhost:3000/

# Expected: HTML content

# Redis health
docker-compose exec redis redis-cli ping

# Expected: PONG
```

## 📊 Project Structure

```
redis-stateful-app/
│
├── README.md                    # This file
├── DOCKER_README.md             # Detailed Docker guide
├── README-TASK2.md              # Development notes
├── claude.md                    # Claude Code context
│
├── .env                         # Your configuration (DO NOT COMMIT)
├── .env.example                 # Template for .env
├── .dockerignore                # Docker build exclusions
├── .gitignore                   # Git exclusions
│
├── docker-compose.yml           # Service orchestration
├── start.sh                     # macOS/Linux startup script
├── start.bat                    # Windows startup script
│
├── backend/                     # FastAPI Application
│   ├── Dockerfile               # Backend container definition
│   ├── requirements.txt         # Python dependencies
│   ├── .dockerignore
│   │
│   ├── main.py                  # API endpoints and routing
│   ├── models.py                # Pydantic models
│   ├── memory_service.py        # Redis + MessageHistory
│   │
│   ├── llm_service.py           # ChatGPT stateless
│   ├── stateful_llm_service.py  # ChatGPT stateful
│   ├── ollama_service.py        # Ollama stateless
│   └── stateful_ollama_service.py # Ollama stateful
│
└── frontend/                    # Static Web UI
    ├── Dockerfile               # Frontend container definition
    ├── nginx.conf               # Nginx configuration
    ├── .dockerignore
    │
    ├── index.html               # Main UI
    ├── app.js                   # JavaScript logic
    └── style.css                # Styling
```

## 🔌 API Reference

### Endpoints

#### GET /

Health check endpoint returning service status.

**Response:**
```json
{
  "status": "running",
  "app": "Redis Memory Magic - Chat API Playground",
  "modes": {
    "stateless": "No memory - each message is independent",
    "stateful": "Redis-backed memory - maintains conversation history"
  },
  "providers": {
    "chatgpt": "OpenAI ChatGPT API (cloud)",
    "ollama": "Ollama local inference (on-premises)"
  },
  "services_available": {
    "chatgpt": {
      "stateless": true,
      "stateful": true
    },
    "ollama": {
      "stateless": true,
      "stateful": true
    }
  }
}
```

#### POST /chat

Send a message and receive an AI response.

**Request:**
```json
{
  "message": "Hello! How are you?",
  "mode": "stateful",
  "provider": "chatgpt",
  "session_id": "optional-session-id"
}
```

**Parameters:**
- `message` (string, required): User's message (1-2000 characters)
- `mode` (string, required): Either "stateless" or "stateful"
- `provider` (string, required): Either "chatgpt" or "ollama"
- `session_id` (string, optional): Session identifier for conversation tracking

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking!",
  "mode": "stateful",
  "provider": "chatgpt",
  "session_id": "session_abc123",
  "message_count": 2
}
```

#### POST /clear-session

Clear conversation history for a specific session.

**Request:**
```json
{
  "session_id": "session_abc123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Session session_abc123 cleared"
}
```

### Using the API with curl

```bash
# Health check
curl http://localhost:9090/

# Send a stateless message
curl -X POST http://localhost:9090/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 2+2?",
    "mode": "stateless",
    "provider": "chatgpt"
  }'

# Send a stateful message with session
curl -X POST http://localhost:9090/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Alice",
    "mode": "stateful",
    "provider": "chatgpt",
    "session_id": "test_session_123"
  }'

# Continue the conversation
curl -X POST http://localhost:9090/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "mode": "stateful",
    "provider": "chatgpt",
    "session_id": "test_session_123"
  }'

# Clear session
curl -X POST http://localhost:9090/clear-session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_session_123"}'
```

## 🎓 Key Concepts

### Stateless vs Stateful Applications

**Stateless Architecture:**
- Each request is independent
- No server-side session data
- LLM receives only current message
- Simpler to scale (no state to sync)
- **Problem**: Can't maintain conversation context

**Stateful Architecture:**
- Server maintains conversation history
- LLM receives full context each time
- Enables natural multi-turn conversations
- **Challenge**: Requires session management

**This Application's Approach:**
- Uses Redis to store conversation history
- Session-based storage with automatic TTL
- Messages stored regardless of mode (enables seamless switching)
- Best of both: scalable storage + conversation memory

### Redis Message Storage

**RedisVL MessageHistory:**
```python
# Modern approach using RedisVL
from redisvl.extensions.message_history import MessageHistory

history = MessageHistory(name="chat_history")
history.add_message(
    {"role": "user", "content": "Hello"},
    session_tag=session_id
)
messages = history.get_recent(session_tag=session_id)
```

**Key Storage:**
- Pattern: `chat_history:{session_id}:*`
- Automatic timestamping
- Efficient retrieval with `get_recent()`
- Support for role filtering

### Session Management

**Session Lifecycle:**
1. Frontend generates unique session ID
2. All messages tagged with session ID
3. Redis stores with TTL (default: 1 hour)
4. TTL resets on each new message
5. Session expires after inactivity

**Session ID Format:**
```javascript
// Frontend generates
const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
```

### Provider Architecture

**Dual Service Pattern:**

Each provider has TWO implementations:
- **Stateless Service**: Sends only current message
- **Stateful Service**: Sends full conversation history

```python
# Backend selection logic
if mode == "stateless":
    service = stateless_service  # Single message
else:
    service = stateful_service   # Full history
```

**ChatGPT Services:**
- Use OpenAI Responses API (v2.6.1+)
- `store=False` to prevent OpenAI-side caching
- Redis is single source of truth

**Ollama Services:**
- Use OpenAI-compatible Chat Completions API
- Local inference, complete privacy
- Same message format as ChatGPT

## 🚀 Advanced Usage

### Running Without Docker

If you prefer local development:

**Prerequisites:**
- Python 3.11+
- Redis Stack Server
- Node.js/npm or Python HTTP server

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py
# Runs on http://localhost:9090
```

**Frontend:**
```bash
cd frontend

# Option 1: Python HTTP server
python -m http.server 3000

# Option 2: Node.js server
npx http-server -p 3000
```

**Redis Stack:**
```bash
# macOS
brew tap redis-stack/redis-stack
brew install redis-stack-server
redis-stack-server

# Docker (alternative)
docker run -d -p 6379:6379 redis/redis-stack-server:latest
```

### Environment Variables Reference

Complete list of available environment variables:

```bash
# ============================================================================
# OpenAI Configuration
# ============================================================================
OPENAI_API_KEY=sk-proj-...        # Required for ChatGPT
OPENAI_MODEL=gpt-5-mini           # Model to use

# ============================================================================
# Ollama Configuration
# ============================================================================
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1  # Ollama endpoint
OLLAMA_API_KEY=ollama                                  # Placeholder
OLLAMA_MODEL=llama3.2:3b                              # Installed model

# ============================================================================
# Redis Configuration
# ============================================================================
REDIS_HOST=redis                  # Hostname (docker service name)
REDIS_PORT=6379                   # Port
REDIS_DB=0                        # Database number
REDIS_PASSWORD=                   # Password (empty = no auth)
SESSION_TTL_SECONDS=3600          # Session expiration (1 hour)
```

### Custom Docker Compose Configuration

**Change Ports:**
```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Change host port to 8080
  backend:
    ports:
      - "8090:9090"  # Change host port to 8090
```

**Add Resource Limits:**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**Enable Redis Persistence:**
```yaml
services:
  redis:
    volumes:
      - redis-data:/data
    command: redis-stack-server --appendonly yes --save 60 1
```

## 🔒 Security Considerations

### Development vs Production

**Current Configuration (Development):**
- ⚠️ CORS allows all origins: `allow_origins=["*"]`
- ⚠️ No authentication or rate limiting
- ⚠️ API keys in plaintext `.env` file
- ⚠️ Redis has no password

**Production Requirements:**

1. **CORS Configuration:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

2. **Secrets Management:**
- Use Docker Secrets or Kubernetes Secrets
- Consider AWS Secrets Manager, HashiCorp Vault
- Never commit `.env` to version control

3. **Redis Security:**
```yaml
# docker-compose.yml
redis:
  command: redis-stack-server --requirepass yourpassword
  environment:
    - REDIS_PASSWORD=yourpassword
```

4. **Add Rate Limiting:**
```python
# Use slowapi or fastapi-limiter
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, ...):
    ...
```

5. **HTTPS/TLS:**
- Use nginx or Traefik as reverse proxy
- Obtain SSL certificates (Let's Encrypt)
- Redirect HTTP to HTTPS

6. **Authentication:**
- Implement JWT tokens or OAuth
- Add user session management
- Rate limit per user, not IP

### Best Practices

✅ **Do:**
- Use `.env` for local development only
- Implement proper secrets management in production
- Enable Redis authentication
- Configure CORS properly
- Add request validation
- Implement rate limiting
- Use HTTPS in production
- Monitor and log security events

❌ **Don't:**
- Commit `.env` file to git
- Use `allow_origins=["*"]` in production
- Store API keys in code
- Run without authentication
- Expose Redis port publicly
- Skip input validation

## 📚 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend Framework** | FastAPI | 0.118.0 | High-performance async API |
| **Runtime** | Python | 3.11 | Backend logic |
| **ASGI Server** | Uvicorn | 0.37.0 | Production server |
| **Database** | Redis Stack | latest | Message storage + RediSearch |
| **Redis Client** | redis-py | 5.0.1 | Redis connectivity |
| **LLM Integration** | RedisVL | 0.9.0 | MessageHistory for LLMs |
| **AI - Cloud** | OpenAI | 2.6.1 | ChatGPT API (Responses API) |
| **AI - Local** | Ollama | latest | Local inference |
| **HTTP Client** | httpx | 0.28.1 | Async HTTP requests |
| **Validation** | Pydantic | 2.11.9 | Request/response models |
| **Web Server** | Nginx | alpine | Static file serving |
| **Frontend** | Vanilla JS | ES6+ | No build tools needed |
| **Container** | Docker | latest | Containerization |
| **Orchestration** | Docker Compose | v2 | Multi-container apps |

## 🤝 Contributing

This is an educational project demonstrating Redis-backed LLM applications. Contributions are welcome!

**How to Contribute:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly with Docker
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

**Development Guidelines:**
- Follow existing code style
- Add comments for complex logic
- Update README if adding features
- Test both stateless and stateful modes
- Ensure Docker build succeeds

## 📄 License

MIT License - feel free to use this project for learning, teaching, or building your own applications!

## 🙏 Acknowledgments

- **Redis** for fast, reliable in-memory storage
- **OpenAI** for powerful language models
- **Ollama** for making local inference accessible
- **FastAPI** for excellent async Python framework
- **RedisVL** for LLM-optimized Redis patterns

## 📞 Support

**Having Issues?**
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review Docker logs: `docker-compose logs`
3. Verify health endpoints
4. Check GitHub issues for similar problems

**Resources:**
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/README.md)
- [Redis Documentation](https://redis.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RedisVL Documentation](https://docs.redisvl.com/)

## 🎯 Use Cases

This architecture pattern is ideal for:

- **Chatbots & Virtual Assistants**: Customer support, personal assistants
- **Document Q&A Systems**: Contextual document analysis and answering
- **Code Assistants**: Programming help with conversation context
- **Educational Tools**: Tutoring systems that remember student progress
- **Healthcare**: Patient interaction systems with medical history context
- **E-commerce**: Shopping assistants that remember preferences
- **Content Creation**: Writing assistants that maintain context

---

**Built with ❤️ to demonstrate production-ready LLM applications with Redis**

🚀 **Ready to get started?**

```bash
docker-compose up -d
```

Then open **http://localhost:3000** and start chatting!

For detailed Docker instructions, see [DOCKER_README.md](DOCKER_README.md)