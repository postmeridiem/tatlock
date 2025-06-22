// Debug console specific functionality

// Debug console functionality
const jsonContainer = document.getElementById('json-container');
const clearLogBtn = document.getElementById('clear-log-btn');
const exportLogBtn = document.getElementById('export-log-btn');
const autoScrollToggle = document.getElementById('auto-scroll');

// Log entries storage
let logEntries = [];

// Add chat interactions to the debug log - define this before DOMContentLoaded
function addToInteractionLog(type, data) {
    let message = '';
    let logType = 'info';
    
    switch (type) {
        case 'User Message':
            message = `User sent message: "${data.message}"`;
            logType = 'user';
            break;
        case 'AI Response':
            message = `AI responded (${data.processing_time}s): "${data.response.substring(0, 100)}${data.response.length > 100 ? '...' : ''}"`;
            logType = 'ai';
            break;
        case 'Chat Error':
            message = `Chat error: ${data.error}`;
            logType = 'error';
            break;
        default:
            message = `${type}: ${JSON.stringify(data)}`;
            logType = 'info';
    }
    
    addLogEntry(message, logType, data);
}

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
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
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
    try {
        const cpuCanvas = document.getElementById('cpu-usage-chart');
        if (!cpuCanvas) {
            console.error('CPU chart canvas not found');
            return;
        }
        
        if (!cpuChart) {
            const ctx = cpuCanvas.getContext('2d');
            if (!ctx) {
                console.error('Could not get 2D context for CPU chart');
                return;
            }
            
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
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        title: {
                            display: true,
                            text: 'CPU Usage Over Time',
                            color: 'var(--text-primary)',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    scales: { 
                        y: { 
                            min: 0, 
                            max: 100,
                            title: {
                                display: true,
                                text: 'Usage (%)',
                                color: 'var(--text-secondary)'
                            }
                        },
                        x: { 
                            display: true,
                            title: {
                                display: true,
                                text: 'Time',
                                color: 'var(--text-secondary)'
                            }
                        }
                    }
                }
            });
            console.log('CPU chart initialized successfully');
        } else {
            cpuChart.data.labels = labels;
            cpuChart.data.datasets[0].data = cpuData;
            cpuChart.update();
        }
    } catch (error) {
        console.error('Error initializing CPU chart:', error);
    }
    
    // RAM Chart
    try {
        const ramCanvas = document.getElementById('ram-usage-chart');
        if (!ramCanvas) {
            console.error('RAM chart canvas not found');
            return;
        }
        
        if (!ramChart) {
            const ctx = ramCanvas.getContext('2d');
            if (!ctx) {
                console.error('Could not get 2D context for RAM chart');
                return;
            }
            
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
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        title: {
                            display: true,
                            text: 'RAM Usage Over Time',
                            color: 'var(--text-primary)',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    scales: { 
                        y: { 
                            min: 0, 
                            max: 100,
                            title: {
                                display: true,
                                text: 'Usage (%)',
                                color: 'var(--text-secondary)'
                            }
                        },
                        x: { 
                            display: true,
                            title: {
                                display: true,
                                text: 'Time',
                                color: 'var(--text-secondary)'
                            }
                        }
                    }
                }
            });
            console.log('RAM chart initialized successfully');
        } else {
            ramChart.data.labels = labels;
            ramChart.data.datasets[0].data = ramData;
            ramChart.update();
        }
    } catch (error) {
        console.error('Error initializing RAM chart:', error);
    }
}

