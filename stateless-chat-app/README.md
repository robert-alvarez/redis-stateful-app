# Stateless Chat Application - Task 1

⚠️ **IMPORTANT**: This application is **intentionally stateless** and has **NO memory management**. It demonstrates the fundamental problem with LLM chat applications that don't maintain conversation history.

## Overview

This is an educational project that shows what happens when an LLM-powered chat application doesn't maintain conversation context. Each message is sent to the LLM independently, causing it to "forget" everything from previous exchanges.

### The Problem

**Without memory management:**
- Each user message is sent to the LLM in isolation
- The LLM has no context from previous messages
- The assistant cannot remember names, facts, or earlier parts of the conversation
- Every response is based solely on the current message

This baseline demonstrates **why** conversation memory is crucial for chat applications.

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Modern web framework
- **OpenAI API** - LLM integration (GPT-3.5/GPT-4)
- **Pydantic** - Data validation
- **python-dotenv** - Environment configuration

### Frontend
- **Vanilla JavaScript** - No frameworks needed
- **HTML5 + CSS3** - Clean, modern UI
- **Fetch API** - HTTP requests

## Project Structure

```
stateless-chat-app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── llm_service.py       # OpenAI API integration
│   ├── models.py            # Pydantic models
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Chat interface
│   ├── style.css            # Styling
│   └── app.js               # Frontend logic
├── .env.example             # Environment template
└── README.md                # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Modern web browser

### 2. Clone/Download the Project

```bash
cd stateless-chat-app
```

### 3. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
# Copy the example environment file
cp ../.env.example ../.env

# Edit .env and add your OpenAI API key
# Use your favorite editor (nano, vim, vscode, etc.)
nano ../.env
```

Add your API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### 4. Run the Backend

```bash
# Make sure you're in the backend directory
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The backend will start at: **http://localhost:8000**

You can test it's working by visiting: http://localhost:8000 (should show a status message)

### 5. Run the Frontend

Open `frontend/index.html` in your web browser:

**Option 1 - Direct Open:**
```bash
# From the project root
open frontend/index.html  # macOS
# or
xdg-open frontend/index.html  # Linux
# or just double-click the file in Windows
```

**Option 2 - Simple HTTP Server (recommended):**
```bash
# From the frontend directory
cd frontend
python -m http.server 8080
```
Then visit: **http://localhost:8080**

## Demonstrating the Stateless Problem

### Example 1: Name Amnesia

**Try this conversation:**

1. **You:** "My name is Alice"
   - **Bot:** "Nice to meet you, Alice!" ✅

2. **You:** "What's my name?"
   - **Bot:** "I don't know your name. You haven't told me yet." ❌

**Why?** The second message was sent without any context from the first message!

### Example 2: Lost Context

**Try this:**

1. **You:** "I have a dog named Max"
   - **Bot:** "That's wonderful! Max sounds like a great dog!" ✅

2. **You:** "What's my dog's name?"
   - **Bot:** "I don't have information about your dog's name." ❌

3. **You:** "Do I have any pets?"
   - **Bot:** "I don't know if you have any pets." ❌

**Why?** Each question is sent independently - the bot can't remember earlier messages.

### Example 3: Conversation Flow Broken

**Try this:**

1. **You:** "I'm planning a trip to Paris"
   - **Bot:** "That sounds exciting! Paris is beautiful..." ✅

2. **You:** "What should I visit there?"
   - **Bot:** "Where are you planning to visit?" ❌

**Why?** The bot doesn't remember you mentioned Paris!

## Technical Details

### API Endpoint

**POST /chat**

Request:
```json
{
  "message": "Hello, my name is Alice"
}
```

Response:
```json
{
  "response": "Hello Alice! Nice to meet you!"
}
```

### How It Works (The Stateless Problem)

**What the backend sends to OpenAI:**

```python
# Only the current message - no history!
messages=[
    {
        "role": "user",
        "content": "What's my name?"  # Only this message
    }
]
```

**What it SHOULD send (with memory):**
```python
# Full conversation history
messages=[
    {"role": "user", "content": "My name is Alice"},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"}
]
```

This application intentionally does NOT include the conversation history, demonstrating the problem.

## Key Code Locations

### Stateless LLM Call
See `backend/llm_service.py:30-47` - Only sends current message, no history

### Frontend Message Sending
See `frontend/app.js:45-64` - Sends each message independently

### API Endpoint
See `backend/main.py:43-75` - Stateless chat endpoint

## What's NOT Included (Intentionally!)

❌ No database
❌ No Redis
❌ No session management
❌ No conversation history storage
❌ No context passing between requests
❌ No memory of any kind

This is the **problem** we're demonstrating!

## Next Steps (Future Tasks)

This baseline application sets the stage for learning about LLM memory management:

1. **Task 2**: Add Redis-based conversation memory
2. **Task 3**: Implement conversation history limits
3. **Task 4**: Add session management
4. **Task 5**: Implement conversation summarization

## Troubleshooting

### Backend won't start
- Check your Python version: `python --version` (need 3.10+)
- Verify your OpenAI API key in `.env`
- Check if port 8000 is already in use

### "API key not found" error
- Make sure you created `.env` file (copy from `.env.example`)
- Verify the API key is correct
- Check the file is in the project root, not in `backend/`

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify the API_URL in `app.js` is correct

### OpenAI API errors
- Check your API key is valid
- Verify you have credits in your OpenAI account
- Check your rate limits

## API Costs

This application uses OpenAI's API:
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens (very cheap)
- **GPT-4**: ~$0.03 per 1K tokens (more expensive)

A typical conversation message costs less than $0.01 with GPT-3.5.

## License

Educational purposes - feel free to use and modify!

## Support

This is a demonstration project for learning about LLM memory management. For questions about the concepts, refer to the documentation of the respective libraries.

---

**Remember**: This application is intentionally broken (no memory) to demonstrate the problem. This is not a bug - it's the whole point! 🎓
