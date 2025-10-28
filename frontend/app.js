/**
 * Stateless Chat Application - Frontend
 *
 * IMPORTANT: This frontend sends each message independently to the backend.
 * The backend is completely STATELESS and has NO memory of previous messages.
 *
 * This demonstrates the fundamental problem with LLM applications that
 * don't maintain conversation history.
 */

// Configuration
// Use environment variable or default to localhost:9090
const API_URL = window.CHAT_API_URL || 'http://localhost:9090/chat';

// DOM Elements
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const messagesContainer = document.getElementById('messages-container');
const welcomeCard = document.getElementById('welcome-card');
const themeToggle = document.getElementById('theme-toggle');
const loadingTemplate = document.getElementById('loading-template');
const modeToggle = document.getElementById('mode-toggle');
const modeBadge = document.getElementById('mode-badge');
const providerToggle = document.getElementById('provider-toggle');
const providerBadge = document.getElementById('provider-badge');

// State
let isLoading = false;
let currentMode = 'stateless'; // 'stateless' or 'stateful'
let currentProvider = 'chatgpt'; // 'chatgpt' or 'ollama'
let sessionId = null; // Session ID for stateful mode

/**
 * Initialize theme from localStorage
 */
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

/**
 * Toggle dark/light mode
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

/**
 * Toggle between stateless and stateful mode
 */
function toggleMode() {
    const isStateful = modeToggle.checked;
    currentMode = isStateful ? 'stateful' : 'stateless';

    // Update badge
    if (isStateful) {
        modeBadge.textContent = 'Has Memory';
        modeBadge.classList.add('stateful');
    } else {
        modeBadge.textContent = 'No Memory';
        modeBadge.classList.remove('stateful');
    }

    // Always maintain session ID - this allows seamless toggling
    // Messages are always logged to Redis, but only sent to API when in stateful mode
    if (!sessionId) {
        sessionId = generateSessionId();
    }

    console.log(`Switched to ${currentMode} mode (session: ${sessionId})`);
}

/**
 * Toggle between Cloud (ChatGPT) and Local (Ollama) provider
 */
function toggleProvider() {
    const isLocal = providerToggle.checked;
    currentProvider = isLocal ? 'ollama' : 'chatgpt';

    // Update badge
    providerBadge.classList.remove('local');

    if (isLocal) {
        providerBadge.textContent = 'Local';
        providerBadge.classList.add('local');
    } else {
        providerBadge.textContent = 'Cloud';
    }

    console.log(`Switched to ${isLocal ? 'Local (Ollama)' : 'Cloud (ChatGPT)'} provider`);
}

/**
 * Generate a unique session ID
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Hide welcome card when first message is sent
 */
function hideWelcome() {
    if (welcomeCard) {
        welcomeCard.style.display = 'none';
    }
}

/**
 * Create a message section element
 */
function createMessageSection(text, isUser = false) {
    const section = document.createElement('section');
    section.className = `message-section ${isUser ? 'user-message' : 'assistant-message'}`;

    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper';

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = isUser ? 'You' : 'Assistant';

    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.textContent = text;

    wrapper.appendChild(label);
    wrapper.appendChild(messageText);
    section.appendChild(wrapper);

    return section;
}

/**
 * Add a message to the chat
 */
function addMessage(text, isUser = false) {
    hideWelcome();

    const messageSection = createMessageSection(text, isUser);
    messagesContainer.appendChild(messageSection);

    // Scroll to bottom
    scrollToBottom();
}

/**
 * Show loading indicator
 */
function showLoading() {
    hideWelcome();

    const loadingElement = loadingTemplate.content.cloneNode(true);
    messagesContainer.appendChild(loadingElement);
    scrollToBottom();
}

/**
 * Remove loading indicator
 */
function removeLoading() {
    const loadingSection = messagesContainer.querySelector('.loading-section');
    if (loadingSection) {
        loadingSection.remove();
    }
}

/**
 * Show error message
 */