async function updateSystemInfoSection() {
    const systemInfoContent = document.getElementById('system-info-content');
    try {
        const info = await fetchSystemInfo();
        
        // Check if this is the first load (no existing content)
        const isFirstLoad = !systemInfoContent.querySelector('.metrics-graphs');
        
        if (isFirstLoad) {
            // First load - create all HTML content
            let html = renderSystemInfoTiles(info);
            // Graphs
            html += `
                <div class="metrics-graphs">
                    <div class="chart-container">
                        <canvas id="cpu-usage-chart" height="80"></canvas>
                        <div class="chart-label">CPU Usage Over Time</div>
                    </div>
                    <div class="chart-container">
                        <canvas id="ram-usage-chart" height="80"></canvas>
                        <div class="chart-label">RAM Usage Over Time</div>
                    </div>
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
            // Small delay to ensure canvas elements are created
            setTimeout(() => {
                renderSystemInfoGraphs(info);
            }, 100);
        } else {
            // Subsequent updates - only update tiles and raw data, preserve charts
            const tilesHtml = renderSystemInfoTiles(info);
            const tilesContainer = systemInfoContent.querySelector('.metrics-tiles');
            if (tilesContainer) {
                tilesContainer.outerHTML = tilesHtml;
            }
            
            // Update raw system info
            const rawInfoContainer = systemInfoContent.querySelector('.system-info-card pre');
            if (rawInfoContainer) {
                rawInfoContainer.innerHTML = highlightJSON(JSON.stringify(info, null, 2));
            }
            
            // Update chart data without recreating charts
            updateChartData(info);
        }
    } catch (error) {
        systemInfoContent.innerHTML = `<div class="error">Error loading system information: ${error.message}</div>`;
    }
}

function updateChartData(info) {
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
    
    // Update existing charts
    if (cpuChart) {
        cpuChart.data.labels = labels;
        cpuChart.data.datasets[0].data = cpuData;
        cpuChart.update('none'); // Update without animation for better performance
    }
    
    if (ramChart) {
        ramChart.data.labels = labels;
        ramChart.data.datasets[0].data = ramData;
        ramChart.update('none'); // Update without animation for better performance
    }
}

// Poll every 10 seconds
setInterval(updateSystemInfoSection, 10000);

// Chat functionality - now handled by shared chat.js
// The chat functionality has been moved to stem/static/js/chat.js
// and is initialized in the DOMContentLoaded event with logging enabled

// Event listeners for debug controls
clearLogBtn.addEventListener('click', clearLog);
exportLogBtn.addEventListener('click', exportLog);

// Initialize debug console
document.addEventListener('DOMContentLoaded', function() {
    setupDebugEventListeners();
    loadServerLog();
    initializeSystemInfo();
    initializeBenchmarks();
    
    // Initialize chat with logging enabled for debug page
    // Add a small delay to ensure all scripts are loaded
    setTimeout(() => {
        initializeChat({
            enableLogging: true,
            logFunction: addToInteractionLog
        });
    }, 100);
});

// Load initial server log entries
async function loadServerLog() {
    // Initialize the log container
    const jsonContainer = document.getElementById('json-container');
    if (jsonContainer) {
        // Clear any existing content
        jsonContainer.innerHTML = '';
        
        // Add a welcome message to indicate the log is ready
        addLogEntry('Debug console initialized. Server interactions will be logged here.', 'info');
    }
}

// Initialize system info section and start polling
function initializeSystemInfo() {
    // Load initial system info
    updateSystemInfoSection();
    
    // Start polling for system info updates every 10 seconds
    setInterval(updateSystemInfoSection, 10000);
}

// Initialize benchmark section
function initializeBenchmarks() {
    // The benchmark functionality is already set up in setupDebugEventListeners()
    // This function can be used for any additional benchmark initialization if needed
    console.log('Benchmark section initialized');
}

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
    
    // Benchmark buttons
    const comprehensiveBenchmarkBtn = document.getElementById('run-comprehensive-benchmark');
    if (comprehensiveBenchmarkBtn) {
        comprehensiveBenchmarkBtn.addEventListener('click', () => runBenchmark('comprehensive'));
    }
    
    const llmBenchmarkBtn = document.getElementById('run-llm-benchmark');
    if (llmBenchmarkBtn) {
        llmBenchmarkBtn.addEventListener('click', () => runBenchmark('llm'));
    }
    
    const toolsBenchmarkBtn = document.getElementById('run-tools-benchmark');
    if (toolsBenchmarkBtn) {
        toolsBenchmarkBtn.addEventListener('click', () => runBenchmark('tools'));
    }
}

// --- Benchmark Functionality ---
async function runBenchmark(type) {
    const benchmarkContent = document.getElementById('benchmark-content');
    const buttons = document.querySelectorAll('.benchmark-controls button');
    
    // Disable buttons and show loading
    buttons.forEach(btn => btn.disabled = true);
    benchmarkContent.innerHTML = '<div class="loading">Running benchmark tests...</div>';
    
    try {
        let endpoint;
        switch (type) {
            case 'comprehensive':
                endpoint = '/parietal/benchmark';
                break;
            case 'llm':
                endpoint = '/parietal/benchmark/llm';
                break;
            case 'tools':
                endpoint = '/parietal/benchmark/tools';
                break;
            default:
                throw new Error('Invalid benchmark type');
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        displayBenchmarkResults(data, type);
        
    } catch (error) {
        benchmarkContent.innerHTML = `
            <div class="error">
                <h3>Benchmark Failed</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        // Re-enable buttons
        buttons.forEach(btn => btn.disabled = false);
    }
}

function displayBenchmarkResults(data, type) {
    const benchmarkContent = document.getElementById('benchmark-content');
    
    if (data.error) {
        benchmarkContent.innerHTML = `
            <div class="error">
                <h3>Benchmark Error</h3>
                <p>${data.error}</p>
            </div>
        `;
        return;
    }
    
    let html = `<div class="benchmark-results">`;
    
    // Add timestamp
    if (data.timestamp) {
        html += `<div class="benchmark-timestamp">Run at: ${new Date(data.timestamp).toLocaleString()}</div>`;
    }
    
    if (type === 'comprehensive') {
        html += renderComprehensiveBenchmark(data);
    } else if (type === 'llm') {
        html += renderLLMBenchmark(data);
    } else if (type === 'tools') {
        html += renderToolsBenchmark(data);
    }
    
    html += `</div>`;
    benchmarkContent.innerHTML = html;
}

function renderComprehensiveBenchmark(data) {
    let html = `
        <div class="benchmark-overview">
            <h3>Overall Performance Grade: <span class="grade-${data.overall_analysis?.performance_grade?.toLowerCase()}">${data.overall_analysis?.performance_grade || 'Unknown'}</span></h3>
            <p>Total Benchmark Time: ${data.overall_analysis?.total_benchmark_time || 0}s</p>
        </div>
    `;
    
    // LLM Results
    if (data.llm_benchmark) {
        html += `<div class="benchmark-section">`;
        html += `<h4>LLM Performance</h4>`;
        html += renderLLMBenchmark(data.llm_benchmark);
        html += `</div>`;
    }
    
    // Tools Results
    if (data.tool_benchmark) {
        html += `<div class="benchmark-section">`;
        html += `<h4>Tools Performance</h4>`;
        html += renderToolsBenchmark(data.tool_benchmark);
        html += `</div>`;
    }
    
    // Overall Analysis
    if (data.overall_analysis) {
        html += `<div class="benchmark-section">`;
        html += `<h4>Analysis & Recommendations</h4>`;
        
        if (data.overall_analysis.bottlenecks?.length > 0) {
            html += `<div class="benchmark-bottlenecks">`;
            html += `<h5>Identified Bottlenecks:</h5>`;
            html += `<ul>`;
            data.overall_analysis.bottlenecks.forEach(bottleneck => {
                html += `<li>${bottleneck}</li>`;
            });
            html += `</ul>`;
            html += `</div>`;
        }
        
        if (data.overall_analysis.recommendations?.length > 0) {
            html += `<div class="benchmark-recommendations">`;
            html += `<h5>Recommendations:</h5>`;
            html += `<ul>`;
            data.overall_analysis.recommendations.forEach(rec => {
                html += `<li>${rec}</li>`;
            });
            html += `</ul>`;
            html += `</div>`;
        }
        
        html += `</div>`;
    }
    
    return html;
}

function renderLLMBenchmark(data) {
    let html = '';
    
    if (data.model) {
        html += `<p><strong>Model:</strong> ${data.model}</p>`;
    }
    
    if (data.summary) {
        html += `<div class="benchmark-summary">`;
        html += `<p><strong>Average Response Time:</strong> ${data.summary.average_time}s</p>`;
        html += `<p><strong>Performance Grade:</strong> <span class="grade-${data.analysis?.performance_grade?.toLowerCase()}">${data.analysis?.performance_grade || 'Unknown'}</span></p>`;
        html += `</div>`;
    }
    
    if (data.tests) {
        html += `<div class="benchmark-tests">`;
        html += `<h5>Test Results:</h5>`;
        html += `<table class="benchmark-table">`;
        html += `<tr><th>Test</th><th>Time</th><th>Status</th><th>Details</th></tr>`;
        
        Object.entries(data.tests).forEach(([testName, testData]) => {
            const statusClass = testData.status === 'success' ? 'success' : 'error';
            html += `<tr>`;
            html += `<td>${testName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>`;
            html += `<td>${testData.time_seconds}s</td>`;
            html += `<td class="${statusClass}">${testData.status}</td>`;
            html += `<td>`;
            if (testData.response_length) {
                html += `${testData.response_length} chars`;
            }
            if (testData.has_tool_calls !== undefined) {
                html += testData.has_tool_calls ? ' (with tool calls)' : ' (no tool calls)';
            }
            if (testData.error) {
                html += `<br><small class="error">${testData.error}</small>`;
            }
            html += `</td>`;
            html += `</tr>`;
        });
        
        html += `</table>`;
        html += `</div>`;
    }
    
    if (data.analysis?.recommendations?.length > 0) {
        html += `<div class="benchmark-recommendations">`;
        html += `<h5>Recommendations:</h5>`;
        html += `<ul>`;
        data.analysis.recommendations.forEach(rec => {
            html += `<li>${rec}</li>`;
        });
        html += `</ul>`;
        html += `</div>`;
    }
    
    return html;
}

function renderToolsBenchmark(data) {
    let html = '';
    
    if (data.summary) {
        html += `<div class="benchmark-summary">`;
        html += `<p><strong>Average Tool Time:</strong> ${data.summary.average_time}s</p>`;
        html += `<p><strong>Performance Grade:</strong> <span class="grade-${data.analysis?.performance_grade?.toLowerCase()}">${data.analysis?.performance_grade || 'Unknown'}</span></p>`;
        html += `</div>`;
    }
    
    if (data.tools) {
        html += `<div class="benchmark-tools">`;
        html += `<h5>Tool Results:</h5>`;
        html += `<table class="benchmark-table">`;
        html += `<tr><th>Tool</th><th>Time</th><th>Status</th><th>Details</th></tr>`;
        
        Object.entries(data.tools).forEach(([toolName, toolData]) => {
            const statusClass = toolData.status === 'success' ? 'success' : 'error';
            html += `<tr>`;
            html += `<td>${toolName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>`;
            html += `<td>${toolData.time_seconds}s</td>`;
            html += `<td class="${statusClass}">${toolData.status}</td>`;
            html += `<td>`;
            if (toolData.result_size) {
                html += `${toolData.result_size} chars`;
            }
            if (toolData.error) {
                html += `<br><small class="error">${toolData.error}</small>`;
            }
            html += `</td>`;
            html += `</tr>`;
        });
        
        html += `</table>`;
        html += `</div>`;
    }
    
    if (data.analysis?.recommendations?.length > 0) {
        html += `<div class="benchmark-recommendations">`;
        html += `<h5>Recommendations:</h5>`;
        html += `<ul>`;
        data.analysis.recommendations.forEach(rec => {
            html += `<li>${rec}</li>`;
        });
        html += `</ul>`;
        html += `</div>`;
    }
    
    return html;
} 