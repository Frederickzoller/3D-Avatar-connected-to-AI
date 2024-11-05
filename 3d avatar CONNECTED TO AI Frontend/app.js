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
        this.apiBaseUrl = 'https://threed-avatar-connected-to-ai-1.onrender.com';

        this.init();
    }

    init() {
        this.loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
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
            }
        } catch (error) {
            this.loginError.textContent = error.message || 'Login failed';
        }
    }

    async login(username, password) {
        const loginUrl = `${this.apiBaseUrl}/chat/login/`;
        
        try {
            const response = await fetch(loginUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ username, password }),
                mode: 'cors',
                credentials: 'include'
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
            throw new Error('Unable to connect to server. Please try again.');
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        try {
            if (!this.currentConversationId) {
                await this.createNewConversation();
            }

            const response = await fetch(`${this.apiBaseUrl}/chat/conversations/${this.currentConversationId}/send_message/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${this.authToken}`
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const data = await response.json();
            this.addMessage(message, 'user');
            this.addMessage(data.message, 'assistant');
            this.messageInput.value = '';

        } catch (error) {
            this.addMessage('Error sending message', 'system');
        }
    }

    async createNewConversation() {
        const response = await fetch(`${this.apiBaseUrl}/chat/conversations/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${this.authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to create conversation');
        }

        const data = await response.json();
        this.currentConversationId = data.id;
    }

    addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.textContent = content;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => new ChatApp()); 