
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
import os

class EVPredictor:
    def __init__(self, model_path='model.pkl', scaler_path='scaler.pkl', config_path='predictor_config.pkl'):
        self.model = None
        self.scaler = None
        self.training_columns = None
        self.numerical_cols = None
        self.categorical_cols = None
        self._load_config(config_path)
        self._load_artifacts(model_path, scaler_path)

    def _load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}. Please ensure it's created during training.")
        with open(config_path, 'rb') as config_file:
            config = pickle.load(config_file)
        self.numerical_cols = config['numerical_cols']
        self.categorical_cols = config['categorical_cols']
        self.training_columns = config['training_columns']

    def _load_artifacts(self, model_path, scaler_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
        
        with open(model_path, 'rb') as model_file:
            self.model = pickle.load(model_file)
        with open(scaler_path, 'rb') as scaler_file:
            self.scaler = pickle.load(scaler_file)
        print("Model and scaler loaded successfully within EVPredictor.")

    def predict_segment(self, user_input_dict: dict):
        if self.model is None or self.scaler is None or self.training_columns is None:
            raise RuntimeError("Predictor not fully initialized. Model, scaler, or config not loaded.")

        # Convert user input to DataFrame
        input_df = pd.DataFrame([user_input_dict])

        # 1. Handle numerical columns: ensure correct type and impute if necessary
        for col in self.numerical_cols:
            if col not in input_df.columns:
                input_df[col] = 0.0 # Add missing numerical column with a default value
            input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
            if input_df[col].isnull().any():
                # Fallback imputation if conversion to numeric resulted in NaNs
                print(f"Warning: Missing numerical value for {col} in input. Imputing with 0.0.")
                input_df[col] = input_df[col].fillna(0.0)

        # 2. One-hot encode categorical features
        # Ensure all categorical columns are present in the input_df for consistent encoding
        for col in self.categorical_cols:
            if col not in input_df.columns:
                input_df[col] = '' # Add missing categorical column as empty string for consistent encoding
        
        input_encoded = pd.get_dummies(input_df[self.categorical_cols], columns=self.categorical_cols, drop_first=True)

        # 3. Scale numerical features
        input_numerical_scaled = self.scaler.transform(input_df[self.numerical_cols])
        input_numerical_scaled_df = pd.DataFrame(input_numerical_scaled, columns=self.numerical_cols, index=input_df.index)

        # 4. Combine processed features
        input_processed = pd.concat([input_numerical_scaled_df, input_encoded], axis=1)

        # 5. Feature alignment
        final_input = input_processed.reindex(columns=self.training_columns, fill_value=0)
        
        # Make prediction
        prediction = self.model.predict(final_input)
        return prediction[0]

# Example of how to use the predictor:
# if __name__ == '__main__':
#     try:
#         predictor = EVPredictor()
#         sample_input = {
#             'PriceEuro': 60000,
#             'Range_Km': 400,
#             'TopSpeed_KmH': 200,
#             'AccelSec': 5.0,
#             'Efficiency_WhKm': 170,
#             'FastCharge_KmH': 700,
#             'PowerTrain': 'AWD',
#             'PlugType': 'Type 2 CCS',
#             'BodyStyle': 'SUV',
#             'Seats': 5
#         }
#         predicted_segment = predictor.predict_segment(sample_input)
#         print(f"Predicted Segment: {predicted_segment}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
