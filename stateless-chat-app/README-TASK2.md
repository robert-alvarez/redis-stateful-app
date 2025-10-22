# Chat Application - Stateless vs Stateful (Task 2)

This application demonstrates the difference between **stateless** and **stateful** LLM chat applications using Redis for conversation memory.

## Overview

### Task 1 (Baseline)
The original implementation was intentionally stateless - showing the problem when LLMs don't maintain conversation history.

### Task 2 (This Version)
Now supports **BOTH** modes with a UI toggle:

| Mode | Memory | Storage | Behavior |
|------|--------|---------|----------|
| **Stateless** | ❌ None | None | Each message independent, LLM has no memory |
| **Stateful** | ✅ Full History | Redis | Conversation stored by session, LLM remembers context |

## What's New in Task 2

### Backend Changes

1. **Redis Integration** (`memory_service.py`)
   - Session-based conversation storage
   - Automatic expiration (default: 1 hour)
   - Message history management

2. **Stateful LLM Service** (`stateful_llm_service.py`)
   - Maintains conversation history in Redis
   - Sends full context with each request
   - Session-aware responses

3. **Dual-Mode API** (`main.py`)
   - Single `/chat` endpoint supports both modes
   - Mode selection via request parameter
   - Session ID generation and tracking

### Frontend Changes

1. **Mode Toggle Switch**
   - Visual toggle in header (Stateless ⟷ Stateful)
   - Dynamic badge updates
   - Persistent session management

2. **Enhanced API Calls**
   - Sends mode parameter
   - Includes session_id for stateful mode
   - Displays message count

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Web framework
- **Redis 5.0+** - Conversation memory store
- **OpenAI API** - LLM provider
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript** - No frameworks
- **Modern CSS** - Clean, responsive design
- **LocalStorage** - Theme and preferences

## Architecture

```
┌─────────────┐
│   Frontend  │
│  (Browser)  │
└──────┬──────┘
       │ HTTP Request: {message, mode, session_id?}
       ↓
┌─────────────────────────┐
│  FastAPI Backend        │
│                         │
│  ┌──────────────────┐  │
│  │  Stateless       │  │ → OpenAI API
│  │  LLM Service     │  │   (single message)
│  └──────────────────┘  │
│                         │
│  ┌──────────────────┐  │
│  │  Stateful        │  │ → OpenAI API
│  │  LLM Service     │  │   (full history)
│  └────────┬─────────┘  │
│           │             │
│  ┌────────▼─────────┐  │
│  │  Memory Service  │  │
│  └────────┬─────────┘  │
└───────────┼─────────────┘
            │
     ┌──────▼──────┐
     │    Redis    │
     │  (Sessions) │
     └─────────────┘
```

## Setup Instructions

### Prerequisites

1. **Python 3.10+**
2. **Redis Server** running locally or remotely
3. **OpenAI API Key**

### 1. Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 2. Backend Setup

```bash
cd stateless-chat-app/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env and add your OPENAI_API_KEY
```

Your `.env` file should contain:
```env
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-3.5-turbo

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=  # Optional

SESSION_TTL_SECONDS=3600  # 1 hour
```

### 3. Start the Backend

```bash
python main.py
```

Backend runs on: **http://localhost:9090**

### 4. Start the Frontend

```bash
cd ../frontend
python -m http.server 8080
```

Frontend available at: **http://localhost:8080**

## Testing the Modes

### Stateless Mode Test

1. Keep toggle OFF (default)
2. Say: **"My name is Alice"**
   - Bot: *"Nice to meet you, Alice!"* ✅
3. Ask: **"What's my name?"**
   - Bot: *"I don't know your name."* ❌

**Why?** Only the second message was sent to the LLM - no history!

### Stateful Mode Test

1. Toggle ON (switch to "Stateful")
2. Say: **"My name is Alice"**
   - Bot: *"Nice to meet you, Alice!"* ✅
3. Ask: **"What's my name?"**
   - Bot: *"Your name is Alice!"* ✅
4. Ask: **"What did we just talk about?"**
   - Bot: *"We discussed your name..."* ✅

**Why?** The entire conversation history is sent with each request!

## Key Implementation Details

### Session Management

**Session Creation:**
- Automatically generated when first message sent in stateful mode
- Format: `session_<timestamp>_<random>`
- Stored in frontend, sent with each request

**Session Storage:**
- Redis key: `chat:session:{session_id}:messages`
- Data: JSON array of `{role, content}` objects
- TTL: 1 hour (configurable)

