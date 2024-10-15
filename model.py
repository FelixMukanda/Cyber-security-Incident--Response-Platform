import joblib
import numpy as np

# Load the trained Random Forest model
def load_model():
    try:
        model = joblib.load('random_forest_model.sav')  # Load the saved model
        return model
    except FileNotFoundError:
        raise Exception("Model file not found. Make sure the model is trained and saved as 'random_forest_model.sav'.")

# Function to preprocess input data (if necessary)
# Modify this function based on the structure of your input data (e.g., network traffic)
def preprocess_data(data):
    # Assuming data is a dictionary of features. For example:
    # data = {"feature1": value1, "feature2": value2, ...}
    
    # Convert dictionary to a numpy array (you can adjust the structure based on your actual data)
    features = np.array(list(data.values())).reshape(1, -1)
    
    return features

# Function to predict DDoS attack using the model
def predict_ddos(data):
    model = load_model()  # Load the trained model
    processed_data = preprocess_data(data)  # Preprocess the input data
    prediction = model.predict(processed_data)  # Make prediction (e.g., 0 for normal, 1 for attack)
    
    # You may want to round predictions or apply thresholding for classification
    # In case of a regression model, you can use a threshold like this:
    # return 1 if prediction >= threshold else 0
    
    return int(prediction[0])  # Assuming binary classification (e.g., 0 = normal, 1 = attack)

def detect(traffic_rate):
    """
    Detects whether the incoming traffic rate suggests a DDoS attack.
    
    :param traffic_rate: Number of requests per second (traffic rate)
    :return: True if DDoS is detected, False otherwise
    """
    threshold = 500  # Set a threshold for DDoS detection
    if traffic_rate > threshold:
        print(f"DDoS attack detected! Traffic rate: {traffic_rate}")
        return True
    else:
        print(f"No DDoS detected. Traffic rate: {traffic_rate}")
        return False
