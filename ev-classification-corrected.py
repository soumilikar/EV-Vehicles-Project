import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import numpy as np
import pickle # Used to save the model and scaler

def run_ev_classification(file_path):
    # Load Dataset
    print("Loading dataset...")
    df = pd.read_csv(file_path)

    # --- Phase 1: Data Preparation and Cleaning ---

    # 1. FIX: Remove segments with only 1 instance to allow for proper stratification during splitting
    segment_counts = df['Segment'].value_counts()
    segments_to_keep = segment_counts[segment_counts > 1].index
    df = df[df['Segment'].isin(segments_to_keep)].copy()
    print(f"Cleaned data: Retained {len(df)} rows after removing single-instance segments.")

    # 2. Handle problematic 'FastCharge_KmH' column (Replace '-', convert to numeric)
    # Replace '-' with 0 (implying no fast charge or unknown) and convert to float
    df['FastCharge_KmH'] = df['FastCharge_KmH'].replace('-', '0').astype(float)

    # Select features (X) and target (y)
    y = df['Segment']
    # Drop identifier columns (Brand, Model) and the target (Segment)
    X = df.drop(['Segment', 'Brand', 'Model'], axis=1)

    # Define numerical and categorical columns
    numerical_cols = ['PriceEuro', 'Range_Km', 'TopSpeed_KmH', 'AccelSec', 'Efficiency_WhKm', 'FastCharge_KmH', 'Seats']
    # Select all remaining object columns (PowerTrain, PlugType, BodyStyle, RapidCharge)
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

    # One-Hot Encode Categorical Features
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

    # Standardize Numerical Features
    scaler = StandardScaler()
    X[numerical_cols] = scaler.fit_transform(X[numerical_cols])

    # --- Phase 2: Model Training and Evaluation ---

    # Split Data (using stratify=y now that single-instance segments are removed)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # Model Training: Random Forest Classifier (Class_weight='balanced' handles imbalanced segments)
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # Model Prediction and Evaluation
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)

    print("\n--- CLASSIFICATION MODEL RESULTS ---")
    print(f"Model Accuracy on Test Set: {accuracy:.4f}")
    print("\nClassification Report:\n", report)

    # --- Phase 3: Interpretation (Feature Importance) ---

    # Get Feature Importance
    feature_importances = pd.Series(model.feature_importances_, index=X.columns)
    # Sort and select top 10 features
    top_10_features = feature_importances.nlargest(10).sort_values(ascending=False)

    print("\n--- TOP 10 FEATURE IMPORTANCE (Defines the Car Segment) ---")
    print(top_10_features.to_markdown(numalign="left", stralign="left"))
    
    # --- Persistence and Integration ---
    # Save the trained model and scaler for use in the final application
    with open('model_rf_segment_classifier.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('scaler_segment_classifier.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    with open('model_features_list.pkl', 'wb') as f:
        pickle.dump(X.columns.tolist(), f)
    
    print("\n--- PERSISTENCE ---")
    print("Model, Scaler, and Feature List saved as .pkl files for integration.")


if __name__ == "__main__":
    # Ensure your ElectricCarData_Clean.csv is in the same directory as this script
    run_ev_classification("ElectricCarData_Clean.csv")