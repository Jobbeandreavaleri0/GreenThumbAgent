const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
let sessionId = null; // Will be set on first message

function addMessage(content, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    
    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = sender === 'user' ? '👤' : '🌱';
    
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.textContent = content;
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatContainer.appendChild(msgDiv);
    
    // Smooth scroll to bottom
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
}

function showTyping() {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'assistant', 'typing');
    msgDiv.id = 'typing-indicator';
    
    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = '🌱';
    
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.innerHTML = `
        <div class="typing-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
}

function removeTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;
    
    // Add user message
    addMessage(text, 'user');
    userInput.value = '';
    
    // Show typing indicator
    showTyping();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        removeTyping();
        
        if (data.error) {
            addMessage("Oops! Something went wrong: " + data.error, 'assistant');
        } else {
            sessionId = data.session_id; // Save session ID to keep conversation
            addMessage(data.response, 'assistant');
        }
    } catch (error) {
        removeTyping();
        addMessage("Failed to connect to the server.", 'assistant');
    }
}

sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});
