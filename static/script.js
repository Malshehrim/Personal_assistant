document.addEventListener('DOMContentLoaded', () => {
    // Task Management
    const addTaskBtn = document.getElementById('add-task-btn');
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', addNewTask);
    }

    // AI Widget Toggle
    const aiToggleBtn = document.getElementById('ai-toggle-btn');
    const aiChatWindow = document.getElementById('ai-chat-window');
    const aiCloseBtn = document.getElementById('ai-close-btn');

    if (aiToggleBtn) {
        aiToggleBtn.addEventListener('click', () => {
            aiChatWindow.classList.toggle('hidden');
        });
    }

    if (aiCloseBtn) {
        aiCloseBtn.addEventListener('click', () => {
            aiChatWindow.classList.add('hidden');
        });
    }

    // AI Chat
    const aiSendBtn = document.getElementById('ai-send-btn');
    const aiInput = document.getElementById('ai-input');
    const aiMessages = document.getElementById('ai-messages');

    if (aiSendBtn) {
        aiSendBtn.addEventListener('click', sendMessage);
        aiInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    function addNewTask() {
        const titleInput = document.getElementById('new-task-title');
        const dateInput = document.getElementById('new-task-date');

        const title = titleInput.value.trim();
        const date = dateInput.value;

        if (!title || !date) {
            alert('Please fill in both the task and the due date.');
            return;
        }

        fetch('/api/add_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                due_date: date
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload(); // Simple reload to refresh lists
                }
            });
    }

    function sendMessage() {
        const message = aiInput.value.trim();
        if (!message) return;

        // User Message
        appendMessage(message, 'user-message');
        aiInput.value = '';

        // AI Loading State (optional)
        const loadingId = 'loading-' + Date.now();
        appendMessage('...', 'ai-message', loadingId);

        fetch('/api/ai_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                const loadingEl = document.getElementById(loadingId);
                if (loadingEl) loadingEl.remove();
                appendMessage(data.response, 'ai-message');
            })
            .catch(err => {
                const loadingEl = document.getElementById(loadingId);
                if (loadingEl) loadingEl.remove();
                appendMessage('Error processing request.', 'ai-message');
            });
    }

    function appendMessage(text, className, id = null) {
        const div = document.createElement('div');
        div.className = `message ${className}`;
        div.textContent = text;
        if (id) div.id = id;
        aiMessages.appendChild(div);
        aiMessages.scrollTop = aiMessages.scrollHeight;
    }
});

// Global function needs to be on window for onclick attribute
window.toggleTask = function (taskId) {
    fetch('/api/toggle_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: taskId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
};