**Session Lifecycle:**
1. User sends first message (stateful mode)
2. Backend generates session_id (if not provided)
3. Message stored in Redis
4. Session_id returned to frontend
5. Subsequent messages use same session_id
6. Session expires after TTL

### Message Flow

**Stateless:**
```python
messages = [
    {"role": "user", "content": "What's my name?"}
]
# Only current message sent to OpenAI
```

**Stateful:**
```python
messages = [
    {"role": "user", "content": "My name is Alice"},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"}
]
# Full conversation history sent to OpenAI
```

### Redis Data Structure

```
Key: chat:session:session_123:messages
Type: List
Value: [
    '{"role": "user", "content": "My name is Alice"}',
    '{"role": "assistant", "content": "Nice to meet you!"}',
    '{"role": "user", "content": "What\'s my name?"}'
]
TTL: 3600 seconds
```

## API Reference

### POST /chat

**Request:**
```json
{
  "message": "Hello!",
  "mode": "stateful",
  "session_id": "session_123"  // optional
}
```

**Response:**
```json
{
  "response": "Hi there!",
  "mode": "stateful",
  "session_id": "session_123",
  "message_count": 4
}
```

### POST /clear-session

**Request:**
```bash
curl -X POST "http://localhost:9090/clear-session?session_id=session_123"
```

**Response:**
```json
{
  "status": "success",
  "message": "Session session_123 cleared"
}
```

### GET /

**Response:**
```json
{
  "status": "running",
  "app": "Chat Application - Stateless vs Stateful",
  "modes": {
    "stateless": "No memory - demonstrates the problem",
    "stateful": "Redis-backed memory - maintains conversation history"
  },
  "stateless_available": true,
  "stateful_available": true
}
```

## Project Structure

```
stateless-chat-app/
├── backend/
│   ├── main.py                    # FastAPI app with dual-mode support
│   ├── llm_service.py             # Stateless LLM service
│   ├── stateful_llm_service.py    # Stateful LLM service (NEW)
│   ├── memory_service.py          # Redis memory management (NEW)
│   ├── models.py                  # Pydantic models (updated)
│   └── requirements.txt           # Dependencies (added redis)
├── frontend/
│   ├── index.html                 # UI with mode toggle (updated)
│   ├── style.css                  # Styles (updated)
│   └── app.js                     # Frontend logic (updated)
├── .env.example                   # Environment template (updated)
├── README.md                      # Original README (Task 1)
└── README-TASK2.md                # This file
```

## Troubleshooting

### Redis Connection Error

**Error:** `Failed to connect to Redis`

**Solutions:**
1. Check Redis is running: `redis-cli ping`
2. Verify REDIS_HOST and REDIS_PORT in `.env`
3. Check firewall rules
4. If using password: Set REDIS_PASSWORD in `.env`

### Session Not Persisting

**Issue:** Bot forgets after toggling modes

**Explanation:** This is expected! Toggling modes clears the context.
- Stateless: No memory by design
- Stateful: New session created when toggling back on

### "Memory service not available"

**Cause:** Redis connection failed at startup

**Fix:**
1. Start Redis: `redis-server` or `brew services start redis`
2. Restart backend: `python main.py`

## Advanced Configuration

### Adjust Session TTL

In `.env`:
```env
SESSION_TTL_SECONDS=7200  # 2 hours
```

### Use Remote Redis

```env
REDIS_HOST=your-redis-server.com
REDIS_PORT=6379
REDIS_PASSWORD=your-password
```

### Change OpenAI Model

```env
OPENAI_MODEL=gpt-4  # Better responses, higher cost
```

## Comparing the Modes

| Feature | Stateless | Stateful |
|---------|-----------|----------|
| Memory | None | Full conversation |
| Storage | None | Redis |
| Context | Single message | All messages |
| Use Case | Demos the problem | Production-ready |
| Cost | Lower (fewer tokens) | Higher (more tokens) |
| Latency | Faster | Slightly slower |

## Next Steps (Future Tasks)

Potential enhancements:
1. **Token Management** - Limit conversation length
2. **Summarization** - Compress old messages
3. **Vector Search** - Semantic retrieval
4. **Multi-User** - Session isolation
5. **Persistence** - Database backup
6. **Analytics** - Usage tracking

## Redis Patterns Used

This implementation follows patterns from [Redis Agent Memory Server](https://github.com/redis/agent-memory-server):

- **Session-scoped working memory**
- **Key-value storage** for conversation history
- **TTL-based expiration** for automatic cleanup
- **Atomic operations** with Redis lists

## License

Educational demonstration project - feel free to use and modify!

---

**Remember**: This demonstrates TWO approaches - toggle between them to see the difference! 🎯
