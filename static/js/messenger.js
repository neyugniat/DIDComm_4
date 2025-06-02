const sentMessages = new Set();
let issuerConnectionIds = new Set();
let verifiedConnectionIds = new Set();
const pendingSentMessages = new Set();

async function fetchConnections() {
    try {
        const response = await fetch('/connections/holder');
        if (!response.ok) throw new Error('Failed to fetch connections');
        const data = await response.json();
        const connectionSelect = document.getElementById('connection');
        connectionSelect.innerHTML = '<option value="">Select a connection</option>';
        // Use data.results here if your API response has that structure
        const connections = data.results || data; // fallback if no results key
        connections.forEach(conn => {
            const option = document.createElement('option');
            option.value = conn.connection_id;
            option.textContent = `${conn.their_label || 'Unknown'} (${conn.connection_id})`;
            connectionSelect.appendChild(option);
        });

        // Pre-select connection from URL path
        const pathSegments = window.location.pathname.split('/');
        const preselectedConnectionId = pathSegments[pathSegments.length - 1];
        if (preselectedConnectionId && preselectedConnectionId !== 'messenger') {
            connectionSelect.value = preselectedConnectionId;
            if (connectionSelect.value !== preselectedConnectionId) {
                console.warn(`Connection ID ${preselectedConnectionId} not found in connections list`);
            }
        }

        const issuerResponse = await fetch('/connections/issuer');
        if (!issuerResponse.ok) throw new Error('Failed to fetch ISSUER connections');
        const issuerData = await issuerResponse.json();
        issuerConnectionIds = new Set(issuerData.results ? issuerData.results.map(conn => conn.connection_id) : issuerData.map(conn => conn.connection_id));
        console.log('Fetched ISSUER connection IDs:', Array.from(issuerConnectionIds));

        const verifiedResponse = await fetch('/connections/verifier');
        if (!verifiedResponse.ok) throw new Error('Failed to fetch VERIFIED connections');
        const verifiedData = await verifiedResponse.json();
        verifiedConnectionIds = new Set(verifiedData.results ? verifiedData.results.map(conn => conn.connection_id) : verifiedData.map(conn => conn.connection_id));
        console.log('Fetched VERIFIED connection IDs:', Array.from(verifiedConnectionIds));

    } catch (error) {
        console.error('Error fetching connections:', error);
        alert('Failed to load connections.');
    }
}

function addMessage(content, connection_id, sent_time, isSent = false, message_id) {
    const chat = document.getElementById('chat');
    const messageDiv = document.createElement('div');
    messageDiv.className = `p-3 ${isSent ? 'chat-bubble-sent' : 'chat-bubble-received'} mb-2`;
    messageDiv.setAttribute('data-message-id', message_id);
    messageDiv.innerHTML = `
        <div class="text-sm ${isSent ? 'text-indigo-100' : 'text-gray-600'}">${connection_id}</div>
        <div>${content}</div>
        <div class="text-xs ${isSent ? 'text-indigo-200' : 'text-gray-500'} mt-1">${sent_time}</div>
    `;
    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;
}

const sendButton = document.getElementById('send');
sendButton.addEventListener('click', async () => {
    const connection_id = document.getElementById('connection').value;
    const content = document.getElementById('message').value.trim();
    if (!connection_id || !content) {
        alert('Please select a recipient and enter a message.');
        return;
    }

    const sent_time = new Date().toISOString();
    const messageKey = `${connection_id}-${content}-${sent_time}`;
    pendingSentMessages.add(`${connection_id}-${content}`); // Track pending message
    sentMessages.add(messageKey); // Track for deduplication

    addMessage(content, connection_id, sent_time, true, messageKey); // Show immediately

    try {
        const response = await fetch('/basicmessages/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                agent_type: 'holder',
                connection_id,
                content
            })
        });

        if (response.ok) {
            document.getElementById('message').value = '';
            pendingSentMessages.delete(`${connection_id}-${content}`); // Clear pending status
        } else {
            throw new Error('Failed to send message');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message.');
        sentMessages.delete(messageKey);
        pendingSentMessages.delete(`${connection_id}-${content}`);
        const messageDiv = document.querySelector(`[data-message-id="${messageKey}"]`);
        if (messageDiv) messageDiv.remove();
    }
});

const connectionSelect = document.getElementById('connection');
// Removed the refreshChatbox listener here

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/chat/ws`;
const ws = new WebSocket(wsUrl);

ws.onopen = () => {
    console.log('WebSocket connected');
};

ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);
        const message = JSON.parse(data.message);
        console.log('Received message:', message);

        if (issuerConnectionIds.has(message.connection_id) || verifiedConnectionIds.has(message.connection_id)) {
            return;
        }

        if (!sentMessages.has(message.message_id)) {
            addMessage(
                message.content,
                message.connection_id,
                message.sent_time,
                false,
                message.message_id
            );
            sentMessages.add(message.message_id);

            // If the message's connection_id matches the selected connection, ensure it's displayed
            const selectedConnectionId = document.getElementById('connection').value;
            if (message.connection_id === selectedConnectionId) {
                const messageDiv = document.querySelector(`[data-message-id="${message.message_id}"]`);
                if (!messageDiv) {
                    addMessage(
                        message.content,
                        message.connection_id,
                        message.sent_time,
                        false,
                        message.message_id
                    );
                }
            }
        }
    } catch (error) {
        console.error('Error processing WebSocket message:', error);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('WebSocket closed');
};

fetchConnections();
