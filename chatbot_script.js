// chatbot_script.js

const API_URL = 'http://127.0.0.1:5000/predict';
const chatMessages = document.getElementById('chat-messages');
const chatInputForm = document.getElementById('chat-input-form');
const chatInput = document.getElementById('chat-input');

// --- CHATBOT STATE ---
let chatState = {
    step: 'price', // 'price', 'range', 'ready'
    specs: {
        // Default values required by the ML model
        'PriceEuro': null,
        'Range_Km': null,
        'AccelSec': 7.0,
        'BodyStyle': "SUV", // Default category
        'TopSpeed_KmH': 180,
        'Efficiency_WhKm': 170,
        'FastCharge_KmH': 500,
        'Seats': 5,
        'PowerTrain': 'AWD',
        'PlugType': 'Type 2 CCS',
        'RapidCharge': 'Yes'
    }
};

// --- CHAT DISPLAY FUNCTIONS ---
function displayChatMessage(message, sender) {
    const msg = document.createElement('div');
    msg.classList.add('chat-message', `${sender}-message`);
    msg.innerHTML = message;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// --- API CALL FUNCTION (Chat-specific) ---
async function runApiPrediction(specs) {
    displayChatMessage('Running the prediction engine...', 'bot');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(specs)
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            const segment = data.predicted_segment;
            const recs = data.recommendations;

            let message = `✅ **Prediction Complete!** Based on your input, your ideal segment is the **${segment}**-Segment.`;

            if (recs.length > 0) {
                message += `<br><br>Here is the top recommendation in that segment:`;
                message += `<br>🚗 **${recs[0].Brand} ${recs[0].Model}**`;
                message += `<br>- Price: €${recs[0].PriceEuro.toLocaleString()}`;
                message += `<br>- Range: ${recs[0].Range_Km} km`;
            } else {
                message += `<br><br>No specific models were found in this segment with your filters.`;
            }

            displayChatMessage(message, 'bot');
        } else {
            displayChatMessage(`[API Error] Prediction failed: ${data.error || 'Unknown error.'}`, 'bot');
        }
    } catch (error) {
        displayChatMessage(`[Connection Error] Could not reach the API. Is app.py running?`, 'bot');
        console.error('Fetch error:', error);
    }

    // Reset state for a new conversation
    chatState.step = 'price';
}


// --- CHAT LOGIC ---

chatInputForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userInput = chatInput.value.trim();
    if (!userInput) return;

    displayChatMessage(userInput, 'user');
    chatInput.value = ''; // Clear input

    const numValue = parseFloat(userInput.replace(/[^0-9.]/g, '')); // Simple number extraction

    if (chatState.step === 'price' && !isNaN(numValue)) {
        chatState.specs.PriceEuro = numValue;
        chatState.step = 'range';
        displayChatMessage(`Got it! Max budget set to €${numValue.toLocaleString()}. Now, what is the **minimum range** you need (in km)?`, 'bot');
        chatInput.placeholder = "Type minimum range...";
    }
    else if (chatState.step === 'range' && !isNaN(numValue)) {
        chatState.specs.Range_Km = numValue;
        chatState.step = 'ready';
        chatInput.placeholder = "Type your max price..."; // Reset placeholder

        await runApiPrediction(chatState.specs);
    }
    else {
        displayChatMessage(`Sorry, I need a valid number for your ${chatState.step} requirement to proceed.`, 'bot');
    }
});