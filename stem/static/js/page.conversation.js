// Conversation page specific functionality for Tatlock
// This file provides conversation page features, debug console, and navigation

// Functions are now globally available from common.js
// import { showSection, registerSectionLoader } from './common.js';

// --- Debug Console Functionality ---
const jsonContainer = document.getElementById('json-container');
const clearLogBtn = document.getElementById('clear-log-btn');
const exportLogBtn = document.getElementById('export-log-btn');
const autoScrollToggle = document.getElementById('auto-scroll');

let logEntries = [];

function addToInteractionLog(type, data) {
    let message = '';
    let logType = 'info';
    switch (type) {
        case 'User Message':
            message = `User sent message: "${data.message}"`;
            logType = 'user';
            addLogEntry(message, logType, data);
            break;
        case 'AI Response':
            message = `AI responded (${data.processing_time}s): "${data.response.substring(0, 100)}${data.response.length > 100 ? '...' : ''}"`;
            logType = 'ai';
            const aiData = {
                response: data.response,
                processing_time: data.processing_time,
                topic: data.topic,
                conversation_id: data.conversation_id,
                history: data.history || []
            };
            addLogEntry(message, logType, aiData);
            break;
        case 'Chat Error':
            message = `Chat error: ${data.error}`;
            logType = 'error';
            addLogEntry(message, logType, data);
            break;
        case 'Voice Command':
            message = `Voice command detected: "${data.extracted_command}" (original: "${data.original_text}")`;
            logType = 'user';
            addLogEntry(message, logType, data);
            break;
        default:
            message = `${type}: ${JSON.stringify(data)}`;
            logType = 'info';
            addLogEntry(message, logType, data);
    }
}

function addLogEntry(content, type = 'info', data = null) {
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
    if (data && typeof highlightJSON === 'function') {
        const jsonString = JSON.stringify(data, null, 2);
        contentDiv.innerHTML = highlightJSON(jsonString);
        contentDiv.classList.add('highlighted');
    } else {
        contentDiv.textContent = content;
    }
    div.appendChild(contentDiv);
    if (jsonContainer && jsonContainer.firstChild) {
        jsonContainer.insertBefore(div, jsonContainer.firstChild);
    } else if (jsonContainer) {
        jsonContainer.appendChild(div);
    }
    if (autoScrollToggle && autoScrollToggle.checked && jsonContainer) {
        jsonContainer.scrollTop = 0;
    }
}

function clearLog() {
    if (jsonContainer) jsonContainer.innerHTML = '';
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

if (clearLogBtn) clearLogBtn.addEventListener('click', clearLog);
if (exportLogBtn) exportLogBtn.addEventListener('click', exportLog);

// --- System Info Section ---
let cpuChart = null;
let ramChart = null;
let systemInfoHistory = [];
const MAX_HISTORY = 60;

async function fetchSystemInfo() {
    const response = await fetch('/parietal/system-info', { credentials: 'include' });
    if (!response.ok) throw new Error('Failed to fetch system info');
    return await response.json();
}

function updateSystemInfoDOM(info) {
    const updateText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    };
    const cpu = info.cpu;
    updateText('cpu-usage-percent', `${cpu.usage.overall_percent}%`);
    updateText('cpu-core-count', cpu.count.logical);
    const ram = info.memory.ram;
    updateText('ram-usage-percent', `${ram.usage_percent}%`);
    updateText('ram-used', ram.used_gb);
    updateText('ram-total', ram.total_gb);
    const disk = info.disk.root_partition;
    updateText('disk-usage-percent', `${disk.usage_percent}%`);
    updateText('disk-used', disk.used_gb);
    updateText('disk-total', disk.total_gb);
    const uptime = info.uptime;
    const uptimeDisplay = uptime.days > 0 ? 
        `${uptime.days}d ${uptime.hours}h ${uptime.minutes}m` :
        uptime.hours > 0 ? 
            `${uptime.hours}h ${uptime.minutes}m` :
            `${uptime.minutes}m`;
    updateText('system-uptime', uptimeDisplay);
    updateText('process-count', info.processes.total);
    const net = info.network;
    updateText('network-sent', `${net.bytes_sent_gb}GB sent`);
    updateText('network-recv', `${net.bytes_recv_gb}GB recv`);
    const rawInfoEl = document.getElementById('system-info-raw');
    if (rawInfoEl && typeof highlightJSON === 'function') {
        rawInfoEl.innerHTML = highlightJSON(JSON.stringify(info, null, 2));
    }
}

