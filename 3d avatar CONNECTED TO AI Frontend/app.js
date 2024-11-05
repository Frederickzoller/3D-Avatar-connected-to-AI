class ChatApp {
    constructor() {
        this.loginForm = document.getElementById('loginForm');
        this.loginError = document.getElementById('loginError');
        this.mainContent = document.getElementById('mainContent');
        this.loginSection = document.getElementById('loginSection');
        
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        
        this.authToken = null;
        this.currentConversationId = null;
        this.maxRetries = 3;
        this.retryDelay = 1000;

        this.isDevelopment = false;
        this.apiBaseUrl = this.getApiBaseUrl();
        console.log('API Base URL:', this.apiBaseUrl);

        this.init();
    }

    getApiBaseUrl() {
        return 'https://threed-avatar-connected-to-ai-1.onrender.com';
    }

    init() {
        this.loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        this.setupEventListeners();
        this.autoResizeInput();
    }

    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            this.loginError.textContent = 'Logging in...';
            
            const success = await this.login(username, password);
            if (success) {
                this.loginSection.style.display = 'none';
                this.mainContent.style.display = 'flex';
                this.addMessage('Welcome! You can start chatting now.', 'system');
            }
        } catch (error) {
            this.loginError.textContent = error.message || 'Login failed. Please try again.';
            if (this.isDevelopment) {
                console.error('Login error:', error);
            }
        }
    }

    async login(username, password) {
        const loginUrl = `${this.apiBaseUrl}/chat/login/`;
        
        console.log('Login attempt:', {
            url: loginUrl,
            username,
            timestamp: new Date().toISOString()
        });

        try {
            const response = await fetch(loginUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('Login failed:', {
                    status: response.status,
                    statusText: response.statusText,
                    error: errorData
                });
                throw new Error(errorData.detail || 'Invalid credentials');
            }

            const data = await response.json();
            this.authToken = data.token;
            return true;

        } catch (error) {
            console.error('Connection error details:', {
                url: loginUrl,
                error: error.toString()
            });
            throw new Error('Unable to connect to server. Please try again in a few moments.');
        }
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