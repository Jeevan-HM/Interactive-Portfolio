document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".card");

    // Dynamic 3D tilt effect for each project card
    cards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();

            // Get mouse position relative to the card
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Calculate center
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            // Calculate rotation amount based on mouse distance from center
            // The constraint here limits the rotation to a maximum of ~10 degrees
            const rotateX = ((y - centerY) / centerY) * -10;
            const rotateY = ((x - centerX) / centerX) * 10;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });

        // Reset card style smoothly when mouse leaves
        card.addEventListener("mouseleave", () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';

            // Clear inline styles after animation frame to ensure CSS transitions take over
            setTimeout(() => {
                card.style.transform = '';
            }, 500);
        });
    });

    // --- Chatbot Logic ---
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotToggleBtn = document.getElementById('chatbot-toggle-btn');
    const chatbotFloatingBtn = document.getElementById('chatbot-floating-btn');
    const chatbotHeader = document.getElementById('chatbot-header');
    const chatInput = document.getElementById('chat-input');
    const chatSubmitBtn = document.getElementById('chat-submit');
    const chatMessagesContainer = document.getElementById('chat-messages');

    let isChatbotOpen = false;

    // Toggle Chatbot
    const toggleChatbot = () => {
        isChatbotOpen = !isChatbotOpen;
        if (isChatbotOpen) {
            chatbotContainer.classList.add('active');
            chatInput.focus();
            chatbotFloatingBtn.style.transform = 'scale(0) rotate(90deg)';
            chatbotFloatingBtn.style.opacity = '0';
            setTimeout(() => chatbotFloatingBtn.style.pointerEvents = 'none', 300);
        } else {
            chatbotContainer.classList.remove('active');
            chatbotFloatingBtn.style.pointerEvents = 'auto';
            chatbotFloatingBtn.style.transform = 'scale(1) rotate(0deg)';
            chatbotFloatingBtn.style.opacity = '1';
        }
    };

    chatbotFloatingBtn.addEventListener('click', toggleChatbot);
    chatbotToggleBtn.addEventListener('click', toggleChatbot);
    chatbotHeader.addEventListener('click', (e) => {
        if (e.target !== chatbotToggleBtn && e.target.closest('.chatbot-toggle') === null) {
            toggleChatbot();
        }
    });

    // Handle user submitting message
    const addMessageToChat = (text, isUser = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

        if (isUser) {
            messageDiv.textContent = text;
        } else {
            messageDiv.innerHTML = text; // Gemini returns pre-formatted HTML 
        }

        chatMessagesContainer.appendChild(messageDiv);
        scrollToBottom();
    };

    const addLoader = () => {
        const loaderDiv = document.createElement('div');
        loaderDiv.className = 'message bot-message bot-loading';
        loaderDiv.innerHTML = `
            <div class="loader">
                <div class="loader-dot"></div>
                <div class="loader-dot"></div>
                <div class="loader-dot"></div>
            </div>
        `;
        chatMessagesContainer.appendChild(loaderDiv);
        scrollToBottom();
        return loaderDiv;
    };

    const scrollToBottom = () => {
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    };

    const sendMessage = async () => {
        const text = chatInput.value.trim();
        if (!text) return;

        // 1. Add UX updates for sending message
        chatInput.value = '';
        chatInput.focus();
        chatSubmitBtn.disabled = true;
        addMessageToChat(text, true);

        // 2. Add loading animation
        const loaderDiv = addLoader();

        try {
            // 3. Make the API Call to Flask backend
            const payload = { message: text };
            if (window.currentViewedFile) {
                payload.current_file = window.currentViewedFile;
                payload.current_code = window.currentViewedCode;
            }

            // Capture any text the user currently has highlighted on the screen
            const selection = window.getSelection();
            if (selection && selection.toString().trim()) {
                payload.selected_text = selection.toString().trim();
            }

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            // 4. Remove loader and display response
            loaderDiv.remove();

            if (response.ok && data.answer) {
                addMessageToChat(data.answer, false);
            } else {
                addMessageToChat(data.answer || "Sorry, I ran into an issue.", false);
            }
        } catch (error) {
            console.error("Chat Error:", error);
            loaderDiv.remove();
            addMessageToChat("Network error. Please try again.", false);
        } finally {
            chatSubmitBtn.disabled = false;
        }
    };

    chatSubmitBtn.addEventListener('click', sendMessage);

    // Also submit when pressing 'Enter' on keyboard
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevents line breaks
            sendMessage();
        }
    });
});
