// Conversation page specific functionality for Tatlock
// This file provides conversation page features and navigation

// Functions are now globally available from common.js
// import { showSection, registerSectionLoader } from './common.js';

// Example for chat messages
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
registerSectionLoader('chat-section', loadChatMessages);
registerSectionLoader('history-section', loadChatHistory);
registerSectionLoader('settings-section', loadChatSettings);

// Navigation handler for conversation page
function handleHashNavigation() {
    const hash = window.location.hash.substring(1);
    const sectionIdMap = {
        'chat': 'chat-section',
        'history': 'history-section',
        'settings': 'settings-section'
    };
    const sectionId = sectionIdMap[hash] || 'chat-section';
    showSection(sectionId);
}

document.addEventListener('DOMContentLoaded', function() {
    handleHashNavigation();
    window.addEventListener('hashchange', handleHashNavigation);
});

// Repeat this pattern for any other dynamic content areas specific to the conversation page. 