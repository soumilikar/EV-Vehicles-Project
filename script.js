// script.js

const API_URL = 'http://127.0.0.1:5000/predict';
const form = document.getElementById('recommendation-form');
const resultsDiv = document.getElementById('results');

// List of all input IDs to extract data from the form
const INPUT_FIELDS = [
    'PriceEuro', 'Range_Km', 'AccelSec', 'BodyStyle',
    'TopSpeed_KmH', 'Efficiency_WhKm', 'FastCharge_KmH', 'Seats',
    'PowerTrain', 'PlugType', 'RapidCharge'
];

// --- API CALL FUNCTION ---

async function runApiPrediction(specs) {
    resultsDiv.innerHTML = '<h2>Loading Recommendation...</h2>';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(specs)
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            // Display Success Results
            displayResults(data.predicted_segment, data.recommendations);
        } else {
            // Display API Error
            const errorMessage = data.error || 'Unknown error.';
            resultsDiv.innerHTML = `<h2>Error</h2><p>API Error: ${errorMessage}</p>`;
        }
    } catch (error) {
        // Display Connection Error (e.g., API is not running)
        resultsDiv.innerHTML = `<h2>Connection Error</h2><p>Could not connect to the API server (${API_URL}). Please ensure **app.py** is running in a separate terminal.</p>`;
        console.error('Fetch error:', error);
    }
}

// --- MAIN FORM SUBMISSION LOGIC ---

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {};
    let allInputsValid = true;

    // Iterate over the defined fields to extract values accurately
    INPUT_FIELDS.forEach(id => {
        const element = document.getElementById(id);
        if (!element || !element.value) {
            allInputsValid = false;
            return;
        }

        // Use parseFloat for numerical/hidden fields; string for others
        if (element.type === 'number' || element.id.includes('Sec') || element.id.includes('Km') || element.id.includes('Euro')) {
            formData[id] = parseFloat(element.value);
        } else {
            formData[id] = element.value;
        }
    });

    if (allInputsValid) {
        // Run prediction using the data from the main form
        await runApiPrediction(formData);
    }
});


// --- RESULT RENDERING FUNCTION ---
function displayResults(segment, recommendations) {
    let html = `<h2>Prediction Results</h2>`;
    html += `<div class="segment-badge">Predicted Segment: ${segment}</div>`;

    if (recommendations.length === 0) {
        html += '<p>No models found in this segment that match your price filter.</p>';
    } else {
        html += `<h3>Top ${recommendations.length} Recommended Models:</h3>`;
        recommendations.forEach(car => {
            html += `
                <div class="car-card">
                    <h4>${car.Brand} ${car.Model}</h4>
                    <p>Price: <strong>€${car.PriceEuro.toLocaleString()}</strong></p>
                    <p>Range: ${car.Range_Km} km | 0-100km/h: ${car.AccelSec}s</p>
                </div>
            `;
        });
    }

    resultsDiv.innerHTML = html;
}