function renderSystemInfoGraphs(info) {
    // Maintain history buffer
    if (!Array.isArray(systemInfoHistory)) systemInfoHistory = [];
    if (systemInfoHistory.length >= MAX_HISTORY) systemInfoHistory.shift();
    systemInfoHistory.push({
        cpu: info.cpu.usage.overall_percent,
        ram: info.memory.ram.usage_percent
    });
    // Prepare data
    const cpuData = systemInfoHistory.map(d => d.cpu);
    const ramData = systemInfoHistory.map(d => d.ram);
    const labels = Array.from({length: systemInfoHistory.length}, (_, i) => `${i - systemInfoHistory.length + 1 + MAX_HISTORY}s`);
    // CPU Chart
    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    if (cpuChart) cpuChart.destroy();
    cpuChart = new Chart(cpuCtx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'CPU %',
                data: cpuData,
                borderColor: '#90caf9',
                backgroundColor: 'rgba(144,202,249,0.1)',
                fill: true,
                tension: 0.2,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, ticks: { color: '#b0bec5' } },
                x: { display: false }
            }
        }
    });
    // RAM Chart
    const ramCtx = document.getElementById('ramChart').getContext('2d');
    if (ramChart) ramChart.destroy();
    ramChart = new Chart(ramCtx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'RAM %',
                data: ramData,
                borderColor: '#a97ffb',
                backgroundColor: 'rgba(169,127,251,0.1)',
                fill: true,
                tension: 0.2,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, ticks: { color: '#b0bec5' } },
                x: { display: false }
            }
        }
    });
}

// --- Section Loaders and Navigation ---
function loadChatMessages() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    chatMessages.innerHTML = '<li class="loading">Loading messages...</li>';
    // ... fetch and populate chat messages ...
}

function loadChatHistory() {
    const historyContainer = document.getElementById('history-container');
    if (!historyContainer) return;
    historyContainer.innerHTML = '<div class="loading">Loading chat history...</div>';
    // ... fetch and populate chat history ...
}

function loadChatSettings() {
    const settingsContainer = document.getElementById('settings-container');
    if (!settingsContainer) return;
    settingsContainer.innerHTML = '<div class="loading">Loading chat settings...</div>';
    // ... fetch and populate chat settings ...
}

// Register section loaders for conversation page
registerSectionLoader('conversation', loadChatMessages);
registerSectionLoader('system-info', loadSystemInfo);
registerSectionLoader('benchmarks', loadBenchmarks);

// Initialize hash navigation for conversation page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize hash navigation with 'conversation' as default section
    initializeHashNavigation('conversation');
    
    // Set up hash change listener for navigation
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash.substring(1);
        const validSections = ['conversation', 'system-info', 'benchmarks'];
        if (validSections.includes(hash)) {
            showSection(hash);
        }
    });
});

