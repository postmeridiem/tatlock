// Sidebar chat functionality for Tatlock
// This file provides the TatlockChat class for sidebar chat across different pages

// Functions are now globally available from common.js
// import { showSection, registerSectionLoader } from './common.js';

class TatlockChat {
    constructor(options = {}) {
        // Configuration options
        this.enableLogging = options.enableLogging || false;
        this.logFunction = options.logFunction || null;
        this.debugMode = options.debugMode || false;
        this.sidebarTitle = options.sidebarTitle || 'Assistant';
        this.welcomeMessage = options.welcomeMessage || 'Good day, sir. I am Tatlock, your AI assistant. Pray, what matters require my attention today?';
        this.placeholder = options.placeholder || 'Ask Tatlock...';
        
        // Try different possible element ID patterns
        this.chatInput = document.getElementById('chat-input') || document.getElementById('sidepane-input');
        this.chatSendBtn = document.getElementById('chat-send-btn') || document.getElementById('sidepane-send-btn');
        this.chatMessages = document.getElementById('chat-messages') || document.getElementById('sidepane-messages');
        this.chatMicBtn = document.getElementById('chat-mic-btn') || document.getElementById('sidepane-mic-btn');
        
        // Voice recording state
        this.isRecording = false;
        this.audioChunks = [];
        this.audioContext = null;
        this.mediaRecorder = null;
        this.voiceWebSocket = null;
        this.voiceTimeout = null;
        this.lastAudioTimestamp = null;
        this.transcriptBuffer = '';
        this.keyword = 'tatlock';
        this.pauseDuration = 5000; // 5 seconds
        
        // Configure marked library for markdown parsing
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                sanitize: false,
                highlight: function(code, lang) {
                    return `<pre><code class="language-${lang}">${code}</code></pre>`;
                }
            });
        }
        
        // Debug logging
        if (this.debugMode) {
            console.log('TatlockChat constructor called with options:', options);
            console.log('Chat elements found:', {
                chatInput: !!this.chatInput,
                chatSendBtn: !!this.chatSendBtn,
                chatMessages: !!this.chatMessages,
                chatMicBtn: !!this.chatMicBtn
            });
        }
        
        if (!this.chatInput || !this.chatSendBtn || !this.chatMessages) {
            console.error('Chat elements not found');
            return;
        }
        
        // Initialize the sidebar with custom content
        this.initializeSidebar();
        this.setupEventListeners();
        this.setupVoiceListeners();
        this.chatInput.focus();
        
        if (this.debugMode) {
            console.log('TatlockChat initialization complete');
        }
    }
    
    initializeSidebar() {
        // Update sidebar title if element exists
        const titleElement = document.querySelector('.sidebar-title');
        if (titleElement) {
            titleElement.textContent = this.sidebarTitle;
        }
        
        // Update welcome message if element exists
        const welcomeElement = document.querySelector('.sidebar-welcome-message');
        if (welcomeElement) {
            welcomeElement.textContent = this.welcomeMessage;
        }
        
        // Update placeholder if element exists
        if (this.chatInput) {
            this.chatInput.placeholder = this.placeholder;
        }
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
    
    setupVoiceListeners() {
        if (this.debugMode) {
            console.log('Setting up voice listeners, mic button:', this.chatMicBtn);
        }
        if (!this.chatMicBtn) {
            console.error('Microphone button not found');
            return;
        }
        this.chatMicBtn.addEventListener('click', () => {
            if (this.debugMode) {
                console.log('Microphone button clicked, isRecording:', this.isRecording);
            }
            if (this.isRecording) {
                this.stopVoiceCapture();
            } else {
                this.startVoiceCapture();
            }
        });
        if (this.debugMode) {
            console.log('Voice listeners setup complete');
        }
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
        
        // Add loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chat-message ai loading';
        loadingDiv.innerHTML = '<em>pondering...</em>';
        this.chatMessages.appendChild(loadingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
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
            
            // Remove loading indicator
            this.chatMessages.removeChild(loadingDiv);
            
            // Add AI response to chat
            if (data.response) {
                this.addMessage(data.response, 'ai', data.processing_time);
            } else {
                this.addMessage('Sorry, I encountered an error processing your message.', 'ai');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            
            // Remove loading indicator
            if (loadingDiv.parentNode) {
                this.chatMessages.removeChild(loadingDiv);
            }
            
            // Add error message
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    }
    
    async startVoiceCapture() {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create MediaRecorder
            this.mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            
            // Set up WebSocket connection
            this.voiceWebSocket = new WebSocket(`ws://${window.location.host}/ws/voice`);
            
            this.mediaRecorder.ondataavailable = (e) => {
                this.sendAudioChunk(e.data);
            };
            
            this.mediaRecorder.onstop = () => {
                stream.getTracks().forEach(track => track.stop());
            };
            
            // Start recording
            this.mediaRecorder.start(250); // 250ms chunks
            this.isRecording = true;
            
            // Update UI
            this.chatMicBtn.classList.add('recording');
            this.showListeningFeedback();
            
            // Set up WebSocket event handlers
            this.voiceWebSocket.onmessage = (event) => {
                this.handleVoiceResult(event);
            };
            
            this.voiceWebSocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.stopVoiceCapture();
            };
            
            this.voiceWebSocket.onclose = () => {
                console.log('WebSocket connection closed');
                this.stopVoiceCapture();
            };
            
            // Start timeout for auto-stop
            this.resetVoiceTimeout();
            
        } catch (error) {
            console.error('Error starting voice capture:', error);
            alert('Error accessing microphone. Please check permissions.');
        }
    }
    
    stopVoiceCapture() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
        }
        
        if (this.voiceWebSocket) {
            this.voiceWebSocket.close();
            this.voiceWebSocket = null;
        }
        
        if (this.voiceTimeout) {
            clearTimeout(this.voiceTimeout);
            this.voiceTimeout = null;
        }
        
        // Update UI
        this.chatMicBtn.classList.remove('recording');
        this.removeListeningFeedback();
        
        // Clear transcript buffer
        this.transcriptBuffer = '';
    }
    
    sendAudioChunk(blob) {
        if (this.voiceWebSocket && this.voiceWebSocket.readyState === WebSocket.OPEN) {
            this.voiceWebSocket.send(blob);
            this.resetVoiceTimeout();
        }
    }
    
    resetVoiceTimeout() {
        if (this.voiceTimeout) {
            clearTimeout(this.voiceTimeout);
        }
        this.voiceTimeout = setTimeout(() => {
            this.stopVoiceCapture();
        }, this.pauseDuration);
    }
    
    handleVoiceResult(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'transcript') {
                const transcript = data.text.toLowerCase();
                
                // Check for keyword
                if (transcript.includes(this.keyword)) {
                    // Extract command after keyword
                    const keywordIndex = transcript.indexOf(this.keyword);
                    const command = transcript.substring(keywordIndex + this.keyword.length).trim();
                    
                    if (command) {
                        this.showVoiceCommandFeedback(command);
                        
                        // Set the command as input and send
                        setTimeout(() => {
                            this.chatInput.value = command;
                            this.chatInput.style.height = 'auto';
                            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
                            this.chatSendBtn.disabled = false;
                            this.sendMessage();
                        }, 500);
                        
                        this.stopVoiceCapture();
                    }
                }
            }
        } catch (error) {
            console.error('Error handling voice result:', error);
        }
    }
    
    showVoiceCommandFeedback(command) {
        // Create feedback message
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'chat-message voice-command';
        feedbackDiv.innerHTML = `
            <div class="voice-command-detected">
                <span class="material-icons">mic</span>
                <span>Voice command detected: "${command}"</span>
                <span class="processing-indicator">Processing...</span>
            </div>
        `;
        
        this.chatMessages.appendChild(feedbackDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Remove the feedback after a short delay
        setTimeout(() => {
            if (feedbackDiv.parentNode) {
                feedbackDiv.parentNode.removeChild(feedbackDiv);
            }
        }, 2000);
    }
    
    showListeningFeedback() {
        if (this.debugMode) {
            console.log('showListeningFeedback called, chatMessages:', this.chatMessages);
        }
        // Create listening feedback message
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'chat-message voice-listening';
        feedbackDiv.id = 'voice-listening-feedback';
        feedbackDiv.innerHTML = `
            <div class="voice-listening-indicator">
                <span class="material-icons">mic</span>
                <span>Listening... Say "tatlock" followed by your command</span>
                <div class="listening-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(feedbackDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        if (this.debugMode) {
            console.log('Listening feedback added to DOM');
        }
    }
    
    removeListeningFeedback() {
        const feedbackDiv = document.getElementById('voice-listening-feedback');
        if (feedbackDiv && feedbackDiv.parentNode) {
            feedbackDiv.parentNode.removeChild(feedbackDiv);
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
                // Parse markdown to HTML
                const htmlContent = marked.parse(content);
                messageDiv.innerHTML = htmlContent;
                
                if (this.debugMode) {
                    console.log('Markdown parsed successfully:', {
                        original: content.substring(0, 100) + '...',
                        html: htmlContent.substring(0, 100) + '...'
                    });
                }
            } catch (error) {
                console.error('Markdown parsing error:', error);
                // Fallback to plain text with line breaks
                messageDiv.innerHTML = content.replace(/\n/g, '<br>');
            }
        } else if (sender === 'ai' && typeof marked === 'undefined') {
            // Marked library not available, log warning and use plain text
            console.warn('Marked library not available, using plain text for AI message');
            messageDiv.innerHTML = content.replace(/\n/g, '<br>');
        } else {
            // For user messages, use plain text
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
    // Default options for different pages
    const defaultOptions = {
        enableLogging: false,
        logFunction: null,
        debugMode: false,
        sidebarTitle: 'Assistant',
        welcomeMessage: 'Good day, sir. I am Tatlock, your AI assistant. Pray, what matters require my attention today?',
        placeholder: 'Ask Tatlock...'
    };
    
    // Merge options with defaults
    const config = { ...defaultOptions, ...options };
    
    if (document.readyState === 'loading') {
        // DOM is still loading, wait for it
        document.addEventListener('DOMContentLoaded', function() {
            new TatlockChat(config);
        });
    } else {
        // DOM is already loaded, initialize immediately
        new TatlockChat(config);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // This is a fallback initialization for pages that don't have a specific chat setup.
    // The main initialization is now handled in specific page scripts (e.g., page.admin.js, page.profile.js)
    if (document.getElementById('sidepane-input')) {
        setTimeout(() => { // Delay to ensure sidebar is loaded
            new TatlockChat({
                chatInput: document.getElementById('sidepane-input'),
                chatSendBtn: document.getElementById('sidepane-send-btn'),
                chatMessages: document.getElementById('sidepane-messages'),
                chatMicBtn: document.getElementById('sidepane-mic-btn'),
                placeholder: 'Ask Tatlock...'
            });
        }, 100);
    }
}); 