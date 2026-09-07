
# app.py
from flask import Flask, request, render_template
from predictor import EVPredictor
import pandas as pd

app = Flask(__name__)

predictor = None
GLOBAL_CAR_DATA = None

# Default values for the specs the forms don't ask the user about directly.
# These match what the original hidden form fields used.
DEFAULT_SPECS = {
    'AccelSec': 7.0,
    'BodyStyle': 'SUV',
    'TopSpeed_KmH': 180,
    'Efficiency_WhKm': 170,
    'FastCharge_KmH': 500,
    'Seats': 5,
    'PowerTrain': 'AWD',
    'PlugType': 'Type 2 CCS',
    'RapidCharge': 'Yes',
}

BODY_STYLES = ['SUV', 'Sedan', 'Hatchback', 'Liftback', 'Cabrio', 'Coupe', 'SPV', 'Pickup']

try:
    predictor = EVPredictor(model_path='model.pkl', scaler_path='scaler.pkl', config_path='predictor_config.pkl')
    print("EVPredictor initialized successfully.")

    # NOTE: Ensure ElectricCarData_Clean.csv is in the same directory!
    GLOBAL_CAR_DATA = pd.read_csv("ElectricCarData_Clean.csv")

    segment_counts = GLOBAL_CAR_DATA['Segment'].value_counts()
    segments_to_keep = segment_counts[segment_counts > 1].index
    GLOBAL_CAR_DATA = GLOBAL_CAR_DATA[GLOBAL_CAR_DATA['Segment'].isin(segments_to_keep)].copy()

    GLOBAL_CAR_DATA['FastCharge_KmH'] = GLOBAL_CAR_DATA['FastCharge_KmH'].replace('-', '0').astype(float)
    print("Car dataset loaded and cleaned successfully.")

except FileNotFoundError as e:
    print(f"Error loading required files: {e}. Please ensure model.pkl, scaler.pkl, predictor_config.pkl, AND ElectricCarData_Clean.csv are present.")
    predictor = None
except Exception as e:
    print(f"An unexpected error occurred during initialization: {e}")
    predictor = None


def run_prediction(user_input_data: dict):
    """Shared prediction + recommendation logic used by both the main form and the chat flow."""
    if predictor is None or GLOBAL_CAR_DATA is None:
        raise RuntimeError('Prediction service or data is not available.')

    # 1. Predict the segment
    predicted_segment = predictor.predict_segment(user_input_data)

    # 2. Filter the database for that segment
    recommendations_df = GLOBAL_CAR_DATA[GLOBAL_CAR_DATA['Segment'] == predicted_segment].copy()

    # 3. Optional max price filter (PriceEuro from the form is a string, so cast it)
    max_price_raw = user_input_data.get('PriceEuro')
    if max_price_raw not in (None, ''):
        try:
            max_price = float(max_price_raw)
            recommendations_df = recommendations_df[recommendations_df['PriceEuro'] <= max_price]
        except ValueError:
            pass

    # 4. Top 5 cheapest matches
    recommendations = recommendations_df[[
        'Brand', 'Model', 'Range_Km', 'PriceEuro', 'BodyStyle', 'AccelSec'
    ]].sort_values(by='PriceEuro', ascending=True).head(5).to_dict('records')

    return predicted_segment, recommendations


@app.route('/')
def home():
    return render_template('index.html', body_styles=BODY_STYLES)


@app.route('/predict', methods=['POST'])
def predict():
    if predictor is None or GLOBAL_CAR_DATA is None:
        return render_template('results.html', error='Prediction service or data is not available.')

    # Pull the fields the user actually filled in from the HTML form
    user_input_data = {
        'PriceEuro': request.form.get('PriceEuro'),
        'Range_Km': request.form.get('Range_Km'),
        'AccelSec': request.form.get('AccelSec'),
        'BodyStyle': request.form.get('BodyStyle'),
    }
    # Fill in the rest with defaults (previously hardcoded hidden inputs)
    for key, value in DEFAULT_SPECS.items():
        user_input_data.setdefault(key, value)

    try:
        predicted_segment, recommendations = run_prediction(user_input_data)
        return render_template('results.html', segment=predicted_segment, recommendations=recommendations)
    except Exception as e:
        return render_template('results.html', error=f'Prediction failed due to processing issue: {str(e)}')


# --- Chatbot flow, reimplemented as a plain multi-step HTML form (no JavaScript) ---

@app.route('/chat')
def chat_start():
    return render_template('chat_step_price.html')


@app.route('/chat/range', methods=['POST'])
def chat_range():
    price = request.form.get('PriceEuro', '')
    return render_template('chat_step_range.html', price=price)


@app.route('/chat/result', methods=['POST'])
def chat_result():
    if predictor is None or GLOBAL_CAR_DATA is None:
        return render_template('results.html', error='Prediction service or data is not available.', is_chat=True)

    user_input_data = {
        'PriceEuro': request.form.get('PriceEuro'),
        'Range_Km': request.form.get('Range_Km'),
    }
    for key, value in DEFAULT_SPECS.items():
        user_input_data.setdefault(key, value)

    try:
        predicted_segment, recommendations = run_prediction(user_input_data)
        return render_template(
            'results.html',
            segment=predicted_segment,
            recommendations=recommendations,
            is_chat=True,
            price=user_input_data['PriceEuro'],
            range_km=user_input_data['Range_Km'],
        )
    except Exception as e:
        return render_template('results.html', error=f'Prediction failed due to processing issue: {str(e)}', is_chat=True)


if __name__ == '__main__':
    app.run(debug=True)