function showError(message) {
    hideWelcome();

    const section = document.createElement('section');
    section.className = 'message-section error-section';

    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper';

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = `Error: ${message}`;

    wrapper.appendChild(errorDiv);
    section.appendChild(wrapper);
    messagesContainer.appendChild(section);

    scrollToBottom();
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
    setTimeout(() => {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

/**
 * Set loading state
 */
function setLoading(loading) {
    isLoading = loading;
    sendButton.disabled = loading;
    messageInput.disabled = loading;

    if (loading) {
        showLoading();
    } else {
        removeLoading();
    }
}

/**
 * Send message to the backend
 *
 * Supports two modes:
 * - STATELESS: Only the current message is sent (no history)
 * - STATEFUL: Message sent with session_id, full history is maintained in Redis
 */
async function sendMessage(message) {
    try {
        // Ensure we have a session ID
        if (!sessionId) {
            sessionId = generateSessionId();
        }

        // Prepare request payload - ALWAYS include session_id
        // This allows messages to be logged even in stateless mode
        const payload = {
            message: message,
            mode: currentMode,
            provider: currentProvider,
            session_id: sessionId
        };

        console.log('Sending request:', payload);

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get response');
        }

        const data = await response.json();

        // Store session_id from response if in stateful mode
        if (data.mode === 'stateful' && data.session_id) {
            sessionId = data.session_id;
            console.log(`Session: ${sessionId}, Messages: ${data.message_count}`);
        }

        return data.response;

    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
}

/**
 * Handle form submission
 */
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message || isLoading) return;

    // Add user message to UI
    addMessage(message, true);

    // Clear input
    messageInput.value = '';

    // Show loading
    setLoading(true);

    try {
        // Send ONLY the current message (stateless!)
        // No conversation history is sent to the backend
        const response = await sendMessage(message);

        // Add assistant response to UI
        addMessage(response, false);

    } catch (error) {
        showError(error.message || 'Something went wrong. Please try again.');
    } finally {
        setLoading(false);
        messageInput.focus();
    }
});

/**
 * Theme toggle event listener
 */
themeToggle.addEventListener('click', toggleTheme);

/**
 * Mode toggle event listener
 */
modeToggle.addEventListener('change', toggleMode);

/**
 * Provider toggle event listener
 */
providerToggle.addEventListener('change', toggleProvider);

/**
 * Initialize app
 */
function init() {
    initTheme();
    messageInput.focus();

    // Set initial mode and generate session ID
    // Session ID is always generated to enable seamless mode toggling
    currentMode = 'stateless';
    sessionId = generateSessionId();

    console.log(`App initialized in ${currentMode} mode (session: ${sessionId})`);
}

// Start the app
init();

/**
 * DEVELOPER NOTE:
 *
 * This application demonstrates Redis-backed memory with TWO dimensions:
 *
 * === MEMORY MODE (Stateless vs Stateful) ===
 *
 * STATELESS MODE (Default):
 * - Only the current message is sent to the LLM
 * - The LLM has NO memory of previous messages
 * - Messages ARE still logged to Redis for seamless mode switching
 *
 * STATEFUL MODE (Toggle On):
 * - The ENTIRE conversation history from Redis is sent with each request
 * - The LLM remembers everything from the current session
 * - Redis is the single source of truth for conversation history
 *
 * === PROVIDER (Cloud vs Local) ===
 *
 * CLOUD (ChatGPT - Default):
 * - Uses OpenAI's cloud API
 * - Requires OPENAI_API_KEY
 * - Production-ready, highly optimized
 * - Best performance and quality
 *
 * LOCAL (Ollama):
 * - Uses local Ollama for on-premises inference
 * - OpenAI-compatible API
 * - Easy to install and use (ollama.com)
 * - Requires running Ollama (default: http://localhost:11434)
 * - Full data privacy and control
 * - No API costs
 *
 * === FOUR COMBINATIONS ===
 * 1. Cloud (ChatGPT) + Stateless
 * 2. Cloud (ChatGPT) + Stateful
 * 3. Local (Ollama) + Stateless
 * 4. Local (Ollama) + Stateful
 *
 * === SEAMLESS TOGGLING ===
 * You can switch between modes and providers at any time!
 * - Messages are ALWAYS logged to Redis (even in stateless mode)
 * - When you enable memory, it picks up the full conversation history
 * - Switch between Cloud (ChatGPT) and Local (Ollama) mid-conversation
 * - No need to restart - toggle on/off as needed!
 *
 * Try toggling between modes and providers during a conversation!
 */