// Section loader functions
function loadSystemInfo() {
    const systemInfoContent = document.getElementById('system-info-content');
    if (!systemInfoContent) return;
    
    systemInfoContent.innerHTML = `
        <div class="loading">Loading system information...</div>
    `;
    
    fetchSystemInfo()
        .then(info => {
            // Group first four tiles, then network tile below
            systemInfoContent.innerHTML = `
                <div class="metrics-tiles" style="margin-bottom:0;">
                    <div class="metric-tile">
                        <div class="tile-title">CPU Usage</div>
                        <div class="tile-value" id="cpu-usage-percent">${info.cpu.usage.overall_percent}%</div>
                        <div class="tile-desc">Cores: <span id="cpu-core-count">${info.cpu.count.logical}</span></div>
                    </div>
                    <div class="metric-tile">
                        <div class="tile-title">RAM Usage</div>
                        <div class="tile-value" id="ram-usage-percent">${info.memory.ram.usage_percent}%</div>
                        <div class="tile-desc">Used: <span id="ram-used">${info.memory.ram.used_gb}GB</span> / <span id="ram-total">${info.memory.ram.total_gb}GB</span></div>
                    </div>
                    <div class="metric-tile">
                        <div class="tile-title">Disk Usage</div>
                        <div class="tile-value" id="disk-usage-percent">${info.disk.root_partition.usage_percent}%</div>
                        <div class="tile-desc">Used: <span id="disk-used">${info.disk.root_partition.used_gb}GB</span> / <span id="disk-total">${info.disk.root_partition.total_gb}GB</span></div>
                    </div>
                    <div class="metric-tile">
                        <div class="tile-title">Uptime</div>
                        <div class="tile-value" id="system-uptime">${formatUptime(info.uptime)}</div>
                        <div class="tile-desc">Processes: <span id="process-count">${info.processes.total}</span></div>
                    </div>
                </div>
                <div class="metrics-tiles">
                    <div class="metric-tile network-metric-tile" style="min-width:100%;max-width:100%;display:flex;flex-direction:column;align-items:stretch;">
                        <div class="tile-title">Network</div>
                        <div class="network-row" style="display:flex;justify-content:space-evenly;align-items:center;width:100%;margin:12px 0;">
                            <div class="network-col" style="flex:1;text-align:center;">
                                <span style='color:#90caf9;font-weight:bold;'><span class="material-icons" style="vertical-align:middle;font-size:1.1em;">arrow_upward</span> <span id="network-sent">${info.network.bytes_sent_gb}GB</span></span>
                                <div style="font-size:0.95em; color:#b0bec5;">sent</div>
                            </div>
                            <div class="network-col" style="flex:1;text-align:center;">
                                <span style='color:#90caf9;font-weight:bold;'><span class="material-icons" style="vertical-align:middle;font-size:1.1em;">arrow_downward</span> <span id="network-recv">${info.network.bytes_recv_gb}GB</span></span>
                                <div style="font-size:0.95em; color:#b0bec5;">recv</div>
                            </div>
                        </div>
                        <div class="tile-desc">Interfaces: ${info.network.interfaces.length}</div>
                    </div>
                </div>
                <div class="metrics-graphs">
                    <div class="chart-container">
                        <canvas id="cpuChart"></canvas>
                        <div class="chart-label">CPU Usage (last 60s)</div>
                    </div>
                    <div class="chart-container">
                        <canvas id="ramChart"></canvas>
                        <div class="chart-label">RAM Usage (last 60s)</div>
                    </div>
                </div>
                <div class="system-info-card">
                    <h3>Raw System Data</h3>
                    <pre id="system-info-raw" style="font-family:monospace;font-size:13px;line-height:1.5;background:var(--bg-tertiary);padding:12px;border-radius:4px;overflow-x:auto;"></pre>
                </div>
            `;
            // Render charts (ensure Chart.js is loaded)
            if (window.Chart) {
                renderSystemInfoGraphs(info);
            } else if (window['plugin_chart_min_js_loaded'] !== true) {
                // Dynamically load plugin.chart.min.js if not already loaded
                const script = document.createElement('script');
                script.src = '/static/js/plugin.chart.min.js';
                script.onload = function() {
                    window['plugin_chart_min_js_loaded'] = true;
                    renderSystemInfoGraphs(info);
                };
                document.body.appendChild(script);
            }
            // Update the raw data display
            const rawInfoEl = document.getElementById('system-info-raw');
            if (rawInfoEl) {
                if (typeof highlightJSON === 'function') {
                    rawInfoEl.innerHTML = highlightJSON(JSON.stringify(info, null, 2));
                } else {
                    rawInfoEl.textContent = JSON.stringify(info, null, 2);
                }
            }
        })
        .catch(error => {
            systemInfoContent.innerHTML = `
                <div class="error">Failed to load system information: ${error.message}</div>
            `;
        });
}

