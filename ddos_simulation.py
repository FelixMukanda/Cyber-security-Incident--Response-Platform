import random
import time
import joblib
import numpy as np
import pandas as pd
from model import predict_ddos  # This is your model prediction function
from database import save_predictions, log_incident  # Functions to log to the database

# Load the model once
model = joblib.load("random_forest_model.sav")
model_features = model.feature_names_in_

# Global log to capture print outputs
simulation_logs = []

def log_message(message):
    simulation_logs.append(message)
    print(message)  # Optional: keep this if you want console output as well

# Simulate network traffic
# Set a threshold value for traffic rate to determine if it's considered abnormal
THRESHOLD = 500  # Adjust this based on your DDoS detection requirements

# Function to detect if the traffic rate indicates a potential DDoS attack
def detect(traffic_rate):
    """
    Checks if the traffic rate exceeds a predefined threshold to flag potential DDoS.
    """
    return traffic_rate > THRESHOLD

# Updated simulate_traffic to use detect function
def simulate_traffic(server_ip, normal_traffic_rate, ddos_traffic_rate, is_ddos=False):
    """
    Simulates traffic to the server. If is_ddos is True, simulate DDoS traffic.
    """
    traffic_rate = ddos_traffic_rate if is_ddos else normal_traffic_rate
    print(f"Simulating {'DDoS' if is_ddos else 'normal'} traffic on {server_ip}...")

    while True:
        requests_sent = random.randint(traffic_rate - 10, traffic_rate + 10)
        print(f"Simulating {requests_sent} requests to {server_ip}")

        # Use detect function to check if the requests_sent is above the threshold
        if detect(requests_sent):
            print("DDoS detected! Taking mitigation action...")
            log_incident(incident_type="DDoS Attack", status="Detected")
            trigger_mitigation_action(requests_sent)
            log_incident(incident_type="DDoS Attack", status="Mitigated")
        else:
            print("No action required. Traffic is normal.")

        # Log prediction outcome
        save_predictions('DDoS' if is_ddos else 'Normal', 'DDoS' if detect(requests_sent) else 'Normal')
        time.sleep(1)

def predict_ddos(traffic_data):
    traffic_df = pd.DataFrame([traffic_data], columns=model_features)
    prediction = model.predict(traffic_df)
    return prediction[0] == 1


def trigger_mitigation_action(traffic_rate):
    # Display feature names for debugging
    log_message("Model was trained with the following features:")
    log_message(", ".join(model_features))

    # Create traffic data dictionary and set 'pktcount' to the current traffic rate
    traffic_data = {feature: 0 for feature in model_features}
    traffic_data["pktcount"] = traffic_rate  # Set traffic rate for prediction

    # Format traffic data as a DataFrame with correct feature names
    processed_data = pd.DataFrame([traffic_data], columns=model_features)

    # Predict with the model
    action = model.predict(processed_data)

    # Check if the action indicates a DDoS attack
    if action[0] == 1:  # Model indicates DDoS
        log_message("Mitigation: Limiting traffic to prevent overload.")
    else:
        log_message("No action required. Traffic is normal.")

# Example of running a test with DDoS traffic
if __name__ == "__main__":
    server_ip = "192.168.1.10"  # Define server IP
    normal_traffic_rate = 100   # Normal traffic rate for simulation
    ddos_traffic_rate = 1000    # DDoS traffic rate for simulation
    is_ddos = True              # Set to True to simulate a DDoS attack

    simulate_traffic(server_ip=server_ip, normal_traffic_rate=normal_traffic_rate,
                     ddos_traffic_rate=ddos_traffic_rate, is_ddos=is_ddos)
