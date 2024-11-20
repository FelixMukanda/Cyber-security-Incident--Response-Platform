import random
import time
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging
from database import log_incident  # Ensure you have a `log_incident` function in your `database` module

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Load the model (ensure that your model file is available in the same directory)
model = joblib.load("random_forest_model.sav")
model_features = model.feature_names_in_

# Dictionaries to track blocked and rate-limited IPs
blocked_ips = set()
rate_limited_ips = {}

# Threshold for detecting abnormal traffic
THRESHOLD = 500  # Adjust based on your DDoS detection requirements

def generate_random_ip():
    """
    Generates a random IPv4 address.
    """
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def detect(traffic_rate, ip_address):
    """
    Detects if the traffic rate exceeds the threshold or if the IP is already mitigated.
    """
    if ip_address in blocked_ips:
        return True  # Treat blocked IPs as ongoing DDoS
    if ip_address in rate_limited_ips:
        return traffic_rate > rate_limited_ips[ip_address]  # Compare with rate limit
    return traffic_rate > THRESHOLD

def mitigate_ddos(ip_address, mitigation_type="block"):
    """
    Mitigates a DDoS attack by either blocking the IP or rate-limiting it.
    """
    if mitigation_type == "block":
        blocked_ips.add(ip_address)
        log_message(f"IP {ip_address} has been blocked.")
        log_incident(incident_type="DDoS Mitigation", status=f"Blocked IP: {ip_address}")
    elif mitigation_type == "rate_limit":
        rate_limited_ips[ip_address] = 50  # Example: Limit to 50 requests per second
        print(f"IP {ip_address} is now rate-limited.")
        log_incident(incident_type="DDoS Mitigation", status=f"Rate-limited IP: {ip_address}")
    else:
        print(f"Unknown mitigation type: {mitigation_type}")

def simulate_traffic(server_ip, normal_traffic_rate, ddos_traffic_rate, is_ddos=False):
    """
    Simulates traffic and applies mitigation strategies for detected DDoS attacks.
    """
    print(f"Simulating {'DDoS' if is_ddos else 'normal'} traffic on {server_ip}...")

    while True:
        ip_address = generate_random_ip()  # Generate random IP for each request batch

        if is_ddos:
            # DDoS traffic: High rate with random spikes
            requests_sent = random.randint(ddos_traffic_rate - 100, ddos_traffic_rate + 500)
        else:
            # Normal traffic: Gaussian distribution around normal rate
            requests_sent = max(1, int(random.gauss(normal_traffic_rate, 20)))

        log_message(f"Simulating {requests_sent} requests from {ip_address} to {server_ip}")

        # Emit traffic data to the frontend
        socketio.emit('traffic_update', {
            'timestamp': time.strftime("%H:%M:%S"),
            'traffic_rate': requests_sent,
            'traffic_type': 'DDoS' if is_ddos else 'Normal',
            'ip_address': ip_address
        })
        
        # Detect and mitigate DDoS attacks
        if detect(requests_sent, ip_address):
            log_message(f"DDoS detected from {ip_address}. Applying mitigation...")
            mitigation_type = "block" if is_ddos else "rate_limit"
            mitigate_ddos(ip_address, mitigation_type)

        # Random delay for natural traffic patterns
        time.sleep(random.uniform(0.5, 2.0))

def log_message(message):
    """
    Logs a message and emits it to the frontend via Socket.IO.
    """
    print(message)  # Print to console
    socketio.emit('log_update', {'message': message})  # Emit to frontend

@app.route('/')
def index():
    """
    Serves the frontend HTML for monitoring traffic.
    """
    return render_template('index2.html')  # Ensure this template exists

if __name__ == "__main__":
    # Simulation parameters
    server_ip = "192.168.1.10"  # Example server IP
    normal_traffic_rate = 100   # Normal traffic rate
    ddos_traffic_rate = 1000    # DDoS traffic rate
    is_ddos = True              # Set to True to simulate a DDoS attack

    # Start the traffic simulation in the background
    socketio.start_background_task(simulate_traffic, server_ip, normal_traffic_rate, ddos_traffic_rate, is_ddos)
    
    # Run the Flask-SocketIO app
    socketio.run(app, debug=True)
