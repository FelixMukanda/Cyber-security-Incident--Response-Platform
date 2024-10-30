import joblib
import pandas as pd

# Define the expected feature names (use actual names used in training the model)
FEATURE_NAMES = ["dt", "switch", "pktcount", "bytecount", "dur", "dur_nsec", "tot_dur",
                 "flows", "packetins", "pktperflow", "byteperflow", "pktrate", 
                 "Pairflow", "tx_bytes", "rx_bytes", "tx_kbps", "rx_kbps", "tot_kbps"]

# Load the trained Random Forest model once
try:
    model = joblib.load('random_forest_model.sav')
    model_features = model.feature_names_in_  # Retrieve feature names from the model
except FileNotFoundError:
    raise Exception("Model file not found. Ensure 'random_forest_model.sav' exists in the directory.")

# Global log to capture print outputs
model_logs = []

def log_message(message):
    model_logs.append(message)
    print(message)  # Optional: keep this if you want console output as well

# Preprocess input data based on model requirements
def preprocess_data(data):
    features = [data.get(feature, 0) for feature in model_features]
    features_df = pd.DataFrame([features], columns=model_features)
    log_message("Data preprocessing completed.")
    return features_df

# Predict DDoS attack using the model
def predict_ddos(traffic_data):
    processed_data = preprocess_data(traffic_data)  # Preprocess input data
    prediction = model.predict(processed_data)
    prediction_result = int(prediction[0])  # Binary output: 0 = normal, 1 = attack
    log_message(f"Prediction: {'DDoS Attack' if prediction_result == 1 else 'Normal Traffic'}")
    return prediction_result

def calculate_traffic_rate(pktcount, duration):
    if duration <= 0:
        raise ValueError("Duration must be greater than zero.")
    traffic_rate = pktcount / duration  # packets per second
    log_message(f"Calculated traffic rate: {traffic_rate} packets/second")
    return traffic_rate

# Threshold-based detection function 
def detect(traffic_rate):
    threshold = 500  # Set a threshold for detection
    if traffic_rate > threshold:
        log_message(f"DDoS attack detected! Traffic rate: {traffic_rate}")
        return True
    else:
        log_message(f"No DDoS detected. Traffic rate: {traffic_rate}")
        return False

# Testing the model independently
if __name__ == "__main__":
    # Example traffic data dictionary to simulate the input from `ddos_simulation.py`
    sample_data = {"pktcount": 2000, "bytecount": 150, "dur": 2}  # Example values
    
    log_message("Calculating traffic rate...")
    traffic_rate = calculate_traffic_rate(sample_data["pktcount"], sample_data["dur"])

    log_message("Preprocessing data...")
    processed_data = preprocess_data(sample_data)
    

    log_message("Loading model and predicting...")
    prediction = predict_ddos(sample_data)
    log_message(f"Prediction: {'DDoS Attack' if prediction == 1 else 'Normal Traffic'}")
