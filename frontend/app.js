const API_BASE = "http://127.0.0.1:8000/api";

let currentSessionId = 'stark_industries_2';

const clientListItems = document.querySelectorAll('.nav-item');
const activeClientNameEl = document.getElementById('active-client-name');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const recalledContextList = document.getElementById('recalled-context-list');
const memoryLog = document.getElementById('memory-log');
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.getElementById('connection-status-text');

// Handle sidebar switching
clientListItems.forEach(item => {
    item.addEventListener('click', () => {
        // Update active class
        clientListItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        // Update state
        currentSessionId = item.dataset.session;
        const clientName = item.textContent.trim();
        activeClientNameEl.textContent = clientName;
        
        // Clear chat
        chatMessages.innerHTML = `
            <div class="message system">
                <div class="message-content">Switched deal workspace to ${clientName}. I have cleared the chat view, but my memory persists.</div>
            </div>
        `;
        
        updateContext([], 'HINDSIGHT'); // Default reset to Hindsight status
        refreshMemoryLog();
    });
});

function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    msgDiv.innerHTML = `
        <div class="message-content">${text}</div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateContext(contextArr, source) {
    recalledContextList.innerHTML = '';
    
    updateStatusIndicator(source);

    if (!contextArr || contextArr.length === 0) {
        recalledContextList.innerHTML = '<div class="empty-state">No context recalled yet.</div>';
        return;
    }
    
    contextArr.forEach(c => {
        const div = document.createElement('div');
        div.className = 'context-item';
        
        // Create a fake category label based on length or content
        let category = "Note";
        if (c.toLowerCase().includes("prefer") || c.toLowerCase().includes("like")) category = "Preference";
        if (c.toLowerCase().includes("aws") || c.toLowerCase().includes("azure") || c.toLowerCase().includes("tech")) category = "Infrastructure";
        if (c.toLowerCase().includes("time") || c.toLowerCase().includes("implement")) category = "Timeline Concern";
        
        div.innerHTML = `
            <div class="context-label">${category}</div>
            <div class="context-text">${c}</div>
        `;
        recalledContextList.appendChild(div);
    });
}

function updateStatusIndicator(source) {
    if (source === 'HINDSIGHT') {
        statusIndicator.className = 'status-indicator status-real';
        statusText.textContent = 'Hindsight connected';
    } else {
        statusIndicator.className = 'status-indicator status-mock';
        statusText.textContent = 'Demo memory';
    }
}

async function refreshMemoryLog() {
    try {
        const res = await fetch(`${API_BASE}/memory/${currentSessionId}`);
        if(res.ok) {
            const data = await res.json();
            updateStatusIndicator(data.source);
            
            memoryLog.innerHTML = '';
            if (data.memories.length === 0) {
                memoryLog.innerHTML = '<div class="empty-state">No activity.</div>';
                return;
            }
            
            // Format chronological list
            data.memories.forEach(m => {
                const div = document.createElement('div');
                div.className = 'memory-item';
                
                const now = new Date();
                const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
                
                div.innerHTML = `
                    <div class="memory-time">${timeString}</div>
                    <div class="memory-text">${m}</div>
                `;
                memoryLog.appendChild(div);
            });
        }
    } catch (e) {
        console.error("Failed to refresh memory", e);
    }
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    
    appendMessage('user', text);
    chatInput.value = '';
    
    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId, message: text })
        });
        
        if(res.ok) {
            const data = await res.json();
            updateContext(data.recalled_context, data.source);
            appendMessage('system', data.reply);
            await refreshMemoryLog();
        } else {
            appendMessage('system', "Error: Unable to connect to backend.");
        }
    } catch (e) {
        console.error(e);
        appendMessage('system', "Error: Backend is not running or unreachable.");
    }
});

// Init
refreshMemoryLog();
