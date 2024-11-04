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

        // Add proper credentials
        this.credentials = {
            username: 'patabrava',  // Update with correct username
            password: 'test123'  // Update with correct password
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
                console.log('Attempting login with credentials:', {
                    username: this.credentials.username,
                    password: '********'
                });
            }

            const response = await fetch(`${this.apiBaseUrl}/chat/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                credentials: 'omit',
                body: JSON.stringify(this.credentials)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                if (response.status === 401) {
                    throw new Error('Invalid credentials. Please check username and password.');
                }
                throw new Error(errorData.message || 'Login failed');
            }

            const data = await response.json();
            if (!data.token) {
                throw new Error('No authentication token received');
            }

            this.authToken = data.token;
            if (this.isDevelopment) {
                console.log('Login successful, token received');
            }
            await this.createNewConversation();
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
            
            this.addMessage(`Authentication error: ${error.message}`, 'system');
        }
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