from flask import Flask, render_template, jsonify, request
import matplotlib.pyplot as plt
import io
import base64
from model import load_model, predict_ddos, detect  # Assume model.py contains loading and prediction code
from database import fetch_prediction_summary, save_predictions, fetch_predictions  # Use the correct name 'fetch_predictions'


app = Flask(__name__)

# Global counters for incident response tracking
incidents_detected = 0
incidents_mitigated = 0

@app.route('/')
def display_predictions():
    # Get predictions from the database
    predictions = fetch_predictions()

    # Track incidents
    global incidents_detected, incidents_mitigated
    incidents_detected = sum([1 for pred in predictions if pred[2] == 1])  # Assuming 1 means attack detected
    incidents_mitigated = incidents_detected  # For simplicity, assume all incidents were mitigated

    prediction_summary = fetch_prediction_summary()  # Get summary data

    # Pass data to the template for rendering the bar chart
    return render_template('index.html', prediction_summary=prediction_summary)

    # Save the chart to a buffer
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('index.html', predictions=predictions, plot_url=plot_url)

@app.route('/predict', methods=['POST'])
def predict_and_respond():
    # Get network traffic data (in practice, this would be from live traffic)
    data = request.get_json()

    # Predict using the model
    prediction = predict_ddos(data)

    # Save the prediction to the database
    save_predictions(data, prediction)

    # Check if attack is predicted (1 means attack detected)
    if prediction == 1:
        apply_rate_limiting()  # Apply mitigation action
        return jsonify({"message": "DDoS attack detected and mitigated."}), 200

    return jsonify({"message": "Traffic normal."}), 200

def apply_rate_limiting():
    # Example function to apply rate limiting
    print("Rate limiting applied to suspicious IP.")

@app.route('/results', methods=['GET'])
def display_results():
    # Fetch predictions from the database
    predictions = fetch_predictions()  # Assume this fetches prediction records
    return render_template('index.html', predictions=predictions)
if __name__ == '__main__':
    app.run(debug=True)
