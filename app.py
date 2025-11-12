
# app.py
from flask import Flask, request, jsonify
from predictor import EVPredictor 
from flask_cors import CORS
import os
import pandas as pd 

app = Flask(__name__)
CORS(app)

predictor = None 
GLOBAL_CAR_DATA = None 


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



@app.route('/predict', methods=['POST'])
def predict():
    if predictor is None or GLOBAL_CAR_DATA is None:
        return jsonify({'error': 'Prediction service or data is not available.'}), 500

    # Get user data from the POST request
    user_input_data = request.get_json()

    if not user_input_data:
        return jsonify({'error': 'No data provided in the request.'}), 400

    try:
        # 1. Call the predictor to get the segment
        predicted_segment = predictor.predict_segment(user_input_data)
        
        # 2. Filter the Database (The Recommendation Logic)
        recommendations_df = GLOBAL_CAR_DATA[GLOBAL_CAR_DATA['Segment'] == predicted_segment].copy()

        # 3. Optional: Apply max price filter if provided by the user
        # We look for 'PriceEuro' in the user data, assuming it represents a maximum budget
        max_price = user_input_data.get('PriceEuro')
        if max_price:
            recommendations_df = recommendations_df[recommendations_df['PriceEuro'] <= max_price]
        
        # 4. Prepare the final list of recommendations
        # Select key columns, sort by price, and return top 5
        recommendations = recommendations_df[[
            'Brand', 'Model', 'Range_Km', 'PriceEuro', 'BodyStyle', 'AccelSec'
        ]].sort_values(by='PriceEuro', ascending=True).head(5).to_dict('records') 

        return jsonify({
            'status': 'success',
            'predicted_segment': predicted_segment,
            'recommendations': recommendations
        })
        
    except Exception as e:
        # Return a clean error message to the user
        return jsonify({'error': f"Prediction failed due to processing issue: {str(e)}"}), 500


@app.route('/')
def home():
    return "EV Segment Predictor API is running. Send POST requests to /predict."

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)