function loadBenchmarks() {
    const benchmarksContent = document.getElementById('benchmarks-content');
    if (!benchmarksContent) return;
    
    benchmarksContent.innerHTML = `
        <div class="benchmark-controls">
            <h3>Performance Benchmarks</h3>
            <div class="button-group">
                <button onclick="runBenchmark('comprehensive')" class="button">Run Comprehensive</button>
                <button onclick="runBenchmark('llm')" class="button">Run LLM Test</button>
                <button onclick="runBenchmark('tools')" class="button">Run Tools Test</button>
            </div>
        </div>
        <div class="benchmark-results" id="benchmark-results">
            <div class="info">Click a benchmark button to run tests...</div>
        </div>
    `;
}

function formatUptime(uptime) {
    if (uptime.days > 0) {
        return `${uptime.days}d ${uptime.hours}h ${uptime.minutes}m`;
    } else if (uptime.hours > 0) {
        return `${uptime.hours}h ${uptime.minutes}m`;
    } else {
        return `${uptime.minutes}m`;
    }
}

// Navigation handler for conversation page
function handleHashNavigation() {
    const hash = window.location.hash.substring(1);
    const validSections = ['conversation', 'system-info', 'benchmarks'];
    const sectionId = validSections.includes(hash) ? hash : 'conversation';
    showSection(sectionId);
}

// --- Benchmark Functionality ---
async function runBenchmark(type) {
    const benchmarkContent = document.getElementById('benchmark-results');
    if (!benchmarkContent) {
        console.error('Benchmark results container not found');
        return;
    }
    
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
    const benchmarkContent = document.getElementById('benchmark-results');
    if (!benchmarkContent) {
        console.error('Benchmark results container not found');
        return;
    }
    
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
        html += `<p><strong>Average Tool Call Time:</strong> ${data.summary.average_time}s</p>`;
        html += `<p><strong>Performance Grade:</strong> <span class="grade-${data.analysis?.performance_grade?.toLowerCase()}">${data.analysis?.performance_grade || 'Unknown'}</span></p>`;
        html += `</div>`;
    }
    if (data.tests) {
        html += `<div class="benchmark-tests">`;
        html += `<h5>Tool Test Results:</h5>`;
        html += `<table class="benchmark-table">`;
        html += `<tr><th>Tool</th><th>Time</th><th>Status</th><th>Details</th></tr>`;
        Object.entries(data.tests).forEach(([toolName, toolData]) => {
            const statusClass = toolData.status === 'success' ? 'success' : 'error';
            html += `<tr>`;
            html += `<td>${toolName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>`;
            html += `<td>${toolData.time_seconds}s</td>`;
            html += `<td class="${statusClass}">${toolData.status}</td>`;
            html += `<td>`;
            if (toolData.response_length) {
                html += `${toolData.response_length} chars`;
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

// --- Event Listeners for Debug Controls and Benchmarks ---
function setupDebugEventListeners() {
    // Log controls
    const clearLogBtn = document.getElementById('clear-log-btn');
    if (clearLogBtn) clearLogBtn.addEventListener('click', clearLog);
    const exportLogBtn = document.getElementById('export-log-btn');
    if (exportLogBtn) exportLogBtn.addEventListener('click', exportLog);
    // Benchmark buttons
    const comprehensiveBtn = document.getElementById('run-comprehensive-benchmark');
    if (comprehensiveBtn) comprehensiveBtn.addEventListener('click', () => runBenchmark('comprehensive'));
    const llmBtn = document.getElementById('run-llm-benchmark');
    if (llmBtn) llmBtn.addEventListener('click', () => runBenchmark('llm'));
    const toolsBtn = document.getElementById('run-tools-benchmark');
    if (toolsBtn) toolsBtn.addEventListener('click', () => runBenchmark('tools'));
}

document.addEventListener('DOMContentLoaded', function() {
    handleHashNavigation();
    window.addEventListener('hashchange', handleHashNavigation);
    // --- System Info Initialization ---
    async function refreshSystemInfo() {
        try {
            const info = await fetchSystemInfo();
            updateSystemInfoDOM(info);
            // Optionally: renderSystemInfoGraphs(info);
        } catch (error) {
            console.error('Error fetching system info:', error);
        }
    }
    refreshSystemInfo(); // Initial fetch
    setInterval(refreshSystemInfo, 10000); // Refresh every 10 seconds
    // --- Debug and Benchmark Controls Initialization ---
    setupDebugEventListeners();
});



// Repeat this pattern for any other dynamic content areas specific to the conversation page. 