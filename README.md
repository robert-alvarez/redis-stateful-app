# 🚀 Redis Memory Magic - LLM Chat Application

A production-ready chat application demonstrating **stateless vs stateful LLM architecture** with Redis-backed conversation memory. Switch between cloud (ChatGPT) and local (Ollama) inference providers seamlessly while maintaining conversation history.

## 📖 Overview

This application showcases the fundamental difference between stateless and stateful AI applications:

- **Stateless Mode**: Each message is sent to the LLM without context - the AI forgets previous messages
- **Stateful Mode**: Full conversation history is maintained in Redis - the AI remembers your entire conversation

Additionally, you can switch between:
- **Cloud Provider (ChatGPT)**: Fast, powerful responses from OpenAI's API
- **Local Provider (Ollama)**: Privacy-focused, offline inference running on your machine

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
vi .env  # or use your preferred editor
```

**Minimum Required Configuration:**

```bash
# ============================================================================
# OpenAI Configuration (REQUIRED for Cloud provider)
# ============================================================================
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
OPENAI_MODEL=gpt-5-mini # or model of choice

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
ollama pull llama3.2:3b  

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