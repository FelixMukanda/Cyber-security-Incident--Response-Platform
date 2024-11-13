from flask import Flask, render_template, jsonify, request
import mysql.connector
from model import predict_ddos, detect, model_logs
from database import fetch_predictions, fetch_prediction_summary, save_predictions
from ddos_simulation import simulation_logs
from flask_socketio import SocketIO, emit
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)

# Global counters for incident response tracking
incidents_detected = 0
incidents_mitigated = 0

# Function to send email alerts
def send_email_alert(subject, body):
    sender = "your_email@gmail.com"
    receiver = "recipient_email@gmail.com"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, 'your_password')
        server.sendmail(sender, receiver, msg.as_string())

# Function to fetch incidents
def fetch_incidents():
    connection = mysql.connector.connect(host='localhost', user='root', password='', database='cybersecurity_db')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM incidents")
        incidents = cursor.fetchall()
    connection.close()
    return incidents
def fetch_prediction_data():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='cybersecurity_db'
    )
    cursor = connection.cursor()
    cursor.execute("SELECT id, actual_label, predicted_label FROM predictions")
    data = cursor.fetchall()
    connection.close()
    return data

@app.route('/incident-logs')
def incident_logs():
    # Fetch or prepare data if needed
    return render_template('incident-logs.html')

@app.route('/')
def dashboard():
    predictions = fetch_predictions()
    incidents = fetch_incidents()
    incidents_mitigated = sum(1 for pred in predictions if pred[2] == 1)
    prediction_summary = fetch_prediction_summary()
    prediction_data = fetch_prediction_data()
    

    return render_template(
        'index.html',
        predictions=predictions,
        incidents=incidents,
        incidents_mitigated=incidents_mitigated,
        prediction_summary=prediction_summary,
        simulation_logs=simulation_logs,
        model_logs=model_logs,
        prediction_data=prediction_data
    )

@socketio.on('connect')
def handle_connect():
    print("Client connected")

# Function to emit data in real-time
def emit_data(data):
    socketio.emit('new_data', data)

def monitor_traffic(request_count):
    if request_count > 1000:
        alert_message = f"High traffic detected: {request_count} requests"
        send_email_alert("DDoS Alert", alert_message)
        emit_data({"is_alert": True, "message": alert_message})

if __name__ == '__main__':
    socketio.run(app, debug=True)
