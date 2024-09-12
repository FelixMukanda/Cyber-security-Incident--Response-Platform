import os
import re
import smtplib
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to send email alerts
def send_email_alert(subject, message):
    sender_email = "mukandafelix63@gmail.com"
    receiver_email = "felix.mukanda@strathmore.edu"
    password = "0000"

    # Set up the MIME structure
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the message content
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Connect to the Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email alert sent successfully!")
    except Exception as e:
        print(f"Failed to send email alert: {str(e)}")

# Function to monitor the log file
def monitor_log_file(log_file_path):
    # If file does not exist, wait until it does
    while not os.path.exists(log_file_path):
        print(f"Waiting for the log file: {log_file_path}")
        sleep(5)

    print(f"Monitoring log file: {log_file_path}")
    
    # Keep track of the file position
    with open(log_file_path, 'r') as log_file:
        # Move the cursor to the end of the file
        log_file.seek(0, os.SEEK_END)

        while True:
            line = log_file.readline()

            if not line:
                # If no new lines, wait and continue monitoring
                sleep(1)
                continue

            # Example patterns to detect (you can modify based on needs)
            if re.search(r"(error|unauthorized|failed login|attack detected)", line, re.IGNORECASE):
                print(f"Incident detected: {line.strip()}")
                send_email_alert("Security Alert: Incident Detected", line.strip())

# Main program entry
if __name__ == "__main__":
    log_file_path = "C:/Users/hp/Documents/GitHub/Cyber-security-Incident--Response-Platform/logfile.log"  # Specify the log file path

    try:
        monitor_log_file(log_file_path)
    except KeyboardInterrupt:
        print("Monitoring stopped.")
