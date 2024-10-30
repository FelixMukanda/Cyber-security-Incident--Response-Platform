from flask import Flask, render_template, jsonify, request
import mysql.connector
from model import predict_ddos, detect, model_logs
from database import fetch_predictions, fetch_prediction_summary, save_predictions
from ddos_simulation import simulation_logs  # Import simulation logs from ddos_simulation.py

app = Flask(__name__)

# Global counters for incident response tracking
incidents_detected = 0
incidents_mitigated = 0

# Function to fetch incidents
def fetch_incidents():
    connection = mysql.connector.connect(host='localhost', user='root', password='', database='cybersecurity_db')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM incidents")
        incidents = cursor.fetchall()
    connection.close()
    return incidents

@app.route('/')
def index():
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
        simulation_logs=simulation_logs,  # Pass logs to HTML
        model_logs=model_logs  # Pass logs to HTML
    )


@app.route('/predict', methods=['POST'])
def predict_and_respond():
    # Get network traffic data
    data = request.get_json()

    # Initial detection based on a threshold
    if detect(data.get("traffic_rate", 0)):
        apply_rate_limiting()  # Mitigation action
        return jsonify({"message": "DDoS attack detected by threshold and mitigated."}), 200

    # Further prediction using the trained model
    prediction = predict_ddos(data)
    save_predictions(data, prediction)  # Save to database

    if prediction == 1:
        apply_rate_limiting()  # Apply further mitigation if needed
        return jsonify({"message": "DDoS attack detected by model and mitigated."}), 200

    return jsonify({"message": "Traffic normal."}), 200

def apply_rate_limiting():
    print("Rate limiting applied to suspicious IP.")

@app.route('/results', methods=['GET'])
def display_results():
    # Fetch predictions from the database
    predictions = fetch_predictions()  # Assume this fetches prediction records
    return render_template('index.html', predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)
