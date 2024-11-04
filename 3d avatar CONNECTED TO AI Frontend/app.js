class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.apiBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:10000'  // Local development
            : 'https://threed-avatar-connected-to-ai-1.onrender.com';  // Production
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
        const loginUrl = `${this.apiBaseUrl}/chat/login/`;
        
        if (this.isDevelopment) {
            console.log('Attempting login...', {
                url: loginUrl,
                username: this.credentials.username,
                timestamp: new Date().toISOString()
            });
        }

        try {
            const response = await fetch(loginUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(this.credentials)
            });

            if (!response.ok) {
                let errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.authToken = data.token;
            
            if (this.isDevelopment) {
                console.log('Login successful:', { 
                    hasToken: !!this.authToken,
                    timestamp: new Date().toISOString()
                });
            }

            return true;
        } catch (error) {
            console.error('Login error:', error);
            if (this.isDevelopment) {
                console.log('Login attempt details:', {
                    url: loginUrl,
                    error: error.toString(),
                    timestamp: new Date().toISOString()
                });
            }
            throw error;
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
                    token: this.authToken ? 'Present' : 'No token',
                    message: message.substring(0, 50) + '...'
                });
            }

            const response = await fetch(`${this.apiBaseUrl}/chat/conversations/${this.currentConversationId}/send_message/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': `Token ${this.authToken}`
                },
                credentials: 'include',
                mode: 'cors',
                body: JSON.stringify({ message })
            });

            // Enhanced error handling
            if (!response.ok) {
                let errorMessage = 'Server error occurred';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.error || `Server error: ${response.status}`;
                } catch (e) {
                    errorMessage = `Server error: ${response.status}`;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            this.addMessage(data.message, 'ai');
        } catch (error) {
            console.error('Message sending error:', error);
            
            // Enhanced error message for users
            let userMessage = 'Failed to send message. ';
            if (error.message.includes('Failed to fetch')) {
                userMessage += 'Please check your internet connection.';
            } else if (error.message.includes('502')) {
                userMessage += 'The server is temporarily unavailable. Please try again in a few moments.';
            } else {
                userMessage += error.message;
            }
            
            this.addMessage(userMessage, 'system');
            
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