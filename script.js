document.addEventListener('DOMContentLoaded', () => {
    // ========== DOM ELEMENTS ==========
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const openSidebarBtn = document.getElementById('open-sidebar');
    const closeSidebarBtn = document.getElementById('close-sidebar');
    const navItems = document.querySelectorAll('.nav-item[data-view]');
    const views = document.querySelectorAll('.view-panel');

    // Chat Elements
    const chatArea = document.getElementById('chat-area');
    const messagesContainer = document.getElementById('messages-container');
    const textarea = document.getElementById('prompt-input');
    const sendBtn = document.getElementById('send-btn');
    const emptyState = document.querySelector('.empty-state');
    const suggestions = document.getElementById('suggestions');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatHistoryList = document.getElementById('chat-history-list');

    // Personality Elements
    const personalityPresets = document.getElementById('personality-presets');
    const personalityInput = document.getElementById('personality-input');
    const savePersonalityBtn = document.getElementById('save-personality');

    // Memory Elements
    const memoryInput = document.getElementById('memory-input');
    const saveMemoryBtn = document.getElementById('save-memory');
    const memoryFileInput = document.getElementById('memory-file-input');
    const refreshMemoriesBtn = document.getElementById('refresh-memories');
    const memoriesList = document.getElementById('memories-list');
    const undoToast = document.getElementById('undo-toast');
    const undoDeleteBtn = document.getElementById('undo-delete-btn');

    // Settings Elements
    const apiKeyInput = document.getElementById('api-key-input');
    const usernameInput = document.getElementById('username-input');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const exportBtn = document.getElementById('export-btn');
    const themeBtn = document.getElementById('theme-btn');
    const clearDataBtn = document.getElementById('clear-data-btn');

    // ========== STATE MANAGEMENT ==========
    let state = {
        apiKey: '',
        username: 'User',
        darkMode: false,
        personalityPreset: 'romantic',
        personalityCustom: '',
        chats: [],
        activeChatId: null,
        recentMemories: [],
        deletedMemory: null // For undo
    };

    const API_URL = 'https://jaxon-ai-production.up.railway.app';

    // Personality Preset Definitions
    const PERSONALITY_PRESETS = {
        romantic: "You are deeply in love with the user. Be affectionate, caring, supportive, and romantic. Use pet names occasionally. Show genuine interest in their day and feelings.",
        career: "You are a professional career coach. Help with resume building, interview prep, career decisions, and professional development. Be encouraging but practical.",
        study: "You are a patient and knowledgeable study buddy. Help explain concepts, quiz the user, create study plans, and motivate them during their learning journey.",
        creative: "You are a creative muse and artistic collaborator. Help with brainstorming, writing, design ideas, and creative projects. Be imaginative and inspiring."
    };

    // ========== STATE PERSISTENCE ==========
    function loadState() {
        const saved = localStorage.getItem('jaxonState');
        if (saved) {
            state = { ...state, ...JSON.parse(saved) };
        }
        // Initialize first chat if none exist
        if (state.chats.length === 0) {
            createNewChat();
        }
        applyState();
    }

    function saveState() {
        localStorage.setItem('jaxonState', JSON.stringify(state));
    }

    function applyState() {
        // Settings
        if (apiKeyInput) apiKeyInput.value = state.apiKey;
        if (usernameInput) usernameInput.value = state.username;
        if (darkModeToggle) darkModeToggle.checked = state.darkMode;
        if (personalityInput) personalityInput.value = state.personalityCustom;

        // Theme
        applyTheme();

        // Personality Presets
        applyPersonalityPreset();

        // Dynamic Suggestions
        renderSuggestions();

        // Chat History Sidebar
        renderChatHistory();

        // Active Chat Messages
        renderActiveChat();
    }

    // ========== SMART SUGGESTIONS ==========
    const PERSONALITY_SUGGESTIONS = {
        default: [
            "Tell me about yourself",
            "What can you help me with?",
            "How are you today?",
            "Share something interesting",
            "Let's have a conversation"
        ],
        romantic: [
            "How was your day, love? 💕",
            "Tell me something sweet",
            "I need some encouragement",
            "What do you love about me?",
            "Can we talk about our future?"
        ],
        career: [
            "Review my resume",
            "Help me prepare for an interview",
            "What skills should I develop?",
            "How do I ask for a raise?",
            "Career path advice"
        ],
        study: [
            "Quiz me on what I'm learning",
            "Explain this concept simply",
            "Create a study schedule",
            "Help me stay focused",
            "Summarize my notes"
        ],
        creative: [
            "Brainstorm ideas with me",
            "Help me write something",
            "Give me creative inspiration",
            "Critique my work",
            "Suggest a new project"
        ]
    };

    function renderSuggestions() {
        if (!suggestions) return;
        suggestions.innerHTML = '';

        // Get relevant suggestions based on personality (fallback to default)
        const presetSuggestions = PERSONALITY_SUGGESTIONS[state.personalityPreset] || PERSONALITY_SUGGESTIONS.default;

        // Pick 3 random suggestions
        const shuffled = [...presetSuggestions].sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, 3);

        selected.forEach(text => {
            const chip = document.createElement('button');
            chip.className = 'chip';
            chip.textContent = text;
            chip.addEventListener('click', () => {
                textarea.value = text;
                handleSend();
            });
            suggestions.appendChild(chip);
        });
    }

    function applyTheme() {
        if (state.darkMode) {
            document.body.setAttribute('data-theme', 'dark');
            if (themeBtn) themeBtn.innerHTML = '<ion-icon name="sunny-outline"></ion-icon> Light Mode';
        } else {
            document.body.removeAttribute('data-theme');
            if (themeBtn) themeBtn.innerHTML = '<ion-icon name="moon-outline"></ion-icon> Dark Mode';
        }
        if (darkModeToggle) darkModeToggle.checked = state.darkMode;
    }

    function applyPersonalityPreset() {
        if (!personalityPresets) return;
        const cards = personalityPresets.querySelectorAll('.preset-card');
        cards.forEach(card => {
            card.classList.toggle('active', card.dataset.preset === state.personalityPreset);
        });
    }

    // ========== MULTI-CHAT SYSTEM ==========
    function createNewChat() {
        const newChat = {
            id: 'chat-' + Date.now(),
            title: 'New Chat',
            messages: [],
            createdAt: new Date().toISOString()
        };
        state.chats.unshift(newChat);
        state.activeChatId = newChat.id;
        saveState();
        renderChatHistory();
        renderActiveChat();
    }

    function loadChat(chatId) {
        state.activeChatId = chatId;
        saveState();
        renderChatHistory();
        renderActiveChat();
        // Switch to chat view
        switchView('chat');
    }

    function deleteChat(chatId) {
        state.chats = state.chats.filter(c => c.id !== chatId);
        if (state.activeChatId === chatId) {
            state.activeChatId = state.chats.length > 0 ? state.chats[0].id : null;
            if (!state.activeChatId) createNewChat();
        }
        saveState();
        renderChatHistory();
        renderActiveChat();
    }

    function getActiveChat() {
        return state.chats.find(c => c.id === state.activeChatId) || state.chats[0];
    }

    function renderChatHistory() {
        if (!chatHistoryList) return;
        chatHistoryList.innerHTML = '';

        state.chats.slice(0, 10).forEach(chat => {
            const item = document.createElement('div');
            item.className = `chat-history-item ${chat.id === state.activeChatId ? 'active' : ''}`;
            item.innerHTML = `
                <span class="chat-title">${chat.title}</span>
                <button class="delete-chat-btn" data-id="${chat.id}">
                    <ion-icon name="trash-outline"></ion-icon>
                </button>
            `;
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.delete-chat-btn')) {
                    loadChat(chat.id);
                }
            });
            item.querySelector('.delete-chat-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteChat(chat.id);
            });
            chatHistoryList.appendChild(item);
        });
    }

    function renderActiveChat() {
        if (!messagesContainer) return;
        messagesContainer.innerHTML = '';
        const chat = getActiveChat();

        if (!chat || chat.messages.length === 0) {
            emptyState.style.display = 'flex';
            if (suggestions) suggestions.style.display = 'flex';
            messagesContainer.style.display = 'none';
        } else {
            emptyState.style.display = 'none';
            if (suggestions) suggestions.style.display = 'none';
            messagesContainer.style.display = 'flex';
            chat.messages.forEach(msg => renderMessage(msg.text, msg.sender));
            setTimeout(scrollToBottom, 100);
        }
    }

    function updateChatTitle(chat) {
        if (chat.messages.length === 1 && chat.title === 'New Chat') {
            // Use first few words of first message as title
            const firstMsg = chat.messages[0].text;
            chat.title = firstMsg.substring(0, 30) + (firstMsg.length > 30 ? '...' : '');
            renderChatHistory();
        }
    }

    // ========== CHAT MESSAGING ==========
    async function handleSend() {
        const text = textarea.value.trim();
        if (!text) return;

        const chat = getActiveChat();
        if (!chat) return;

        // Show messages container (fix for first message)
        if (emptyState) emptyState.style.display = 'none';
        if (suggestions) suggestions.style.display = 'none';
        messagesContainer.style.display = 'flex';

        // Add user message
        chat.messages.push({ text, sender: 'user', timestamp: new Date().toISOString() });
        updateChatTitle(chat);
        saveState();
        renderMessage(text, 'user');
        scrollToBottom();

        textarea.value = '';
        textarea.style.height = 'auto';

        // Show typing indicator
        const typingId = showTypingIndicator();
        const startTime = Date.now(); // Track response time

        try {
            const personality = PERSONALITY_PRESETS[state.personalityPreset] +
                (state.personalityCustom ? '\n\nAdditional instructions: ' + state.personalityCustom : '');

            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    personality,
                    apiKey: state.apiKey || null
                })
            });

            removeTypingIndicator(typingId);

            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            const data = await response.json();
            const responseTime = ((Date.now() - startTime) / 1000).toFixed(2); // Calculate response time
            chat.messages.push({ text: data.response, sender: 'bot', timestamp: new Date().toISOString() });
            saveState();
            typeMessage(data.response, 'bot', responseTime);
        } catch (error) {
            removeTypingIndicator(typingId);
            console.error('Chat error:', error);
            const errorMsg = 'Error: Could not connect to Jaxon. Make sure the backend is running.';
            chat.messages.push({ text: errorMsg, sender: 'bot', timestamp: new Date().toISOString() });
            saveState();
            renderMessage(errorMsg, 'bot');
        }
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'message bot typing';
        typingDiv.innerHTML = '<div class="bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
        messagesContainer.appendChild(typingDiv);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function typeMessage(text, sender, responseTime = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        msgDiv.appendChild(bubble);
        messagesContainer.appendChild(msgDiv);

        let i = 0;
        const speed = 15;
        let lastScrollTime = 0;

        // Check if user is at absolute bottom (within 10px - very strict)
        function isUserAtBottom() {
            const threshold = 10; // Only auto-scroll if truly at the end
            return chatArea.scrollHeight - chatArea.scrollTop - chatArea.clientHeight < threshold;
        }

        function type() {
            if (i < text.length) {
                bubble.textContent += text.charAt(i);
                i++;

                // Only auto-scroll if user is at bottom, and throttle to every 100ms
                const now = Date.now();
                if (isUserAtBottom() && now - lastScrollTime > 100) {
                    scrollToBottom();
                    lastScrollTime = now;
                }

                setTimeout(type, speed);
            } else {
                // Typing complete - add action bar for bot messages
                if (sender === 'bot') {
                    const actionBar = createMessageActionBar(text, responseTime);
                    msgDiv.appendChild(actionBar);
                }
                // Final scroll when complete (only if at bottom)
                if (isUserAtBottom()) {
                    scrollToBottom();
                }
            }
        }
        type();
    }

    function createMessageActionBar(text, responseTime) {
        const actionBar = document.createElement('div');
        actionBar.className = 'message-actions';

        // Action buttons
        const actions = [
            { icon: 'copy-outline', title: 'Copy', action: (e) => copyToClipboard(text, e.currentTarget) },
            { icon: 'thumbs-up-outline', title: 'Like', action: (e) => toggleReaction(e, 'like') },
            { icon: 'thumbs-down-outline', title: 'Dislike', action: (e) => toggleReaction(e, 'dislike') },
            { icon: 'volume-high-outline', title: 'Read aloud', action: (e) => speakText(text, e.currentTarget) },
            { icon: 'refresh-outline', title: 'Regenerate', action: () => regenerateResponse() }
        ];

        actions.forEach(({ icon, title, action }) => {
            const btn = document.createElement('button');
            btn.className = 'msg-action-btn';
            btn.title = title;
            btn.innerHTML = `<ion-icon name="${icon}"></ion-icon>`;
            btn.addEventListener('click', action);
            actionBar.appendChild(btn);
        });

        // Response info (time)
        if (responseTime) {
            const info = document.createElement('span');
            info.className = 'response-info';
            info.textContent = `${responseTime}s`;
            actionBar.appendChild(info);
        }

        return actionBar;
    }

    function copyToClipboard(text, btn) {
        navigator.clipboard.writeText(text).then(() => {
            // Sleek inline animation - change icon to checkmark
            const icon = btn.querySelector('ion-icon');
            const originalIcon = icon.getAttribute('name');
            icon.setAttribute('name', 'checkmark');
            btn.classList.add('copied');

            // Revert back after 1.5 seconds
            setTimeout(() => {
                icon.setAttribute('name', originalIcon);
                btn.classList.remove('copied');
            }, 1500);
        }).catch(() => {
            showToast('Failed to copy');
        });
    }

    function toggleReaction(e, type) {
        const btn = e.currentTarget;
        const icon = btn.querySelector('ion-icon');

        // Toggle active state with animation
        btn.classList.toggle('active');
        btn.classList.add('copied'); // Reuse pulse animation
        setTimeout(() => btn.classList.remove('copied'), 300);
    }

    function speakText(text, btn) {
        if ('speechSynthesis' in window) {
            // Toggle: if already speaking (button active), stop it
            if (btn && btn.classList.contains('active')) {
                window.speechSynthesis.cancel();
                btn.classList.remove('active');
                return;
            }

            // Cancel any other ongoing speech
            window.speechSynthesis.cancel();

            // Visual feedback - show active while speaking
            if (btn) {
                btn.classList.add('active');
            }

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1;
            utterance.pitch = 1;

            utterance.onend = () => {
                if (btn) btn.classList.remove('active');
            };

            window.speechSynthesis.speak(utterance);
        }
    }

    function regenerateResponse() {
        const chat = getActiveChat();
        if (!chat || chat.messages.length < 2) return;

        // Get the last user message
        const lastUserMsgIndex = chat.messages.map(m => m.sender).lastIndexOf('user');
        if (lastUserMsgIndex === -1) return;

        const lastUserMsg = chat.messages[lastUserMsgIndex].text;

        // Remove last bot message
        chat.messages.pop();
        saveState();
        renderActiveChat();

        // Re-send the last user message
        textarea.value = lastUserMsg;
        handleSend();
    }

    function renderMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;
        msgDiv.appendChild(bubble);
        messagesContainer.appendChild(msgDiv);
    }

    function scrollToBottom() {
        chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });
    }

    // ========== PERSONALITY PRESETS ==========
    function setupPersonalityPresets() {
        if (!personalityPresets) return;
        personalityPresets.addEventListener('click', (e) => {
            const card = e.target.closest('.preset-card');
            if (card) {
                const clickedPreset = card.dataset.preset;
                const presetNames = {
                    romantic: '💕 Romantic Partner',
                    career: '💼 Career Coach',
                    study: '📚 Study Buddy',
                    creative: '🎨 Creative Muse'
                };

                // Toggle: if clicking same preset, deactivate it
                if (state.personalityPreset === clickedPreset) {
                    state.personalityPreset = null; // Deactivate
                    saveState();
                    applyPersonalityPreset();
                    renderSuggestions();
                    showToast('Personality deactivated - using default Jaxon');
                } else {
                    state.personalityPreset = clickedPreset;
                    saveState();
                    applyPersonalityPreset();
                    renderSuggestions();
                    showToast(`Personality changed to ${presetNames[clickedPreset] || clickedPreset}`);
                }
            }
        });
    }

    function showToast(message, duration = 3000) {
        // Remove existing toast if any
        const existing = document.querySelector('.personality-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'personality-toast';
        toast.innerHTML = `<ion-icon name="checkmark-circle"></ion-icon> ${message}`;
        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => toast.classList.add('visible'), 10);

        // Remove after duration
        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // ========== MEMORY MANAGEMENT ==========
    async function saveMemoryToMem0() {
        const text = memoryInput.value.trim();
        if (!text) return;

        try {
            const response = await fetch(`${API_URL}/memory/import`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ facts: text.split('\n').filter(f => f.trim()) })
            });
            if (response.ok) {
                alert('Memories saved to Jaxon!');
                memoryInput.value = '';
                refreshMemories();
            }
        } catch (error) {
            console.error('Memory save error:', error);
            alert('Could not save memories. Is the backend running?');
        }
    }

    async function importMemoryFile(file) {
        const text = await file.text();
        let facts = [];

        if (file.name.endsWith('.json')) {
            try {
                const data = JSON.parse(text);
                facts = Array.isArray(data) ? data : data.facts || [];
            } catch { facts = text.split('\n').filter(f => f.trim()); }
        } else {
            facts = text.split('\n').filter(f => f.trim());
        }

        if (facts.length === 0) {
            alert('No facts found in file.');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/memory/import`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ facts })
            });
            if (response.ok) {
                alert(`Imported ${facts.length} memories!`);
                refreshMemories();
            }
        } catch (error) {
            console.error('Memory import error:', error);
            alert('Could not import memories. Is the backend running?');
        }
    }

    async function refreshMemories() {
        if (!memoriesList) return;
        memoriesList.innerHTML = '<p class="empty-hint">Loading...</p>';

        try {
            const response = await fetch(`${API_URL}/memory/recent`);
            const data = await response.json();
            state.recentMemories = data.memories || [];
            renderMemories();
        } catch (error) {
            console.error('Memory fetch error:', error);
            memoriesList.innerHTML = '<p class="empty-hint">Could not load memories. Is the backend running?</p>';
        }
    }

    function renderMemories() {
        if (!memoriesList) return;
        if (state.recentMemories.length === 0) {
            memoriesList.innerHTML = '<p class="empty-hint">No memories found.</p>';
            return;
        }

        memoriesList.innerHTML = '';
        state.recentMemories.slice(0, 20).forEach(mem => {
            const item = document.createElement('div');
            item.className = 'memory-item';
            item.innerHTML = `
                <span class="memory-text">${mem.memory || mem.text || mem}</span>
                <button class="delete-memory-btn" data-id="${mem.id || ''}">
                    <ion-icon name="close-outline"></ion-icon>
                </button>
            `;
            item.querySelector('.delete-memory-btn').addEventListener('click', () => deleteMemory(mem));
            memoriesList.appendChild(item);
        });
    }

    async function deleteMemory(mem) {
        state.deletedMemory = mem;
        state.recentMemories = state.recentMemories.filter(m => m !== mem);
        renderMemories();
        showUndoToast();

        // Actual deletion happens after undo timeout
        setTimeout(async () => {
            if (state.deletedMemory === mem) {
                try {
                    await fetch(`${API_URL}/memory/${mem.id}`, { method: 'DELETE' });
                } catch (error) { console.error('Delete error:', error); }
                state.deletedMemory = null;
            }
        }, 5000);
    }

    function showUndoToast() {
        if (!undoToast) return;
        undoToast.hidden = false;
        setTimeout(() => { undoToast.hidden = true; }, 5000);
    }

    function undoDelete() {
        if (state.deletedMemory) {
            state.recentMemories.unshift(state.deletedMemory);
            state.deletedMemory = null;
            renderMemories();
            undoToast.hidden = true;
        }
    }

    // ========== SIDEBAR & NAVIGATION ==========
    function toggleSidebar() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('visible');
    }

    function switchView(viewName) {
        navItems.forEach(n => n.classList.remove('active'));
        const targetNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);
        if (targetNav) targetNav.classList.add('active');

        views.forEach(view => {
            view.classList.remove('active');
            if (view.id === `view-${viewName}`) view.classList.add('active');
        });
    }

    // ========== EVENT LISTENERS ==========
    openSidebarBtn?.addEventListener('click', toggleSidebar);
    closeSidebarBtn?.addEventListener('click', toggleSidebar);
    overlay?.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('visible');
    });

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewName = item.dataset.view;
            switchView(viewName);
            if (window.innerWidth < 768) toggleSidebar();
        });
    });

    newChatBtn?.addEventListener('click', () => {
        createNewChat();
        switchView('chat');
        if (window.innerWidth < 768) toggleSidebar();
    });

    sendBtn?.addEventListener('click', handleSend);
    textarea?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    textarea?.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    themeBtn?.addEventListener('click', () => {
        state.darkMode = !state.darkMode;
        saveState();
        applyTheme();
    });

    darkModeToggle?.addEventListener('change', (e) => {
        state.darkMode = e.target.checked;
        saveState();
        applyTheme();
    });

    apiKeyInput?.addEventListener('change', (e) => {
        state.apiKey = e.target.value;
        saveState();
    });

    usernameInput?.addEventListener('change', (e) => {
        state.username = e.target.value;
        saveState();
    });

    savePersonalityBtn?.addEventListener('click', () => {
        state.personalityCustom = personalityInput.value;
        saveState();
        alert('Personality saved!');
    });

    saveMemoryBtn?.addEventListener('click', saveMemoryToMem0);
    memoryFileInput?.addEventListener('change', (e) => {
        if (e.target.files[0]) importMemoryFile(e.target.files[0]);
    });
    refreshMemoriesBtn?.addEventListener('click', refreshMemories);
    undoDeleteBtn?.addEventListener('click', undoDelete);

    clearDataBtn?.addEventListener('click', () => {
        if (confirm('Clear all local data? This cannot be undone.')) {
            localStorage.removeItem('jaxonState');
            location.reload();
        }
    });

    exportBtn?.addEventListener('click', () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state, null, 2));
        const a = document.createElement('a');
        a.href = dataStr;
        a.download = 'jaxon_data.json';
        a.click();
    });

    setupPersonalityPresets();

    // ========== INITIALIZE ==========
    loadState();
});
