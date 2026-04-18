/**
 * F6: AI Case Assistant - Chat Interface
 * Handles context-aware chat with FAISS RAG and persistence
 */

// Global variables
let chatHistory = [];
const messagesContainer = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');

// Load chat history on page load
document.addEventListener('DOMContentLoaded', function() {
    loadChatHistory();
});

// Handle form submission
chatForm?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to UI
    addMessageToUI('user', message);
    chatInput.value = '';
    chatInput.disabled = true;
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`/ai/chat/${CASE_ID}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (response.ok) {
            // Add assistant message
            addMessageToUI('assistant', data.response, data.sources);
        } else {
            addMessageToUI('error', data.error || 'An error occurred');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessageToUI('error', 'Failed to send message: ' + error.message);
    } finally {
        chatInput.disabled = false;
        chatInput.focus();
    }
});

/**
 * Load chat history from server (F6: Persistence)
 */
async function loadChatHistory() {
    try {
        const response = await fetch(`/ai/chat/${CASE_ID}/history`);
        const data = await response.json();
        
        if (response.ok && data.messages.length > 0) {
            messagesContainer.innerHTML = '';
            data.messages.forEach(msg => {
                addMessageToUI(msg.message_type, msg.content, null, false);
            });
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

/**
 * Add message to UI
 */
function addMessageToUI(type, content, sources = null, scrollToBottom = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message mb-4 ${type === 'user' ? 'text-end' : ''}`;
    
    if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="d-inline-block bg-primary text-white rounded-3 px-4 py-2 max-w-75">
                <small class="d-block text-white-50 mb-1">You</small>
                <div>${escapeHtml(content)}</div>
            </div>
        `;
    } else if (type === 'assistant') {
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="mt-3 pt-3 border-top border-secondary">
                    <small class="text-muted d-block mb-2">
                        <i class="bi bi-paperclip"></i> Sources (${sources.length}):
                    </small>
                    ${sources.map(s => `
                        <span class="badge bg-info me-2 mb-1">
                            ${s.filename} (${s.document_type})
                        </span>
                    `).join('')}
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="d-inline-block bg-dark text-white rounded-3 px-4 py-3 max-w-75 border border-secondary">
                <small class="d-block text-white-50 mb-2">
                    <i class="bi bi-robot"></i> AI Assistant
                </small>
                <div class="message-content">${formatMarkdown(content)}</div>
                ${sourcesHtml}
            </div>
        `;
    } else if (type === 'error') {
        messageDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle"></i> ${escapeHtml(content)}
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    
    if (scrollToBottom) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

/**
 * Add typing indicator
 */
function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator mb-4';
    typingDiv.id = 'typing-' + Date.now();
    typingDiv.innerHTML = `
        <div class="d-inline-block bg-dark text-white rounded-3 px-4 py-3 border border-secondary">
            <small class="text-white-50 d-block mb-2">
                <i class="bi bi-robot"></i> AI Assistant
            </small>
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return typingDiv.id;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator(id) {
    const typing = document.getElementById(id);
    if (typing) typing.remove();
}

/**
 * Format markdown-style text
 */
function formatMarkdown(text) {
    // Simple markdown formatting
    let formatted = escapeHtml(text);
    
    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Headers
    formatted = formatted.replace(/^## (.*?)$/gm, '<h5 class="mt-3 mb-2">$1</h5>');
    formatted = formatted.replace(/^# (.*?)$/gm, '<h4 class="mt-3 mb-2">$1</h4>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// CSS for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-dots {
        display: inline-flex;
        gap: 4px;
    }
    .typing-dots .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #6c757d;
        animation: typing 1.4s infinite;
    }
    .typing-dots .dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-dots .dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes typing {
        0%, 60%, 100% {
            opacity: 0.3;
            transform: translateY(0);
        }
        30% {
            opacity: 1;
            transform: translateY(-10px);
        }
    }
    .max-w-75 {
        max-width: 75%;
    }
`;
document.head.appendChild(style);
