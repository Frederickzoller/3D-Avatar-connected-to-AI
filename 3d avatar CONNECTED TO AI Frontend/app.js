class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.apiBaseUrl = 'https://threed-avatar-connected-to-ai-1.onrender.com';
        this.authToken = null;
        this.currentConversationId = null;
        this.maxRetries = 3;
        this.retryDelay = 1000; // 1 second

        // Add development configuration
        this.isDevelopment = window.location.hostname === 'localhost' || window.location.protocol === 'file:';
        if (this.isDevelopment) {
            console.log('Running in development mode');
        }

        this.init();
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
            const response = await fetch(`${this.apiBaseUrl}/chat/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                credentials: 'omit',
                body: JSON.stringify({
                    username: 'demo_user',
                    password: 'demo_password'
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || 'Login failed');
            }

            const data = await response.json();
            this.authToken = data.token;
            this.createNewConversation();
        } catch (error) {
            console.error('Login error:', error);
            
            if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                const corsError = 'Connection error: Unable to reach the server. ';
                console.error(corsError + 'Please ensure you are using a proper HTTP server.');
                
                if (retryCount < this.maxRetries) {
                    this.addMessage(`Attempting to reconnect... (${retryCount + 1}/${this.maxRetries})`, 'system');
                    setTimeout(() => this.login(retryCount + 1), this.retryDelay * (retryCount + 1));
                    return;
                }
            }
            
            this.addMessage('Unable to connect to the chat service. Please ensure you are using a proper HTTP server.', 'system');
        }
    }

    async createNewConversation() {
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

            if (!response.ok) throw new Error('Failed to create conversation');

            const data = await response.json();
            this.currentConversationId = data.id;
            this.addMessage('Hello! How can I assist you today?', 'ai');
        } catch (error) {
            console.error('Conversation creation error:', error);
            this.addMessage('Unable to start a new conversation. Please try refreshing the page.', 'system');
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/conversations/${this.currentConversationId}/send_message/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${this.authToken}`,
                    'Content-Type': 'application/json',
                },
                mode: 'cors',
                credentials: 'omit',
                body: JSON.stringify({ message })
            });

            if (!response.ok) throw new Error('Failed to send message');

            const data = await response.json();
            this.addMessage(data.message, 'ai');
        } catch (error) {
            console.error('Message sending error:', error);
            this.addMessage('Failed to send message. Please try again.', 'system');
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

// Initialize the chat application
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
}); 