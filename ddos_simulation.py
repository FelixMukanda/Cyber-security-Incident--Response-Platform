import random
import time
import joblib
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from database import log_incident  # Ensure you have a `log_incident` function in your `database` module

app = Flask(__name__)
socketio = SocketIO(app)

# Load the model (ensure that your model file is available in the same directory)
model = joblib.load("random_forest_model.sav")
model_features = model.feature_names_in_

# Dictionaries to track blocked and rate-limited IPs
blocked_ips = set()
rate_limited_ips = {}

# Simulation Parameters
normal_traffic_rate = 100   # Normal traffic rate
ddos_traffic_rate = 1000    # DDoS traffic rate
is_simulating_traffic = False  # Flag to control traffic simulation

def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def detect(traffic_rate, ip_address):
    if ip_address in blocked_ips:
        return True
    if ip_address in rate_limited_ips:
        return traffic_rate > rate_limited_ips[ip_address]
    return traffic_rate > 500  # Default threshold for DDoS detection

def mitigate_ddos(ip_address, mitigation_type="block"):
    if mitigation_type == "block":
        blocked_ips.add(ip_address)
        log_incident(incident_type="DDoS Mitigation", status=f"Blocked IP: {ip_address}")
    elif mitigation_type == "rate_limit":
        rate_limited_ips[ip_address] = 50
        log_incident(incident_type="DDoS Mitigation", status=f"Rate-limited IP: {ip_address}")

def simulate_traffic(traffic_type):
    global is_simulating_traffic
    is_simulating_traffic = True
    server_ip = "192.168.1.10"  # Example server IP
    while is_simulating_traffic:
        ip_address = generate_random_ip()
        if traffic_type == "ddos":
            requests_sent = random.randint(ddos_traffic_rate - 100, ddos_traffic_rate + 500)
        else:
            requests_sent = max(1, int(random.gauss(normal_traffic_rate, 20)))

        log_message(f"Simulating {requests_sent} requests from {ip_address} to {server_ip}.")
        
        socketio.emit('traffic_update', {
            'timestamp': time.strftime("%H:%M:%S"),
            'traffic_rate': requests_sent,
            'traffic_type': 'DDoS' if traffic_type == "ddos" else 'Normal',
            'ip_address': ip_address
        })
        
        if detect(requests_sent, ip_address):
            log_message(f"DDoS detected from {ip_address}. Applying mitigation...")
            mitigate_ddos(ip_address, "block" if traffic_type == "ddos" else "rate_limit")

        time.sleep(random.uniform(0.5, 2.0))

def log_message(message):
    print(message)
    socketio.emit('log_update', {'message': message})

@socketio.on('simulate_traffic')
def start_simulation(data):
    traffic_type = data.get('type', 'normal')
    if not is_simulating_traffic:
        socketio.start_background_task(simulate_traffic, traffic_type)

@socketio.on('stop_traffic')
def stop_simulation():
    global is_simulating_traffic
    is_simulating_traffic = False
    log_message("Traffic simulation stopped.")

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@app.route('/')
def index():
    return render_template('index2.html')

if __name__ == "__main__":
    socketio.run(app, debug=True)
