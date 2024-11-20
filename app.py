from flask import Flask, render_template, jsonify, request, abort
import mysql.connector
import subprocess
from model import predict_ddos, detect, model_logs
from database import fetch_predictions, fetch_prediction_summary, save_predictions
from ddos_simulation import simulate_traffic
from flask_socketio import SocketIO, emit
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)

# Route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Handle new client connection for real-time updates
@socketio.on('connect')
def handle_connect():
    print("Client connected")

# Start traffic simulation on a separate thread
@app.route('/start-simulation', methods=['POST'])
def start_simulation():
    try:
        # Update the path to your ddos_simulation.py as needed
        result = subprocess.run(
            ["python3", "ddos_simulation.py"],  # Ensure the path is correct
            text=True,
            capture_output=True
        )
        if result.returncode == 0:
            return jsonify({"message": "Simulation started successfully", "output": result.stdout}), 200
        else:
            return jsonify({"message": "Simulation failed", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"message": "Error starting simulation", "error": str(e)}), 500

# Global counters for incident response tracking
incidents_detected = 0
incidents_mitigated = 0

# Dictionary to track request timestamps for each IP
request_log = defaultdict(list)
blocklist = set()
REQUEST_LIMIT = 100  # Set the number of allowed requests
TIME_WINDOW = timedelta(seconds=60)  # Time window for rate limiting
BLOCK_DURATION = timedelta(minutes=5)  # Duration to block an IP
block_time = {}  # Dictionary to track when an IP was blocked

# Rate-limiting and DDoS mitigation
@app.before_request
def ddos_mitigation():
    client_ip = request.remote_addr

    # Check if the IP is blocked and the block duration
    if client_ip in blocklist:
        if datetime.now() < block_time[client_ip] + BLOCK_DURATION:
            abort(403)  # Deny access with a 403 Forbidden response
        else:
            # Remove IP from blocklist if block duration has expired
            blocklist.remove(client_ip)
            del block_time[client_ip]

    # Record the current time for this request
    current_time = datetime.now()
    request_log[client_ip].append(current_time)

    # Remove old timestamps outside of the time window
    request_log[client_ip] = [t for t in request_log[client_ip] if current_time - t <= TIME_WINDOW]

    # Check if the request count exceeds the limit
    if len(request_log[client_ip]) > REQUEST_LIMIT:
        blocklist.add(client_ip)
        block_time[client_ip] = current_time
        print(f"IP {client_ip} blocked due to potential DDoS attack.")
        abort(403)  # Deny access with a 403 Forbidden response

# Function to send email alerts
def send_email_alert(subject, message):
    sender = "your_email@example.com"
    receiver = "admin_email@example.com"
    password = "your_email_password"
    
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.example.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            print(f"Alert email sent to {receiver}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

# Function to fetch incidents from database
def fetch_incidents():
    connection = mysql.connector.connect(host='localhost', user='root', password='', database='cybersecurity_db')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM incidents")
        incidents = cursor.fetchall()
    connection.close()
    return incidents

# Route for incident logs page
@app.route('/incident-logs')
def incident_logs():
    return render_template('incident-logs.html')

# Trigger mitigation action for an IP
@app.route('/trigger_mitigation', methods=['POST'])
def trigger_mitigation():
    data = request.get_json()
    ip_address = data.get('ip_address')  # Get the IP address from the request payload

    if ip_address:
        # Add the IP to the blocklist and set block time
        blocklist.add(ip_address)
        block_time[ip_address] = datetime.now()
        print(f"Mitigation action triggered: IP {ip_address} blocked.")
        return jsonify({"message": f"IP {ip_address} has been blocked.", "status": "success"}), 200
    else:
        return jsonify({"message": "IP address not provided", "status": "error"}), 400

# Dashboard route to render the index page with data
@app.route('/')
def dashboard():
    predictions = fetch_predictions()
    incidents = fetch_incidents()
    incidents_mitigated = sum(1 for pred in predictions if pred[2] == 1)
    prediction_summary = fetch_prediction_summary()

    return render_template(
        'index.html',
        predictions=predictions,
        incidents=incidents,
        incidents_mitigated=incidents_mitigated,
        prediction_summary=prediction_summary,
        model_logs=model_logs,
    )

# Function to emit data in real-time using SocketIO
def emit_data(data):
    socketio.emit('new_data', data)

# Monitor traffic to detect high request counts
def monitor_traffic(request_count):
    if request_count > 1000:
        alert_message = f"High traffic detected: {request_count} requests"
        send_email_alert("DDoS Alert", alert_message)
        emit_data({"is_alert": True, "message": alert_message})

# Run the Flask app with SocketIO
if __name__ == '__main__':
    socketio.run(app, debug=True)
