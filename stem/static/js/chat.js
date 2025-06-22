// Shared chat functionality for Tatlock
// This file provides chat functionality that can be used across different pages

class TatlockChat {
    constructor(options = {}) {
        // Try different possible element ID patterns
        this.chatInput = document.getElementById('chat-input') || document.getElementById('sidepane-input');
        this.chatSendBtn = document.getElementById('chat-send-btn') || document.getElementById('sidepane-send-btn');
        this.chatMessages = document.getElementById('chat-messages') || document.getElementById('sidepane-messages');
        this.enableLogging = options.enableLogging || false;
        this.logFunction = options.logFunction || null;
        
        if (!this.chatInput || !this.chatSendBtn || !this.chatMessages) {
            console.error('Chat elements not found');
            return;
        }
        
        this.setupEventListeners();
        this.chatInput.focus();
    }
    
    setupEventListeners() {
        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
            
            // Enable/disable send button based on content
            this.chatSendBtn.disabled = !this.chatInput.value.trim();
        });
        
        // Send message on Enter (but allow Shift+Enter for new lines)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button click
        this.chatSendBtn.addEventListener('click', () => this.sendMessage());
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Log to interaction log if enabled
        if (this.enableLogging && this.logFunction) {
            this.logFunction('User Message', { message });
        }
        
        // Clear input and disable send button
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';
        this.chatSendBtn.disabled = true;
        
        try {
            // Send message to backend
            const response = await fetch('/cortex', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    message: message,
                    history: [] // Start fresh conversation for each message
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            
            const data = await response.json();
            
            // Log AI response to interaction log if enabled
            if (this.enableLogging && this.logFunction) {
                this.logFunction('AI Response', { 
                    response: data.response, 
                    processing_time: data.processing_time,
                    topic: data.topic,
                    conversation_id: data.conversation_id
                });
            }
            
            // Add AI response to chat
            if (data.response) {
                this.addMessage(data.response, 'ai', data.processing_time);
            } else {
                this.addMessage('Sorry, I encountered an error processing your message.', 'ai');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            
            // Log error to interaction log if enabled
            if (this.enableLogging && this.logFunction) {
                this.logFunction('Chat Error', { error: error.message });
            }
            
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    }
    
    addMessage(content, sender, processingTime = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        // Create copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '<span class="material-icons">content_copy</span>';
        copyBtn.title = 'Copy message';
        
        // Add click handler for copy functionality
        copyBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
                await navigator.clipboard.writeText(content);
                copyBtn.innerHTML = '<span class="material-icons">check</span>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<span class="material-icons">content_copy</span>';
                }, 1000);
            } catch (err) {
                console.error('Failed to copy message:', err);
                const textArea = document.createElement('textarea');
                textArea.value = content;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                copyBtn.innerHTML = '<span class="material-icons">check</span>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<span class="material-icons">content_copy</span>';
                }, 1000);
            }
        });
        
        // Parse markdown for AI messages, keep plain text for user messages
        if (sender === 'ai' && typeof marked !== 'undefined') {
            try {
                // Configure marked options for security and styling
                marked.setOptions({
                    breaks: true,
                    gfm: true,
                    sanitize: false,
                    highlight: function(code, lang) {
                        return `<pre><code class="language-${lang}">${code}</code></pre>`;
                    }
                });
                
                // Parse markdown to HTML
                const htmlContent = marked.parse(content);
                messageDiv.innerHTML = htmlContent;
            } catch (error) {
                console.error('Markdown parsing error:', error);
                messageDiv.innerHTML = content.replace(/\n/g, '<br>');
            }
        } else {
            // For user messages or if marked is not available, use plain text
            messageDiv.innerHTML = content.replace(/\n/g, '<br>');
        }
        
        messageDiv.appendChild(copyBtn);
        
        // Add processing time for AI messages
        if (sender === 'ai' && processingTime !== null) {
            const timeDiv = document.createElement('div');
            timeDiv.className = 'processing-time';
            timeDiv.textContent = `${processingTime.toFixed(1)}s`;
            messageDiv.appendChild(timeDiv);
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize chat when DOM is loaded
function initializeChat(options = {}) {
    document.addEventListener('DOMContentLoaded', function() {
        new TatlockChat(options);
    });
} 