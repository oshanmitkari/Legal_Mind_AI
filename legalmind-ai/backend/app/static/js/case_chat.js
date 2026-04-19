/**
 * F6: AI Case Assistant - Chat Interface
 * Handles context-aware chat with FAISS RAG and persistence
 */

// Global variables
let chatHistory = [];
let messagesContainer, chatForm, chatInput;

// Load chat history and attach event listeners on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements (updated for new tabbed interface)
    messagesContainer = document.getElementById('chatContainer');
    chatForm = document.getElementById('chatForm');
    chatInput = document.getElementById('chatInput');

    // Load chat history
    if (typeof CASE_ID !== 'undefined') {
        loadChatHistory();
    }

    // Handle form submission
    if (chatForm) {
        chatForm.addEventListener('submit', async function(e) {
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
 * Add message to UI (Modern Tailwind Design)
 */
function addMessageToUI(type, content, sources = null, scrollToBottom = true) {
    const messageDiv = document.createElement('div');

    if (type === 'user') {
        // User Message Bubble
        messageDiv.className = 'flex justify-end';
        messageDiv.innerHTML = `
            <div class="max-w-[75%]">
                <div class="mb-1 flex items-center justify-end gap-2">
                    <span class="text-xs font-medium text-slate-400">You</span>
                    <div class="flex h-7 w-7 items-center justify-center rounded-full bg-slate-700">
                        <svg class="h-4 w-4 text-slate-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                    </div>
                </div>
                <div class="rounded-2xl rounded-tr-sm bg-cyan-500 px-4 py-3 text-sm leading-relaxed text-slate-950 shadow-lg">
                    ${escapeHtml(content)}
                </div>
            </div>
        `;
    } else if (type === 'assistant') {
        // AI Agent Message Bubble
        messageDiv.className = 'flex justify-start';

        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="mt-2 rounded-lg border border-cyan-700/30 bg-cyan-950/20 p-2">
                    <div class="mb-1 flex items-center gap-1 text-xs text-cyan-400">
                        <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                        <span class="font-semibold">Sources (${sources.length}):</span>
                    </div>
                    <div class="flex flex-wrap gap-1">
                        ${sources.map(s => `
                            <span class="rounded bg-cyan-500/20 px-2 py-0.5 text-xs text-cyan-300">
                                ${s.filename}
                            </span>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="max-w-[85%]">
                <div class="mb-1 flex items-center gap-2">
                    <div class="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-cyan-600">
                        <svg class="h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                    </div>
                    <span class="text-xs font-medium text-cyan-400">AI Agent</span>
                </div>
                <div class="rounded-2xl rounded-tl-sm border border-slate-700 bg-slate-800 px-4 py-3 text-sm leading-relaxed text-slate-100 shadow-lg">
                    <div class="message-content">${formatMarkdown(content)}</div>
                    ${sourcesHtml}
                </div>
            </div>
        `;
    } else if (type === 'error') {
        // Error Message
        messageDiv.className = 'flex justify-center';
        messageDiv.innerHTML = `
            <div class="w-full max-w-md rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
                <div class="flex items-center gap-2">
                    <svg class="h-5 w-5 text-rose-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>${escapeHtml(content)}</span>
                </div>
            </div>
        `;
    }

    messagesContainer.appendChild(messageDiv);

    if (scrollToBottom) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

/**
 * Add typing indicator (Modern Tailwind Design)
 */
function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'flex justify-start';
    typingDiv.id = 'typing-' + Date.now();
    typingDiv.innerHTML = `
        <div class="max-w-[85%]">
            <div class="mb-1 flex items-center gap-2">
                <div class="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-cyan-600">
                    <svg class="h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                </div>
                <span class="text-xs font-medium text-cyan-400">AI Agent</span>
            </div>
            <div class="rounded-2xl rounded-tl-sm border border-slate-700 bg-slate-800 px-4 py-3 shadow-lg">
                <div class="flex items-center gap-2">
                    <div class="flex gap-1">
                        <span class="h-2 w-2 animate-bounce rounded-full bg-cyan-400" style="animation-delay: 0ms"></span>
                        <span class="h-2 w-2 animate-bounce rounded-full bg-cyan-400" style="animation-delay: 150ms"></span>
                        <span class="h-2 w-2 animate-bounce rounded-full bg-cyan-400" style="animation-delay: 300ms"></span>
                    </div>
                    <span class="text-xs text-slate-400">AI is thinking...</span>
                </div>
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
