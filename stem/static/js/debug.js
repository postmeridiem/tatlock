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

// --- System Info Section ---
let cpuChart = null;
let ramChart = null;
let systemInfoHistory = [];
const MAX_HISTORY = 60; // Keep 60 samples (5 min if polling every 5s)

async function fetchSystemInfo() {
    const response = await fetch('/parietal/system-info', { credentials: 'include' });
    if (!response.ok) throw new Error('Failed to fetch system info');
    return await response.json();
}

function renderSystemInfoTiles(info) {
    const cpu = info.cpu;
    const ram = info.memory.ram;
    const disk = info.disk.root_partition;
    const uptime = info.uptime;
    const net = info.network;
    
    // Format uptime without seconds for display
    const uptimeDisplay = uptime.days > 0 ? 
        `${uptime.days}d ${uptime.hours}h ${uptime.minutes}m` :
        uptime.hours > 0 ? 
            `${uptime.hours}h ${uptime.minutes}m` :
            `${uptime.minutes}m`;
    
    return `
        <div class="metrics-tiles">
            <div class="tile metric-tile">
                <div class="tile-title">CPU Usage</div>
                <div class="tile-value">${cpu.usage.overall_percent}%</div>
                <div class="tile-desc">Cores: ${cpu.count.logical}</div>
            </div>
            <div class="tile metric-tile">
                <div class="tile-title">RAM Usage</div>
                <div class="tile-value">${ram.usage_percent}%</div>
                <div class="tile-desc">${ram.used_gb}GB / ${ram.total_gb}GB</div>
            </div>
            <div class="tile metric-tile">
                <div class="tile-title">Disk Usage</div>
                <div class="tile-value">${disk.usage_percent}%</div>
                <div class="tile-desc">${disk.used_gb}GB / ${disk.total_gb}GB</div>
            </div>
            <div class="tile metric-tile">
                <div class="tile-title">Uptime</div>
                <div class="tile-value">${uptimeDisplay}</div>
                <div class="tile-desc">Processes: ${info.processes.total}</div>
            </div>
            <div class="tile metric-tile">
                <div class="tile-title">Network</div>
                <div class="tile-value">${net.bytes_sent_gb}GB sent</div>
                <div class="tile-desc">${net.bytes_recv_gb}GB recv</div>
            </div>
        </div>
    `;
}

function renderSystemInfoGraphs(info) {
    // Prepare history
    if (systemInfoHistory.length >= MAX_HISTORY) systemInfoHistory.shift();
    systemInfoHistory.push({
        time: new Date(),
        cpu: info.cpu.usage.overall_percent,
        ram: info.memory.ram.usage_percent
    });
    // Prepare data
    const labels = systemInfoHistory.map(x => x.time.toLocaleTimeString());
    const cpuData = systemInfoHistory.map(x => x.cpu);
    const ramData = systemInfoHistory.map(x => x.ram);
    // CPU Chart
    if (!cpuChart) {
        const ctx = document.getElementById('cpu-usage-chart').getContext('2d');
        cpuChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'CPU Usage (%)',
                    data: cpuData,
                    borderColor: '#42a5f5',
                    backgroundColor: 'rgba(66,165,245,0.1)',
                    fill: true,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { min: 0, max: 100 } }
            }
        });
    } else {
        cpuChart.data.labels = labels;
        cpuChart.data.datasets[0].data = cpuData;
        cpuChart.update();
    }
    // RAM Chart
    if (!ramChart) {
        const ctx = document.getElementById('ram-usage-chart').getContext('2d');
        ramChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'RAM Usage (%)',
                    data: ramData,
                    borderColor: '#66bb6a',
                    backgroundColor: 'rgba(102,187,106,0.1)',
                    fill: true,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { min: 0, max: 100 } }
            }
        });
    } else {
        ramChart.data.labels = labels;
        ramChart.data.datasets[0].data = ramData;
        ramChart.update();
    }
}

async function updateSystemInfoSection() {
    const systemInfoContent = document.getElementById('system-info-content');
    try {
        const info = await fetchSystemInfo();
        // Tiles
        let html = renderSystemInfoTiles(info);
        // Graphs
        html += `
            <div class="metrics-graphs">
                <canvas id="cpu-usage-chart" height="80"></canvas>
                <canvas id="ram-usage-chart" height="80"></canvas>
            </div>
        `;
        // Raw system info card (always open)
        html += `
            <div class="system-info-card">
                <h3>Raw System Information</h3>
                <pre class="json-content">${highlightJSON(JSON.stringify(info, null, 2))}</pre>
            </div>
        `;
        systemInfoContent.innerHTML = html;
        renderSystemInfoGraphs(info);
    } catch (error) {
        systemInfoContent.innerHTML = `<div class="error">Error loading system information: ${error.message}</div>`;
    }
}

// Poll every 10 seconds
setInterval(updateSystemInfoSection, 10000);

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
    updateSystemInfoSection();
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