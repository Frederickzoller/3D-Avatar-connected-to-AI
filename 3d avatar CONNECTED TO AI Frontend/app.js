class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.apiBaseUrl = 'https://threed-avatar-connected-to-ai-1.onrender.com';
        this.authToken = null;
        this.currentConversationId = null;
        this.maxRetries = 3;
        this.retryDelay = 1000;

        // Enhanced development configuration
        this.isDevelopment = window.location.protocol === 'file:' || 
                            window.location.hostname === 'localhost' || 
                            window.location.hostname === '127.0.0.1';

        if (window.location.protocol === 'file:') {
            this.showServerInstructions();
            return; // Don't initialize if running from file://
        }

        // Update credentials to match server requirements
        this.credentials = {
            username: 'demo_user',  // Updated username
            password: 'demo_password'  // Updated password
        };

        this.init();
    }

    showServerInstructions() {
        const instructions = `
            To run this application, you need to use a local development server.
            
            Option 1 - Using Python:
            1. Open terminal/command prompt
            2. Navigate to the project directory
            3. Run: python -m http.server 5500
            4. Open: http://localhost:5500
            
            Option 2 - Using Node.js:
            1. Install: npm install -g http-server
            2. Navigate to project directory
            3. Run: http-server
            4. Open: http://localhost:8080
            
            After setting up the server, refresh this page in your browser.
        `;
        
        this.addMessage(instructions, 'system');
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
    }

    init() {
        this.setupEventListeners();
        this.autoResizeInput();
        this.login();
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    autoResizeInput() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
    }

    async login(retryCount = 0) {
        try {
            if (this.isDevelopment) {
                console.log('Attempting login...', {
                    url: `${this.apiBaseUrl}/chat/login/`,
                    username: this.credentials.username,
                    timestamp: new Date().toISOString()
                });
            }

            const response = await fetch(`${this.apiBaseUrl}/chat/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                credentials: 'same-origin',
                body: JSON.stringify({
                    username: this.credentials.username,
                    password: this.credentials.password
                })
            });

            // Log the raw response in development
            if (this.isDevelopment) {
                console.log('Server response:', {
                    status: response.status,
                    statusText: response.statusText,
                    headers: Object.fromEntries(response.headers.entries())
                });
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.authToken = data.token;
            
            if (this.isDevelopment) {
                console.log('Login successful:', {
                    userId: data.user_id,
                    hasToken: Boolean(this.authToken)
                });
            }

            await this.createConversation();
        } catch (error) {
            console.error('Login error:', error);
            
            if (retryCount < this.maxRetries) {
                console.log(`Retrying login... Attempt ${retryCount + 1} of ${this.maxRetries}`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                return this.login(retryCount + 1);
            }
            
            this.addMessage('Failed to connect to the server. Please try again later.', 'system');
        }
    }

    // Add helper method to clear system messages
    clearSystemMessages() {
        const systemMessages = this.chatMessages.querySelectorAll('.message.system');
        systemMessages.forEach(msg => msg.remove());
    }

    async createNewConversation() {
        if (!this.authToken) {
            this.addMessage('Error: Not authenticated. Please refresh the page.', 'system');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/conversations/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${this.authToken}`,
                    'Content-Type': 'application/json',
                },
                mode: 'cors',
                credentials: 'omit',
                body: JSON.stringify({
                    title: 'New Chat'
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    this.authToken = null;
                    throw new Error('Authentication expired. Please refresh the page.');
                }
                throw new Error('Failed to create conversation');
            }

            const data = await response.json();
            this.currentConversationId = data.id;
            this.addMessage('Hello! How can I assist you today?', 'ai');
        } catch (error) {
            console.error('Conversation creation error:', error);
            this.addMessage(error.message, 'system');
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        if (!this.authToken || !this.currentConversationId) {
            this.addMessage('Error: Not properly connected. Please refresh the page.', 'system');
            return;
        }

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        try {
            if (this.isDevelopment) {
                console.log('Sending message...', {
                    url: `${this.apiBaseUrl}/chat/conversations/${this.currentConversationId}/send_message/`,
                    token: this.authToken ? 'Token present' : 'No token',
                    message: message.substring(0, 50) + '...'
                });
            }

            const response = await fetch(`${this.apiBaseUrl}/chat/conversations/${this.currentConversationId}/send_message/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${this.authToken}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Origin': window.location.origin
                },
                mode: 'cors',
                credentials: 'include',
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({
                    detail: `Server error: ${response.status}`
                }));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();
            this.addMessage(data.message, 'ai');
        } catch (error) {
            console.error('Message sending error:', error);
            this.addMessage(`Error: ${error.message}. Please try again.`, 'system');
            
            // Add detailed error logging
            if (this.isDevelopment) {
                console.log('Detailed error information:', {
                    error: error.toString(),
                    stack: error.stack,
                    authToken: this.authToken ? 'Present' : 'Missing',
                    conversationId: this.currentConversationId
                });
            }
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        messageDiv.textContent = content;
        
        if (type === 'system') {
            messageDiv.style.backgroundColor = 'var(--error)';
            messageDiv.style.opacity = '0.8';
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize with protocol check
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.protocol === 'file:') {
        console.warn(`
            Running from file:// protocol. 
            Please use a local development server to avoid CORS issues.
            Check the instructions in the chat window for setup details.
        `);
    }
    new ChatApp();
}); 