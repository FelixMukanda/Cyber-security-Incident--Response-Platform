import random
import time
from model import predict_ddos, detect  # This is your model
from database import save_predictions, log_incident  # Functions to log to the database

# Simulate network traffic
def simulate_traffic(server_ip, normal_traffic_rate, ddos_traffic_rate, is_ddos=False):
    """
    Simulates traffic to the server. If is_ddos is True, simulate DDoS traffic.
    """
    if is_ddos:
        traffic_rate = ddos_traffic_rate
        print(f"Simulating DDoS attack on {server_ip}...")
    else:
        traffic_rate = normal_traffic_rate
        print(f"Simulating normal traffic on {server_ip}...")

    while True:
        # Randomize traffic to simulate fluctuating traffic patterns
        requests_sent = random.randint(traffic_rate - 10, traffic_rate + 10)
        print(f"Simulating {requests_sent} requests to {server_ip}")
        """ddos_detected = detect(requests_sent)"""
        # Feed traffic data into the DDoS model
        ddos_detected = detect(traffic_rate=requests_sent)
        if ddos_detected:
            print("DDoS detected! Taking mitigation action...")
            # Log detection to the database
            log_incident(incident_type="DDoS Attack", status="Detected")
            # Take action (rate limit or reroute traffic)
            trigger_mitigation_action()
            # Log the mitigation
            log_incident(incident_type="DDoS Attack", status="Mitigated")

        # Log normal or attack traffic prediction
        save_predictions(actual_label='DDoS' if is_ddos else 'Normal', predicted_label='DDoS' if ddos_detected else 'Normal')

        time.sleep(1)

def trigger_mitigation_action():
    """
    Dummy function to represent traffic mitigation actions such as rate-limiting or rerouting.
    """
    print("Traffic is being limited or rerouted to prevent overload.")

# Example of running a test with DDoS traffic
if __name__ == "__main__":
    simulate_traffic(server_ip="192.168.1.10", normal_traffic_rate=100, ddos_traffic_rate=1000, is_ddos=True)
