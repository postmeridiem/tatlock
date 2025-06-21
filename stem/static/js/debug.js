// Debug console specific functionality

// Debug console functionality
const jsonContainer = document.getElementById('json-container');
const clearLogBtn = document.getElementById('clear-log-btn');
const exportLogBtn = document.getElementById('export-log-btn');
const autoScrollToggle = document.getElementById('auto-scroll');

// Log entries storage
let logEntries = [];

function addLogEntry(content, type = 'info', data = null) {
    // Only log chat-related entries
    if (type === 'tool-call' || type === 'tool-response' || type === 'error') {
        const entry = {
            timestamp: new Date(),
            type: type,
            content: content,
            data: data
        };
        
        logEntries.push(entry);
        
        const div = document.createElement('div');
        div.className = `json-entry ${type}`;
        
        const timestamp = document.createElement('div');
        timestamp.className = 'json-timestamp';
        timestamp.textContent = entry.timestamp.toLocaleTimeString();
        div.appendChild(timestamp);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'json-content';
        if (data) {
            const jsonString = JSON.stringify(data, null, 2);
            contentDiv.innerHTML = highlightJSON(jsonString);
            contentDiv.classList.add('highlighted');
        } else {
            contentDiv.textContent = content;
        }
        div.appendChild(contentDiv);
        
        // Insert at the beginning to show latest entries at the top
        if (jsonContainer.firstChild) {
            jsonContainer.insertBefore(div, jsonContainer.firstChild);
        } else {
            jsonContainer.appendChild(div);
        }
        
        // Auto-scroll if enabled
        if (autoScrollToggle.checked) {
            jsonContainer.scrollTop = 0;
        }
    }
}

function clearLog() {
    jsonContainer.innerHTML = '';
    logEntries = [];
}

function exportLog() {
    const logData = {
        exportTime: new Date().toISOString(),
        entries: logEntries
    };
    
    const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tatlock-debug-log-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// System info functionality
async function loadSystemInfo() {
    const systemInfoContent = document.getElementById('system-info-content');
    
    try {
        // Get basic system info
        const systemInfo = {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            timestamp: new Date().toISOString()
        };
        
        // Try to get server info
        try {
            const response = await fetch('/admin/stats', {
                credentials: 'include'  // Include session cookies
            });
            if (response.ok) {
                const stats = await response.json();
                systemInfo.serverStats = stats;
            }
        } catch (e) {
            systemInfo.serverStatsError = e.message;
        }
        
        // Display system info
        systemInfoContent.innerHTML = `
            <div class="info-grid">
                <div class="info-item">
                    <h4>Browser Information</h4>
                    <pre class="json-content">${highlightJSON(JSON.stringify(systemInfo, null, 2))}</pre>
                </div>
            </div>
        `;
        
    } catch (error) {
        systemInfoContent.innerHTML = `
            <div class="error">
                Error loading system information: ${error.message}
            </div>
        `;
    }
}

// Sidepane chat functionality
const sidepaneInput = document.getElementById('sidepane-input');
const sidepaneSendBtn = document.getElementById('sidepane-send-btn');
const sidepaneMessages = document.getElementById('sidepane-messages');

// Sidepane chat input handling
sidepaneInput.addEventListener('input', () => {
    sidepaneSendBtn.disabled = !sidepaneInput.value.trim();
    // Auto-resize textarea
    sidepaneInput.style.height = 'auto';
    sidepaneInput.style.height = Math.min(sidepaneInput.scrollHeight, 100) + 'px';
});

sidepaneInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendSidepaneMessage();
    }
});

sidepaneSendBtn.addEventListener('click', sendSidepaneMessage);

// Sidepane chat conversation history
let sidepaneHistory = [];
let sidepaneConversationId = null;

function sendSidepaneMessage() {
    const message = sidepaneInput.value.trim();
    if (!message) return;
    
    // Add user message to sidepane chat
    addSidepaneMessage(message, 'user');
    
    // Add to conversation history
    sidepaneHistory.push({ role: 'user', content: message });
    
    // Log the outgoing message to debug console
    addLogEntry('Sidepane chat message sent', 'tool-call', {
        message: message,
        history: sidepaneHistory
    });
    
    // Clear input
    sidepaneInput.value = '';
    sidepaneInput.style.height = 'auto';
    sidepaneSendBtn.disabled = true;
    
    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message ai';
    typingDiv.innerHTML = '<em>Typing...</em>';
    sidepaneMessages.appendChild(typingDiv);
    sidepaneMessages.scrollTop = sidepaneMessages.scrollHeight;
    
    // Prepare request data
    const requestData = { 
        message: message, 
        history: sidepaneHistory,
        conversation_id: sidepaneConversationId
    };
    
    // Send to Tatlock
    fetch('/cortex', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',  // Include session cookies
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        sidepaneMessages.removeChild(typingDiv);
        
        // Add AI response
        const aiResponse = data.response || 'I apologize, but I encountered an error processing your request.';
        addSidepaneMessage(aiResponse, 'ai');
        
        // Add to conversation history
        sidepaneHistory.push({ role: 'assistant', content: aiResponse });
        
        // Update conversation ID from response
        if (data.conversation_id) {
            sidepaneConversationId = data.conversation_id;
        }
        
        // Log the response to debug console
        addLogEntry('Sidepane chat response received', 'tool-response', {
            response: aiResponse,
            fullResponse: data,
            history: sidepaneHistory
        });
        
        // Keep history manageable (last 20 messages)
        if (sidepaneHistory.length > 20) {
            sidepaneHistory = sidepaneHistory.slice(-20);
        }
    })
    .catch(error => {
        // Remove typing indicator
        sidepaneMessages.removeChild(typingDiv);
        
        // Add error message
        addSidepaneMessage('Sorry, I encountered an error. Please try again.', 'ai');
        
        // Log the error to debug console
        addLogEntry('Sidepane chat error', 'error', {
            error: error.message,
            message: message,
            stack: error.stack
        });
        
        console.error('Sidepane chat error:', error);
    });
}

function addSidepaneMessage(content, sender) {
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
            // Show feedback (you could add a toast notification here)
            copyBtn.innerHTML = '<span class="material-icons">check</span>';
            setTimeout(() => {
                copyBtn.innerHTML = '<span class="material-icons">content_copy</span>';
            }, 1000);
        } catch (err) {
            console.error('Failed to copy message:', err);
            // Fallback for older browsers
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
    
    // Convert \n to <br> tags and use innerHTML to preserve line breaks
    messageDiv.innerHTML = content.replace(/\n/g, '<br>');
    messageDiv.appendChild(copyBtn);
    sidepaneMessages.appendChild(messageDiv);
    sidepaneMessages.scrollTop = sidepaneMessages.scrollHeight;
}

// Event listeners for debug controls
clearLogBtn.addEventListener('click', clearLog);
exportLogBtn.addEventListener('click', exportLog);

// Initialize debug console
document.addEventListener('DOMContentLoaded', function() {
    setupDebugEventListeners();
    loadSystemInfo();
    checkAuthenticationStatus();
});

function checkAuthenticationStatus() {
    // Try to fetch a protected endpoint to check authentication
    fetch('/login/test', {
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else if (response.status === 401) {
            // Redirect to login page
            window.location.href = '/login';
            return null;
        } else {
            return null;
        }
    })
    .then(data => {
        // Authentication check completed silently
    })
    .catch(error => {
        // Authentication check failed silently
    });
}

function setupDebugEventListeners() {
    // Clear log button
    const clearLogBtn = document.getElementById('clear-log-btn');
    if (clearLogBtn) {
        clearLogBtn.addEventListener('click', clearLog);
    }
    
    // Export log button
    const exportLogBtn = document.getElementById('export-log-btn');
    if (exportLogBtn) {
        exportLogBtn.addEventListener('click', exportLog);
    }
} 